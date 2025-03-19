#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/6
# @Author  : yanxiaodong
# @File    : entrypoint.py
"""
import os
from argparse import ArgumentParser
import base64
import json

from bcelogger.base_logger import setup_logger
import bcelogger
from pygraphv1.client.graph_api_graph import GraphContent

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.runner.runner import Runner
from vistudio_image_analysis.runner.flow import flows_run_async
from vistudio_image_analysis.service.clients import Clients


def parse_args():
    """
    Parse arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--graph", type=str, default=os.environ.get("GRAPH"))
    parser.add_argument("--config", type=str, default=os.environ.get("CONFIG"))

    args, _ = parser.parse_known_args()

    return args


def main(args):
    """
    Main function
    """
    graph = json.loads(base64.b64decode(args.graph).decode('utf-8'))
    bcelogger.info(f"Graph is: {graph}")

    config = json.loads(base64.b64decode(args.config).decode('utf-8'))
    bcelogger.info(f"Config is: {config}")

    config = Config(config)
    client = Clients(config=config)
    graph = GraphContent(**graph)
    runner = Runner(client=client.get_job_client(), graph=graph, config=config)

    flows_run_async(flows=runner.flows)


if __name__ == "__main__":
    setup_logger(config=dict(logger_name='ray.serve'))

    args = parse_args()

    main(args)