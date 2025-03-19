#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   base_pipeline.py
"""

import bcelogger
import json

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.util import string
from vistudio_image_analysis.datasource import mongo_query_pipeline
from vistudio_image_analysis.datasource.sharded_mongo_datasource import ShardedMongoDatasource


class BaseDataProcessingPipeline(object):
    """
    BaseImportPipline
    """

    def __init__(self, args: dict()):
        bcelogger.info("BaseInferPipline Init Start!")
        self.args = args
        self.config = Config(args)
        self.datasource = self._get_datasource()

        bcelogger.info("BaseInferPipline Init End!")

    def _get_decoded_json_arg(self, arg_name):
        """
        _get_decoded_json_arg
        :return:
        """
        if self.args.get(arg_name) is not None and self.args.get(arg_name) != '':
            decoded_json = json.loads(string.decode_from_base64(self.args.get(arg_name)))
        else:
            decoded_json = None
        bcelogger.info(f"{arg_name}: decoded_json")
        return decoded_json

    def _get_datasource(self):
        """
        get datasource
        :return:
        """
        pipeline = self._get_decoded_json_arg('q')
        if pipeline is None:
            return
        func = mongo_query_pipeline.get_pipeline_func(pipeline)

        return ShardedMongoDatasource(uri=self.config.mongo_uri,
                                      database=self.config.mongodb_database,
                                      collection=self.config.mongodb_collection,
                                      pipeline_func=func,
                                      shard_username=self.config.mongodb_shard_username,
                                      shard_password=self.config.mongodb_shard_password)


