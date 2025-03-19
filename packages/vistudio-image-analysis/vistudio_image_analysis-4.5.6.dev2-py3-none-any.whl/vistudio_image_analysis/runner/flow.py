#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/12/16
# @Author  : yanxiaodong
# @File    : flow.py
"""
from typing import Any, List, Dict, Tuple
import re
from collections import defaultdict
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import bcelogger

from vistudio_image_analysis.operator.base_operator import BaseOperator


class Flow(object):
    """
    Flow
    """
    def __init__(self, kind: str, flow: Any):
        self.kind = kind
        self.flow = flow

        self.input_schema_pattern = r"\$\{([^}]*)\}"

    def validate(self, *args, **kwargs):
        """
        validate the flow
        """
        pass

    def compile(self):
        """
        compile a flow
        """
        visited: Dict[str, Tuple] = defaultdict(tuple)

        # datasource operator 处理
        for path in self.flow:
            bcelogger.info(f"Datasource operator {path[0].meta.local_name}")
            self.transform_datasource(operator=path[0], visited=visited)
            bcelogger.info(f"Datasource operator {path[0].meta.local_name} start to run")

        # processor operator 处理
        # 如果一个 flow 有多个并行路径，先把其他路径位置记录下来
        operator_positions: Dict[str, List] = defaultdict(list)
        for path in self.flow[1:]:
            for idx, operator in enumerate(path):
                operator_positions[operator.meta.local_name].append((path, idx))
        bcelogger.info(f"Other path processor operator {operator_positions}")

        for operator in self.flow[0][1:-1]:
            bcelogger.info(f"Processor operator {operator.meta.local_name}")
            if operator.meta.local_name not in operator_positions:
                self.transform_processor(operator=operator, visited=visited)
                bcelogger.info(f"Processor operator {operator.meta.local_name} start to run")
                continue

            for path, idx in operator_positions[operator.meta.local_name]:
                for other_operator in path[1:idx]:
                    bcelogger.info(f"Other processor operator {other_operator.meta.local_name}")
                    self.transform_processor(operator=other_operator, visited=visited)
                    bcelogger.info(f"Other processor operator {other_operator.meta.local_name} start to run")
            self.transform_processor(operator=operator, visited=visited)
            bcelogger.info(f"Processor operator {operator.meta.local_name} start to run")

        # datasink operator 处理
        for path in self.flow:
            bcelogger.info(f"Datasink operator {path[-1].meta.local_name}")
            self.transform_datasink(operator=path[-1], visited=visited)
            bcelogger.info(f"Datasink operator {path[-1].meta.local_name} start to run")

    def transform_datasource(self, operator: BaseOperator, visited: Dict):
        """
        transform source operator
        """
        assert operator.meta.inputs is None or len(operator.meta.inputs) == 0, \
            f"Source operator {operator.meta.local_name} must have no inputs"
        assert len(operator.meta.outputs) > 0, \
            f"Processor operator {operator.meta.local_name} outputs must be greater than zero"

        if operator.meta.local_name in visited:
            bcelogger.info(f"Datasource operator {operator.meta.local_name} has been visited {visited}")
            return

        output_dataset = operator()
        visited[operator.meta.local_name] = (operator.meta.local_name, None, output_dataset)

    def transform_processor(self, operator: BaseOperator, visited: Dict):
        """
        transform processor operator
        """
        assert len(operator.meta.inputs) > 0, \
            f"Processor operator {operator.meta.local_name} inputs must be greater than zero"
        assert len(operator.meta.outputs) > 0, \
            f"Processor operator {operator.meta.local_name} outputs must be greater than zero"

        if operator.meta.local_name in visited:
            bcelogger.info(f"Processor operator {operator.meta.local_name} has been visited {visited}")
            return

        input_dataset = []
        for input_ in operator.meta.inputs:
            bcelogger.info(f"Processor operator {operator.meta.local_name} input is {input_.name}")
            for schema_ in input_.schema_:
                bcelogger.info(f"Processor operator {operator.meta.local_name} input {input_.name} schema is {schema_}")
                split_value = re.search(self.input_schema_pattern, schema_.value).group(1).split(".")
                assert len(split_value) == 4, \
                    f"schema {schema_.value} split must be length 4, but get is len(split_value)"
                input_dataset.append(visited[split_value[0]][2][split_value[2]])

        output_dataset = operator(input_dataset)
        visited[operator.meta.local_name] = (operator.meta.local_name, input_dataset, output_dataset)

    def transform_datasink(self, operator: BaseOperator, visited: Dict):
        """"
        transform sink operator
        """
        assert len(operator.meta.inputs) > 0, \
            f"Processor operator {operator.meta.local_name} inputs must be greater than zero"
        assert len(operator.meta.outputs) == 0, f"Sink operator {operator.meta.local_name} must have no outputs"

        if operator.meta.local_name in visited:
            bcelogger.info(f"Datasink operator {operator.meta.local_name} has been visited {visited}")
            return

        input_dataset = []
        for input_ in operator.meta.inputs:
            bcelogger.info(f"Datasink operator {operator.meta.local_name} input is {input_.name}")
            for schema_ in input_.schema_:
                bcelogger.info(f"Datasink operator {operator.meta.local_name} input {input_.name} schema is {schema_}")
                split_value = re.search(self.input_schema_pattern, schema_.value).group(1).split(".")
                assert len(split_value) == 4, \
                    f"schema {schema_.value} split must be length 4, but get is len(split_value)"
                input_dataset.append(visited[split_value[0]][2][split_value[2]])

        operator(input_dataset[0])
        visited[operator.meta.local_name] = (operator.meta.local_name, input_dataset, None)


def flows_run_async(flows: List[Flow]):
    """
    run flows asynchronously
    """
    futures = {}
    with ThreadPoolExecutor() as executor:
        for idx, flow in enumerate(flows):
            bcelogger.info(f"The flow will be submit: {flow.flow}")
            futures[executor.submit(flow.compile)] = idx

    success_flow = []
    fail_flow = []
    for future in as_completed(futures):
        task_id = futures[future]
        try:
            future.result()
            bcelogger.info(f"Flow {flows[task_id].flow} is successful")
            success_flow.append(flows[task_id].flow)
        except Exception as e:
            traceback.print_exc()
            bcelogger.error(f"Flow {flows[task_id].flow} failed, reason is {e}")
            fail_flow.append(flows[task_id].flow)

    bcelogger.info(f"All flows are compiled, contain {len(success_flow)} success and {len(fail_flow)} failure")
    if len(fail_flow) > 0:
        raise RuntimeError(f"{fail_flow} flows failed")