"""
mongo_datasource.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
import json
from typing import Optional, Dict

import bcelogger
from pygraphv1.client.graph_api_operator import Operator
from ray.data import Dataset, read_datasource

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.datasource import mongo_query_pipeline, ShardedMongoDatasource
from vistudio_image_analysis.operator.datasource.datasource import Datasource
from vistudio_image_analysis.util import string
from vistudio_image_analysis.operator.base_operator import OPERATOR


@OPERATOR.register_module(name="MongoDatasource", version="1")
class MongoDatasourceV1(Datasource):
    """
    MongoDatasourceV1
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        super().__init__(config=config, meta=meta)

        # TODO Metric Tricker

    def execute(self) -> Optional[Dict[str, Dataset]]:
        """
        execute
        """
        self.datasource = self._get_datasource()
        ds = read_datasource(self.datasource)
        if self.outputs is not None and len(self.outputs) > 0:
            ds = ds.select_columns(cols=self.outputs)

        return {self.meta.outputs[0].name: ds}

    def _get_mongo_pipeline(self):
        """
        get mongo pipeline
        :return:
        """
        q = self.meta.get_property("q").value
        if q is not None and q != '':
            mongo_pipeline = json.loads(string.decode_from_base64(q))
        else:
            mongo_pipeline = None

        bcelogger.info("mongo_pipeline:{}".format(mongo_pipeline))
        return mongo_pipeline

    def _get_datasource(self):
        """
        get datasource
        :return:
        """
        pipeline = self._get_mongo_pipeline()
        if pipeline is None:
            return
        func = mongo_query_pipeline.get_pipeline_func(pipeline)

        return ShardedMongoDatasource(uri=self.config.mongodb.mongo_uri,
                                      database=self.config.mongodb.db,
                                      collection=self.config.mongodb.collection,
                                      pipeline_func=func,
                                      shard_username=self.config.mongodb.shard_user,
                                      shard_password=self.config.mongodb.shard_password)
