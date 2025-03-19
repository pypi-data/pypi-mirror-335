# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/11/1 09:45
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : inference_preprocessor.py
# @Software: PyCharm
"""
import os
import time
import bcelogger
import ray.data
import json
import re
import traceback
from urllib.parse import urlparse

from ray.data.preprocessor import Preprocessor
from tritonv2.client_factory import TritonClientFactory
from tritonv2.constants import LimiterConfig, RequestRateDuration
from windmillclient.client.windmill_client import WindmillClient
from windmillendpointv1.client.endpoint_api import parse_endpoint_name, CreateEndpointRequest
from windmillendpointv1.client.endpoint_api_deploy_job import get_template_parameters
from windmillendpointv1.client.endpoint_api_deployment import get_deployment_name
from windmillendpointv1.client.endpoint_api_endpoint_hub import CreateEndpointHubRequest

from windmilltrainingv1.client.training_api_job import parse_job_name
from windmillmodelv1.client.model_api_model import PreferModelServerParameters, parse_model_name

from windmillcomputev1.filesystem import init_py_filesystem
from windmillartifactv1.client.artifact_api_artifact import parse_artifact_name
from windmillcategoryv1.client.category_api import match

from vistudio_image_analysis.operator.infer import Infer
from vistudio_image_analysis.datasource import mongo_query_pipeline
from vistudio_image_analysis.util.label import random_color
from vistudio_image_analysis.util import string
from vistudio_image_analysis.datasource.image_datasource import CityscapesImageDatasource
from vistudio_image_analysis.datasource.sharded_mongo_datasource import ShardedMongoDatasource
from vistudio_image_analysis.operator.label_formatter import LabelFormatter
from vistudio_image_analysis.util.filter import filter_image_by_artifact_name
from vistudio_image_analysis.table.image import INFER_STATE_INFERED
from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name

deployments = {
    "nvidia": "",
    "kunlun": "workspaces/public/endpointhubs/default/deployments/triton-kunlun"
}

multimodal_port = str(os.environ.get('MULTIMODAL_PORT', '8312'))
multimodal_endpoint_name = str(os.environ.get("MULTIMODAL_ENDPOINT_NAME", ''))
multimodal_batch_size = int(os.environ.get("MULTIMODAL_BATCH_SIZE", "1"))
multimodal_concurrency = int(os.environ.get("MULTIMODAL_CONCURRENCY", "1"))


class InferencePreprocessor(Preprocessor):
    """
    InferencePreprocessor
    """

    def __init__(self, config, operator_params):
        self._is_fittable = True
        self._fitted = True
        self.config = config
        self.operator_params = operator_params

        self.q = operator_params["q"]
        self.artifact_name = operator_params["artifact_name"]
        self.annotation_set_name = operator_params["annotation_set_name"]

        self.datasource = self._get_datasource()
        self.annotation_client = AnnotationClient(
            endpoint=self.config.vistudio_endpoint,
            context=self.config.bce_client_context
        )
        self.windmill_client = WindmillClient(
            endpoint=self.config.windmill_endpoint,
            context=self.config.bce_client_context
        )

        self._get_labels()
        self.operator_params['job_created_at'] = self._get_job_time()

        self._py_fs = init_py_filesystem(self.config.filesystem)

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        is_multimodal = match(self.annotation_set_category, "Multimodal")
        use_public = "workspaces/public/modelstores/default" in self.artifact_name

        if is_multimodal and use_public:
            server_uri = self._get_multimodal_endpoint_uri()
            self.stats_ = self._multimodal_inference(ds, server_uri)
        else:
            self._create_endpoint_job()
            try:
                server_uri = self._get_endpoint_uri()
                if is_multimodal:
                    self.stats_ = self._multimodal_inference(ds=ds, server_uri=server_uri)
                else:
                    self.stats_ = self._model_inference(ds=ds, server_uri=server_uri)
            finally:
                self.undeploy_endpoint()
        return self

    def _get_multimodal_endpoint_uri(self):
        """
        get_multimodal_endpoint_uri
        """
        bcelogger.info("_get_multimodal_endpoint_uri "
                       "multimodal_endpoint_name:{}"
                       " multimodal_batch_size:{} "
                       "multimodal_concurrency:{}".format(multimodal_endpoint_name,
                                                          multimodal_batch_size,
                                                          multimodal_concurrency))
        # get deploy_endpoint_job  TODO 暂时注释， endpoint_name 固定
        if multimodal_endpoint_name == '':
            deploy_endpoint_job_response = self.windmill_client.list_deploy_endpoint_job(
                workspace_id='public',
                endpoint_hub_name='default',
                kind="Deploy",
                artifact_name=self.artifact_name,
            )
            if deploy_endpoint_job_response is None:
                self.update_annotation_job("未检测到推理服务，请检查服务")
                raise Exception("未检测到推理服务，请检查服务")

            deploy_endpoint_job = deploy_endpoint_job_response.result[0]
            bcelogger.info(f"deploy_endpoint_job: {deploy_endpoint_job}")

            # check endpoint
            ep_workspace_id = deploy_endpoint_job['workspaceID']
            ep_hub_name = deploy_endpoint_job['endpointHubName']
            ep_local_name = deploy_endpoint_job['endpointName']

        else:
            ep_name = parse_endpoint_name(multimodal_endpoint_name)
            ep_workspace_id = ep_name.workspace_id
            ep_hub_name = ep_name.endpoint_hub_name
            ep_local_name = ep_name.local_name

        endpoint_info = self.windmill_client.get_endpoint(
            workspace_id=ep_workspace_id,
            endpoint_hub_name=ep_hub_name,
            local_name=ep_local_name
        )
        if endpoint_info is None:
            self.update_annotation_job("未正常获取到推理服务信息，请检查服务")
            raise Exception("未正常获取到推理服务信息，请检查服务")

        # check endpoint status
        monitor_info = self.windmill_client.get_endpoint_status(
            workspace_id=ep_workspace_id,
            endpoint_hub_name=ep_hub_name,
            local_name=ep_local_name
        )
        if monitor_info.deploymentStatus != "Completed" or monitor_info.status != "Available":
            bcelogger.error(f"get_endpoint_status resp: {monitor_info}")
            self.update_annotation_job("推理服务未正常上线，请检查服务")
            raise Exception("推理服务未正常上线，请检查服务")

        bcelogger.info(f"服务正常，Good News! endpoint uri: {endpoint_info.uri}")
        return endpoint_info.uri

    def _multimodal_inference(self, ds, server_uri):
        """
        _multimodal_inference
        """
        bcelogger.info("开始推理.....................operator_params:{} "
                       "multimodal_batch_size:{}"
                       " multimodal_concurrency:{}".format(self.operator_params,
                                                           multimodal_batch_size,
                                                           multimodal_concurrency))
        # 修改端口
        parsed_uri = urlparse(server_uri)
        server_uri = server_uri.replace(str(parsed_uri.port), multimodal_port)

        image_ids = list()
        try:
            image_ids = ds.unique(column="image_id")

            # 进行推理
            infer_operator = Infer(config=self.config, operator_params=self.operator_params)
            infer_annotation_ds = ds.map_batches(
                lambda batch: infer_operator.batch_lmdeploy_inference_single_chat(batch, server_uri),
                batch_size=multimodal_batch_size,
                batch_format="pandas",
                concurrency=multimodal_concurrency
            ).drop_columns(cols=['annotations']) \
                .filter(lambda x: x['lmdeploy_status'] is not None and x['lmdeploy_status'] == 'succeed')
            annotation_ds = infer_operator.to_vistudio_v1(
                ds=infer_annotation_ds,
                annotation_set_id=self.annotation_set_id,
                annotation_set_category=self.annotation_set_category,
            )

            # 数据入库
            annotation_ds.write_mongo(uri=self.config.mongo_uri,
                                      database=self.config.mongodb_database,
                                      collection=self.config.mongodb_collection)

            self.update_infer_state(image_ids=image_ids)
            return ds
        except Exception as e:
            bcelogger.error(f"data_processing_pipeline run error: {e}")
            bcelogger.error(f"Traceback: {traceback.format_exc()}")
            self.delete_annotation(image_ids=image_ids)
            raise Exception("data_processing_pipeline run error")

    def _create_endpoint_job(self):
        """
        create_endpoint_job
        """
        artifact_name = parse_artifact_name(self.artifact_name)
        model_name = parse_model_name(artifact_name.object_name)

        # 创建endpoint hub
        try:
            self.windmill_client.create_endpoint_hub(CreateEndpointHubRequest(
                workspaceID=model_name.workspace_id,
                localName=model_name.model_store_name,
                description="auto created by data processing"
            ))
        except Exception as e:
            if e.last_error.status_code == 409:
                pass
            else:
                raise ValueError(f"create endpoint_hub error: {e}")

        # 创建endpoint
        if len(model_name.local_name) >= 36:
            model_name.local_name = model_name.local_name[:35]
        endpoint_local_name = model_name.local_name + artifact_name.version
        try:
            endpoint_resp = self.windmill_client.get_endpoint(workspace_id=model_name.workspace_id,
                                                             endpoint_hub_name=model_name.model_store_name,
                                                             local_name=endpoint_local_name)
        except Exception as e:
            if e.last_error.status_code == 404:
                endpoint_resp = self.windmill_client.create_endpoint(CreateEndpointRequest(
                    workspaceID=model_name.workspace_id,
                    endpointHubName=model_name.model_store_name,
                    localName=endpoint_local_name,
                    displayName=endpoint_local_name,
                    description="auto created by data processing",
                    kind="Endpoint"))
            else:
                raise ValueError(f"create endpoint error: {e}")

        # 获取model信息
        try:
            model_resp = self.windmill_client.get_model(workspace_id=model_name.workspace_id,
                                                     model_store_name=model_name.model_store_name,
                                                     local_name=model_name.local_name)
        except Exception as e:
            raise ValueError(f"The selected model is not exist{e}")

        if model_resp.preferModelServerParameters is not None:
            accelerator = model_resp.preferModelServerParameters["resource"]["accelerator"]

        # 根据accelerator选择不同的deployment_name
        server_kind = "Triton"
        if match(self.annotation_set_category, "Multimodal"):
            server_kind = "LMDeploy"
        self.deployment_name = get_deployment_name(accelerator, deployments, server_kind)

        # 更新endpoint的tags
        tags = self.update_endpoint_tags(tags=endpoint_resp.tags, annotation_set_id=self.annotation_set_id)
        endpoint_name = parse_endpoint_name(endpoint_resp.name)
        try:
            self.windmill_client.update_endpoint(
                workspace_id=endpoint_name.workspace_id,
                endpoint_hub_name=endpoint_name.endpoint_hub_name,
                local_name=endpoint_name.local_name,
                tags=tags
            )
        except Exception as e:
            raise ValueError(f"update endpoint failed: {e}")

        # 创建endpoint job
        template_parameters = get_template_parameters(
            PreferModelServerParameters(**model_resp.preferModelServerParameters))
        template_parameters["hpa.enabled"] = "true"
        try:
            deploy_endpoint_job_response = self.windmill_client.create_deploy_endpoint_job(
                workspace_id=model_name.workspace_id,
                endpoint_hub_name=model_name.model_store_name,
                endpoint_name=endpoint_local_name,
                kind="Deploy",
                policy="IfNotPresent",
                artifact_name=self.artifact_name,
                spec_name=self.deployment_name,
                template_parameters=template_parameters,
                resource_tips=[f"tags.accelerator={accelerator}"],
            )
            self.endpoint_name = endpoint_resp.name
            bcelogger.info(f"deploy job succeed! deploy_endpoint_job_response: {deploy_endpoint_job_response}")
            time.sleep(5)
        except Exception as e:
            raise ValueError(f"create endpoint job failed: {e}")

    def update_endpoint_tags(self, tags: dict, annotation_set_id: str):
        """
        update_endpoint_tags
        """
        key = f"skill-{annotation_set_id}"
        value = "Using"

        if tags is None:
            tags = {}

        tags[key] = value
        return tags

    def _get_decoded_json_arg(self, arg):
        """
        _get_decoded_json_arg
        :return:
        """
        if arg is not None and arg != '':
            decoded_json = json.loads(string.decode_from_base64(arg))
        else:
            decoded_json = None
        bcelogger.info(f"{arg}: decoded_json")
        return decoded_json

    def _get_datasource(self):
        """
        get datasource
        :return:
        """
        pipeline = self._get_decoded_json_arg(self.q)
        if pipeline is None:
            return
        func = mongo_query_pipeline.get_pipeline_func(pipeline)

        return ShardedMongoDatasource(uri=self.config.mongo_uri,
                                      database=self.config.mongodb_database,
                                      collection=self.config.mongodb_collection,
                                      pipeline_func=func,
                                      shard_username=self.config.mongodb_shard_username,
                                      shard_password=self.config.mongodb_shard_password)

    def check_status(self, endpoint_name: str) -> bool:
        """
        check_status
        """
        ep_name = parse_endpoint_name(name=endpoint_name)

        monitor_info = self.windmill_client.get_endpoint_status(
            workspace_id=ep_name.workspace_id,
            endpoint_hub_name=ep_name.endpoint_hub_name,
            local_name=ep_name.local_name)
        bcelogger.info("check_status_monitor_info monitor_info:{}".format(monitor_info))

        if monitor_info.deploymentStatus == "Init" or monitor_info.deploymentStatus == "Progressing":
            bcelogger.info("check_status endpoint 部署中....")
            return None

        if monitor_info.deploymentStatus == "Failed":
            bcelogger.info("check_status endpoint 部署失败")
            return False

        if monitor_info.deploymentStatus == "Completed" and monitor_info.status == "NotAvailable":
            bcelogger.info("check_status 服务异常，请及时排查问题")
            return False

        if monitor_info.deploymentStatus == "Completed" and monitor_info.status == "Available":
            bcelogger.info("check_status 服务上线了，Good News!")
            return True
        else:
            return None

    def get_model_metadata_with_retry(self, server_uri, model_name, max_retries=3, delay=5):
        """
        get_model_metadata_with_retry
        """
        triton_client = TritonClientFactory.create_http_client(
            server_url=server_uri,
            limiter_config=LimiterConfig(limit=10, interval=RequestRateDuration.SECOND, delay=True),
        )
        retries = 0
        while retries < max_retries:
            try:
                # 尝试获取输入和输出的详细信息
                input_metadata, output_metadata, batch_size = triton_client.get_inputs_and_outputs_detail(
                    model_name=model_name)
                bcelogger.info(f"get_model_metadata_with_retry Success: {input_metadata},"
                               f" {output_metadata}, {batch_size}")
                return input_metadata, output_metadata, batch_size
            except Exception as e:
                retries += 1
                bcelogger.info(f"get_model_metadata_with_retry Error: {e}. Retrying {retries}/{max_retries}...")
                # 如果达到最大重试次数，抛出异常
                if retries == max_retries:
                    raise e
                # 延迟一段时间后重试
                time.sleep(delay)

    def _get_endpoint_uri(self):
        """
        _get_endpoint_uri
        """
        start_time = time.time()
        deploy_suc = None
        while time.time() - start_time < 150:
            deploy_suc = self.check_status(endpoint_name=self.endpoint_name)
            if deploy_suc is None:
                time.sleep(5)
                continue
            else:
                break

        if deploy_suc is None or not deploy_suc:
            self.update_annotation_job("推理服务未正常启动，请检查服务")
            bcelogger.info("模型部署失败 endpoint_name:{}".format(self.endpoint_name))
            raise Exception("推理服务未正常启动，请检查服务")

        endpoint_name = parse_endpoint_name(name=self.endpoint_name)
        endpoint_info = self.windmill_client.get_endpoint(
            workspace_id=endpoint_name.workspace_id,
            endpoint_hub_name=endpoint_name.endpoint_hub_name,
            local_name=endpoint_name.local_name
        )
        bcelogger.info(f"get_endpoint endpoint_info: {endpoint_info}")
        if endpoint_info is None:
            self.update_annotation_job("未正常获取到推理服务信息，请检查服务")
            raise Exception("未正常获取到推理服务信息，请检查服务")

        bcelogger.info(f"get endpoint uri: {endpoint_info.uri}")
        return endpoint_info.uri

    def _model_inference(self, ds, server_uri):
        """
        _model_inference
        小模型推理
        """
        bcelogger.info("开始推理.....................")
        image_ids = []
        try:
            filter_image_ds = filter_image_by_artifact_name(source=ds, artifact_name=self.artifact_name)
            file_uris = filter_image_ds.unique(column="file_uri")
            if len(file_uris) == 0:
                bcelogger.info("filter_image_by_artifact_name .file_uris is blank")
                return
            image_ids = filter_image_ds.unique(column="image_id")

            # 进行标签校验
            skill_labels = self._get_skill_labels()
            label_formatter = LabelFormatter(labels=self.labels)
            need_insert_labels = label_formatter.get_need_add_labels(import_labels=skill_labels)
            bcelogger.info("need_insert_labels:{}".format(need_insert_labels))

            self.import_labels(need_add_labels=need_insert_labels)
            bcelogger.info("after_insert_labels:{}".format(need_insert_labels))
            self._get_labels()
            bcelogger.info("after_insert_labels:{}".format(self.labels))

            # 进行推理
            server_uri = os.path.join(server_uri.replace("http://", ""), "http")
            input_metadata, output_metadata, batch_size = self.get_model_metadata_with_retry(
                server_uri=server_uri, model_name="ensemble")
            infer_operator = Infer(config=self.config, operator_params=self.operator_params)
            cityscapes_datasource = CityscapesImageDatasource(paths=file_uris, filesystem=self._py_fs)
            infer_annotation_ds = ray.data.read_datasource(datasource=cityscapes_datasource).map(
                lambda row: infer_operator.triton_inference_picture(
                    image=row['image'],
                    file_name=row['image_name'],
                    server_uri=server_uri,
                    input_metadata=input_metadata,
                    output_metadata=output_metadata
                ), concurrency=8). \
                filter(lambda x: x['prediction_status'] is not None and x['prediction_status'] == 'succeed')

            annotation_ds = infer_operator.to_vistudio_v1(
                ds=infer_annotation_ds,
                annotation_set_id=self.annotation_set_id,
                annotation_labels=self.labels,
                annotation_set_category=self.annotation_set_category
            )

            # 数据入库
            annotation_ds.write_mongo(uri=self.config.mongo_uri,
                                      database=self.config.mongodb_database,
                                      collection=self.config.mongodb_collection)
            self.update_infer_state(image_ids=image_ids)
            return ds
        except Exception as e:
            bcelogger.error(f"data_processing_pipeline run error: {e}")
            bcelogger.error(f"Traceback: {traceback.format_exc()}")
            self.delete_annotation(image_ids=image_ids)
            raise Exception("data_processing_pipeline run error")

    def update_infer_state(self, image_ids: list()):
        """
        update_infer_state
        """
        bcelogger.info("update_infer_state image_ids:{}".format(image_ids))
        self.datasource.get_collection().update_many(
            {'image_id': {'$in': image_ids},
             'data_type': 'Image',
             'annotation_set_id': self.annotation_set_id},  # 查询条件：image_id 在给定的列表中
            {'$set': {'infer_state': INFER_STATE_INFERED}}
        )

    def delete_annotation(self, image_ids: list()):
        """
        delete_annotation
        """
        delete_query = {
            'annotation_set_id': self.annotation_set_id,
            "image_id": {"$in": image_ids},
            "task_kind": "Model",
            "artifact_name": self.artifact_name,
            "data_type": "Annotation",
            "job_name": self.config.job_name.split('/')[-1],
        }
        result = self.datasource.get_collection().delete_many(delete_query)
        bcelogger.info("delete_annotation result:{}".format(result))

    def undeploy_endpoint(self):
        """
        undeploy_endpoint
        """
        bcelogger.info("undeploy job.....................")

        # 首先判断服务状态
        ep_name = parse_endpoint_name(name=self.endpoint_name)
        endpoint_info = self.windmill_client.get_endpoint(
            workspace_id=ep_name.workspace_id,
            endpoint_hub_name=ep_name.endpoint_hub_name,
            local_name=ep_name.local_name)
        bcelogger.info(f"endpoint info:{endpoint_info}")

        tags = endpoint_info.tags
        key = 'skill-' + self.annotation_set_id

        if key not in endpoint_info.tags:
            found = any(key.startswith("skill-") and value == "Using" for key, value in tags.items())
            if not found:
                bcelogger.info("[Using][skill-] tag not in endpoint tags.")
                need_undeploy = True
            else:
                need_undeploy = False
        else:
            v = endpoint_info.tags.get(key)
            if v == 'Using':
                tags[key] = 'Used'
                bcelogger.info("更新endpoint tag. endpoint_name:{}".format(self.endpoint_name))
                self.windmill_client.update_endpoint(
                    workspace_id=ep_name.workspace_id,
                    endpoint_hub_name=ep_name.endpoint_hub_name,
                    local_name=ep_name.local_name,
                    tags=tags
                )
            found = any(key.startswith("skill-") and value == "Using" for key, value in tags.items())
            if not found:
                need_undeploy = True
            else:
                need_undeploy = False

        if need_undeploy:
            # 这里不再判断状态 直接去卸载
            bcelogger.info("卸载endpoint endpoint_name:{}".format(self.endpoint_name))
            self.windmill_client.create_deploy_endpoint_job(
                workspace_id=ep_name.workspace_id,
                endpoint_hub_name=ep_name.endpoint_hub_name,
                endpoint_name=ep_name.local_name,
                artifact_name=self.artifact_name,
                spec_name=self.deployment_name,
                kind="Undeploy",
            )

    def _get_job_time(self):
        """
        get data processing job
        """
        job_name = parse_job_name(self.config.job_name)
        job_resp = self.windmill_client.get_job(
            workspace_id=job_name.workspace_id,
            project_name=job_name.project_name,
            local_name=job_name.local_name
        )
        bcelogger.info("get job resp is {}".format(job_resp))

        from dateutil import parser
        import pytz

        dt = parser.isoparse(job_resp.createdAt)
        # 如果时间字符串包含 'Z'，表示 UTC，需要将其调整为 UTC 时区
        dt = dt.astimezone(pytz.UTC)
        # 获取秒级时间戳并转换为纳秒
        timestamp_in_nanoseconds = int(dt.timestamp() * 1_000_000_000)
        # 补充纳秒部分
        nanoseconds = dt.microsecond * 1_000
        # 得到完整的纳秒时间戳
        full_nanosecond_timestamp = timestamp_in_nanoseconds + nanoseconds
        return full_nanosecond_timestamp

    def update_annotation_job(self, err_msg):
        """
        更新标注任务状态
        """
        job_name = parse_job_name(self.config.job_name)
        job_resp = self.windmill_client.get_job(
            workspace_id=job_name.workspace_id,
            project_name=job_name.project_name,
            local_name=job_name.local_name
        )
        bcelogger.info("get job resp is {}".format(job_resp))
        tags = job_resp.tags
        if tags is None or len(tags) == 0:
            tags = {"errMsg": err_msg}
        else:
            tags['errMsg'] = err_msg

        update_job_resp = self.windmill_client.update_job(
            workspace_id=job_name.workspace_id,
            project_name=job_name.project_name,
            local_name=job_name.local_name,
            tags=tags,
        )
        bcelogger.info("update job resp is {}".format(update_job_resp))

    def _get_labels(self):
        """
        get annotation labels
        :return:
        """
        try:
            as_name = parse_annotation_set_name(self.annotation_set_name)
            as_data = self.annotation_client.get_annotation_set(
                workspace_id=as_name.workspace_id,
                project_name=as_name.project_name,
                local_name=as_name.local_name,
            )
        except Exception as e:
            bcelogger.error(f"get labels error: {e}, annotation_set_name:{self.annotation_set_name}")
            raise Exception(f"get labels error. annotation_set_name:{self.annotation_set_name}")

        annotation_labels = as_data.labels
        labels = list()
        if annotation_labels is not None:
            for label in annotation_labels:
                labels.append(
                    {
                        "local_name": label.get("localName", None),
                        "display_name": label.get("displayName", None),
                        "parent_id": label.get("parentID", None),
                    }
                )
        self.labels = labels
        self.annotation_set_id = as_data.id
        self.annotation_set_category = as_data.category.get("category")

    def _get_skill_labels(self) -> list():
        """
        _get_model_labels
        labels:[{"id":1, name:"cat", displayName:""}]
        return:
        """
        if self.artifact_name is None:
            return []
        artifact_resp = None
        skill_labels = list()
        try:
            artifact_resp = self.windmill_client.get_artifact(name=self.artifact_name)
            bcelogger.info("get_artifact resp:{} artifact_name:{}".format(artifact_resp, self.artifact_name))
            labels = artifact_resp.metadata.get("labels", [])
            bcelogger.info("skill_label_from_model labels:{}".format(labels))
            for label in labels:
                skill_labels.append(
                    {
                        "local_name": str(label.get("id")),
                        "display_name": str(label.get("name")),
                        "parent_id": None if label.get("parentID") is None else str(label.get("parentID")),
                    }
                )

        except Exception as e:
            bcelogger.error("get_artifact error.resp:{} artifact_name:{}".format(artifact_resp, self.artifact_name), e)

        # todo get model_label
        return skill_labels

    def import_labels(self, need_add_labels: list()):
        """
        import_labels_attr
        """
        if need_add_labels is None or len(need_add_labels) == 0:
            return
        as_name = parse_annotation_set_name(self.annotation_set_name)
        for label in need_add_labels:
            try:
                if label['type'] == "label":  # 需要创建标签 及其属性
                    resp = self.annotation_client.create_annotation_label(
                        workspace_id=as_name.workspace_id,
                        project_name=as_name.project_name,
                        annotation_set_name=as_name.local_name,
                        display_name=label.get("display_name"),
                        color=random_color(),
                        local_name=None,

                    )
                    bcelogger.info("import label req:{} resp:{}".format(label, resp))

                    # 创建属性
                    parent_id = resp.localName
                    label['local_name'] = resp.localName
                    attributes = label.get("attributes", None)
                    if attributes is not None:
                        for attr in attributes:
                            create_attr_resp = self.annotation_client.create_annotation_label(
                                workspace_id=as_name.workspace_id,
                                project_name=as_name.project_name,
                                annotation_set_name=as_name.local_name,
                                display_name=attr.get("display_name"),
                                color=random_color(),
                                local_name=None,
                                parent_id=parent_id

                            )
                            bcelogger.info("import label attr label:{} resp:{} parent_id:{}".format(label,
                                                                                                    create_attr_resp,
                                                                                                    parent_id))
                            attr['local_name'] = create_attr_resp.localName
                            attr['parent_id'] = parent_id
                elif label['type'] == "attr":  # 只需要创建属性
                    create_attr_resp = self.annotation_client.create_annotation_label(
                        workspace_id=as_name.workspace_id,
                        project_name=as_name.project_name,
                        annotation_set_name=as_name.local_name,
                        display_name=label.get("display_name"),
                        color=random_color(),
                        parent_id=label.get("parent_id"),
                        local_name=None

                    )
                    label['local_name'] = create_attr_resp.localName
                    bcelogger.info("import label attr label:{} resp:{}".format(label, create_attr_resp))
            except Exception as e:
                bcelogger.error("import label exception.label:{}".format(label), e)
                raise Exception("创建labels失败")
