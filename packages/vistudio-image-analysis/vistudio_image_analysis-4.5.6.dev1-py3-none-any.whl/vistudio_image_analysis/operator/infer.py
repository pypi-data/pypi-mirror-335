#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   infer.py
"""
from typing import Dict, Any, List
from ray.data import Dataset
import bcelogger
import numpy as np
import cv2
import json
import time

from tritonv2.client_factory import TritonClientFactory
from tritonv2.constants import LimiterConfig, RequestRateDuration
from tritonv2.utils import list_stack_ndarray
import tritonclient.http as http_client
from tritonclient.utils import triton_to_np_dtype

from windmillcomputev1.filesystem import blobstore
from windmillcategoryv1.client.category_api import match
from windmillendpointv1.client.gaea.api import ModelInferRequest, InferConfig, ModelInferOutput
from windmillendpointv1.client.gaea.infer import infer

from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name
from vistudio_image_analysis.util.label import convert_annotation_labels
from vistudio_image_analysis.util import string

from lmdeployv1.client import LMDeployClient, build_batch_chat_messages, format_base64_string
from lmdeployv1.api import BatchChatCompletionRequest

model_name = "ensemble"


class Infer(object):
    """
    Infer
    """

    def __init__(self, config, operator_params):
        self.config = config

        self.infer_config = operator_params.get("infer_config")
        self.artifact_name = operator_params.get("artifact_name")
        self.job_created_at = operator_params.get("job_created_at")
        self.annotation_set_name = operator_params.get("annotation_set_name")

        if operator_params.get("question_id") is not None:
            self._get_question(operator_params['question_id'])

        self.prompt = None
        self.instructions = None
        self.question = None

    def _get_question(self, question_id):
        self.annotation_client = AnnotationClient(
            endpoint=self.config.vistudio_endpoint, context=self.config.bce_client_context)
        try:
            as_name = parse_annotation_set_name(self.annotation_set_name)
            resp = self.annotation_client.get_prompt_template(
                workspace_id=as_name.workspace_id,
                project_name=as_name.project_name,
                annotation_set_name=as_name.local_name,
                local_name=question_id,
            )
        except Exception as e:
            bcelogger.error(f"get_prompt_template error: {e}, question_id: {question_id}")
            raise e

        self.prompt = resp.prompt
        self.instructions = resp.instructions
        self.question = resp.question

    def batch_lmdeploy_inference_single_chat(self, batch, server_uri):
        """
        batch_lmdeploy_inference
        """
        import pandas as pd
        file_uris = batch['file_uri'].tolist()
        bs = blobstore(filesystem=self.config.filesystem)

        client = LMDeployClient(
            endpoint=server_uri,
            context={"OrgID": self.config.org_id, "UserID": self.config.user_id}
        )
        answer = []
        for file_uri in file_uris:
            try:
                resp = self._lmdeploy_inference_with_retry(client, file_uri, bs)
                if resp is not None and len(resp) > 0:
                    ans = resp[0].predictions[0].answer
                    if len(ans) > 1000:
                        ans = ans[:1000]
                    answer.append(ans)
            except Exception as e:
                answer.append("")
                import traceback
                traceback.print_exc()
                bcelogger.error("_lmdeploy_inference_with_retry error. file_uri:{}, err:{}".format(file_uri, e))
                continue

        batch['answer'] = answer
        batch['lmdeploy_status'] = pd.Series(["succeed"] * len(batch), index=batch.index)
        return batch

    def _lmdeploy_inference_with_retry(self, client: LMDeployClient, file_uri,
                                       bs, max_retries=3, delay=5) -> List[ModelInferOutput]:
        """
        _lmdeploy_inference_with_retry
        """
        image_bytes = bs.read_raw(file_uri)
        req = ModelInferRequest(
            infer_config=InferConfig(
                top_p=self.infer_config["top_p"],
                temperature=self.infer_config["temperature"],
                repetition_penalty=self.infer_config["repetition_penalty"],
                prompt=self.question,
            )
        )
        req.image_buffer = image_bytes
        retries = 0
        while retries < max_retries:
            try:
                # 尝试获取输入和输出的详细信息
                start_time = time.time()
                bcelogger.info("chat_completion  begin....file_uris:{}".format(file_uri))
                resp = infer(client, req)
                end_time = time.time()
                elapsed_time = end_time - start_time
                bcelogger.info("chat_completion  end....file_uris:{} resp:{} elapsed_time:{}"
                               .format(file_uri, resp, elapsed_time))
                return resp
            except Exception as e:
                retries += 1
                bcelogger.info(
                    f"_lmdeploy_inference_with_retry file_uris:{file_uri} "
                    f"Error: {e}. Retrying {retries}/{max_retries}...")

                # 如果达到最大重试次数，抛出异常
                if retries == max_retries:
                    raise e
                # 延迟一段时间后重试
                time.sleep(delay)

    def _batch_lmdeploy_inference_with_retry(self, client: LMDeployClient, file_uris, multimodal_model,
                                             messages, max_retries=3, delay=5):
        """
        _batch_lmdeploy_inference_with_retry
        """

        retries = 0
        while retries < max_retries:
            try:
                # 尝试获取输入和输出的详细信息
                bcelogger.info("batch_chat_completion  begin....file_uris:{}".format(file_uris))
                resp = client.batch_chat_acompletion(BatchChatCompletionRequest(
                    model=multimodal_model,
                    messages=messages,
                    temperature=self.infer_config["temperature"],
                    top_p=self.infer_config["top_p"],
                    repetition_penalty=self.infer_config["repetition_penalty"],
                ))
                bcelogger.info("batch_chat_completion  end....file_uris:{} resp:{}".format(file_uris, resp))
                return resp
            except Exception as e:
                retries += 1
                bcelogger.info(
                    f"_batch_lmdeploy_inference_with_retry file_uris:{file_uris} "
                    f"Error: {e}. Retrying {retries}/{max_retries}...")

                # 如果达到最大重试次数，抛出异常
                if retries == max_retries:
                    raise e
                # 延迟一段时间后重试
                time.sleep(delay)

    @staticmethod
    def triton_inference_picture(image, file_name, server_uri, input_metadata, output_metadata) -> Dict[str, Any]:
        """
        inference picture
        Args:
            image: 图像，nparray
            file_name: 图像名，如：1.jpg
            server_uri: 服务地址，如：10.93.32.12:8412/ep-ghuspbaj/http
        Returns:
        """
        bcelogger.info("triton_inference_picture file_name:{} server_uri:{}".format(file_name, server_uri))
        triton_client = TritonClientFactory.create_http_client(
            server_url=server_uri,
            limiter_config=LimiterConfig(limit=1, interval=RequestRateDuration.SECOND, delay=True),
        )
        # 处理数据
        # 1. 读取图片
        repeated_image_data = []
        img_encode = cv2.imencode('.jpg', image)[1]
        img = np.frombuffer(img_encode.tobytes(), dtype=triton_to_np_dtype(input_metadata[0]['datatype']))
        repeated_image_data.append(np.array(img))
        batched_image_data = list_stack_ndarray(repeated_image_data)
        # 2. 添加meta信息
        meta_json = json.dumps({"image_id": str(file_name), "camera_id": "camera_id_string"})
        byte_meta_json = meta_json.encode()
        np_meta_json = np.frombuffer(byte_meta_json, dtype='uint8')
        send_meta_json = np.array(np_meta_json)
        send_meta_json = np.expand_dims(send_meta_json, axis=0)

        # build triton input
        inputs = [
            http_client.InferInput(input_metadata[0]["name"], list(
                batched_image_data.shape), input_metadata[0]["datatype"]),
            http_client.InferInput(input_metadata[1]["name"], send_meta_json.shape,
                                   input_metadata[1]["datatype"])
        ]
        inputs[0].set_data_from_numpy(batched_image_data, binary_data=False)
        inputs[1].set_data_from_numpy(send_meta_json)

        # build triton output
        output_names = [
            output["name"] for output in output_metadata
        ]
        outputs = []
        for output_name in output_names:
            outputs.append(
                http_client.InferRequestedOutput(output_name,
                                                 binary_data=True))

        # infer
        def build_fake_skill_out_json():
            return {"image_id": file_name, "image_name": file_name, "predictions": [], "prediction_status": "failed"}

        try:
            result = triton_client.model_infer(model_name, inputs, outputs=outputs)
        except Exception as e:
            bcelogger.error("model_infer_error. file_name:{} error:{}".format(file_name, e))
            return build_fake_skill_out_json()
        bcelogger.info("model_infer_result result:{}, output_names:{}".format(result, output_names))
        # print detailed output
        output_dict = {}
        for output_name in output_names:
            try:
                output_dict[output_name] = eval(result.as_numpy(output_name))
            except Exception as e:
                output_dict[output_name] = json.loads(
                    result.as_numpy(output_name).tobytes()
                )
        bcelogger.info("model_output_dict, output_dict:{}".format(output_dict))

        skill_out_json = output_dict['skill_out_json'][0]
        if "_leftImg8bit" in file_name:
            file_name = file_name.rsplit('.', 1)[0].replace("_leftImg8bit", "", 1)
        skill_out_json['image_name'] = file_name
        skill_out_json['prediction_status'] = "succeed"
        return skill_out_json

    def _convert_skill_output(
            self,
            row: Dict[str, Any],
            annotation_set_id: str,
            annotation_labels_dict: dict() = None,
    ) -> Dict[str, Any]:
        """
        convert_skill_output
        """
        res_row = {
            'annotation_set_id': annotation_set_id,
            'image_id': string.generate_md5(row['image_name']),
            'artifact_name': self.artifact_name,
            'task_kind': 'Model',
            'data_type': 'Annotation',
            'user_id': self.config.user_id,
            'infer_config': self.infer_config,
            'job_name': self.config.job_name.split('/')[-1],
            'job_created_at': self.job_created_at,
        }

        predictions = row['predictions']
        annotations = list()
        for element in predictions:
            bbox = element['bbox']
            area = element['area']
            id = string.generate_md5(str(time.time_ns()))
            labels = element['categories']
            segmentation = element.get("segmentation", [])
            quadrangle = element.get("quadrangle", [])
            ocr = element.get("ocr", None)
            new_labels = list()
            for label in labels:
                label_name = str(label.get("id"))
                super_category = str(label.get("super_category", ""))
                confidence = label.get("confidence", 0)
                if super_category == "":
                    label_info = annotation_labels_dict.get(label_name, None)
                    if label_info is None:
                        label_info = annotation_labels_dict.get(str(label.get("name")), None)
                        if label_info is None:
                            continue
                        label_name = str(label.get("name"))
                    new_label = {
                        "id": label_info.get("local_name"),
                        "name": label_name,
                        "confidence": confidence,
                        "parent_id": ""
                    }

                else:
                    label_info = annotation_labels_dict.get(super_category)
                    if label_info is None:
                        continue
                    attrs = label_info.get("attributes", [])
                    attrs_dict = {item["display_name"]: item['local_name'] for item in attrs}
                    attr_id = attrs_dict.get(label_name, None)
                    if attr_id is None:
                        attr_id = attrs_dict.get(label.get("name"), None)
                        if attr_id is None:
                            continue
                    new_label = {
                        "id": attr_id,
                        "name": label_name,
                        "confidence": confidence,
                        "parent_id": label_info.get("local_name")
                    }

                import math
                import pandas as pd
                if np.isnan(confidence) or math.isnan(confidence) or pd.isna(confidence):
                    del new_label['confidence']
                new_labels.append(new_label)

            annotation_element = {
                "id": id,
                "bbox": bbox,
                "area": area,
                "labels": new_labels,
                "quadrangle": quadrangle,
                "segmentation": segmentation,
            }
            if ocr is not None:
                word = ocr.get("word", "")
                direction = ocr.get("direction", "")
                ocr_confidence = ocr.get("confidence", None)
                anno_ocr = {
                    "word": str(word),
                    "direction": str(direction)
                }
                if ocr_confidence is not None:
                    anno_ocr['confidence'] = ocr_confidence
                annotation_element['ocr'] = anno_ocr
            annotations.append(annotation_element)
        res_row['annotations'] = annotations
        res_row['created_at'] = time.time_ns()
        return res_row

    def _convert_multimodal_output(
            self,
            row: Dict[str, Any],
            annotation_set_id: str,
    ) -> Dict[str, Any]:
        """
        _convert_multimodal_output
        """
        anno = {
            "id": string.generate_random_string(8),
            "question_id": int(string.generate_random_digits(6)),
            "question": self.question,
            "answer": row['answer'],
            "prompt": self.prompt,
        }
        if self.instructions is not None and len(self.instructions) > 0:
            json_success, anno['answer'] = string.extract_json(anno['answer'])
            if json_success:
                anno['instructions'] = self.instructions

        item = {
            'annotation_set_id': annotation_set_id,
            'image_id': string.generate_md5(row['image_name']),
            'artifact_name': self.artifact_name,
            'task_kind': 'Model',
            'data_type': 'Annotation',
            'user_id': self.config.user_id,
            'infer_config': self.infer_config,
            'job_name': self.config.job_name.split('/')[-1],
            'annotations': [anno],
            'job_created_at': self.job_created_at,
            'created_at': time.time_ns()
        }

        return item

    def to_vistudio_v1(
            self,
            ds: Dataset,
            annotation_set_id: str,
            annotation_set_category: str,
            annotation_labels: list() = None,
    ) -> Dataset:
        """
        to_vistudio_v1
        """
        if match(annotation_set_category, "Multimodal"):
            annotation_ds = ds.map(
                lambda row: self._convert_multimodal_output(row=row,
                                                            annotation_set_id=annotation_set_id))
        else:
            annotation_labels_dict = convert_annotation_labels(labels=annotation_labels)
            annotation_ds = ds.map(
                lambda row: self._convert_skill_output(row=row,
                                                       annotation_set_id=annotation_set_id,
                                                       annotation_labels_dict=annotation_labels_dict))
        return annotation_ds
