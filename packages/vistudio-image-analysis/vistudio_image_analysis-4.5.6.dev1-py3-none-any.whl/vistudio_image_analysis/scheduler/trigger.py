#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/12/17
# @Author  : yanxiaodong
# @File    : trigger.py
"""
from croniter import croniter
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger as APScheduleCronTrigger
from apscheduler.triggers.date import DateTrigger as APScheduleDateTrigger
from apscheduler.triggers.interval import IntervalTrigger as APScheduleIntervalTrigger

import bcelogger


class CronTrigger(APScheduleCronTrigger):
    """
    CronTrigger
    继承 apscheduler 的 CronTrigger
    1. 校验 cron_expression 格式是否正确
    2. 转换为 apscheduler 的 CronTrigger 参数
    """
    def __init__(self, cron_expression: str = None):
        # 1. 校验 cron_expression 格式是否正确
        try:
            croniter(cron_expression, datetime.now())
        except Exception as err:
            bcelogger.error(f"Cron expression: {cron_expression} is not valid")
            raise ValueError(err)

        # 2. 转换为 apscheduler 的 CronTrigger 参数
        values = cron_expression.split()
        super(CronTrigger, self).\
            __init__(minute=values[0], hour=values[1], day=values[2], month=values[3], day_of_week=values[4])


class OnceTrigger(APScheduleDateTrigger):
    """
    OnceTrigger
    继承 apscheduler 的 DateTrigger
    """
    def __init__(self, run_date: str = None):
        super(OnceTrigger, self).__init__(run_date=run_date)


class IntervalTrigger(APScheduleIntervalTrigger):
    """
    IntervalTrigger
    继承 apscheduler 的 IntervalTrigger
    1. 转换为 apscheduler 的 IntervalTrigger 参数
    """

    def __init__(self, interval: int = None):
        super(IntervalTrigger, self).__init__(minutes=interval)