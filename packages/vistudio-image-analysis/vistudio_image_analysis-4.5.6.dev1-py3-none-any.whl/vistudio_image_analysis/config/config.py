# !/usr/bin/env python3
# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
config.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
import os
from typing import Optional, Dict, Any, Union, Tuple

from bceserver.db.config import DBConfig
from pydantic import BaseModel

from bceserver.conf import DEFAULT_CONFIG_FILE_PATH, ENV_SERVER_CONFIG_PATH


class SchedulerConfig(BaseModel):
    """
    APScheduler配置
    """
    store_kind: str = "mongodb"
    max_instances: int = 1  # maximum number of concurrently running instances allowed for the job


class MongoDBConfig(BaseModel):
    """
    MongoDB配置
    """
    host: str
    port: int
    user: str
    password: str
    db: str
    collection: str
    shard_user: str = None
    shard_password: str = None
    mongo_uri: str = ""


class WindmillConfig(BaseModel):
    """
    Windmill配置
    """
    endpoint: str
    ak: str = ""
    sk: str = ""


class VistudioConfig(BaseModel):
    """
    Vistudio配置
    """
    endpoint: str
    ak: str = ""
    sk: str = ""


class AuthConfig(BaseModel):
    """
    Auth配置
    """
    org_id: str = ""
    user_id: str = ""


class ImageAnalysisConfig(BaseModel):
    """
    Vistudio配置
    """
    endpoint: str


class Config(BaseModel):
    """
    作业运行时配置
    """
    job_name: str = "",
    mongodb: MongoDBConfig = None,
    windmill: WindmillConfig = None,
    vistudio: VistudioConfig = None,
    auth: AuthConfig = None
    scheduler_config: SchedulerConfig = None
    image_analysis: ImageAnalysisConfig = None
    db: DBConfig = None

    def __init__(self, config_data: Dict[str, Any]):
        super().__init__()
        self.job_name = config_data.get('job_name', None)

        if config_data.get("mongodb") is not None:
            self.mongodb = MongoDBConfig(**config_data.get("mongodb"))
            self._parse_config()

        if config_data.get("windmill") is not None:
            self.windmill = WindmillConfig(**config_data.get("windmill"))

        if config_data.get("vistudio") is not None:
            self.vistudio = VistudioConfig(**config_data.get("vistudio"))

        if config_data.get("image_analysis") is not None:
            self.image_analysis = ImageAnalysisConfig(**config_data.get("image_analysis"))

        if config_data.get("db") is not None:
            self.db = DBConfig(**config_data.get("db"))

        if config_data.get("auth") is not None:
            self.auth = AuthConfig(**config_data.get("auth"))
        else:
            self.auth = AuthConfig()

        if config_data.get("scheduler_config") is not None:
            self.scheduler_config = SchedulerConfig(**config_data.get("scheduler_config"))
        else:
            self.scheduler_config = SchedulerConfig()

    def _get_mongo_uri(self):
        """
        get_mongo_uri
        """

        if not self.mongodb:
            return ''
        mongo_uri = "mongodb://{}:{}@{}:{}".format(
            self.mongodb.user,
            self.mongodb.password,
            self.mongodb.host,
            self.mongodb.port
        )
        return mongo_uri

    def _parse_config(self):
        """
        parse_config
        """

        if self.mongodb:
            self.mongodb.mongo_uri = self._get_mongo_uri()


def init_config() -> Config:
    """
    init_config
    """
    from toml import load
    config_file_path = DEFAULT_CONFIG_FILE_PATH
    if (
            os.environ.get(ENV_SERVER_CONFIG_PATH) is not None
            and os.environ.get(ENV_SERVER_CONFIG_PATH) != ""
    ):
        config_file_path = os.environ.get(ENV_SERVER_CONFIG_PATH)

    config_data = load(config_file_path)

    init_params = list(Config.__fields__.keys())

    filtered_config = {k: v for k, v in config_data.items() if k in init_params}
    config = Config(filtered_config)
    return config


if __name__ == "__main__":
    config_file_path = "../service/config.toml"
    os.environ[ENV_SERVER_CONFIG_PATH] = config_file_path
    config = init_config()
