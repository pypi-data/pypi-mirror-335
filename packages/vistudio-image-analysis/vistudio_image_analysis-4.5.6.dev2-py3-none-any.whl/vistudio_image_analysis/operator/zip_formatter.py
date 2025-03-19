#!/usr/bin/env python3
# -*-coding:utf-8-*-
# -*- encoding: utf-8 -*-
"""
@File    :   zip_formatter.py
"""
import os.path
from typing import Union, Dict
import bcelogger
import subprocess
import shutil

from windmillcomputev1.filesystem import blobstore, upload_by_filesystem

from vistudio_image_analysis.operator.reader import zip_extensions


class ZipFormatter(object):
    """
    ZipFormatter
    """
    def __init__(self, filesystem: Union[Dict] = dict):
        self.filesystem = filesystem
        self.bs = blobstore(filesystem)

    def unzip_and_upload(self, file_uris: list()) -> str:
        """
        unzip_and_upload
        :param file_uris:
        :return:
        """
        data_uri = None
        for file_uri in file_uris:
            file_name = file_uri.split("/")[-1]
            if not (file_name.lower().endswith(zip_extensions)):
                return file_uris
            base_name, _ = os.path.splitext(file_name)
            directory_path = "/".join(file_uri.split("/")[:-1]).replace("s3://", "")
            directory_path = os.path.join(directory_path, base_name)

            dest_file = os.path.join(directory_path, file_name)
            if not os.path.exists(os.path.dirname(dest_file)):
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)

            self.bs.download_file(path=file_uri, file_name=dest_file)
            self.extract_archive(dest_file, directory_path)
            os.remove(dest_file)

            file_path = os.path.join(directory_path, file_name).rsplit("/", 1)[0]
            dest_path = os.path.join(("/".join(file_uri.split("/")[:-1])), base_name)
            bcelogger.info("unzip_and_upload file_path:{} dest_path:{}".format(file_path, dest_path))

            upload_by_filesystem(filesystem=self.filesystem, file_path=file_path, dest_path=dest_path)
            shutil.rmtree(file_path)
            data_uri = "s3://" + directory_path

        return data_uri

    @staticmethod
    def extract_archive(file_path, output_dir):
        """
        使用 subprocess 解压文件，根据文件扩展名判断解压方式。

        :param file_path: 压缩包的路径
        :param output_dir: 解压目标目录
        """
        # 创建输出目录（如果不存在）
        os.makedirs(output_dir, exist_ok=True)

        # 根据文件扩展名选择解压方法
        if file_path.endswith('.zip'):
            # 解压 .zip 文件
            subprocess.run(['unzip', file_path, '-d', output_dir], check=True)
            bcelogger.info(f"{file_path} unzipped successfully to {output_dir}")

        elif file_path.endswith(('.tar.gz', '.tgz')):
            # 解压 .tar.gz 或 .tgz 文件
            subprocess.run(['tar', '-xzf', file_path, '-C', output_dir], check=True)
            bcelogger.info(f"{file_path} extracted successfully to {output_dir}")

        elif file_path.endswith('.tar'):
            # 解压 .tar 文件
            subprocess.run(['tar', '-xf', file_path, '-C', output_dir], check=True)
            bcelogger.info(f"{file_path} extracted successfully to {output_dir}")

        else:
            bcelogger.info(f"Unsupported file format: {file_path}")
