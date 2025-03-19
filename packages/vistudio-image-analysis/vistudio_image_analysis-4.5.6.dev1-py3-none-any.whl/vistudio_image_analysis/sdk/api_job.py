# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
api_job.py
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""
from typing import Optional
from pydantic import BaseModel

from pygraphv1.client.graph_api_graph import GraphContent


class TriggerConfig(BaseModel):
    """
    TriggerConfig
    """
    cron_expression: str = None  # 传入时间表达是"* * * * * *" 分别代表 分 时 日 月 周 年
    interval: int = None  # 间隔时间，单位秒


class Trigger(BaseModel):
    """
    Trigger
    """
    kind: str  # once | cron | interval
    """
    周期，触发时间，间隔时间等 
    如果 kind 是 once, 不需要传参
    """
    config: Optional[TriggerConfig] = None


# 定义 Pydantic 模型，用于 API 请求
class CreateJobRequest(BaseModel):
    """
    CreateJobRequest
    """
    workspace_id: str
    local_name: str
    trigger: Trigger
    graph: GraphContent = None  # 图内容
    display_name: str = None