#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   Processor.py
"""
from typing import Union, List, Optional, Dict, Any

import bcelogger
from jobv1.client.job_api_job import UpdateJobRequest, GetJobRequest, parse_job_name, GetJobResponse
from jobv1.client.job_client import JobClient
from pygraphv1.client.graph_api_operator import Operator
from ray.data import Dataset
from windmillcomputev1.filesystem import init_py_filesystem
from windmillendpointv1.client.endpoint_client import EndpointClient
from windmillendpointv1.client.endpoint_monitor_client import EndpointMonitorClient
from windmilltrainingv1.client.training_client import TrainingClient

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.operator.base_operator import BaseOperator


class Processor(BaseOperator):
    """
    Processor
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        super().__init__(config=config, meta=meta)

    def execute(self,  ds_list: List[Dataset]) -> Optional[Dict[str, Dataset]]:
        """
        execute
        """
        # Your logic here
        pass
