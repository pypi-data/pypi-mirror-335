# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/24 19:01
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : test_export_multiattributedataset_pipeline.py
# @Software: PyCharm
"""
from unittest import mock

from vistudio_image_analysis.pipeline.export_multiattributedataset_pipeline import ExportMultiAttributeDatasetPipeline
from vistudio_image_analysis.tests.test_import_multiattributedataset_pipeline_config import \
    GET_FILESYSTEM_CREDENTIAL
from vistudio_image_analysis.tests.mock.mock_server import get_bce_response
from vistudio_image_analysis.operator.multiattributedataset_formatter import MultiAttributeDatasetFormatter
import os
import ray

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 读取本地文件
train_txt = ray.data.read_text(os.path.join(current_dir, "testdata/multiattributedataset/annotations/train.txt"))


def test_test_multi_attribute_dataset_formatter():
    multiattribute_formatter = MultiAttributeDatasetFormatter(
        annotation_labels=ANNOTATION_LABELS,
        merge_labels={'0_0': '0_0', '1_0': '0_0'})
    multiattribute_formatter.from_vistudio_v1(train_txt.to_pandas())


@mock.patch('ray.data.read_api.read_datasource')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.create_dataset')
@mock.patch('windmillcomputev1.filesystem.s3.S3BlobStore.write_raw')
@mock.patch('ray.data.dataset.Dataset.write_csv')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.create_location')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
def test_export_multiattributedataset_pipeline(mock_get_filesystem_credential,
                                               mock_get_annotation_set,
                                               mock_create_location,
                                               mock_write_csv,
                                               mock_write_raw,
                                               mock_create_dataset,
                                               mock_read_datasource):
    """
    test_export_multiattributedataset_pipeline
    """
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE)
    mock_get_filesystem_credential.return_value = get_bce_response(GET_FILESYSTEM_CREDENTIAL)
    mock_read_datasource.read_datasource = train_txt
    mock_create_location.return_value = get_bce_response({
        "metadata": {
            "content_type": "application/json; charset=utf-8",
            "date": "Thu, 24 Oct 2024 11:14:49 GMT",
            "content_length": "123"
        },
        "location": "s3://windmill/store/workspaces/wsicykvi/projects/proj-NMX22gln/"
                    "datasets/ds-KbNozriY/versions/3-1729768489863"
    })
    mock_write_csv.return_value = None
    mock_write_raw.return_value = None
    mock_create_dataset.return_value = None

    args = {'mongo_host': '10.27.240.49',
            'mongo_port': '8719',
            'mongo_user': 'root',
            'mongo_password': 'mongo123#',
            'mongo_database': 'annotation',
            'mongo_collection': 'annotation',
            'windmill_endpoint': '10.27.240.49:8340',
            'filesystem_name': 'workspaces/wsicykvi/filesystems/wsicykviffss',
            'job_name': 'workspaces/public/projects/default/jobs/annoJob-dcsmb6um',
            'vistudio_endpoint': '10.27.240.49:8510',
            'annotation_set_name': 'workspaces/wsicykvi/projects/proj-NMX22gln/annotationsets/as-CvxBLTK6',
            'org_id': '7957b155b5cf4e43833527b10132a928',
            'user_id': '419b412dd5ff43c7b809960dfaf355e7',
            'mongo_shard_password': '',
            'mongo_shard_username': '',
            'q': 'W3siYWdncmVnYXRpb24iOlt7IiRtYXRjaCI6eyJhbm5vdGF0aW9uX3NldF9pZCI6ImFzLTM5bjIzdzk'
                 '0In19LHsiJG1hdGNoIjp7ImRhdGFfdHlwZSI6IkltYWdlIn19LHsiJG1hdGNoIjp7IiRhbmQiOlt7ImltYW'
                 'dlX2lkIjp7IiRuaW4iOltdfX1dfX1dLCJjb2xsZWN0aW9uIjoiYW5ub3RhdGlvbiIsInF1ZXJ5X3Jlc3VsdF9tY'
                 'XBwaW5nIjp7IiI6ImltYWdlcyIsImltYWdlX2lkIjoiaW1hZ2VfaWRzIn0sImRlZmF1bHRfcXVlcnlfcmVzdWx0'
                 'Ijp7ImltYWdlX2lkcyI6W10sImltYWdlcyI6W119LCJhZ2dyZWdhdGlvbl9qc29uIjoiIn0seyJhZ2dyZWdhdGlvbiI'
                 '6W3siJG1hdGNoIjp7ImFubm90YXRpb25fc2V0X2lkIjoiYXMtMzluMjN3OTQifX0seyIkbWF0Y2giOnsiZGF0YV90eXBlI'
                 'joiQW5ub3RhdGlvbiJ9fSx7IiRtYXRjaCI6eyJpbWFnZV9pZCI6eyIkaW4iOiIkbG9va3VwOmltYWdlX2lkcyJ9fX0seyIk'
                 'bWF0Y2giOnsiYXJ0aWZhY3RfbmFtZSI6IiJ9fV0sImNvbGxlY3Rpb24iOiJhbm5vdGF0aW9uIiwicXVlcnlfcmVzdWx0X21hc'
                 'HBpbmciOnsiIjoiYW5ub3RhdGlvbnMifSwiZGVmYXVsdF9xdWVyeV9yZXN1bHQiOm51bGwsImFnZ3JlZ2F'
                 '0aW9uX2pzb24iOiIifV0=',
            'annotation_format': 'MultiAttributeDataset',
            'export_to': 'Dataset',
            'dataset': 'eyJhbm5vdGF0aW9uRm9ybWF0IjoiTXVsdGlBdHRyaWJ1dGVEYXRhc2V0IiwiYXJ0aWZhY3QiOnsidGFncyI6e'
                       '319LCJjYXRlZ29yeSI6IkltYWdlL0ltYWdlQ2xhc3NpZmljYXRpb24vTXVsdGlUYXNrIiwiZGF0YVR5cGUiOiJJbW'
                       'FnZSIsImxvY2FsTmFtZSI6ImRzLUtiTm96cmlZIiwicHJvamVjdE5hbWUiOiJwcm9qLU5NWDIyZ2xuIiwid29ya3'
                       'NwYWNlSUQiOiJ3c2ljeWt2aSJ9',
            'merge_labels': 'eyIwXzAiOiIwXzAiLCIxXzAiOiIwXzAifQ==',
            'split': ''}
    pipeline = ExportMultiAttributeDatasetPipeline(args)
    pipeline.run()


GET_ANNOTATION_SET_RESPONSE = {
    "metadata": {
        "content_type": "application/json; charset=utf-8",
        "date": "Thu, 24 Oct 2024 11:08:23 GMT",
        "transfer_encoding": "chunked"
    },
    "id": "as-39n23w94",
    "name": "workspaces/wsicykvi/projects/proj-NMX22gln/annotationsets/as-CvxBLTK6",
    "localName": "as-CvxBLTK6",
    "displayName": "多属性",
    "description": "",
    "category": {
        "objectType": "annotationset",
        "objectName": "workspaces/wsicykvi/projects/proj-NMX22gln/annotationsets/as-CvxBLTK6",
        "parentType": "project",
        "parentName": "workspaces/wsicykvi/projects/proj-NMX22gln",
        "workspaceID": "wsicykvi",
        "name": "workspaces/wsicykvi/categories/category-5gkm7gdz",
        "localName": "category-5gkm7gdz",
        "category": "Image/ImageClassification/MultiTask",
        "createdAt": "2024-10-22T13:06:04.413Z",
        "updatedAt": "2024-10-22T13:06:04.413Z"
    },
    "labels": [
        {
            "localName": "0",
            "id": "⚄",
            "displayName": "安全帽",
            "color": "#0ce77e",
            "parentID": "",
            "confidence": 0,
            "labels": None,
            "annotationSetName": "as-CvxBLTK6",
            "projectName": "proj-NMX22gln",
            "workspaceID": "wsicykvi",
            "createdAt": "2024-10-22T13:09:36.872Z",
            "updatedAt": "2024-10-22T13:09:36.872Z",
            "deletedAt": 0
        },
        {
            "localName": "0",
            "id": "⚅",
            "displayName": "未戴安全帽",
            "color": "#081fa8",
            "parentID": "0",
            "confidence": 0,
            "labels": None,
            "annotationSetName": "as-CvxBLTK6",
            "projectName": "proj-NMX22gln",
            "workspaceID": "wsicykvi",
            "createdAt": "2024-10-22T13:09:36.919Z",
            "updatedAt": "2024-10-22T13:09:36.919Z",
            "deletedAt": 0
        },
        {
            "localName": "1",
            "id": "⚆",
            "displayName": "戴安全帽",
            "color": "#9473f8",
            "parentID": "0",
            "confidence": 0,
            "labels": None,
            "annotationSetName": "as-CvxBLTK6",
            "projectName": "proj-NMX22gln",
            "workspaceID": "wsicykvi",
            "createdAt": "2024-10-22T13:09:36.962Z",
            "updatedAt": "2024-10-22T13:09:36.962Z",
            "deletedAt": 0
        },
        {
            "localName": "1",
            "id": "⚇",
            "displayName": "工服",
            "color": "#126ec8",
            "parentID": "",
            "confidence": 0,
            "labels": None,
            "annotationSetName": "as-CvxBLTK6",
            "projectName": "proj-NMX22gln",
            "workspaceID": "wsicykvi",
            "createdAt": "2024-10-22T13:09:36.986Z",
            "updatedAt": "2024-10-22T13:09:36.986Z",
            "deletedAt": 0
        },
        {
            "localName": "0",
            "id": "⚈",
            "displayName": "未穿工服",
            "color": "#9c884b",
            "parentID": "1",
            "confidence": 0,
            "labels": None,
            "annotationSetName": "as-CvxBLTK6",
            "projectName": "proj-NMX22gln",
            "workspaceID": "wsicykvi",
            "createdAt": "2024-10-22T13:09:37.028Z",
            "updatedAt": "2024-10-22T13:09:37.028Z",
            "deletedAt": 0
        },
        {
            "localName": "1",
            "id": "⚉",
            "displayName": "工服",
            "color": "#58d2b6",
            "parentID": "1",
            "confidence": 0,
            "labels": None,
            "annotationSetName": "as-CvxBLTK6",
            "projectName": "proj-NMX22gln",
            "workspaceID": "wsicykvi",
            "createdAt": "2024-10-22T13:09:37.058Z",
            "updatedAt": "2024-10-22T13:09:37.058Z",
            "deletedAt": 0
        }
    ],
    "imageCount": 2,
    "annotatedImageCount": 2,
    "inferedImageCount": 2,
    "size": "67.85kB",
    "uri": "s3://windmill/store/workspaces/wsicykvi/projects/proj-NMX22gln/annotationsets/as-CvxBLTK6",
    "jobs": [
        {
            "workspaceID": "public",
            "name": "workspaces/public/projects/default/jobs/annoJob-dcsmb6um",
            "localName": "annoJob-dcsmb6um",
            "displayName": "",
            "description": "",
            "kind": "Annotation/Export",
            "experimentName": "",
            "specKind": "Ray",
            "specName": "workspaces/public/projects/default/pipelines/anno-export-multiattributedataset/versions/16",
            "computeName": "workspaces/public/computes/raydefault",
            "fileSystemName": "workspaces/public/filesystems/defaulttest",
            "parameters": {"args": ""},
            "config": None,
            "tags": {
                "annotationSetName": "workspaces/wsicykvi/projects/proj-NMX22gln/annotationsets/as-CvxBLTK6",
                "artifactName": ""
            },
            "output": None,
            "status": "Succeeded",
            "orgID": "7957b155b5cf4e43833527b10132a928",
            "userID": "419b412dd5ff43c7b809960dfaf355e7",
            "projectName": "default",
            "createdAt": "2024-10-24T06:14:57.092Z",
            "updatedAt": "2024-10-24T10:59:31.564Z"
        },
        {
            "workspaceID": "public",
            "name": "workspaces/public/projects/default/jobs/annoJob-2s3vyquf",
            "localName": "annoJob-2s3vyquf",
            "displayName": "",
            "description": "",
            "kind": "Annotation/Export",
            "experimentName": "",
            "specKind": "Ray",
            "specName": "workspaces/public/projects/default/pipelines/anno-export-multiattributedataset/versions/16",
            "computeName": "workspaces/public/computes/raydefault",
            "fileSystemName": "workspaces/public/filesystems/defaulttest",
            "parameters": {"args": ""},
            "config": None,
            "tags": {
                "annotationSetName": "workspaces/wsicykvi/projects/proj-NMX22gln/annotationsets/as-CvxBLTK6",
                "artifactName": ""
            },
            "output": None,
            "status": "Succeeded",
            "orgID": "7957b155b5cf4e43833527b10132a928",
            "userID": "419b412dd5ff43c7b809960dfaf355e7",
            "projectName": "default",
            "createdAt": "2024-10-24T06:13:56.982Z",
            "updatedAt": "2024-10-24T10:59:31.596Z"
        }
    ]
}
ANNOTATION_LABELS = [{'local_name': '0', 'display_name': '安全帽', 'parent_id': ''},
                     {'local_name': '0', 'display_name': '未戴安全帽', 'parent_id': '0'},
                     {'local_name': '1', 'display_name': '戴安全帽', 'parent_id': '0'},
                     {'local_name': '1', 'display_name': '工服', 'parent_id': ''},
                     {'local_name': '0', 'display_name': '未穿工服', 'parent_id': '1'},
                     {'local_name': '1', 'display_name': '工服', 'parent_id': '1'}]
