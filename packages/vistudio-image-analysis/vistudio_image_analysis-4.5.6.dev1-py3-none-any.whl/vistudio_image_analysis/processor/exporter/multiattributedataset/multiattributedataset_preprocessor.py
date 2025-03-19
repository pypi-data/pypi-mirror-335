#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File :   preprocessor.py
"""
from typing import Union, Dict, List, Any
from ray.data.preprocessor import Preprocessor
from vistudio_image_analysis.operator.multiattributedataset_formatter import MultiAttributeDatasetFormatter
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class MultiAttributeDatasetFormatExportPreprocessor(Preprocessor):
    """
    MultiAttributeDatasetFormatExportPreprocessor
    """

    def __init__(self,
                 annotation_labels: Union[List] = None,
                 merge_labels: Union[Dict] = None,
                 counter: ImageAnnotationCounter = None
                 ):
        self._is_fittable = True
        self._fitted = True
        self.merge_labels = merge_labels
        self.annotation_labels = annotation_labels
        self.counter = counter

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        multiattr_operator = MultiAttributeDatasetFormatter(annotation_labels=self.annotation_labels,
                                                            merge_labels=self.merge_labels,
                                                            counter=self.counter)
        return multiattr_operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 100}
