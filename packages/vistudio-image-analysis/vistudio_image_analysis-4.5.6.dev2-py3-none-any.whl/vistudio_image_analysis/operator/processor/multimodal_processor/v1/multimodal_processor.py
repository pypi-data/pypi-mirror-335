"""
mongo_datasource.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
import base64
import json
from typing import Optional, Dict, List
from urllib.parse import urlparse

import mysql.connector

import bcelogger
import ray
from jobv1.client.job_api_job import parse_job_name, UpdateJobRequest
from jobv1.client.job_client import JobClient
from lmdeployv1.api import BatchChatCompletionRequest, LimiterConfig
from lmdeployv1.client import build_batch_chat_messages, LMDeployClient
from pygraphv1.client.graph_api_operator import Operator
from ray.data import Dataset, read_datasource
from windmillcomputev1.filesystem import blobstore
from windmillendpointv1.client.endpoint_client import EndpointClient
from windmillendpointv1.client.endpoint_monitor_client import EndpointMonitorClient
from windmillendpointv1.client.gaea.api import InferConfig, ModelInferRequest
from windmillendpointv1.client.gaea.infer import infer
from windmilltrainingv1.client.training_client import TrainingClient

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.datasource import mongo_query_pipeline, ShardedMongoDatasource
from vistudio_image_analysis.operator.datasource.datasource import Datasource
from vistudio_image_analysis.operator.processor.processor import Processor
from vistudio_image_analysis.util import string
from vistudio_image_analysis.operator.base_operator import OPERATOR


@OPERATOR.register_module(name="MultiModalProcessor", version="1")
class MultiModalProcessorV1(Processor):
    """
    MultiModalProcessorV1
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        super().__init__(config=config, meta=meta)

        # TODO Metric Tricker

    def execute(self, ds_list: List[Dataset]) -> Optional[Dict[str, Dataset]]:
        """
        execute
        """
        # TODO
        return {self.meta.outputs[0].name: ds_list[0]}

