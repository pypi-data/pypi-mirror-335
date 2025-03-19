# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
mongo_datasource_meta.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
from typing import Optional, List

import yaml
from pydantic import Field, BaseModel
from pygraphv1.client.graph_api_operator import CategoryVisual
from pygraphv1.client.graph_api_variable import Variable

from vistudio_image_analysis.operator.base_operator import OPERATOR_META


class Output(Variable):
    """
    输出
    """
    name: str = "output0"
    display_name: str = Field("输出", alias="displayName")
    type: str = "ray.data.Dataset"
    schema_: Optional[List['Variable']] = Field([
        Variable(name="width", display_name="图片宽度", type="int", description="图片宽度"),
        Variable(name="height", display_name="图片高度", type="int", description="图片高度"),
        Variable(name="image_id", display_name="图片ID", type="str", description="图片对应的ID"),
        Variable(name="image_name", display_name="图片名称", type="str", description="图片名称"),
        Variable(name="annotation_set_id", display_name="标注集ID", type="str", description="标注集ID"),
        Variable(name="annotation_set_name", display_name="标注集Name", type="str", description="标注集Name"),
        Variable(name="user_id", display_name="user_id", type="str", description="用户ID"),
        Variable(name="created_at", display_name="创建时间", type="int64", description="创建时间"),
        Variable(name="data_type", display_name="数据类型", type="str", description="数据类型"),
        Variable(name="file_uri", display_name="文件路径", type="str", description="文件路径"),
        Variable(name="org_id", display_name="组织ID", type="str", description="组织ID"),
        Variable(name="tags", display_name="标签", type="dict", description="标签"),
        Variable(name="image_state", display_name="图片状态", type="object", description="图片状态"),
        Variable(name="updated_at", display_name="更新时间", type="int64", description="更新时间"),
        Variable(name="annotation_state", display_name="标注状态", type="str", description="标注状态"),
        Variable(name="annotations", display_name="标注信息", type="list", description="标注信息"),
    ], alias="schema")


@OPERATOR_META.register_module(name="MongoDatasource", version="1")
class MongoDatasourceMetaV1(Variable):
    """
    MongoDatasourceMetaV1
    """
    name: str = "MongoDatasourceMetaV1"
    local_name: str = "MongoDatasource"
    kind: str = "MongoDatasource"
    kind_display_name: str = Field("MongoDB数据源", alias="kindDisplayName")
    parent_kind: str = Field("Datasource", alias="parentKind")
    description: str = "MongoDB数据源读取"
    runtime: str = "ImageAnalysis"
    version: str = "1"
    category: List[str] = ["Datasource:数据源节点"]
    category_visual: Optional[CategoryVisual] = Field(None, alias="categoryVisual")
    states: Optional[List[Variable]] = None
    properties: List[Variable] = [
        Variable(
            name="q",
            display_name="查询语句",
            type="str",
            description="查询语句",
            Optional=False,
            readonly=False
        ),
    ]
    inputs: List[Variable] = None
    outputs: List[Variable] = [Output()]
