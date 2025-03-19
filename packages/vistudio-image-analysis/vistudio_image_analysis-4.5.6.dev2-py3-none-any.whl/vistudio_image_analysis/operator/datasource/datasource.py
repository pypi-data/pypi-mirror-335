#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   datasource.py
"""
from typing import List, Optional, Dict, Any

from pygraphv1.client.graph_api_operator import Operator
from ray.data import Dataset

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.operator.base_operator import BaseOperator


class Datasource(BaseOperator):
    """
    Datasource
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        super().__init__(config=config, meta=meta)

    def execute(self) -> Optional[Dict[str, Dataset]]:
        """
        execute
        """
        # Your logic here
        raise NotImplementedError("Must implement process() in subclass")
