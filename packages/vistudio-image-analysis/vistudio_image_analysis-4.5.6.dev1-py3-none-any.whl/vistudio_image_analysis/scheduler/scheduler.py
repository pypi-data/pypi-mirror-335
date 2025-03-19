#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/12/11
# @Author  : yanxiaodong
# @File    : trigger.py
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import MemoryJobStore

import bcelogger
from jobv1.client.job_api_job import JobName, StopJobRequest

from vistudio_image_analysis.scheduler.types import TriggerKind, JobStoreKind
from vistudio_image_analysis.scheduler.trigger import CronTrigger, OnceTrigger, IntervalTrigger
from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.runner.runner import Runner
from vistudio_image_analysis.sdk.api_job import CreateJobRequest


class Scheduler(object):
    """
    Scheduler 全局调度器
    """

    def __init__(self, config: Config):
        self.config = config

        self.scheduler = AsyncIOScheduler()

        bcelogger.info(f"Scheduler job store kind is {config.scheduler_config.store_kind}")
        if config.scheduler_config.store_kind == JobStoreKind.MONGODB.value:
            job_store = MongoDBJobStore(host=config.mongodb.host,
                                        port=config.mongodb.port,
                                        username=config.mongodb.user,
                                        password=config.mongodb.password)
        else:
            job_store = MemoryJobStore()
        self.scheduler.add_jobstore(jobstore=job_store)

        self.scheduler.start()

    def add_job(self, request: CreateJobRequest, runner: Runner):
        """
        scheduler add job
        """
        # 1、根据 request 中的 trigger kind，创建对应的 trigger
        if request.trigger.kind == TriggerKind.CRON.value:
            trigger = CronTrigger(cron_expression=request.trigger.config.cron_expression)
        elif request.trigger.kind == TriggerKind.ONCE.value:
            trigger = OnceTrigger()
        elif request.trigger.kind == TriggerKind.INTERVAL.value:
            trigger = IntervalTrigger(interval=request.trigger.config.interval)
        else:
            raise ValueError(f"Trigger Kind is not supported {request.trigger.kind}")

        # 2、scheduler 添加 job
        job_name = JobName(workspace_id=request.workspace_id, local_name=request.local_name)
        bcelogger.info(f"Adding job {job_name.get_name()} to scheduler")
        job = self.scheduler.add_job(func=runner.run,
                                     trigger=trigger,
                                     id=job_name.get_name(),
                                     args=[request],
                                     max_instances=self.config.scheduler_config.max_instances)
        bcelogger.info(f"Added job {job.id} to scheduler successful")

    def remove_job(self, request: StopJobRequest):
        """
        scheduler remove job
        """
        job_name = JobName(workspace_id=request.workspace_id, local_name=request.local_name)
        self.scheduler.remove_job(job_id=job_name.get_name())