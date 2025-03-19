# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
multiattributedataset
"""

from typing import List, Dict
from pydantic import BaseModel
import yaml


# 定义单个任务结构
class Task(BaseModel):
    """
    Task
    """
    task_type: str
    task_name: str
    anno_key: int
    categories: dict


# 定义包含多个任务的结构
class Tasks(BaseModel):
    """
    Tasks
    """
    tasks: List[Task]



