# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
example.py  因 Ray Serve App 无法直接debug   故而开发此类主要用于使用uvicorn  启动服务，用于服务调试。
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""
import asyncio
import os
import uvicorn

from fastapi import FastAPI, HTTPException, Depends, Request
from starlette.middleware.cors import CORSMiddleware

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

setup_logger(config=dict(logger_name='uvicorn.fastapi'))


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


class Job:
    """
    JobManager class
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = Clients(config=config)
        self.scheduler = None

    async def init_scheduler(self):
        """
        init_scheduler
        """
        self.scheduler = Scheduler(config=self.config)
        await asyncio.sleep(0)

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


job_manager = Job(config=init_config())

@app.on_event("startup")
async def startup_event():
    """
    startup_event
    """
    await job_manager.init_scheduler()


@app.get("/v1/workspaces/{workspace_id}/analysisjobs",
         dependencies=[Depends(get_authenticate_dependency(new_config()))])
def hello():
    """
    get all jobs
    """
    return "hello job"


@app.post("/v1/workspaces/{workspace_id}/analysisjobs",
          dependencies=[Depends(get_authenticate_dependency(new_config()))])
async def create_job(request: CreateAnalysisJobRequest):
    """
    create a job
    """
    bcelogger.info("create job  request:{}".format(request))

    runner = Runner(client=job_manager.client.get_job_client(), graph=request.graph, config=job_manager.config)

    if request.trigger.kind == TriggerKind.ONCE.value:
        return runner.run(request)

    job_manager.scheduler.add_job(request=request, runner=runner)
    return job_manager._create_local_job(request)


@app.post("/v1/workspaces/{workspace_id}/analysisjobs/job/stop",
          dependencies=[Depends(get_authenticate_dependency(new_config()))])
async def stop_job(request: StopJobRequest):
    """
    stop a job
    """
    bcelogger.info("stop job  request:{}".format(request))
    job_manager.scheduler.remove_job(request=request)
    job_manager._stop_local_job(request)
    return {"message": "Job stopped successfully"}


def main():
    """
    启动 FastAPI 应用
    """
    uvicorn.run(app, host="0.0.0.0", port=8899)


if __name__ == "__main__":
    main()
