#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   preprocessor.py
"""

from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.operator.zip_formatter import ZipFormatter


class ZipFormatPreprocessor(Preprocessor):
    """
    ZipFormatPreprocessor
    """
    def __init__(self, config: Config):
        self.config = config

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """
        zip_formatter = ZipFormatter(filesystem=self.config.filesystem)
        file_uris = zip_formatter.unzip_and_upload(file_uris=ds.unique(column='item'))
        self.stats_ = file_uris
        return self



