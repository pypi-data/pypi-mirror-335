#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_export.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/25 10:52
"""
import os.path
import json
from unittest import mock
import pandas as pd
import ray.data

from vistudio_image_analysis.tests.mock.mock_mongodb import MongoDBClient
from vistudio_image_analysis.tests.mock.mock_data import GET_LOCAL_FILESYSTEM, GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR,\
    CREATE_LOCATION_RESPONSE
from windmillclient.client.mock import get_mock_server
from vistudio_image_analysis.tests.mock.mock_server import get_mock_server as get_mock_as_server, get_bce_response
from vistudio_image_analysis.operator.coco_formatter import CocoFormatter
from vistudio_image_analysis.pipeline.export_coco_pipeline import ExportCocoPipeline
from vistudio_image_analysis.pipeline.export_paddleseg_pipeline import ExportPaddleSegPipeline
from vistudio_image_analysis.pipeline.export_paddleclas_pipeline import ExportPaddleClasPipeline
from vistudio_image_analysis.pipeline.export_paddleocr_detect_pipeline import ExportPaddleOCRDetectPipeline
from vistudio_image_analysis.pipeline.export_paddleocr_recogn_pipeline import ExportPaddleOCRRecognPipeline


args = {
    'mongo_host': '10.27.240.45',
    'mongo_port': '8719',
    'mongo_user': 'root',
    'mongo_password': 'mongo123#',
    'mongo_database': 'annotation_ut',
    'mongo_collection': 'annotation_ut',
    'windmill_endpoint': get_mock_server(),
    'vistudio_endpoint': get_mock_as_server(),
    'filesystem_name': 'workspaces/public/filesystems/defaultfs',
    'job_name': 'workspaces/public/projects/default/jobs/annoJob-azonn3Vv',
    'annotation_set_name': 'workspaces/default/projects/pj-ut/annotationsets/as-ut',
    'annotation_format': '',
    'org_id': 'test-org-id',
    'user_id': 'test-user-id',
    'mongo_shard_password': '',
    'mongo_shard_username': '',
    'dataset': 'eyJhbm5vdGF0aW9uRm9ybWF0IjoiQ09DTyIsImFydGlmYWN0Ijp7InRhZ3MiOnt9fSwiY2F0ZWdvcnkiOiJJbWFnZS9PYmplY3RE'
               'ZXRlY3Rpb24iLCJkYXRhVHlwZSI6IkltYWdlIiwiZGlzcGxheU5hbWUiOiLnm67moIfmo4DmtYsxMDI1IiwibG9jYWxOYW1lIjoiZH'
               'MtdzRNUDZnUXYiLCJwcm9qZWN0TmFtZSI6InNwaXByb2plY3QiLCJ3b3Jrc3BhY2VJRCI6IndzZmR0bXRjIn0=',
    'export_to': "Dataset",
    'q': 'W3siYWdncmVnYXRpb24iOlt7IiRtYXRjaCI6eyJhbm5vdGF0aW9uX3NldF9pZCI6ImFzLTdkcHk0dXNqIn19LHsiJG1hdGNoIjp7ImRhdGF' \
         'fdHlwZSI6IkltYWdlIn19LHsiJG1hdGNoIjp7IiRhbmQiOlt7ImFubm90YXRpb25fc3RhdGUiOnsiJGluIjpbIkFubm90YXRlZCJdfX0sey' \
         'JpbWFnZV9pZCI6eyIkbmluIjpbXX19XX19XSwiY29sbGVjdGlvbiI6ImFubm90YXRpb24iLCJxdWVyeV9yZXN1bHRfbWFwcGluZyI6eyIiOiJ' \
         'pbWFnZXMiLCJpbWFnZV9pZCI6ImltYWdlX2lkcyJ9LCJkZWZhdWx0X3F1ZXJ5X3Jlc3VsdCI6eyJpbWFnZV9pZHMiOltdLCJpbWFnZXMiOltd' \
         'fSwiYWdncmVnYXRpb25fanNvbiI6IiJ9LHsiYWdncmVnYXRpb24iOlt7IiRtYXRjaCI6eyJhbm5vdGF0aW9uX3NldF9pZCI6ImFzLTdkcHk0' \
         'dXNqIn19LHsiJG1hdGNoIjp7ImRhdGFfdHlwZSI6IkFubm90YXRpb24ifX0seyIkbWF0Y2giOnsiaW1hZ2VfaWQiOnsiJGluIjoiJGxvb2t1' \
         'cDppbWFnZV9pZHMifX19LHsiJG1hdGNoIjp7ImFydGlmYWN0X25hbWUiOiIifX1dLCJjb2xsZWN0aW9uIjoiYW5ub3RhdGlvbiIsInF1ZXJ5' \
         'X3Jlc3VsdF9tYXBwaW5nIjp7IiI6ImFubm90YXRpb25zIn0sImRlZmF1bHRfcXVlcnlfcmVzdWx0IjpudWxsLCJhZ2dyZWdhdGlvbl9qc29u' \
         'IjoiIn1d',
    'merge_labels': 'e30=',
}


data = [
    {
        'image_id': "fffdc2d92e7d68a2",
        'file_uri': os.path.dirname(os.path.abspath(__file__)) + "/store/image/xinpian.jpg",
        'width': 300,
        'height': 300,
        'annotation_state': 'Annotated',
        'annotations': [
            {
                'annotations': [
                    {
                        "area": 7158.201633849831,
                        "bbox": [38.4525, 74.52693, 67.28091, 113.99186],
                        "labels": [{"id": "1"}],
                        "segmentation": [105.30486270838438,182.09067147507045,72.3072201880243,188.51878365436136,
                                         38.45249604375883,180.80504903921224,40.166659291569744,78.812335794463,
                                         71.45013856411887,74.5269276749357,105.7334035203371,79.66941741836845]
                    },
                    {
                        "area": 3286,
                        "bbox": [117, 239, 73, 49],
                        "labels": [{"id": "1"}],
                        "rle": {
                            "size": [300,300],
                            "counts": [35364,11,280,23,273,30,268,34,264,37,262,39,259,41,259,42,257,43,256,45,255,
                                       45,254,46,253,48,252,48,251,49,251,49,251,49,251,49,251,49,251,49,251,49,252,
                                       48,252,48,252,48,252,48,252,48,252,48,252,48,251,49,251,49,251,49,251,48,252,
                                       48,252,48,252,47,253,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,
                                       48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,
                                       48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,47,253,47,253,
                                       47,253,46,255,45,256,43,258,41,261,38,266,33,292,6,33021]
                        },
                    },
                    {
                        "area": 7013.854913027673,
                        "bbox": [77.3409007409222, 161.54917028963325, 131.99057008144015, 53.13906068213828],
                        "labels": [{"id": "1"}]
                    }
                ],
                'task_kind': 'Manual'
            }
        ]
    }
]

@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.operator.writer.init_py_filesystem')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.pipeline.export_coco_pipeline.read_datasource')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.create_location')
@mock.patch('ray.data.Dataset.write_json')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.create_dataset')
def test_export_coco(
    mock_create_dataset,
    mock_write_json,
    mock_create_location,
    mock_read_datasource,
    mock_get_annotation_set,
    mock_init_py_fs,
    mock_get_fs_credential
):
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_create_location.return_value = get_bce_response(CREATE_LOCATION_RESPONSE)
    mock_write_json.return_value = None
    mock_create_dataset.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    args['annotation_format'] = 'COCO'
    pipeline = ExportCocoPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.operator.writer.init_py_filesystem')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.pipeline.export_paddleseg_pipeline.read_datasource')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.create_location')
@mock.patch('ray.data.Dataset.write_images')
@mock.patch('ray.data.Dataset.write_csv')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.create_dataset')
def test_export_paddleseg(
    mock_create_dataset,
    mock_write_images,
    mock_write_csv,
    mock_create_location,
    mock_read_datasource,
    mock_get_annotation_set,
    mock_init_py_fs,
    mock_get_fs_credential
):
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_create_location.return_value = get_bce_response(CREATE_LOCATION_RESPONSE)
    mock_write_images.return_value = None
    mock_write_csv.return_value = None
    mock_create_dataset.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    args['annotation_format'] = 'PaddleSeg'
    pipeline = ExportPaddleSegPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.operator.writer.init_py_filesystem')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.pipeline.export_paddleclas_pipeline.read_datasource')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.create_location')
@mock.patch('ray.data.Dataset.write_csv')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.create_dataset')
def test_export_paddleclas(
    mock_create_dataset,
    mock_write_csv,
    mock_create_location,
    mock_read_datasource,
    mock_get_annotation_set,
    mock_init_py_fs,
    mock_get_fs_credential
):
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_create_location.return_value = get_bce_response(CREATE_LOCATION_RESPONSE)
    mock_write_csv.return_value = None
    mock_create_dataset.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    args['annotation_format'] = 'PaddleClas'
    pipeline = ExportPaddleClasPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.operator.writer.init_py_filesystem')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.pipeline.export_paddleocr_detect_pipeline.read_datasource')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.create_location')
@mock.patch('ray.data.Dataset.write_csv')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.create_dataset')
def test_export_paddleocr_detect(
    mock_create_dataset,
    mock_write_csv,
    mock_create_location,
    mock_read_datasource,
    mock_get_annotation_set,
    mock_init_py_fs,
    mock_get_fs_credential
):
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_create_location.return_value = get_bce_response(CREATE_LOCATION_RESPONSE)
    mock_write_csv.return_value = None
    mock_create_dataset.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    args['annotation_format'] = 'PaddleOCR'
    pipeline = ExportPaddleOCRDetectPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.operator.writer.init_py_filesystem')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.pipeline.export_paddleocr_recogn_pipeline.read_datasource')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.create_location')
@mock.patch('ray.data.Dataset.write_csv')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.create_dataset')
def test_export_paddleocr_recogn(
    mock_create_dataset,
    mock_write_csv,
    mock_create_location,
    mock_read_datasource,
    mock_get_annotation_set,
    mock_init_py_fs,
    mock_get_fs_credential
):
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_create_location.return_value = get_bce_response(CREATE_LOCATION_RESPONSE)
    mock_write_csv.return_value = None
    mock_create_dataset.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    args['annotation_format'] = 'PaddleOCR'
    pipeline = ExportPaddleOCRRecognPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()