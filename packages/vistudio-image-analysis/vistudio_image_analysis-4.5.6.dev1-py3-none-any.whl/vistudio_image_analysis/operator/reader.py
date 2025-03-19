#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   reader.py
"""

from typing import List, Union, Dict
import os

import bcelogger
import ray
from ray.data import Dataset
from urllib.parse import urlparse
from windmillcomputev1.filesystem import blobstore, init_py_filesystem
from windmillcomputev1.filesystem.blobstore import BlobMeta, KIND_S3, blobstore_config
from windmillcomputev1.filesystem.s3 import remove_prefix

from vistudio_image_analysis.datasource.label_yaml_datasource import LabelYamlDatasource
from vistudio_image_analysis.datasource.multi_json_datasource import MultiJSONDatasource
from vistudio_image_analysis.datasource.xml_datasource import XMLDatasource

image_extensions = ('.jpeg', '.jpg', '.png', '.bmp')
zip_extensions = ('.zip', '.tar.gz', '.tar', '.tgz')
cityscape_annotation_file_extensions = ('.jpeg', '.jpg', '.png', '.bmp', '.txt')
annotation_extensions = ('.json', '.jsonl', '.xml')
multiattributedataset_annotation_extensions = ('.txt', '.yaml')
vqa_extensions = '.jsonl'

exclude_pkg = ("-thumbnail", "-webp", "_MACOSX")


class Reader(object):
    """
    Reader
    """

    def __init__(self,
                 filesystem: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 ):
        self._filesystem = filesystem
        self.annotation_set_id = annotation_set_id
        self.s3_bucket = filesystem.get('endpoint').split("/")[0]

        self.bs = blobstore(filesystem)
        self.fs = init_py_filesystem(filesystem)
        kind, endpoint, config = blobstore_config(filesystem=filesystem)
        self._bucket = endpoint.split("/")[0]

    def _get_filenames(self, file_uri, layer):
        """
        :param file_uri: s3地址
        :param layer: 遍历的层数
        :return: 文件filename列表
        """

        filenames = []
        dest_path = file_uri.split(self.s3_bucket + '/')[1]
        if not dest_path.endswith("/"):
            dest_path += "/"
        dest_parts = dest_path.split('/')[:-1]

        file_list = self._list_meta_by_continuation_token(dest_path)
        for file in file_list:
            f_path = file.url_path.split(self.s3_bucket + '/')[1]
            f_parts = f_path.split('/')[:-1]
            # 此处表示取文件夹3层内的数据
            if len(f_parts) - len(dest_parts) > layer:
                continue
            filename = "s3://" + os.path.join(self.s3_bucket, f_path)
            filenames.append(filename)

        bcelogger.info("_get_filenames filenames counts:{}".format(filenames))
        return filenames

    def get_annotation_file_uris(self, data_uri, valid_extensions, layer=3):
        """
        get annotation file uris by data_uri
        :param data_uri: 传入的数据地址
        :param valid_extensions: 有效的文件后缀，由导入的标注格式限制
        :param layer: 遍历的层数
        :return: list
        """
        annotation_file_uri = data_uri
        # 获取全部要处理的标注文件
        ext = os.path.splitext(annotation_file_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(annotation_file_uri, layer)
        else:
            filenames = [annotation_file_uri]

        file_uris = list()
        for filename in filenames:
            if not filename.lower().endswith(valid_extensions) or "._" in filename:
                continue
            file_uris.append(filename)
        return file_uris

    def get_imagenet_annotation_fileuris(self, data_uri) -> list():
        """
        get annotation file uris by data_uri
        :param data_uri:
        :return: list
        """
        file_uris = list()
        image_uris = self._get_filenames(data_uri, 2)
        for image_uri in image_uris:
            if not image_uri.lower().endswith(image_extensions) or "._" in image_uri:
                continue
            # 获取相对路径
            relative_path = os.path.relpath(image_uri, data_uri)

            # 获取下一级目录
            label_name = relative_path.split(os.sep)[0]
            if label_name.endswith(exclude_pkg):
                continue
            file_uri_dict = {"label": label_name, "image": image_uri}
            file_uris.append(file_uri_dict)

        return file_uris

    def get_image_file_uris(self, data_uri, valid_extensions) -> list():
        """
        get image file uris by data_uri
        :param data_uri:
        :param valid_extensions:
        :return:
        """
        image_uri = data_uri

        ext = os.path.splitext(image_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(image_uri, 3)
        else:
            filenames = [image_uri]

        # 插入图像
        file_uris = list()
        for filename in filenames:
            if "-thumbnail/" in filename or "-webp/" in filename or "._" in filename:
                continue

            if not filename.lower().endswith(valid_extensions):
                continue

            _, file_name = os.path.split(filename)
            file_uris.append(filename)

        return file_uris

    @staticmethod
    def _fetch_path(path: str):
        if os.path.splitext(path)[1] == "":
            path = path.rstrip("/") + "/"

        return path

    def _get_bucket_and_key(self, path: str):
        parse_endpoint = urlparse(path)
        if parse_endpoint.scheme == "":
            return self._bucket, path.lstrip('/')

        assert parse_endpoint.scheme == KIND_S3, "Path scheme should be {}, bug got is {}".format(KIND_S3,
                                                                                                  parse_endpoint.scheme)
        bucket = parse_endpoint.netloc
        bucket_index = path.find(bucket)
        return bucket, path[bucket_index + len(bucket):].lstrip('/')

    def _list_meta_by_continuation_token(self, path):
        path = self._fetch_path(path)
        bucket, key = self._get_bucket_and_key(path)
        metas = []
        continuation_token = None
        while True:
            response = self.bs.list_objects_v2(path=path, continuation_token=continuation_token)

            # 处理当前批次对象
            for obj in response.get("Contents", []):
                if os.path.splitext(obj['Key'])[1] != "":
                    metas.append(BlobMeta(
                        name=remove_prefix(obj["Key"], response["Prefix"]),
                        size=obj["Size"],
                        url_path=KIND_S3 + "://" + bucket + "/" + obj["Key"],
                        last_modified=obj["LastModified"],
                    ))

            # 检查是否还有下一页
            if not response.get("IsTruncated"):
                break

            # 更新 continuation token
            continuation_token = response.get("NextContinuationToken")
        return metas

    def get_file_uris(self, data_uri: str, data_types: list(), annotation_format: str = None) -> list():
        """
        get_file_uris
        :param data_uri:
        :param data_types:
        :param annotation_format:
        :return:
        """
        annotation_pkg_suffix = 'annotations' if annotation_format in {'multiattributedataset', 'coco'} else ''

        if len(data_types) == 1:
            if data_types[0] == "image":
                file_uris = self.get_image_file_uris(data_uri=data_uri, valid_extensions=image_extensions)

            if data_types[0] == "annotation":
                if annotation_format == 'cityscapes':
                    file_uris = self.get_image_file_uris(
                        data_uri=data_uri, valid_extensions=cityscape_annotation_file_extensions)
                elif annotation_format == 'vqa':
                    file_uris = self.get_annotation_file_uris(data_uri=data_uri, valid_extensions=vqa_extensions)
                else:
                    file_uris = self.get_annotation_file_uris(data_uri=data_uri, valid_extensions=annotation_extensions)
        else:
            anno_uri = os.path.join(data_uri, annotation_pkg_suffix)
            # 获取所有的图片和文件 uri
            if annotation_format == 'imagenet':
                file_uris = self.get_imagenet_annotation_fileuris(data_uri=anno_uri)
            elif annotation_format == 'cityscapes':
                file_uris = self.get_image_file_uris(
                    data_uri=anno_uri, valid_extensions=cityscape_annotation_file_extensions)
            elif annotation_format == 'multiattributedataset':
                file_uris = self.get_annotation_file_uris(
                    data_uri=anno_uri, valid_extensions=multiattributedataset_annotation_extensions)
            elif annotation_format == 'vqa':
                file_uris = self.get_annotation_file_uris(
                    data_uri=anno_uri, valid_extensions=vqa_extensions, layer=0)
            else:
                file_uris = self.get_annotation_file_uris(data_uri=anno_uri, valid_extensions=annotation_extensions)

        return file_uris

    def get_zip_file_uris(self, data_uri: str) -> list():
        """
        get_zip_file_uris
        :param data_uri:
        :return:
        """
        zip_uri = data_uri

        ext = os.path.splitext(zip_uri)[1].lower()
        if ext == "":
            filenames = self._get_filenames(zip_uri, 0)
        else:
            filenames = [zip_uri]

        # 插入图像
        file_uris = list()
        for filename in filenames:
            if not filename.lower().endswith(zip_extensions):
                continue

            _, file_name = os.path.split(filename)
            file_uris.append(filename)

        return file_uris

    def read_json(self, file_uris: List[str]) -> Dataset:
        """
        read json
        :param file_uris:
        :return: Dataset
        """
        import pyarrow.json as pajson
        block_size = 100 << 20
        ds = ray.data.read_json(paths=file_uris, filesystem=self.fs,
                                read_options=pajson.ReadOptions(block_size=block_size),
                                parse_options=pajson.ParseOptions(newlines_in_values=True))
        return ds

    def read_multijson(self, file_uris: List[str]) -> Dataset:
        """
        read multijson
        :param file_uris:
        :return: Dataset
        """
        import pyarrow.json as pajson
        block_size = 100 << 20
        multi_json_datasource = MultiJSONDatasource(paths=file_uris, filesystem=self.fs)
        ds = ray.data.read_datasource(datasource=multi_json_datasource,
                                      read_options=pajson.ReadOptions(block_size=block_size),
                                      parse_options=pajson.ParseOptions(newlines_in_values=True)
                                      )
        return ds

    def read_xml(self, file_uris: List[str]) -> Dataset:
        """
        read xml
        :param file_uris:
        :return: Dataset
        """
        xml_datasource = XMLDatasource(paths=file_uris, filesystem=self.fs)
        ds = ray.data.read_datasource(datasource=xml_datasource)
        return ds

    def read_label_yaml(self, label_file_uris: List[str]) -> Dataset:
        """
        read xml
        :param file_uris:
        :return: Dataset
        """
        label_yaml_datasource = LabelYamlDatasource(paths=label_file_uris, filesystem=self.fs)
        ds = ray.data.read_datasource(datasource=label_yaml_datasource)
        return ds
