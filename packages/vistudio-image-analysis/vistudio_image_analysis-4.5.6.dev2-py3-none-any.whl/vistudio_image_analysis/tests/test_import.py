# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_import.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/25 10:52
"""
import os.path
import json
import shutil
import pandas as pd
import ray
from unittest import mock
from ray.data import read_json
from vistudio_image_analysis.tests.mock.mock_data import GET_LOCAL_FILESYSTEM, \
    GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR, CREATE_ANNOTATION_LABEL_RESPONSE
from windmillclient.client.mock import get_mock_server
from vistudio_image_analysis.tests.mock.mock_server import get_mock_server as get_mock_as_server, get_bce_response
from vistudio_image_analysis.pipeline.import_vistudio_pipeline import ImportVistudioPipeline
from vistudio_image_analysis.pipeline.import_coco_pipeline import ImportCocoPipeline
from vistudio_image_analysis.pipeline.import_cvat_pipeline import ImportCVATPipeline
from vistudio_image_analysis.pipeline.import_imagenet_pipeline import ImportImageNetPipeline
from vistudio_image_analysis.pipeline.import_cityscapes_pipeline import ImportCityscapesPipeline


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
    'data_uri': os.path.dirname(os.path.abspath(__file__)) + "/testdata/",
    'data_types': 'annotation,image',
    'file_format': 'file',
}


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.operator.reader.init_py_filesystem')
@mock.patch('vistudio_image_analysis.operator.reader.Reader._get_filenames')
@mock.patch('vistudio_image_analysis.operator.reader.Reader.read_json')
@mock.patch('vistudio_image_analysis.operator.label_formatter.init_py_filesystem')
@mock.patch('ray.data.Dataset.write_mongo')
def test_import_vistudio(
        mock_write_mongo,
        mock_label_init_py_fs,
        mock_read_json,
        mock_get_filenames,
        mock_init_py_fs,
        mock_get_annotation_set,
        mock_get_fs_credential
):
    mock_write_mongo.return_value = None
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_file_uris = [
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/vistudio/meta.json",
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/vistudio/jsonls/image.jsonl",
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/vistudio/jsonls/annotation.jsonl",
    ]
    mock_get_filenames.return_value = mock_file_uris
    mock_read_json.return_value = read_json(mock_file_uris)
    mock_label_init_py_fs.return_value = GET_LOCAL_FILESYSTEM

    args['annotation_format'] = 'VisionStudio'
    pipeline = ImportVistudioPipeline(args)
    pipeline.run()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.operator.reader.init_py_filesystem')
@mock.patch('vistudio_image_analysis.operator.reader.Reader._get_filenames')
@mock.patch('vistudio_image_analysis.operator.reader.Reader.read_multijson')
@mock.patch('vistudio_image_analysis.operator.label_formatter.init_py_filesystem')
@mock.patch('ray.data.Dataset.write_mongo')
def test_import_coco(
    mock_write_mongo,
    mock_label_init_py_fs,
    mock_read_multijson,
    mock_get_filenames,
    mock_init_py_fs,
    mock_get_annotation_set,
    mock_get_fs_credential
):
    mock_write_mongo.return_value = None
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_file_uris = [
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/coco/annotation.json",
    ]
    mock_get_filenames.return_value = mock_file_uris
    mock_read_multijson.return_value = read_json(mock_file_uris)
    mock_label_init_py_fs.return_value = GET_LOCAL_FILESYSTEM

    args['annotation_format'] = 'COCO'
    pipeline = ImportCocoPipeline(args)
    pipeline.run()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('bceinternalsdk.client.bce_internal_client.BceInternalClient._send_request')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.operator.reader.init_py_filesystem')
@mock.patch('vistudio_image_analysis.operator.label_formatter.init_py_filesystem')
@mock.patch('ray.data.Dataset.write_mongo')
@mock.patch('vistudio_image_analysis.operator.reader.Reader._get_filenames')
@mock.patch('vistudio_image_analysis.operator.reader.Reader.read_xml')
def test_import_cvat(
    mock_read_xmls,
    mock_get_filenames,
    mock_write_mongo,
    mock_label_init_py_fs,
    mock_init_py_fs,
    mock_get_annotation_set,
    mock_send_request,
    mock_get_fs_credential
):
    data = [
        {
            'labels': [
                {'color': '#a3bea1', 'name': '铁轨'},
                {'color': '#acc4aa', 'name': '人'}
            ],
            'images': [
                {'height': '720', 'id': '0', 'name': '09efa0d2-10198.jpg', 'width': '1280'},
                {'height': '960', 'id': '1', 'name': '11b77a31-12234.jpg', 'width': '1280'}
            ]
        }
    ]

    # 使用 ray.data.from_items() 初始化 Dataset
    ds = ray.data.from_items(data)
    mock_get_filenames.return_value = [os.path.dirname(os.path.abspath(__file__)) +
                                       "/testdata/cvat/annotations.xml",
                                       os.path.dirname(os.path.abspath(__file__)) +
                                       '/testdata/cvat/images/09efa0d2-10198.jpg',
                                       os.path.dirname(os.path.abspath(__file__)) +
                                       '/testdata/cvat/images/11b77a31-12234.jpg']
    folder_path = os.path.dirname(os.path.abspath(__file__)) + "/testdata/cvat/"
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cvat_compressed")
    shutil.make_archive(output_filename, 'zip', folder_path)
    mock_read_xmls.return_value = ds
    mock_write_mongo.return_value = None
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_send_request.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_label_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    args['annotation_format'] = 'CVAT'
    args['data_uri'] = output_filename + ".zip"
    args['file_format'] = 'zip'
    pipeline = ImportCVATPipeline(args)
    pipeline.run()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.operator.reader.init_py_filesystem')
@mock.patch('vistudio_image_analysis.operator.label_formatter.init_py_filesystem')
@mock.patch('ray.data.Dataset.write_mongo')
@mock.patch('vistudio_image_analysis.operator.reader.Reader._get_filenames')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.create_annotation_label')
def test_import_imagenet(
    mock_create_annotation_label,
    mock_get_filenames,
    mock_write_mongo,
    mock_label_init_py_fs,
    mock_init_py_fs,
    mock_get_annotation_set,
    mock_get_fs_credential
):
    mock_get_filenames.return_value = [
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/imagenet/铁轨/铁轨1.jpeg",
    ]

    mock_write_mongo.return_value = None
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_label_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_create_annotation_label.return_value = get_bce_response(CREATE_ANNOTATION_LABEL_RESPONSE)

    args['annotation_format'] = 'ImageNet'
    args['file_format'] = 'file'
    args['data_uri'] = os.path.dirname(os.path.abspath(__file__)) + "/testdata/imagenet"

    pipeline = ImportImageNetPipeline(args)
    pipeline.run()


@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('vistudio_image_analysis.operator.reader.init_py_filesystem')
@mock.patch('vistudio_image_analysis.operator.label_formatter.init_py_filesystem')
@mock.patch('ray.data.Dataset.write_mongo')
@mock.patch('vistudio_image_analysis.operator.reader.Reader._get_filenames')
@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.create_annotation_label')
@mock.patch('ray.data.read_text')
@mock.patch('vistudio_image_analysis.operator.cityscapes_formatter.init_py_filesystem')
def test_import_cityscapes(
    mock_cityscapes_init_py_fs,
    mock_read_text,
    mock_create_annotation_label,
    mock_get_filenames,
    mock_write_mongo,
    mock_label_init_py_fs,
    mock_init_py_fs,
    mock_get_annotation_set,
    mock_get_fs_credential
):
    mock_get_filenames.return_value = [
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes/label_colors.txt",
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes/leftImg8bit/cat3_leftImg8bit.jpeg",
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes/gtFine/cat3_gtFine_color.png",
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes/gtFine/cat3_gtFine_instanceIds.png",
        os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes/gtFine/cat3_gtFine_labels.png",
    ]

    mock_write_mongo.return_value = None
    mock_get_fs_credential.return_value = get_bce_response({"raw_data": json.dumps(GET_LOCAL_FILESYSTEM)})
    mock_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE_WITHOUT_ATTR)
    mock_label_init_py_fs.return_value = GET_LOCAL_FILESYSTEM
    mock_create_annotation_label.return_value = get_bce_response(CREATE_ANNOTATION_LABEL_RESPONSE)
    mock_read_text.return_value = ray.data.read_text(
        paths=os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes/label_colors.txt").to_pandas()['text']
    mock_cityscapes_init_py_fs.return_value = GET_LOCAL_FILESYSTEM

    args['annotation_format'] = 'Cityscapes'
    args['file_format'] = 'file'
    args['data_uri'] = os.path.dirname(os.path.abspath(__file__)) + "/testdata/cityscapes"

    pipeline = ImportCityscapesPipeline(args)
    pipeline.run()
