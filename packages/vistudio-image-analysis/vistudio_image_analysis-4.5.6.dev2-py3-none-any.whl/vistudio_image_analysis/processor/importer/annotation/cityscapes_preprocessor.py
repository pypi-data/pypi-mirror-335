#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   preprocessor.py
"""
from typing import Union, Dict
import bcelogger
from ray.data import Dataset
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import _get_exist_images, _get_exist_annotation
from vistudio_image_analysis.operator.cityscapes_formatter import CityscapesFormatter
from vistudio_image_analysis.operator.background_formatter import BackGroundFormatter
from vistudio_image_analysis.util import filter


class CityscapesFormatPreprocessor(Preprocessor):
    """
    CityscapesFormatPreprocessor
    """
    def __init__(self,
                 config: Config,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 labels: Union[Dict] = None,
                 tag: Union[Dict] = None,
                 import_labels: Union[Dict] = None,
                 ):
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.labels = labels
        self.tag = tag
        self.import_labels = import_labels
        self.exist_images = _get_exist_images(config=self.config,
                                              annotation_set_id=self.annotation_set_id)  # 已经存在的图片，用于过滤
        self.exist_annotations = _get_exist_annotation(config=self.config,
                                                      annotation_set_id=self.annotation_set_id)  # 已经存在的标注，用于过滤

    def _fit(self, ds: Dataset) -> Preprocessor:
        cityscapes_formatter = CityscapesFormatter(labels=self.labels,
                                                   annotation_set_id=self.annotation_set_id,
                                                   annotation_set_name=self.annotation_set_name,
                                                   user_id=self.config.user_id,
                                                   org_id=self.config.org_id,
                                                   filesystem=self.config.filesystem,
                                                   tag=self.tag,
                                                   import_labels=self.import_labels)
        format_ds_dict = cityscapes_formatter.to_vistudio_v1(ds=ds)
        image_ds = format_ds_dict.get("image_ds", None)
        annotation_ds = format_ds_dict.get("annotation_ds", None)

        bg_formatter = BackGroundFormatter()
        annotation_ds = bg_formatter.generator_background_annotation(image_ds=image_ds, annotation_ds=annotation_ds)
        filter_image_ds = None
        filter_annotation_ds = None
        if image_ds is not None:
            filter_image_ds = filter.filter_image(source=image_ds, existed_images=self.exist_images)
            bcelogger.info("filter cityscapes image ds count={}".format(filter_image_ds.count()))
        if annotation_ds is not None:
            filter_annotation_ds = filter.filter_annotation(source=annotation_ds,
                                                        existed_annotations=self.exist_annotations)
            bcelogger.info("filter cityscapes annotation ds count={}".format(filter_annotation_ds.count()))
        self.stats_ = {"image_ds": filter_image_ds, "annotation_ds": filter_annotation_ds}
        return self


