# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_update.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/15 10:52
"""
import ray
import pandas as pd
import bcelogger
import time

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.table.image import ImageData
from vistudio_image_analysis.operator.updater.annotation_state_updater import AnnotationStateUpdater
from vistudio_image_analysis.operator.updater.image_created_at_updater import ImageCreatedAtUpdater

from unittest.mock import patch, MagicMock, ANY


args = {
    'mongo_host': '10.27.240.45',
    'mongo_port': '8719',
    'mongo_user': 'root',
    'mongo_password': 'mongo123#',
    'mongo_database': 'annotation_ut',
    'mongo_collection': 'annotation_ut'
}


@patch('vistudio_image_analysis.table.image.ImageData.objects')
@patch('vistudio_image_analysis.table.annotation.AnnotationData.objects')
def test_update_image_created_at(mock_annotation_data_objects, mock_image_data_objects):
    """
    test_update_image_created_at
    """
    # mock 图像数据
    mock_image = ImageData()
    mock_image.created_at = time.time_ns()
    mock_image.annotation_state = "Unannotated"

    mock_image_data_objects.return_value.first.side_effect = [mock_image, None]
    mock_annotation_data_objects.return_value.delete.return_value = None

    # mock ds数据
    anno_data = [
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

    # 测试
    df = pd.DataFrame(anno_data)
    ope = ImageCreatedAtUpdater(config=Config(args))
    df = ope.update_image_created_at(df)
    ds = ray.data.from_pandas(df)
    bcelogger.info(f"UpdateImageCreatedAt Count: {ds.count()}")

    # 验证
    assert mock_image_data_objects.call_count == 3


@patch('vistudio_image_analysis.table.annotation.AnnotationData.objects')
@patch('vistudio_image_analysis.table.image.ImageData.objects')
def test_update_annotation_state(mock_image_data_objects, mock_annotation_data_objects):
    """
    test_update_annotation_stat
    """
    # 模拟 AnnotationData 的行为
    mock_annotation_data_objects.return_value.count.side_effect = [0, 1]

    # 模拟 ImageData 的更新行为
    mock_image_data_objects.return_value.update_one.return_value = None

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

    # 更新状态
    df = pd.DataFrame(image_data)
    ope = AnnotationStateUpdater(config=Config(args))
    df = ope.update_annotation_state(df)
    ds = ray.data.from_pandas(df)
    bcelogger.info(f"UpdateAnnotationState Count: {ds.count()}")

    # 验证
    assert mock_image_data_objects.call_count == 2

