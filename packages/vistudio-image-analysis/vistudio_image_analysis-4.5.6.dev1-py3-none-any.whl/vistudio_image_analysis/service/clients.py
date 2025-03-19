# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
clients.py
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""
from bceserver.context import  get_context
from jobv1.client.job_client import JobClient

from vistudio_image_analysis.config.config import Config


class Clients:
    """
    Client class
    """

    def __init__(self, config: Config):
        """job sdk client"""
        self.config = config
        self.job_client = JobClient(endpoint=config.windmill.endpoint)

    def get_job_client(self):
        """
        get_job_client
        """
        if not self.job_client:
            raise ValueError("client cannot be empty")
        if self.config.auth is not None \
                and self.config.auth.org_id != "" \
                and self.config.auth.user_id != "":
            self.job_client.context = {"OrgID": self.config.auth.org_id, "UserID": self.config.auth.user_id}
        else:
            self.job_client.context = get_context()['auth_info']
        return self.job_client
