#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/12/16
# @Author  : yanxiaodong
# @File    : types.py
"""
from enum import Enum


class TriggerKind(Enum):
    """
    Trigger Kind
    """
    CRON = "cron"
    ONCE = "once"
    INTERVAL = "interval"


class JobStoreKind(Enum):
    """
    Job Store Kind
    """
    MEMORY = "memory"
    MONGODB = "mongodb"