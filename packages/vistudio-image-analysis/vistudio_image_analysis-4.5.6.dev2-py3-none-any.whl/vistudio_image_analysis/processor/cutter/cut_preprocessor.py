#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   cut_preprocessor.py
@Time    :   2024/5/11 16:48
@Author  :   dongling
"""

import pandas as pd
from typing import Union, Dict, Any
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.operator.vistudio_cutter import VistudioCutter


class VistudioCutterPreprocessor(Preprocessor):
    """
    to cut vistudio
    """

    def __init__(self, config, location, split):
        self._is_fittable = True
        self._fitted = True

        self.config = config
        self.location = location
        self.split = split

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 1, "concurrency": 128}

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = VistudioCutter(self.config.filesystem, self.location, self.split)
        return operator.cut_images_and_annotations(source=df)
