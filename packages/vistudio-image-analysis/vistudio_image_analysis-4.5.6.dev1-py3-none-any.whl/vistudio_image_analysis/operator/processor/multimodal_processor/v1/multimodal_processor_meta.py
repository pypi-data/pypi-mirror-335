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

from vistudio_image_analysis.operator.base_operator import OPERATOR_META


class Input(Variable):
    """
    输入
    """
    name: str = "input0"
    display_name: str = Field("输入", alias="displayName")
    type: str = "ray.data.Dataset"
    schema_: Optional[List['Variable']] = Field([
        Variable(
            name="image_uri",
            display_name="图片地址",
            type="str",
            description="图片地址"
        ),
        Variable(
            name="image_id",
            display_name="图片ID",
            type="str",
            description="图片ID",
        ),
        Variable(
            name="image",
            display_name="图片",
            type="image",
            description="图片",
            readonly=True,
            optional=True
        ),
    ], alias="schema")


class Output(Variable):
    """
    输出
    """
    name: str = "output0"
    display_name: str = Field("输出", alias="displayName")
    type: str = "ray.data.Dataset"
    schema_: Optional[List['Variable']] = Field([], alias="schema")


#@OPERATOR_META.register_module(name="MultiModalProcessor", version="1")
class MultiModalProcessorMetaV1(Variable):
    """
    SkillEventProcessorMetaV1
    """
    name: str = None
    local_name: str = "MultiModalProcessor"
    kind: str = "MultiModalProcessor"
    kind_display_name: str = Field("多模态大模型", alias="kindDisplayName")
    parent_kind: str = Field("Processor", alias="parentKind")
    description: str = "多模态大模型"
    runtime: str = "ImageAnalysis"
    version: str = "1"
    category: List[str] = ["Processor:多模态大模型节点"]
    category_visual: Optional[CategoryVisual] = Field(None, alias="categoryVisual")
    states: Optional[List[Variable]] = None
    properties: List[Variable] = [
        Variable(
            name="prompt",
            display_name="提示词",
            type="str",
            description="提示词",
            Optional=False,
            readonly=False
        ),
        Variable(
            name="artifact_name",
            display_name="模型artifact name",
            type="str",
            description="模型artifact name",
            readonly=True,
            optional=False

        ),
        Variable(
            name="temperature",
            display_name="temperature",
            type="float",
            description="Temperature（采样温度）",
            default_value="0.0",
            readonly=True,
            optional=True
        ),
        Variable(
            name="top_p",
            display_name="top_p",
            type="float",
            description="Top_P（核采样）",
            default_value="0.0",
            readonly=True,
            optional=True
        ),
        Variable(
            name="repetition_penalty",
            display_name="repetition_penalty",
            type="float",
            description="Repetition_Penalty（重复惩罚）",
            default_value="0.0",
            readonly=True,
            optional=True
        ),
        Variable(
            name="port",
            display_name="大模型服务端口",
            type="int",
            description="大模型服务端口",
            Optional=False,
            readonly=True,
            default_value="8312"
        )

    ]
    inputs: List[Variable] = [Input()]
    outputs: List[Variable] = [Output()]
