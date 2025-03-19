# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/9 16:02
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : test_import_multiattributedataset_pipeline.py
# @Software: PyCharm
"""
import os
import yaml
import ray

from unittest import mock

from vistudio_image_analysis.tests.test_import_multiattributedataset_pipeline_config import \
    MULTIATTRIBUTE_PIPELINE_ARGS, \
    MULTIATTRIBUTE_PIPELINE_DOCUMENTS
from vistudio_image_analysis.operator.multiattributedataset_formatter import MultiAttributeDatasetFormatter
from vistudio_image_analysis.pipeline.import_multiattributedataset_pipeline import run
from vistudio_image_analysis.tests.mock.mock_mongodb import MongoDBClient
from vistudio_image_analysis.tests.test_import_multiattributedataset_pipeline_config import \
    GET_ANNOTATION_SET_RESPONSE, \
    GET_FILESYSTEM_CREDENTIAL, \
    FILE_URIS, \
    ZIP_FILE_URI, \
    ZIP_DIR
from vistudio_image_analysis.tests.mock.mock_server import get_bce_response

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 读取本地文件
train_txt = ray.data.read_text(os.path.join(current_dir, "testdata/multiattributedataset/annotations/train.txt"))

label_info_path = os.path.join(current_dir, "testdata/multiattributedataset/annotations/label_description.yaml")
label_info = ray.data.from_items([yaml.safe_load(open(label_info_path))])


@mock.patch('ray.data.read_text')
def test_multi_attribute_dataset_formatter(mock_read_text):
    """
    Test the MultiAttributeDatasetFormatter class.
    """
    mock_read_text.return_value = train_txt
    multiattribute_formatter = MultiAttributeDatasetFormatter(annotation_labels=ANNOTATION_SET_LABEL,
                                                              annotation_set_id='as-n6jdhp8z',
                                                              annotation_set_name='workspaces/default/projects/'
                                                                                  'proj-vistudio-ut/annotationsets/'
                                                                                  'as-vistudio-ut',
                                                              user_id="test",
                                                              org_id="test",
                                                              tag=None,
                                                              multi_attribute_labels=MULTI_ATTRIBUTE_LABELS,
                                                              data_uri='s3://windmill-test/store/workspaces/default/'
                                                                       'projects/proj-vistudio-ut/annotationsets/'
                                                                       'as-vistudio-ut/nt7Svx1B/'
                                                                       'data/multiattribute_dataset',
                                                              data_types=['annotation', 'image'])
    ds = ray.data.read_text()
    rows = ds.take_all()
    # 对每一行进行处理
    for row in rows:
        # 调用填充图像信息和注释信息的函数
        multiattribute_formatter._fill_image_info_vistudio(row=row)
        multiattribute_formatter._fill_annotation_info_vistudio(row=row)


@mock.patch('vistudio_image_analysis.client.annotation_client.AnnotationClient.get_annotation_set')
@mock.patch('windmillcomputev1.client.compute_client.ComputeClient.get_filesystem_credential')
@mock.patch('vistudio_image_analysis.operator.reader.Reader.get_zip_file_uris')
@mock.patch('vistudio_image_analysis.processor.importer.zip.zip_preprocessor.ZipFormatPreprocessor.fit')
@mock.patch('vistudio_image_analysis.operator.reader.Reader.get_file_uris')
@mock.patch('vistudio_image_analysis.operator.reader.Reader.read_label_yaml')
@mock.patch('ray.data.read_text')
def test_import_multiattributedataset_pipeline(
        mock_read_text,
        mock_read_label_yaml,
        mock_get_file_uris,
        mock_fit,
        mock_get_zip_file_uris,
        mock_get_filesystem_credential,
        mock_get_annotation_set
):
    """
    Test the ImportMultiAttributeDatasetPipeline class.
    """
    # 设置 Mock 返回值
    mock_read_text.return_value = train_txt
    mock_read_label_yaml.return_value = label_info
    mock_get_file_uris.return_value = FILE_URIS
    mock_get_zip_file_uris.return_value = ZIP_FILE_URI
    mock_fit.return_value = MockZip()
    mock_get_annotation_set.return_value = get_bce_response(GET_ANNOTATION_SET_RESPONSE)
    mock_get_filesystem_credential.return_value = get_bce_response(GET_FILESYSTEM_CREDENTIAL)

    # 初始化 MongoDB
    mongo_client = MongoDBClient(MULTIATTRIBUTE_PIPELINE_ARGS)
    mongo_client.init()
    mongo_client.insert(MULTIATTRIBUTE_PIPELINE_DOCUMENTS)

    # 测试多属性数据集导入流程
    run(MULTIATTRIBUTE_PIPELINE_ARGS)

    # 清理 MongoDB 集合
    mongo_client.delete_collection()
    mongo_client.close()


class MockZip:
    """Mock class for ZipFormatPreprocessor"""

    def __init__(self):
        self.stats_ = ZIP_DIR


ANNOTATION_SET_LABEL = [{'local_name': '0', 'display_name': '安全帽', 'parent_id': ''},
                        {'local_name': '0', 'display_name': '未戴安全帽', 'parent_id': '0'},
                        {'local_name': '1', 'display_name': '戴安全帽', 'parent_id': '0'},
                        {'local_name': '1', 'display_name': '工服', 'parent_id': ''},
                        {'local_name': '0', 'display_name': '未穿工服', 'parent_id': '1'},
                        {'local_name': '1', 'display_name': '工服', 'parent_id': '1'}]

MULTI_ATTRIBUTE_LABELS = [{'display_name': '安全帽', 'parent_id': None, 'anno_key': 1, 'local_name': '1'},
                          {'local_name': '0', 'display_name': '未戴安全帽', 'parent_name': '安全帽', 'parent_id': '1'},
                          {'local_name': '1', 'display_name': '戴安全帽', 'parent_name': '安全帽', 'parent_id': '1'},
                          {'display_name': '工服', 'parent_id': None, 'anno_key': 2, 'local_name': '2'},
                          {'local_name': '0', 'display_name': '未穿工服', 'parent_name': '工服', 'parent_id': '2'},
                          {'local_name': '1', 'display_name': '工服', 'parent_name': '工服', 'parent_id': '2'}]