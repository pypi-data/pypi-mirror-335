# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
crop_image_processor_meta.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
from typing import Optional, List

import yaml
from pydantic import Field, BaseModel
from pygraphv1.client.graph_api_operator import CategoryVisual
from pygraphv1.client.graph_api_variable import Variable, Constraint, FloatRangeConstraint


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
            display_name="图片Uri",
            type="str",
            description="图片Uri"
        ),
        Variable(
            name="image",
            display_name="图片",
            type="image",
            description="图片"
        ),
        Variable(
            name="bboxes",
            display_name="目标框",
            type="list",
            description="目标框",
            Optional=False
        ),
    ], alias="schema")


class Output(Variable):
    """
    输出
    """
    name: str = "output0"
    display_name: str = Field("输出", alias="displayName")
    type: str = "ray.data.Dataset"
    schema_: Optional[List['Variable']] = Field([
        Variable(
            name="image",
            display_name="图片",
            type="image",
            description="图片"
        ),
        Variable(
            name="image_name",
            display_name="图片名称",
            type="str",
            description="图片名称"),
        Variable(
            name="bboxes",
            display_name="目标框",
            type="list",
            description="目标框",
            Optional=False
        ),
    ], alias="schema")


class CropImageProcessorMetaV1(Variable):
    """
    CropImageProcessorMetaV1
    """
    name: str = None
    local_name: str = "CropImageProcessorMetaV1"
    kind: str = "CropImageProcessorMetaV1"
    kind_display_name: str = Field("目标抠图", alias="kindDisplayName")
    parent_kind: str = Field("Processor", alias="parentKind")
    description: str = "目标抠图"
    runtime: str = "ImageAnalysis"
    version: str = "1"
    category: List[str] = ["Processor:目标抠图节点"]
    category_visual: Optional[CategoryVisual] = Field(None, alias="categoryVisual")
    states: Optional[List[Variable]] = None
    properties: List[Variable] = [
        Variable(
            name="width_factor",
            display_name="宽度倍数",
            type="double",
            description="宽度倍数",
            default_value="1.4",
            Optional=False,
            readonly=False,
            constraint=Constraint(
                float_range=FloatRangeConstraint(
                    min=0.1,
                    max=10.0
                )
            )
        ),
        Variable(
            name="height_factor",
            display_name="高度倍数",
            type="double",
            description="高度倍数",
            Optional=False,
            readonly=False,
            constraint=Constraint(
                float_range=FloatRangeConstraint(
                    min=0.1,
                    max=10.0
                )
            )
        )

    ]
    inputs: List[Variable] = [Input()]
    outputs: List[Variable] = [Output()]
