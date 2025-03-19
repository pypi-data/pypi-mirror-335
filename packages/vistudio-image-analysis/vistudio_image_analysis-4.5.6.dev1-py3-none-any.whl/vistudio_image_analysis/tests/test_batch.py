# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_batch.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/15 10:52
"""

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.tests.mock.mock_server import get_mock_server, get_bce_response
from vistudio_image_analysis.tests.mock.mock_data import GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR
from vistudio_image_analysis.pipeline.batch_delete import batch_delete

from unittest.mock import patch, MagicMock


query = [{
    "aggregation": [
        {"$match": {"annotation_set_id": "as-n6jdhp8z"}},
        {"$match": {"data_type": "Image"}},
        {"$match": {"$and": [{"image_id": {"$in": ["1", "2"]}}]}},
        {"$project": {"image_id": 1}}
    ],
    "collection": "annotation",
    "query_result_mapping": {"": "images", "image_id": "image_ids"},
    "default_query_result": {"image_ids": [], "images": []},
    "aggregation_json": ""
}]

args = {
    'vistudio_endpoint': get_mock_server(),
    'annotation_set_name': 'workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut',
    'org_id': 'test-org-id',
    'user_id': 'test-user-id',
}


@patch('pymongo.MongoClient')
@patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@patch('vistudio_image_analysis.pipeline.batch_delete.query_mongo')
@patch('vistudio_image_analysis.table.image.ImageData.objects')
def test_batch_delete(mock_image_data_objects, mock_query_mongo, mock_get_annotation_set, mock_mongo_client):
    # mock mongo
    mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value = MagicMock()
    # mock get_annotation_set
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    # mock query_mongo
    mock_query_mongo.return_value = {'image_ids': ['1', '2']}
    # mock ImageData.objects
    mock_image_data_objects.return_value.delete.return_value = None  # 假设删除操作没有返回

    # 测试
    base_conf = Config(args)
    batch_delete(base_conf, args["annotation_set_name"], query)

    # 断言
    mock_get_annotation_set.assert_called_once()
    mock_query_mongo.assert_called_once()
    mock_image_data_objects.assert_called_once_with(
        annotation_set_id='as-01',
        image_id__in=['1', '2']
    )
    mock_image_data_objects.return_value.delete.assert_called_once()
