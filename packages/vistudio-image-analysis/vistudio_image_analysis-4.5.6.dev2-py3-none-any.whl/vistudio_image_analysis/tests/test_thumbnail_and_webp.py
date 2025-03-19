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
import bcelogger
from unittest import mock

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.tests.mock.mock_mongodb import MongoDBClient
from vistudio_image_analysis.tests.mock.mock_data import GET_LOCAL_FILESYSTEM
from vistudio_image_analysis.operator.thumbnail_generator import ThumbnailGenerator
from vistudio_image_analysis.operator.updater.webp_state_updater import WebpStateUpdater
from vistudio_image_analysis.operator.webp_generator import WebpGenerator
from vistudio_image_analysis.operator.updater.thumbnail_state_updater import ThumbnailStateUpdater
from windmillclient.client.mock import get_mock_server


args = {
    'mongo_host': '10.27.240.45',
    'mongo_port': '8719',
    'mongo_user': 'root',
    'mongo_password': 'mongo123#',
    'mongo_database': 'annotation_ut',
    'mongo_collection': 'annotation_ut'
}


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.suggest_first_filesystem')
def test_generate_and_update(mock_suggest_first_filesystem):
    """
    Test
    """
    mock_suggest_first_filesystem.return_value = GET_LOCAL_FILESYSTEM

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    # 生成缩略图
    image_data = [
        {
            "image_id": "1",
            "annotation_set_id": "as1",
            "annotation_set_name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
            "file_uri": os.path.dirname(os.path.abspath(__file__)) + "/store/image/cat.jpeg",
            "org_id": "test-org-id",
            "user_id": "test-user-id",
        }
    ]
    df = pd.DataFrame(image_data)
    windmill_endpoint = get_mock_server()
    operator = ThumbnailGenerator(windmill_endpoint=windmill_endpoint)
    df1 = operator.generate_thumbnail(source=df)
    ds1 = ray.data.from_pandas(df1)
    bcelogger.info(f"GenerateThumbnail: {ds1.take_all()}")

    # 更新缩略图状态
    config = Config(args)
    updater = ThumbnailStateUpdater(config)
    df1 = updater.update_thumbnail_state(df1)
    ds1 = ray.data.from_pandas(df1)
    bcelogger.info(f"UpdateThumbnail: {ds1.take_all()}")

    # 生成webp
    operator = WebpGenerator(windmill_endpoint=windmill_endpoint)
    df2 = operator.generate_webp(source=df)
    ds2 = ray.data.from_pandas(df2)
    bcelogger.info(f"GenerateWebp: {ds2.take_all()}")

    # 更新webp图状态
    updater = WebpStateUpdater(config)
    df2 = updater.update_webp_state(df2)
    ds2 = ray.data.from_pandas(df2)
    bcelogger.info(f"UpdateWebp : {ds2.take_all()}")

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()