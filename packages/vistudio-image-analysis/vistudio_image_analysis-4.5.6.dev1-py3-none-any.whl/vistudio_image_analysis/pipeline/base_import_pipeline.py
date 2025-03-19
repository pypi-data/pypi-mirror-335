#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   base_import_pipeline.py
"""

import re
import bcelogger
import json
import ray

from windmilltrainingv1.client.training_api_job import parse_job_name
from windmilltrainingv1.client.training_client import TrainingClient

from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name
from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import parse_mongo_uri, get_mongo_collection
from vistudio_image_analysis.operator.reader import Reader
from vistudio_image_analysis.processor.importer.image.image_preprocessor import ImageFormatterPreprocessor
from vistudio_image_analysis.processor.importer.zip.zip_preprocessor import ZipFormatPreprocessor
from vistudio_image_analysis.util import string
from vistudio_image_analysis.util.label import random_color


class BaseImportPipline(object):
    """
    BaseImportPipline
    """

    def __init__(self, args: dict()):
        bcelogger.info("BaseImportPipline Init Start!")
        self.args = args
        self.config = Config(args)
        self.annotation_set_name = args.get('annotation_set_name')
        self.annotation_format = args.get('annotation_format').lower()
        self.data_uri = args.get('data_uri')
        self.data_types = self._get_data_types()
        self.file_format = args.get('file_format').lower()

        self.annotation_client = AnnotationClient(
            endpoint=self.config.vistudio_endpoint,
            context=self.config.bce_client_context
        )
        self.train_client = TrainingClient(
            endpoint=self.config.windmill_endpoint,
            context=self.config.bce_client_context
        )

        self._get_labels()
        self.mongo_uri = self._get_mongo_uri()
        self.mongodb = get_mongo_collection(config=self.config)
        self.tag = self._get_tag()
        bcelogger.info("BaseImportPipline Init End!")

    def _get_data_types(self):
        """
        get data types
        :return:
        """
        data_types = self.args.get('data_types').split(",")
        if not ((len(data_types) == 1 and data_types[0] in {"image", "annotation"}) or
                (len(data_types) == 2 and set(data_types) == {"image", "annotation"})):
            raise ValueError(f"无效的data_types: {data_types}")

        return data_types

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

    def import_labels(self, need_add_labels: list()):
        """
        创建导入的标签
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
                    attributes = label.get("attributes", None)
                    if attributes is None and len(attributes) == 0:
                        continue
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
                        bcelogger.info(f"import label attr label:{label} resp:{create_attr_resp} parent_id:{parent_id}")

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
                    bcelogger.info("import label attr label:{} resp:{}".format(label, create_attr_resp))
            except Exception as e:
                bcelogger.error("import label exception.label:{}".format(label), e)
                continue

    def _get_mongo_uri(self):
        """
        get mongo uri
        :return:
        """
        uri = "mongodb://{}:{}@{}:{}".format(self.args.get('mongo_user'),
                                             self.args.get('mongo_password'),
                                             self.args.get('mongo_host'),
                                             self.args.get('mongo_port'))
        return uri

    def _get_tag(self):
        """
        get merge labels
        :return:
        """
        if self.args.get('tag') is not None and self.args.get('tag') != '':
            tag = json.loads(string.decode_from_base64(self.args.get('tag')))
        else:
            tag = None

        return tag

    def update_annotation_job(self, err_msg):
        """
        更新标注任务状态
        """
        job_name = self.config.job_name
        bcelogger.info("update job name is {}".format(job_name))
        client_job_name = parse_job_name(self.config.job_name)
        job_resp = self.train_client.get_job(
            workspace_id=client_job_name.workspace_id,
            project_name=client_job_name.project_name,
            local_name=client_job_name.local_name
        )
        bcelogger.info("get job resp is {}".format(job_resp))
        tags = job_resp.tags
        if tags is None or len(tags) == 0:
            tags = {"errMsg": err_msg}
        else:
            tags['errMsg'] = err_msg
        update_job_resp = self.train_client.update_job(
            workspace_id=client_job_name.workspace_id,
            project_name=client_job_name.project_name,
            local_name=client_job_name.local_name,
            tags=tags,
        )
        bcelogger.info("update job resp is {}".format(update_job_resp))

    def _import_image(self):
        """
        import_images
        """
        # 读取图片
        reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)

        if self.file_format == 'zip':
            zip_file_uris = reader.get_zip_file_uris(data_uri=self.data_uri)
            if len(zip_file_uris) > 0:
                zip_formatter = ZipFormatPreprocessor(config=self.config)
                self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_

        file_uris = reader.get_file_uris(data_uri=self.data_uri, data_types=self.data_types)
        if len(file_uris) == 0:
            self.update_annotation_job("未获取到相关文件，请检查文件")
            raise Exception("未获取到相关文件，请检查文件")
        ds = ray.data.from_items(file_uris)
        bcelogger.info("import cityscapes image from json.dataset count = {}".format(ds.count()))

        image_formatter = ImageFormatterPreprocessor(
            config=self.config,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            tag=self.tag
        )
        final_ds = image_formatter.fit(ds).stats_
        bcelogger.info("format dataset.dataset count = {}".format(final_ds.count()))

        # 写入mongo
        final_ds.write_mongo(uri=self.mongo_uri,
                             database=self.config.mongodb_database,
                             collection=self.config.mongodb_collection)
