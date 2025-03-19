# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
service.py
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""
import os

from ray import serve
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends

import bcelogger
from bcelogger.base_logger import setup_logger
from bceserver.auth import get_authenticate_dependency
from bceserver.conf import ENV_SERVER_CONFIG_PATH, new_config
from bceserver.middleware.response import ModifyResponseMiddleware
from jobv1.client.job_api_job import StopJobRequest, CreateJobRequest, CreateJobResponse

from vistudio_image_analysis.config.config import Config, init_config
from vistudio_image_analysis.scheduler.types import TriggerKind
from vistudio_image_analysis.sdk.api_job import CreateJobRequest as CreateAnalysisJobRequest
from vistudio_image_analysis.service.clients import Clients
from vistudio_image_analysis.scheduler.scheduler import Scheduler
from vistudio_image_analysis.runner.runner import Runner

setup_logger(config=dict(logger_name='ray.serve'))

def create_app():
    """
    创建FastAPI应用
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'],
        allow_headers=['Origin', 'X-Requested-With',
                       'Content-Type', 'Accept', 'Authorization', 'X-Timezone-Offset'],
        allow_credentials=True,
        max_age=86400
    )

    return app


cfg_path = "/home/ray/config.toml"
os.environ[ENV_SERVER_CONFIG_PATH] = cfg_path
app = create_app()
app.add_middleware(ModifyResponseMiddleware)


# 创建 Serve Deployment
@serve.deployment()
@serve.ingress(app)
class Job:
    """
    JobManager class
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = Clients(config=config)

        # 初始化全局调度器
        self.scheduler = Scheduler(config=config)

        # operator 注册  TODO SDK 待更改
        # operator_meta(endpoint=self.config.windmill.endpoint,
        #               ak=self.config.windmill.ak,
        #               sk=self.config.windmill.sk)

    def _create_local_job(self, request: CreateAnalysisJobRequest) -> CreateJobResponse:
        """
        _build_job_request
        """
        bcelogger.info("create local job  req:{}".format(request))

        callback_endpoint = self.config.image_analysis.endpoint + f"/v1/workspaces/{request.workspace_id}/analysisjobs"
        create_job_request = CreateJobRequest(
            workspace_id=request.workspace_id,
            local_name=request.local_name,
            display_name=request.display_name,
            kind="ImageAnalysis",
            spec_kind="Local",
            callback_endpoint=callback_endpoint
        )
        resp = self.client.get_job_client().create_job(request=create_job_request)
        bcelogger.info("create local job  {} resp:{}".format(create_job_request.local_name, resp))

        return resp

    def _stop_local_job(self, request: StopJobRequest):
        """
        _stop_local_job
        """
        bcelogger.info("stop job  request:{}".format(request))

        stop_job_request = StopJobRequest()
        stop_job_request.workspace_id = request.workspace_id
        stop_job_request.local_name = request.local_name
        resp = self.client.get_job_client().stop_job(request=stop_job_request)
        bcelogger.info("stop job {} resp:{}".format(stop_job_request.local_name, resp))

    @app.get(path="/v1/workspaces/{workspace_id}/analysisjobs",
             dependencies=[Depends(get_authenticate_dependency(new_config()))])
    def hello(self):
        """
        get all jobs
        """
        return "hello job"

    @app.post(path="/v1/workspaces/{workspace_id}/analysisjobs",
              dependencies=[Depends(get_authenticate_dependency(new_config()))])
    async def create_job(self, request: CreateAnalysisJobRequest):
        """
        create a job
        """
        bcelogger.info("create job  request:{}".format(request))

        runner = Runner(client=self.client.get_job_client(), graph=request.graph, config=self.config)

        if request.trigger.kind == TriggerKind.ONCE.value:
            return runner.run(request)

        self.scheduler.add_job(request=request, runner=runner)
        return self._create_local_job(request)


    @app.post(path="/v1/workspaces/{workspace_id}/analysisjobs/job/stop",
              dependencies=[Depends(get_authenticate_dependency(new_config()))])
    async def stop_job(self, request: StopJobRequest):
        """
        stop a job
        """
        # 调用scheduler 删除job
        bcelogger.info("stop job  request:{}".format(request))

        self.scheduler.remove_job(request=request)
        self._stop_local_job(request)


def main():
    """
    启动serve
    """
    config = init_config()
    # 部署服务
    job = Job.bind(config)
    serve.run(job, name="job-server")


if __name__ == "__main__":
    main()