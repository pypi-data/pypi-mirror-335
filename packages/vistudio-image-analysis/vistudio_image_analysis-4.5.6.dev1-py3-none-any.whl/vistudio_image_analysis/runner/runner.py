#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/12/16
# @Author  : yanxiaodong
# @File    : runner.py
"""
import json
from typing import Dict, List
import base64
from collections import defaultdict
import networkx as nx

import bcelogger
from bceserver.context import get_context
from pygraphv1.client.graph_api_graph import GraphContent
from jobv1.client.job_api_job import CreateJobRequest, SpecKind, JobName, CreateJobResponse
from jobv1.client.job_client import JobClient
from bceidaas.middleware.auth.const import ORG_ID, USER_ID

from vistudio_image_analysis.runner.flow import Flow
from vistudio_image_analysis.runner.types import FlowKind
from vistudio_image_analysis.operator.base_operator import OPERATOR, BaseOperator
from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.scheduler.types import TriggerKind
from vistudio_image_analysis.sdk.api_job import CreateJobRequest as CreateAnalysisJobRequest


class Runner(object):
    """
    Runner
    """

    def __init__(self,
                 client: JobClient = None,
                 graph: GraphContent = None,
                 config: Config = None):
        self.client = client
        self.graph = graph

        self.config = Config(config.dict(exclude_none=True))
        if self.config.auth.org_id == "":
            self.config.auth.org_id = get_context()["auth_info"][ORG_ID]
        if self.config.auth.user_id == "":
            self.config.auth.user_id = get_context()["auth_info"][USER_ID]
        bcelogger.info(f"Graph name {graph.name} config is {self.config.dict(exclude_none=True, by_alias=True)}")

        self.operators: Dict[str, BaseOperator] = {}
        for node in self.graph.nodes:
            self.operators[node.local_name] = \
                OPERATOR.get(name=node.kind, version=node.version)(config=self.config, meta=node)

        self.flows = self.parse()

    @property
    def get_flows(self):
        """
        Get flows.
        """
        return self.flows

    def parse(self) -> List[Flow]:
        """
        Parse graph to flow.
        """
        # 1.构建图的邻接表描述DAG
        adjacency_table = self._build_adjacency_table()
        bcelogger.info(f"Graph {self.graph.name} adjacency table is {adjacency_table}")

        # 2.获取所有路径
        paths = self._get_all_paths(adjacency_table=adjacency_table)
        bcelogger.info(f"Graph {self.graph.name} all paths are {paths}")

        # 3.合并叶子结点相同的路径
        leaf_to_paths: Dict[str, List] = defaultdict(list)
        for path in paths:
            leaf_to_paths[path[-1]].append(path)
        bcelogger.info(f"Group paths by leaf is: {leaf_to_paths}")

        # 4.构建Flow
        flows = []
        for _, paths in leaf_to_paths.items():
            flow = self._build_flow(paths=paths)
            flow.validate()
            flows.append(flow)

        return flows

    def _build_adjacency_table(self):
        """
        Build adjacency table.
        """
        adjacency_table = defaultdict(list)
        for edge in self.graph.edges:
            from_node = edge.from_.operator
            to_node = edge.to.operator
            adjacency_table[from_node].append(to_node)

        return adjacency_table

    def _get_all_paths(self, adjacency_table: Dict[str, List]):
        """
        Get all paths.
        """
        graph = nx.DiGraph(incoming_graph_data=adjacency_table)
        root_nodes = [node for node in graph.nodes if graph.in_degree(node) == 0]
        leaf_nodes = [node for node in graph.nodes if graph.out_degree(node) == 0]

        all_paths = []
        for root in root_nodes:
            for leaf in leaf_nodes:
                paths = list(nx.all_simple_paths(graph, source=root, target=leaf))
                all_paths.extend(paths)

        return all_paths

    def _build_flow(self, paths: List):
        """
        Build flow.
        """
        flow = []
        for path in paths:
            assert len(path) >= 3, f"Path must have at least 3 nodes, but got {len(path)}"

            for idx in range(len(path)):
                node = path[idx]
                assert node in self.operators, f"{node} not in operators {self.operators.keys()}"
                path[idx] = self.operators[node]
            flow.append(path)
        bcelogger.info(f"Build flow {flow}")

        flow = Flow(kind=FlowKind.RAY.value, flow=flow)

        return flow

    def run(self, request: CreateAnalysisJobRequest) -> CreateJobResponse:
        """
        APScheduler run the function at the given time.
        """
        if request.trigger.kind == TriggerKind.ONCE.value:
            local_name = request.local_name
        else:
            local_name = ""

        self.config.job_name = JobName(workspace_id=request.workspace_id, local_name=local_name).get_name()

        graph_bytes = json.dumps(self.graph.dict(exclude_none=True, by_alias=True)).encode('utf-8')
        graph_base64 = base64.b64encode(graph_bytes).decode('utf-8')
        config_bytes = json.dumps(self.config.dict(exclude_none=True, by_alias=True)).encode('utf-8')
        config_base64 = base64.b64encode(config_bytes).decode('utf-8')
        parameters = \
            {"args":
                {
                    "graph": graph_base64,
                    "config": config_base64
                }
            }

        spec_raw = \
            {"kind": "RayJob",
             "apiVersion": "ray.io/v1alpha1",
             "name": "",
             "spec":
                 {
                     "entrypoint": "python -m vistudio_image_analysis.runner.entrypoint",
                     "metadata":
                         {
                             "version": "v1"
                         }
                 }
             }

        request = CreateJobRequest(workspace_id=request.workspace_id,
                                   local_name=local_name,
                                   kind="ImageAnalysis",
                                   spec_kind=SpecKind.Ray,
                                   spec_raw=json.dumps(spec_raw),
                                   parameters=parameters)

        bcelogger.info(f"Scheduler create job request is: {request.dict(exclude_none=True, by_alias=True)}")
        job = self.client.create_job(request=request)
        bcelogger.info(f"Scheduler create job {job.name} successfully {job.dict(exclude_none=True, by_alias=True)}")

        return job