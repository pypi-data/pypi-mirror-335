# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_thumbnail_and_webp.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/15 10:52
"""
import os.path
import ray
import pandas as pd
import time
from unittest import mock
from pydantic import BaseModel

from vistudio_image_analysis.tests.mock.mock_mongodb import MongoDBClient
from vistudio_image_analysis.table.image import ImageData
from vistudio_image_analysis.pipeline.generate_thumbnail_pipeline import GenerateThumbnailPipeline
from vistudio_image_analysis.pipeline.generate_webp_pipeline import GenerateWebpPipeline
from vistudio_image_analysis.pipeline.update_annotation_state_pipeline import UpdateAnnotationStatePipeline
from vistudio_image_analysis.pipeline.update_image_created_at_pipeline import UpdateImageCreatedAtPipeline

from vistudio_image_analysis.operator.updater.annotation_state_updater import AnnotationStateUpdater
from vistudio_image_analysis.operator.updater.image_created_at_updater import ImageCreatedAtUpdater

from windmillclient.client.mock import get_mock_server


class Conifg(BaseModel):
    mongo_uri: str = ""
    mongodb_database: str = ""
    mongodb_collection: str = ""
    mongodb_shard_password: str = ""
    mongodb_shard_username: str = ""
    windmill_endpoint: str = ""


config = Conifg(
    mongo_uri="mongodb://root:mongo123#@10.27.240.45:8719",
    mongodb_database="annotation_ut",
    mongodb_collection="annotation_ut",
    mongodb_shard_password="mongo123#",
    mongodb_shard_username="shard_readonly",
    windmill_endpoint=get_mock_server(),
)

args = {
    'mongo_host': '10.27.240.45',
    'mongo_port': '8719',
    'mongo_user': 'root',
    'mongo_password': 'mongo123#',
    'mongo_database': 'annotation_ut',
    'mongo_collection': 'annotation_ut'
}


@mock.patch('vistudio_image_analysis.pipeline.generate_thumbnail_pipeline.read_datasource')
def test_thumbnail(mock_read_datasource):
    """
    Test
    """
    image_data = [
        {
            "image_id": "1",
            "annotation_set_id": "as1",
            "annotation_set_name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
            "file_uri": "s3://windmill/store/68b4691df5fd48a7a23742fed8d39c36/python_ut/testdata/cat.jpeg",
            "org_id": "test-org-id",
            "user_id": "test-user-id",
        }
    ]
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(image_data))

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    ppl = GenerateThumbnailPipeline(config)
    ppl.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('vistudio_image_analysis.pipeline.generate_webp_pipeline.read_datasource')
def test_webp(mock_read_datasource):
    """
    Test
    """
    image_data = [
        {
            "image_id": "1",
            "annotation_set_id": "as1",
            "annotation_set_name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
            "file_uri": "s3://windmill/store/68b4691df5fd48a7a23742fed8d39c36/python_ut/testdata/3.png",
            "org_id": "test-org-id",
            "user_id": "test-user-id",
        }
    ]
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(image_data))

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    ppl = GenerateWebpPipeline(config)
    ppl.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('vistudio_image_analysis.pipeline.update_annotation_state_pipeline.read_datasource')
@mock.patch('vistudio_image_analysis.table.annotation.AnnotationData.objects')
@mock.patch('vistudio_image_analysis.table.image.ImageData.objects')
def test_annotation_state(mock_image_data_objects, mock_annotation_data_objects, mock_read_datasource):
    """
    Test
    """
    # mock ds数据
    image_data = [
        {
            "image_id": "1",
            "annotation_set_id": "as",
        },
        {
            "image_id": "2",
            "annotation_set_id": "as",
        }
    ]
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(image_data))

    # 模拟 AnnotationData 的行为
    mock_annotation_data_objects.return_value.count.side_effect = [1, 0]

    # 模拟 ImageData 的更新行为
    mock_image_data_objects.return_value.update_one.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    # 测ppl
    ppl = UpdateAnnotationStatePipeline(config)
    ppl.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('vistudio_image_analysis.pipeline.update_image_created_at_pipeline.read_datasource')
@mock.patch('vistudio_image_analysis.table.annotation.AnnotationData.objects')
@mock.patch('vistudio_image_analysis.table.image.ImageData.objects')
def test_image_created_at(mock_image_data_objects, mock_annotation_data_objects, mock_read_datasource):
    """
    Test
    """
    # mock ds数据
    image_data = [
        {
            "image_id": "1",
            "annotation_set_id": "as",
            "task_kind": "Manual",
            "created_at": time.time_ns() - 7 * 24 * 60 * 60 * 1e+9  # 超过3天的时间戳,
        },
        {
            "image_id": "2",
            "annotation_set_id": "as",
            "task_kind": "Manual",
            "created_at": time.time_ns()
        }
    ]
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(image_data))

    # mock 图像数据
    mock_image = ImageData()
    mock_image.created_at = time.time_ns()
    mock_image.annotation_state = "Unannotated"

    mock_image_data_objects.return_value.first.side_effect = [mock_image, None]
    mock_annotation_data_objects.return_value.delete.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    # 测ppl
    ppl = UpdateImageCreatedAtPipeline(config)
    ppl.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()

