"""
mongo_datasink.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
import json
from typing import Optional, Dict

import bcelogger
from pygraphv1.client.graph_api_operator import Operator
from ray.data import Dataset, read_datasource

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.operator.base_operator import OPERATOR
from vistudio_image_analysis.operator.datasink.datasink import Datasink


@OPERATOR.register_module(name="MongoDatasink", version="1")
class MongoDatasinkV1(Datasink):
    """
    MongoDatasinkV1
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        super().__init__(config=config, meta=meta)
        # TODO Metric Tricker

    def execute(self, ds: Dataset):
        """
        execute
        """
        ds.write_mongo(uri=self.config.mongodb.mongo_uri,
                       database=self.config.mongodb.db,
                       collection=self.config.mongodb.collection)


