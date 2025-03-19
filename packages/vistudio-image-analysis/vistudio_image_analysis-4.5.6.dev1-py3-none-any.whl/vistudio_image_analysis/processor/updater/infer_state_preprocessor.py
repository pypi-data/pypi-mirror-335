#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   infer_state_preprocessor.py
@Time    :   2024/03/13 16:49:57
@Author  :   <chujianfei@baidu.com>
"""
from typing import Dict, Any

import pandas as pd
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.operator.updater.infer_state_updater import InferStateUpdater


class InferStateUpdaterPreprocessor(Preprocessor):
    """
    to update infer_state
    """

    def __init__(self, config):
        self._is_fittable = True
        self._fitted = True

        self.config = config

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 100}

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = InferStateUpdater(config=self.config)
        return operator.update_infer_state(source=df)