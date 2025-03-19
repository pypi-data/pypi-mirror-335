#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   base_export_pipeline.py
"""
import os
import json
import bcelogger
from typing import List, Dict, Any, Optional

from windmillclient.client.windmill_client import WindmillClient
from windmillcomputev1.filesystem import blobstore
from windmilltrainingv1.client.training_api_dataset import DatasetName

from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource import mongo_query_pipeline
from vistudio_image_analysis.datasource.sharded_mongo_datasource import ShardedMongoDatasource
from vistudio_image_analysis.util import string
from vistudio_image_analysis.util.label import convert_annotation_labels_id, merge_labels
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name


class BaseExportPipeline(object):
    """
    BaseExportPipeline
    """

    def __init__(self, args):
        self.args = args
        self.config = Config(args)
        self.annotation_set_name = args.get('annotation_set_name')
        self.annotation_format = args.get('annotation_format')

        self.windmill_client = WindmillClient(
            endpoint=self.config.windmill_endpoint,
            context=self.config.bce_client_context
        )
        self.annotation_client = AnnotationClient(
            endpoint=self.config.vistudio_endpoint,
            context=self.config.bce_client_context
        )

        self.bs = blobstore(filesystem=self.config.filesystem)
        self.datasource = self._get_datasource()
        self._get_labels()

        dataset_conf = args.get('dataset')
        if dataset_conf is not None and dataset_conf != '':
            self.dataset = json.loads(string.decode_from_base64(dataset_conf))
        self.merge_labels = self._get_merge_labels()
        self.split = self._get_split()

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

        self.annotation_set_id = as_data.id
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
        self.annotation_set_category = as_data.category.get("category")
        self.annotation_uri = as_data.uri

    def _get_mongo_pipeline(self):
        """
        get mongo pipeline
        :return:
        """
        if self.args.get('q') is not None and self.args.get('q') != '':
            mongo_pipeline = json.loads(string.decode_from_base64(self.args.get('q')))
        else:
            mongo_pipeline = None

        bcelogger.info("mongo_pipeline:{}".format(mongo_pipeline))
        return mongo_pipeline

    def _get_datasource(self):
        """
        get datasource
        :return:
        """
        pipeline = self._get_mongo_pipeline()
        if pipeline is None:
            return
        func = mongo_query_pipeline.get_pipeline_func(pipeline)

        return ShardedMongoDatasource(uri=self.config.mongo_uri,
                                      database=self.config.mongodb_database,
                                      collection=self.config.mongodb_collection,
                                      pipeline_func=func,
                                      shard_username=self.config.mongodb_shard_username,
                                      shard_password=self.config.mongodb_shard_password)

    def _get_merge_labels(self):
        """
        get merge labels
        :return:
        """
        merge_labels = None

        if self.args.get('merge_labels') is not None and self.args.get('merge_labels') != '':
            merge_labels = json.loads(string.decode_from_base64(self.args.get('merge_labels')))

        return merge_labels

    def _get_split(self):
        """
        get split
        :return:
        """
        split = None
        if self.args.get('split') is not None and self.args.get('split') != '':
            split = json.loads(string.decode_from_base64(self.args.get('split')))
        bcelogger.info("split:{}".format(split))

        return split

    def create_dataset_location(self):
        """
        create dataset location
        :param path:
        :return:
        """
        dataset_name = DatasetName(
            workspace_id=self.dataset.get('workspaceID'),
            project_name=self.dataset.get('projectName'),
            local_name=self.dataset.get('localName')
        )
        object_name = dataset_name.get_name()
        location_resp = self.windmill_client.create_location(
            object_name=object_name
        )
        location = location_resp.location
        return location

    def create_dataset(self, location, artifact_metadata: Optional[dict] = None):
        """
        create dataset
        :param location:
        :param artifact_metadata
        :return:
        """
        # 创建数据集
        artifact = self.dataset.get('artifact', {})
        annotation_format = self.dataset.get('annotationFormat', 'Other')

        dataset_resp = self.windmill_client.create_dataset(
            workspace_id=self.dataset.get("workspaceID"),
            project_name=self.dataset.get("projectName"),
            category=self.dataset.get("category", "Other"),
            local_name=self.dataset.get("localName"),
            artifact_uri=location,
            description=self.dataset.get('description', ''),
            display_name=self.dataset.get('displayName', ''),
            data_type=self.dataset.get('dataType', 'Image'),
            annotation_format=annotation_format,
            artifact_description=artifact.get('description', ''),
            artifact_alias=artifact.get('alias', []),
            artifact_tags=artifact.get('tags', []),
            artifact_metadata=artifact_metadata,
        )
        bcelogger.info("create dataset resp is {}".format(dataset_resp))

    def save_label_file(self, file_path: str, label_index_map: dict()):
        """
        save_label_file
        :param file_path:
        :param label_index_map:
        :return:
        """
        labels = list()

        for _, v in enumerate(label_index_map.values()):
            if v['index'] == 0 and v['name'] == '背景':
                continue
            labels.append("{} {}".format(v['name'], v['index']) + os.linesep)
        self.bs.write_raw(path=file_path, content_type="text/plain", data=''.join(labels))

    def build_label_index_map(self) -> dict():
        """
        build_label_index_map
        构造标签索引映射
        return：
            {
                "1": {"name": "cat", "index": 1},
                "3": {"name": "dog", "index": 2},
                "4": {"name": "person", "index": 3},
            }
        """
        labels_dict = convert_annotation_labels_id(labels=self.labels, ignore_parent_id=True)
        merged_labels = merge_labels(labels_dict, self.merge_labels)

        start_index = 0

        # 按id排序
        sorted_ids = sorted(merged_labels.keys(), key=int)
        return {k: {'name': merged_labels[k], 'index': i + start_index} for i, k in enumerate(sorted_ids)}
