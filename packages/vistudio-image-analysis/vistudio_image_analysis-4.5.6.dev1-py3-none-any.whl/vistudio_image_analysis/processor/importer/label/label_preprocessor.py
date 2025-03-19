#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   label_preprocessor.py
"""
from typing import Union, Dict, List
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.operator.label_formatter import LabelFormatter


class LabelFormatPreprocessor(Preprocessor):
    """
    LabelFormatPreprocessor
    """
    def __init__(
        self,
        config: Config,
        annotation_format: str,
        labels: Union[List] = list,
        annotation_set_category: str = None,
    ):
        self._is_fittable = True
        self.config = config
        self.labels = labels
        self.annotation_format = annotation_format
        self.annotation_set_category = annotation_set_category

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        """
        _fit
        :param ds:
        :return:
        """
        label_formatter = LabelFormatter(
            labels=self.labels,
            annotation_format=self.annotation_format,
            filesystem=self.config.filesystem,
            annotation_set_category=self.annotation_set_category
        )
        labels_dict = label_formatter.labels_to_vistudio_v1(ds=ds)

        self.stats_ = labels_dict
        return self
