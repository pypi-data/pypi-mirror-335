# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/23 14:32
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : merge_label_preprocessor.py
# @Software: PyCharm
"""
import pandas as pd
from typing import Union, Dict, Any
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.operator.label_merger import LabelMerger


class MergeLabelPreprocessor(Preprocessor):
    """
    to merge label
    """

    def __init__(self, config, operator_params):
        self._is_fittable = True
        self._fitted = True
        self.config = config
        self.operator_params = operator_params

    def _get_transform_config(self) -> Dict[str, Any]:
        """Returns kwargs to be passed to :meth:`ray.data.Dataset.map_batches`.

        This can be implemented by subclassing preprocessors.
        """
        return {"batch_size": 100, "concurrency": 128}

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        _transform_pandas
        :param df:
        :return:
        """
        operator = LabelMerger(self.config, self.operator_params)
        return operator.merge_label(source=df)
