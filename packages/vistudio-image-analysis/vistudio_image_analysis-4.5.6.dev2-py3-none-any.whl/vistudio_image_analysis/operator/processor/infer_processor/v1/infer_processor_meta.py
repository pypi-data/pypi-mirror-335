# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
infer_processor_meta.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
from typing import Optional, List

import yaml
from pydantic import Field, BaseModel
from pygraphv1.client.graph_api_operator import CategoryVisual
from pygraphv1.client.graph_api_variable import Variable


class Input(Variable):
    """
    输入
    """
    name: str = "input0"
    display_name: str = Field("输入", alias="displayName")
    type: str = "ray.data.Dataset"
    schema_: Optional[List['Variable']] = Field([
        Variable(name="file_uri", display_name="图片路径", type="str", description="图片路径")
    ], alias="schema")


class Output(Variable):
    """
    输出
    """
    name: str = "output0"
    display_name: str = Field("输出", alias="displayName")
    type: str = "ray.data.Dataset"
    schema_: Optional[List['Variable']] = Field([
        Variable(name="predictions", display_name="预测结果", type="list", description="预测结果")
    ], alias="schema")


class InferProcessorMetaV1(Variable):
    """
    InferProcessorMetaV1
    """
    name: str = None
    local_name: str = "InferProcessor"
    kind: str = "InferProcessor"
    kind_display_name: str = Field("推理", alias="kindDisplayName")
    parent_kind: str = Field("Processor", alias="parentKind")
    description: str = "预标注推理"
    runtime: str = "ImageAnalysis"
    version: str = "1"
    category: List[str] = ["Processor:推理节点"]
    category_visual: Optional[CategoryVisual] = Field(None, alias="categoryVisual")
    states: Optional[List[Variable]] = None
    properties: List[Variable] = [
        Variable(
            name="artifact_name",
            display_name="artifactName",
            type="str",
            description="模型artifact name",
            readonly=False,
            optional=False

        ),
        Variable(
            name="temperature",
            display_name="temperature",
            type="float",
            description="Temperature（采样温度）",
            default_value="0.0",
            readonly=False,
            optional=True
        ),
        Variable(
            name="top_p",
            display_name="top_p",
            type="float",
            description="Top_P（核采样）",
            default_value="0.0",
            readonly=False,
            optional=True
        ),
        Variable(
            name="repetition_penalty",
            display_name="repetition_penalty",
            type="float",
            description="Repetition_Penalty（重复惩罚）",
            default_value="0.0",
            readonly=False,
            optional=True
        ),
        Variable(
            name="annotation_set_name",
            display_name="annotationSetName",
            type="str",
            description="标注集",
            readonly=False,
            optional=False
        ),
        Variable(
            name="prompt",
            display_name="prompt",
            type="str",
            description="提示词",
            Optional=True,
            readonly=False
        )
    ]
    inputs: List[Variable] = [Input()]
    outputs: List[Variable] = [Output()]
