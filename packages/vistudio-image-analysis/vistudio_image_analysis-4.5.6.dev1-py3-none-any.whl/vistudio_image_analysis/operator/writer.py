#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   writer.py
"""
from typing import List, Union, Dict

from windmillcomputev1.filesystem import init_py_filesystem

from vistudio_image_analysis.datasink.filename_provider import MultiFilenameProvider
from vistudio_image_analysis.datasink.csv_datasink import exclude_csv_header_func


class Writer(object):
    """
    Writer
    """
    def __init__(
            self,
            filesystem: Union[Dict] = dict,
    ):
        self.fs = init_py_filesystem(filesystem)

    def write_json_file(self, ds, base_path: str, file_name: str):
        """
        将数据集写成json
        """
        provider = MultiFilenameProvider(file_name=file_name)
        ds.write_json(
            path=base_path,
            filesystem=self.fs,
            filename_provider=provider,
            force_ascii=False
        )

    def write_txt_file(self, ds, base_path: str, file_name: str):
        """
        将数据集写成txt
        """
        provider = MultiFilenameProvider(file_name=file_name)
        ds.write_csv(
            path=base_path,
            filesystem=self.fs,
            filename_provider=provider,
            arrow_csv_args_fn=lambda: exclude_csv_header_func())

    def write_image_file(self, ds, base_path: str):
        """
        将数据集写成图片
        """
        provider = MultiFilenameProvider(is_full_file_name=False)
        ds.write_images(
            path=base_path,
            filesystem=self.fs,
            column="image",
            filename_provider=provider
        )
