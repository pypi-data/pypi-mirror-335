#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   paddleclas_preprocessor.py
"""

from typing import Union, Dict, Any
import pandas as pd
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.operator.paddleclas_formatter import PaddleClasFormatter
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class PaddleClasFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert  vistudio to paddleclas
    """

    def __init__(
            self,
            label_index_map: Union[Dict] = dict,
            merge_labels: Union[Dict] = dict,
            counter: ImageAnnotationCounter = None,
    ):
        self._is_fittable = True
        self._fitted = True
        self.merge_labels = merge_labels
        self.label_index_map = label_index_map
        self.counter = counter

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        paddleclas_operator = PaddleClasFormatter(
            label_index_map=self.label_index_map,
            merge_labels=self.merge_labels,
            counter=self.counter
        )
        return paddleclas_operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 1, "concurrency": 128}
