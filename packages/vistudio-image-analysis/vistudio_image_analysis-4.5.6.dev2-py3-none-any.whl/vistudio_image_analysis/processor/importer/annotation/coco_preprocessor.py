#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   coco_preprocessor.py
"""
from typing import Union, Dict, Any
import bcelogger
from ray.data.preprocessor import Preprocessor

from windmilltrainingv1.client.training_client import TrainingClient

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import _get_exist_images, _get_exist_annotation
from vistudio_image_analysis.operator.coco_formatter import CocoFormatter
from vistudio_image_analysis.operator.background_formatter import BackGroundFormatter
from vistudio_image_analysis.util import filter


class CocoFormatPreprocessor(Preprocessor):
    """
    CocoFormatPreprocessor
    """
    def __init__(
        self,
        config: Config,
        labels: Union[Dict] = dict,
        annotation_set_id: str = None,
        annotation_set_name: str = None,
        data_uri: str = "",
        data_types: list() = None,
        tag: Union[Dict] = None,
        annotation_set_category: str = None,
        import_labels: Union[Dict] = None,
    ):
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.labels = labels
        self.tag = tag
        self.annotation_set_category = annotation_set_category
        self.import_labels = import_labels

        # 已经存在的图片，用于过滤
        self.exist_images = _get_exist_images(config=self.config, annotation_set_id=self.annotation_set_id)
        # 已经存在的标注，用于过滤
        self.exist_annotations = _get_exist_annotation(config=self.config, annotation_set_id=self.annotation_set_id)

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """
        coco_formatter = CocoFormatter(
            labels=self.labels,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            data_uri=self.data_uri,
            data_types=self.data_types,
            user_id=self.config.user_id,
            org_id=self.config.org_id,
            tag=self.tag,
            annotation_set_category=self.annotation_set_category,
            import_labels=self.import_labels
        )
        res = dict()
        format_ds_dict = coco_formatter.to_vistudio_v1(ds=ds)
        image_ds = format_ds_dict.get("image_ds", None)
        annotation_ds = format_ds_dict.get("annotation_ds", None)

        bg_formatter = BackGroundFormatter()
        annotation_ds = bg_formatter.generator_background_annotation(image_ds=image_ds, annotation_ds=annotation_ds)
        if image_ds is not None:
            filter_image_ds = filter.filter_image(source=image_ds, existed_images=self.exist_images)
            bcelogger.info("filter coco image ds.filter_image_ds count={}".format(filter_image_ds.count()))
            res['image_ds'] = filter_image_ds
        if annotation_ds is not None:
            filter_annotation_ds = filter.filter_annotation(source=annotation_ds,
                                                            existed_annotations=self.exist_annotations)
            bcelogger.info(
                "filter coco annotation ds.filter_annotation_ds count={}".format(filter_annotation_ds.count()))
            res['annotation_ds'] = filter_annotation_ds
        self.stats_ = res
        return self
