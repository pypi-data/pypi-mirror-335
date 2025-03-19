#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   preprocessor.py
"""
from typing import Union, Dict, List
from ray.data.preprocessor import Preprocessor
import bcelogger

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import _get_exist_images, _get_exist_annotation
from vistudio_image_analysis.operator.background_formatter import BackGroundFormatter
from vistudio_image_analysis.util import filter
from vistudio_image_analysis.operator.multiattributedataset_formatter import MultiAttributeDatasetFormatter


class MultiAttributeDatasetFormatPreprocessor(Preprocessor):
    """
    MultiAttributeDatasetFormatPreprocessor
    """

    def __init__(self,
                 config: Config,
                 data_uri: str = "",
                 data_types: list() = None,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 annotation_labels: Union[List] = list,
                 multi_attribute_labels: Union[List] = list,
                 tag: Union[Dict] = None
                 ):
        self.config = config
        self.data_uri = data_uri
        self.data_types = data_types
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.annotation_labels = annotation_labels
        self.multi_attribute_labels = multi_attribute_labels
        self.tag = tag
        self.exist_images = _get_exist_images(config=self.config,
                                              annotation_set_id=self.annotation_set_id)  # 已经存在的图片，用于过滤
        self.exist_annotations = _get_exist_annotation(config=self.config,
                                                      annotation_set_id=self.annotation_set_id)  # 已经存在的标注，用于过滤

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        fit
        :param ds:
        :return:
        """

        multiattribute_formatter = MultiAttributeDatasetFormatter(annotation_labels=self.annotation_labels,
                                                                  annotation_set_id=self.annotation_set_id,
                                                                  annotation_set_name=self.annotation_set_name,
                                                                  user_id=self.config.user_id,
                                                                  org_id=self.config.org_id,
                                                                  tag=self.tag,
                                                                  multi_attribute_labels=self.multi_attribute_labels,
                                                                  data_uri=self.data_uri,
                                                                  data_types=self.data_types)
        ds_dict = multiattribute_formatter.to_vistudio_v1(ds=ds)

        image_ds = ds_dict.get("image_ds")
        annotation_ds = ds_dict.get("annotation_ds")

        bg_formatter = BackGroundFormatter()
        annotation_ds = bg_formatter.generator_background_annotation(image_ds=image_ds, annotation_ds=annotation_ds)
        filter_image_ds = filter.filter_image(source=image_ds, existed_images=self.exist_images)
        bcelogger.info("filter imagenet image ds count={}".format(filter_image_ds.count()))
        filter_annotation_ds = filter.filter_annotation(source=annotation_ds,
                                                        existed_annotations=self.exist_annotations)
        bcelogger.info("filter imagenet annotation ds count={}".format(filter_annotation_ds.count()))
        self.stats_ = {"image_ds": filter_image_ds, "annotation_ds": filter_annotation_ds}
        return self
