#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   BaseOperator
"""
import json
import re
import traceback
from typing import Any, List, Dict
import pandas as pd

import bcelogger
from jobv1.client.job_api_base import JobStatus
from jobv1.client.job_api_job import parse_job_name
from jobv1.client.job_api_metric import CreateMetricRequest, MetricLocalName, MetricKind, DataType
from jobv1.client.job_api_task import CreateTaskRequest
from jobv1.client.job_client import JobClient
from jobv1.tracker.tracker import Tracker
from pygraphv1.client.graph_api_operator import Operator
from pygraphv1.registry.registry import Registry
from windmillclient.client.windmill_client import WindmillClient
from windmillcomputev1.filesystem import init_py_filesystem

from vistudio_image_analysis.config.config import Config

OPERATOR = Registry('operator')
OPERATOR_META = Registry('operator_meta')
input_value_pattern = r"\$\{([^}]*)\}"


class BaseOperator:
    """
    BaseOperator
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        self.meta = meta
        self.config = config
        bcelogger.info(f"operator [{self.meta.name}] init, meta:{meta} and config:{config}")

        self.bce_context = {"OrgID": self.config.auth.org_id,
                            "UserID": self.config.auth.user_id}
        self.windmill_client = WindmillClient(
            context=self.bce_context,
            endpoint=self.config.windmill.endpoint,
        )
        self.job_client = JobClient(
            endpoint=self.config.windmill.endpoint,
            context=self.bce_context
        )

        self.is_exception = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        execute
        """
        result = None
        try:
            # 主要逻辑
            self.prepare()
            result = self.execute(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            self.exception(e)
        finally:
            bcelogger.info(f"Operator [{self.meta.name}] finished ")
            self.finish(result, *args, **kwargs)
            return result

    def prepare(self):
        """
        init
        """
        bcelogger.info(f"running before for operator [{self.meta.name}]")
        self._job_name = parse_job_name(self.config.job_name)
        self.filesystem = self._get_filesystem(workspace_id=self._job_name.workspace_id)
        self._py_fs = init_py_filesystem(self.filesystem)
        self.inputs = self.get_inputs()
        self.outputs = self.get_outputs()

        self.tracker = Tracker(
            client=self.job_client,
            job_name=self.config.job_name,
            workspace_id=self._job_name.workspace_id
        )

        # create_task_request.order = order
        bcelogger.info(f"create task for operator [{self.meta.name}]  job_name:{self.config.job_name}")
        self.tracker.create_task(
            kind=self.meta.kind,
            local_name=self.meta.local_name.rsplit("-", 1)[0],
            display_name=self.meta.display_name,
            description=self.meta.description)

        # status=Running
        bcelogger.info(f"log metric for operator [{self.meta.name}]. value:[JobStatus.Running]")
        self.tracker.log_metric(
            value=[JobStatus.Running],
            local_name=MetricLocalName.Status,
            kind=MetricKind.Gauge,
            data_type=DataType.String,
            task_name=self.meta.local_name.rsplit("-", 1)[0]
        )

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        主要的业务处理逻辑
        """
        raise NotImplementedError("Must implement execute() in subclass")

    def exception(self, error: Exception):
        """
        异常后的处理逻辑
        """
        self.is_exception = True
        bcelogger.error(f"Running exception for operator [{self.meta.name}] due to error: {error}")

        # 上报状态 Failed
        bcelogger.error(f"log metric for operator [{self.meta.name}]. value:[JobStatus.Failed]")
        self.tracker.log_metric(
            value=[JobStatus.Failed],
            local_name=MetricLocalName.Status,
            kind=MetricKind.Gauge,
            data_type=DataType.String,
            task_name=self.meta.local_name.rsplit("-", 1)[0]
        )

    def finish(self, result: Any, *args: Any, **kwargs: Any):
        """
        finish 后处理逻辑
        """

        bcelogger.info(f"Running finish for operator [{self.meta.name}]")
        if not self.is_exception:
            # 上报状态 Succeeded
            bcelogger.info(f"log metric for operator [{self.meta.name}]. value:[JobStatus.Succeeded]")
            self.tracker.log_metric(
                value=[JobStatus.Succeeded],
                local_name=MetricLocalName.Status,
                kind=MetricKind.Gauge,
                data_type=DataType.String,
                task_name=self.meta.local_name.rsplit("-", 1)[0]
            )
            self.parse_output(result)

    def stop(self, *args: Any, **kwargs: Any) -> Any:
        """
        stop 逻辑
        """
        bcelogger.info(f"Running stop for operator [{self.meta.name}]")

    def _get_filesystem(self, workspace_id):
        """
        根据workspace_id  获取fs
        """
        guest_name = f"workspaces/{workspace_id}"
        try:
            resp = self.windmill_client.suggest_first_filesystem(workspace_id=workspace_id, guest_name=guest_name)
            bcelogger.info("suggest_first_filesystem  resp:{}".format(resp))
            return resp
        except Exception as e:
            traceback.print_exc()
            bcelogger.error("suggest_first_filesystem error.guest_name:{}".format(guest_name), e)

    def get_inputs(self) -> Dict:
        """
        get_inputs
        返回的示例：
        {
            "input0": {"image_id":"MongoDatasource-node.image_id","file_uri":"MongoDatasource-node.file_uri"},
            "input1": {"image_id":"MultiModalProcessor-node.image_id"}
        }
        这里只取一层, 此方法主要是为了能快速的根据meta 中的某一个schema  找到 dataset 中某一列
        """
        inputs = {}
        if self.meta.inputs is None:
            return inputs
        for input in self.meta.inputs:
            if input is None:
                return None
            schema_map = {}
            for var in input.schema_:
                if var.name is None:
                    continue
                value = var.value
                split_value = re.search(input_value_pattern, value).group(1).split(".")
                schema_map[var.name] = f"{split_value[0]}.{split_value[-1]}"
            inputs[input.name] = schema_map

        return inputs

    def get_outputs(self) -> Dict:
        """
        get_outputs
        返回的示例
        {
            "output0": ["image_id","file_uri"],
            "output1": ["image_id"]
        }
        }
        这里只取一层, 此方法主要目的是为了快速获取到output 的 schema, 方便dataset 的  select_columns 方法
        """
        outputs = {}
        for output in self.meta.outputs:
            if output is None:
                return None
            schema_names = [var.name for var in output.schema_ if var.name is not None]
            outputs[output.name] = schema_names

        return outputs

    def parse_output(self, result: Any):
        """
        _parse_output_schema
        将结果转换为DataFrame，并添加前缀
        这里注意，我们约定， 每一个算子的输出的时候， 都会讲dataset 的每一列的列名拼上 当前节点的名称，原因是，只有这样做，当dataset 在加列之后
        ，下一个节点才能准确的获取到上一个节点的输入，防止串联

        流程图 (DAG):

            source
                │
                │
                ▼
            ┌───┴───┐
            ▼       ▼
        processor_A processor_B
            │       │
            └───┬───┘
                ▼
              merge
                │
                ▼
               sink

        说明:
        - source: 数据源
        - processor_A/B/: 并行处理
        - merge: 合并处理结果
        - sink: 最终输出

        因为在整个过程中，数据传输是通过加列的方式去进行，多个相同的算子在并行处理时，会导致列名冲突，所以需要在列名前加上节点名称作为前缀，
        这样才能保证每个节点的输出列名都是唯一的。

        """
        node_name = self.meta.name

        def add_prefix_to_columns(batch: dict) -> pd.DataFrame:
            # Convert the dictionary batch to a DataFrame
            df = pd.DataFrame(batch)
            df.columns = [f"{node_name}.{col.split('.')[-1]}" for col in df.columns]
            return df

        prefix_ds = result[self.meta.outputs[0].name].map_batches(add_prefix_to_columns, batch_format="pandas")
        bcelogger.info(f"{self.meta.name} run finish. ds schema:{prefix_ds.schema()}")
        result[self.meta.outputs[0].name] = prefix_ds
