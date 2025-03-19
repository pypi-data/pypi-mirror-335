#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   vistudio_preprocessor.py
"""
from typing import Union, Dict
import bcelogger
from ray.data.preprocessor import Preprocessor
from ray.data import Dataset

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import _get_exist_images, _get_exist_annotation
from vistudio_image_analysis.util import filter
from vistudio_image_analysis.operator.background_formatter import BackGroundFormatter
from vistudio_image_analysis.operator.vistudio_formatter import VistudioFormatter


class VistudioFormatPreprocessor(Preprocessor):
    """
    VistudioFormatPreprocessor
    """
    def __init__(
        self,
        config: Config,
        labels: Union[Dict] = None,
        annotation_set_id: str = None,
        annotation_set_name: str = None,
        data_uri: str = None,
        data_types: list() = None,
        tag: Union[Dict] = None,
        import_labels: Union[Dict] = None,
        annotation_set_category: str = None,
    ):
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.tag = tag
        self.import_labels = import_labels
        self.annotation_set_category = annotation_set_category

        if labels is not None:
            self.labels = labels

        # 已经存在的图片，用于过滤
        self.exist_images = _get_exist_images(config=self.config, annotation_set_id=self.annotation_set_id)
        # 已经存在的人工标注，用于过滤
        self.exist_manual_annotations = _get_exist_annotation(
            config=self.config, annotation_set_id=self.annotation_set_id)
        # 已经存在的模型标注，用于过滤
        self.exist_model_annotations = _get_exist_annotation(
            config=self.config, annotation_set_id=self.annotation_set_id, task_kind='Model')

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        fit dataset
        :param ds:
        :return: Preprocessor
        """
        vistudio_formatter = VistudioFormatter(
            config=self.config,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            annotation_set_category=self.annotation_set_category,
            data_uri=self.data_uri,
            data_types=self.data_types,
            tag=self.tag,
            labels=self.labels,
            import_labels=self.import_labels,
        )
        format_ds_dict = vistudio_formatter.to_vistudio_v1(ds=ds)

        image_ds = format_ds_dict["image_ds"]
        anno_ds = format_ds_dict["annotation_ds"]
        pred_ds = format_ds_dict["prediction_ds"]

        bg_formatter = BackGroundFormatter()
        anno_ds = bg_formatter.generator_background_annotation(image_ds=image_ds, annotation_ds=anno_ds)

        res = {}
        filter_image_ds = filter.filter_image(source=image_ds, existed_images=self.exist_images)
        res['image_ds'] = filter_image_ds

        filter_anno_ds = filter.filter_annotation(source=anno_ds, existed_annotations=self.exist_manual_annotations)
        res['annotation_ds'] = filter_anno_ds

        filter_pred_ds = filter.filter_annotation(source=pred_ds, existed_annotations=self.exist_model_annotations)
        res['prediction_ds'] = filter_pred_ds

        self.stats_ = res
        return self
