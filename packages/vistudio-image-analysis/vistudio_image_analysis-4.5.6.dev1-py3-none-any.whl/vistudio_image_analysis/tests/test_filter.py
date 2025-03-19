# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_filter.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/25 10:52
"""

from vistudio_image_analysis.util.filter import _filter_image_fn, _filter_image_by_artifact_name_fn, \
    _filter_annotation_fn


def test_filter_image_fn():
    row = {
        "image_name": "05d1c7c1-cfe8-4579-ba1a-8fd75486bfbf.jpg",
        "image_id": "29f1e5b408618271",
        "annotation_set_id": "as-xkwgfgut",
        "annotation_set_name": "workspaces/wsyiiiad/projects/spiproject/annotationsets/as-QRj2fQtw",
        "user_id": "05c4100af26e4628ab527eecf184ab48",
        "created_at": {
            "$numberLong": "1730102381611791431"
        },
        "data_type": "Image",
        "infer_state": "UnInfer",
        "file_uri": "s3://windmill-online/store/workspaces/wsyiiiad/projects/spiproject/annotationsets/as-QRj2fQtw/CYRIkSUN/data/nahui/images/CVAT数据复核/nahui/双面坡/05d1c7c1-cfe8-4579-ba1a-8fd75486bfbf.jpg",
        "org_id": "7b7456100c1848ecad0ab8280674fe5a",
        "annotation_state": "Annotated",
        "image_state": {
            "webp_state": "NotNeed",
            "thumbnail_state": "Completed"
        },
        "updated_at": {
            "$numberLong": "1730102412873291496"
        },
        "height": 309,
        "size": 88251,
        "width": 550
    }

    existed_images = ['29f1e5b408618271']
    filter_res = _filter_image_fn(row=row, existed_images=existed_images)

    assert filter_res is False


def test_filter_image_by_artifact_name_fn():
    row = {
        "annotationSetName": "workspaces/wsyiiiad/projects/spiproject/annotationsets/as-QRj2fQtw",
        "annotation_state": "Annotated",
        "annotations": [
            {
                "annotation_set_name": "",
                "annotations": [
                    {
                        "area": 78854.92176713464,
                        "bbox": [
                            692.04322730343,
                            95.72358637186234,
                            376.3278118177869,
                            209.53785314521264
                        ],
                        "labels": [
                            {
                                "annotationSetName": "",
                                "color": "",
                                "confidence": 0,
                                "createdAt": "0001-01-01T00:00:00Z",
                                "deletedAt": 0,
                                "displayName": "",
                                "id": "1",
                                "localName": "",
                                "projectName": "",
                                "updatedAt": "0001-01-01T00:00:00Z",
                                "workspaceID": ""
                            }
                        ],
                    }
                ],
                "artifact_name": "",
                "image_created_at": "2024-10-28T07:59:41.625557829Z",
                "image_id": "658b11982ca5f1f7",
                "task_id": "",
                "task_kind": "Manual"
            }
        ],
        "created_at": "2024-10-28T07:59:41.625557829Z",
        "file_uri": "s3://windmill-online/store/workspaces/wsyiiiad/projects/spiproject/annotationsets/as-QRj2fQtw/CYRIkSUN/data/nahui/images/CVAT数据复核/nahui/双面坡/26.png",
        "height": 850,
        "image_id": "658b11982ca5f1f7",
        "image_name": "26.png",
        "image_state": [
            {
                "Key": "webp_state",
                "Value": "Completed"
            },
            {
                "Key": "thumbnail_state",
                "Value": "Completed"
            }
        ],
        "infer_state": "UnInfer",
        "tags": {},
        "task_id": "",
        "updated_at": "2024-10-28T08:00:12.956329077Z",
        "user_id": "05c4100af26e4628ab527eecf184ab48",
        "width": 1242
    }
    artifact_name = 'workspaces/wsyiiiad/modelstores/ms-SfUEMyCa/models/nahui-R200-moxingbao/versions/2'
    filter_res = _filter_image_by_artifact_name_fn(row=row, artifact_name=artifact_name)
    assert filter_res is True


def test_filter_annotation_fn():
    row = {
        "image_id": "658b11982ca5f1f7",
        "image_created_at": {
            "$numberLong": "1730102381625557829"
        },
        "artifact_name": "",
        "annotations": [
            {
                "id": "anno-g547n5sc",
                "bbox": [
                    692.04322730343,
                    95.72358637186234,
                    376.3278118177869,
                    209.53785314521264
                ],
                "area": 78854.92176713464,
                "labels": [
                    {
                        "id": "1"
                    }
                ],
            }
        ],
        "task_id": "",
        "task_kind": "Manual",
        "data_type": "Annotation",
        "user_id": "",
        "annotation_set_id": "as-xkwgfgut",
        "created_at": {
            "$numberLong": "1730116205547526677"
        },
        "updated_at": {
            "$numberLong": "1730116205547526677"
        }
    }
    existed_annotations = ['658b11982ca5f1f7']
    filter_res = _filter_annotation_fn(row=row, existed_annotations=existed_annotations)
    assert  filter_res is False
