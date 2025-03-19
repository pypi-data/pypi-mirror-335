#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   ImageUriFormatter.py
"""
from typing import Union, Dict, Any, List
from ray.data.preprocessor import Preprocessor
from ray.data import Dataset
import ray.data

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import _get_exist_images
from vistudio_image_analysis.util import filter
from vistudio_image_analysis.operator.image_formatter import ImageFormatter

import bcelogger

time_pattern = "%Y-%m-%dT%H:%M:%SZ"


class ImageFormatterPreprocessor(Preprocessor):
    """
    ImageFormatterPreprocessor
    """

    def __init__(self,
                 config: Config,
                 annotation_set_id: str,
                 annotation_set_name: str,
                 tag: Union[Dict] = None):
        self._is_fittable = True
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.tag = tag

        self.exist_images = _get_exist_images(config=self.config,
                                              annotation_set_id=self.annotation_set_id)  # 已经存在的图片，用于过滤

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return: Preprocessor
        """
        bcelogger.info("only import image. original_image_ds_count:{} ".format(ds.count()))
        image_formatter = ImageFormatter(
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            user_id=self.config.user_id,
            org_id=self.config.org_id,
            tag=self.tag
        )
        format_ds = image_formatter.to_vistudio_v1(ds)
        bcelogger.info("only import image. format_ds count:{} ".format(format_ds.count()))

        df = filter.drop_duplicates(source=format_ds.to_pandas(), cols=['image_id'])
        format_ds = ray.data.from_pandas(df)

        filter_image_ds = filter.filter_image(source=format_ds, existed_images=self.exist_images)
        bcelogger.info("filter  image ds.filter_image_ds count={}".format(filter_image_ds.count()))

        self.stats_ = filter_image_ds
        return self
