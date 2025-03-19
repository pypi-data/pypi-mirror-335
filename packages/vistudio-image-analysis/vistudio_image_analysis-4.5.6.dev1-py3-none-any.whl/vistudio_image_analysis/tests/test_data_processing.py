#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_data_processing.py
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
    GET_ARTIFACT_RESPONSE, GET_ENDPOINT_RESPONSE, GET_ENDPOINT_STATUS_RESPONSE, GET_MODEL_RESPONSE, \
    CREATE_ANNOTATION_LABEL_RESPONSE, GET_JOB_RESPONSE, LIST_DEPLOY_JOBS_RESPONSE, \
    GET_ANNOTATION_SET_RESPONSE_WITH_MULTIMODAL
from windmillclient.client.mock import get_mock_server
from vistudio_image_analysis.tests.mock.mock_server import get_mock_server as get_mock_as_server, get_bce_response
from vistudio_image_analysis.pipeline.data_processing_pipeline import DataProcessingPipeline



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
    'org_id': 'test-org-id',
    'user_id': 'test-user-id',
    'artifact_name': 'workspaces/wsicykvi/modelstores/test-dl/models/paomaodilou-T4-moxingbao/versions/1',
    'operators': 'W3siYXJ0aWZhY3RfbmFtZSI6IndvcmtzcGFjZXMvd3NpY3lrdmkvbW9kZWxzdG9yZXMvbXMtTndnOHpiY20vbW9kZWxzL2R1b3No'
                 'dXhpbmdqaXN1MTExNS1SMjAwLW1veGluZ2Jhby92ZXJzaW9ucy8xIiwib3BlcmF0b3JfbmFtZSI6ImluZmVyIn0seyJtZXJnZV9sY'
                 'WJlbHMiOnsiMF8wIjoiMF8wIiwiMF8xIjoiMF8wIn0sIm9wZXJhdG9yX25hbWUiOiJtZXJnZV9sYWJlbCJ9XQ=='
}


data = [
    {
        'image_id': "fffdc2d92e7d68a2",
        'file_uri': os.path.dirname(os.path.abspath(__file__)) + "/store/image/xinpian.jpg",
        'image_name': 'xinpian.jpg',
        'width': 300,
        'height': 300,
        'annotation_state': 'Unannotated',
        'annotations': [],
    }
]

infer_data = [
    {
        'image_name': 'xinpian.jpg',
        'predictions': [
            {
                "area": 7158.201633849831,
                "bbox": [38.4525, 74.52693, 67.28091, 113.99186],
                "categories": [{"id": "1"}],
                "segmentation": [105.30486270838438, 182.09067147507045, 72.3072201880243, 188.51878365436136,
                                 38.45249604375883, 180.80504903921224, 40.166659291569744, 78.812335794463,
                                 71.45013856411887, 74.5269276749357, 105.7334035203371, 79.66941741836845]
            },
        ],
    }
]

@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.InferencePreprocessor.get_model_metadata_with_retry')
@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.init_py_filesystem')
@mock.patch('windmillartifactv1.client.artifact_client.ArtifactClient.get_artifact')
@mock.patch('vistudio_image_analysis.pipeline.data_processing_pipeline.read_datasource')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.get_endpoint')
@mock.patch('windmillendpointv1.client.endpoint_monitor_client.EndpointMonitorClient.get_endpoint_status')
@mock.patch('windmillmodelv1.client.model_client.ModelClient.get_model')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.create_annotation_label')
@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.CityscapesImageDatasource')
@mock.patch('ray.data.read_datasource')
@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.InferencePreprocessor.update_infer_state')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.create_endpoint_hub')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.update_endpoint')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.create_deploy_endpoint_job')
@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.get_template_parameters')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.get_job')
@mock.patch('ray.data.Dataset.write_mongo')
def test_data_processing(
    mock_write_mongo,
    mock_get_job,
    mock_get_template_parameters,
    mock_create_deploy_endpoint_job,
    mock_update_endpoint,
    mock_create_endpoint_hub,
    mock_update_infer_state,
    mock_read_ray_data_datasource,
    mock_cityscapes_image_datasource,
    mock_create_annotation_label,
    mock_get_model,
    mock_get_endpoint_status,
    mock_get_endpoint,
    mock_read_datasource,
    mock_get_artifact,
    mock_init_py_fs,
    mock_get_annotation_set,
    mock_get_fs_credential,
    mock_get_model_metadata_with_retry
):
    mock_get_template_parameters.return_value = {}
    mock_create_deploy_endpoint_job.return_value = None
    mock_update_endpoint.return_value = None
    mock_create_endpoint_hub.return_value = None
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_get_artifact.return_value = get_bce_response(GET_ARTIFACT_RESPONSE)
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_get_endpoint.return_value = get_bce_response(GET_ENDPOINT_RESPONSE)
    mock_get_endpoint_status.return_value = get_bce_response(GET_ENDPOINT_STATUS_RESPONSE)
    mock_get_model.return_value = get_bce_response(GET_MODEL_RESPONSE)
    mock_create_annotation_label.return_value = get_bce_response(CREATE_ANNOTATION_LABEL_RESPONSE)
    mock_cityscapes_image_datasource.return_value = None
    mock_read_ray_data_datasource.return_value.map.return_value = ray.data.from_pandas(pd.DataFrame(infer_data))
    mock_update_infer_state.return_value = None
    mock_get_job.return_value = get_bce_response(GET_JOB_RESPONSE)
    mock_write_mongo.return_value = None
    mock_get_model_metadata_with_retry.return_value = None, None, None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    pipeline = DataProcessingPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()


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
    'org_id': 'test-org-id',
    'user_id': 'test-user-id',
    'artifact_name': 'workspaces/wsicykvi/modelstores/test-dl/models/paomaodilou-T4-moxingbao/versions/1',
    'operators': 'W3siYXJ0aWZhY3RfbmFtZSI6IndvcmtzcGFjZXMvcHVibGljL21vZGVsc3RvcmVzL2RlZmF1bHQvbW9kZWxzL21vZGVsLVpUa1Npc2VyL3ZlcnNpb25zLzEiLCJpbmZlcl9jb25maWciOnsicmVwZXRpdGlvbl9wZW5hbHR5IjoxLjUsInRlbXBlcmF0dXJlIjowLjYsInRvcF9wIjoxfSwib3BlcmF0b3JfbmFtZSI6ImluZmVyIiwicHJvbXB0Ijoi5Zu+5Lit5Yqo54mp55qE6aKc6Imy5piv77yfXG4ifV0='
}

@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.init_py_filesystem')
@mock.patch('vistudio_image_analysis.pipeline.data_processing_pipeline.read_datasource')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.get_endpoint')
@mock.patch('windmillendpointv1.client.endpoint_monitor_client.EndpointMonitorClient.get_endpoint_status')
@mock.patch('vistudio_image_analysis.processor.data_processor.inference_preprocessor.InferencePreprocessor.update_infer_state')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.list_deploy_endpoint_job')
@mock.patch('windmillendpointv1.client.endpoint_client.EndpointClient.update_endpoint')
@mock.patch('windmilltrainingv1.client.training_client.TrainingClient.get_job')
@mock.patch('ray.data.Dataset.write_mongo')
def test_multimodal_data_processing(
    mock_write_mongo,
    mock_get_job,
    mock_update_endpoint,
    mock_list_deploy_endpoint_job,
    mock_update_infer_state,
    mock_get_endpoint_status,
    mock_get_endpoint,
    mock_read_datasource,
    mock_init_py_fs,
    mock_get_annotation_set,
    mock_get_fs_credential,
):
    mock_update_endpoint.return_value = None
    mock_list_deploy_endpoint_job.return_value = get_bce_response(LIST_DEPLOY_JOBS_RESPONSE)
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITH_MULTIMODAL)
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_read_datasource.return_value = ray.data.from_pandas(pd.DataFrame(data))
    mock_get_endpoint.return_value = get_bce_response(GET_ENDPOINT_RESPONSE)
    mock_get_endpoint_status.return_value = get_bce_response(GET_ENDPOINT_STATUS_RESPONSE)
    mock_update_infer_state.return_value = None
    mock_get_job.return_value = get_bce_response(GET_JOB_RESPONSE)
    mock_write_mongo.return_value = None

    # mock mongo
    mongo_client = MongoDBClient(args)
    mongo_client.init()

    pipeline = DataProcessingPipeline(args)
    pipeline.run()

    # 删除集合
    mongo_client.delete_collection()
    # 关闭连接
    mongo_client.close()