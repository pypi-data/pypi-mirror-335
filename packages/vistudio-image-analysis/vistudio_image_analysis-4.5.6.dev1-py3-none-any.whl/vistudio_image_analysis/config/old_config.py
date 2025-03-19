# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
Vistudio Spec
"""
from typing import Optional, Dict
from pydantic import BaseModel
import bcelogger
import json

from windmillcomputev1.client.compute_api_filesystem import parse_filesystem_name
from windmillcomputev1.client.compute_client import ComputeClient


class Config(BaseModel):
    """
    定义基础变量
    """
    filesystem: dict = None
    mongo_uri: str = ""
    mongodb_database: str = ""
    mongodb_collection: str = ""
    mongodb_shard_password: str = ""
    mongodb_shard_username: str = ""

    windmill_endpoint: str = ""

    vistudio_endpoint: str = ""
    job_name: str = ""
    iou_threshold: float = 0.5

    org_id: str = ""
    user_id: str = ""
    bce_client_context: dict = {}

    bce_client_context: Optional[Dict[str, str]] = None

    def __init__(self, args: dict()):
        super().__init__(
            job_name=args.get('job_name', ''),
            mongodb_database=args.get('mongo_database', ''),
            mongodb_collection=args.get('mongo_collection', ''),
            windmill_endpoint=args.get('windmill_endpoint', ''),
            vistudio_endpoint=args.get('vistudio_endpoint', ''),
            org_id=args.get('org_id', ''),
            user_id=args.get('user_id', ''),
            mongodb_shard_password=args.get('mongo_shard_password', ''),
            mongodb_shard_username=args.get('mongo_shard_username', ''),
        )

        self.parse_args(args)

    def parse_args(self, args: dict()):
        """
        parse_args
        :param args:
        :return:
        """
        mongo_user = args.get('mongo_user')
        mongo_password = args.get('mongo_password')
        mongo_host = args.get('mongo_host')
        mongo_port = args.get('mongo_port')
        self.mongo_uri = "mongodb://{}:{}@{}:{}".format(
            mongo_user,
            mongo_password,
            mongo_host,
            mongo_port
        )
        self.bce_client_context = {"OrgID": self.org_id, "UserID": self.user_id}

        if args.get('filesystem_name') is None:
            return

        fs_name = parse_filesystem_name(args.get('filesystem_name'))
        compute_client = ComputeClient(
            endpoint=self.windmill_endpoint,
            context=self.bce_client_context
        )

        fs_res = compute_client.get_filesystem_credential(
            fs_name.workspace_id,
            fs_name.local_name
        )
        self.filesystem = json.loads(fs_res.raw_data)

        try:
            self.iou_threshold = float(args.get('iou_threshold'))
        except Exception as e:
            self.iou_threshold = 0.5
            bcelogger.info("Failed to convert iou_threshold to float, using default value 0.5. Error: {}".format(e))