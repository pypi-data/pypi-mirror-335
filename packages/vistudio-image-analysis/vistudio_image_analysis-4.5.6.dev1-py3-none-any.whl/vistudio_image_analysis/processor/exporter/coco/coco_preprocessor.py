#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
formater.py
"""

from typing import Union, Dict, Any
import pandas as pd
import ray.data
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.operator.coco_formatter import CocoFormatter
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class CocoFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert vistudio_v1 to coco
    """

    def __init__(self,
                 merge_labels: Union[Dict] = dict,
                 labels: Union[Dict] = dict,
                 counter: ImageAnnotationCounter = None):
        self._is_fittable = True
        self._fitted = True
        self.merge_labels = merge_labels
        self.labels = labels
        self.counter = counter

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        coco_operator = CocoFormatter(labels=self.labels,
                                      merge_labels=self.merge_labels,
                                      counter=self.counter)
        return coco_operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 1, "concurrency": 128}


class CocoMergePreprocessor(Preprocessor):
    """
    use this Preprocessor to merge coco dataset by item
    """

    def __init__(self, labels: Union[Dict] = dict, merge_labels: Union[Dict] = dict):
        self._is_fittable = True
        self._fitted = True
        self.labels = labels
        self.merge_labels = merge_labels

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        coco_operator = CocoFormatter(labels=self.labels, merge_labels=self.merge_labels)
        df = ds.to_pandas()
        self.stats_ = ray.data.from_pandas(coco_operator.merge(rows=df))
        return self
