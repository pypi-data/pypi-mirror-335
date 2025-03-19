#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
formater.py
"""

from typing import Union, Dict, Any
import pandas as pd
import ray.data
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.operator.paddleocr_detect_formatter import PaddleOCRDetectFormatter
from vistudio_image_analysis.operator.paddleocr_recogn_formatter import PaddleOCRRecognFormatter
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class PaddleOCRDetectFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert vistudio_v1 to paddleseg
    """

    def __init__(self, counter: ImageAnnotationCounter = None):
        self._is_fittable = True
        self._fitted = True
        self.counter = counter

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = PaddleOCRDetectFormatter(counter=self.counter)
        return operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 1, "concurrency": 16}


class PaddleOCRRecognFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert vistudio_v1 to paddleseg
    """

    def __init__(self,
                 config: Config,
                 location: str = None,
                 counter: ImageAnnotationCounter = None
                 ):
        self._is_fittable = True
        self._fitted = True
        self.config = config
        self.location = location
        self.counter = counter

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = PaddleOCRRecognFormatter(
            filesystem=self.config.filesystem,
            location=self.location,
            counter=self.counter
        )
        return operator.from_vistudio_v1(source=df)

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 1, "concurrency": 128}
