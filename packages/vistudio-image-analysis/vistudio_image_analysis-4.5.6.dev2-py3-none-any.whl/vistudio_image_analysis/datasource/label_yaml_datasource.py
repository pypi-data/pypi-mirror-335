# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
label_yaml_datasource.py
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""

from typing import TYPE_CHECKING, Iterator, List

from pydantic import BaseModel
from ray.data._internal.delegating_block_builder import DelegatingBlockBuilder
from ray.data.block import Block
from ray.data.datasource.file_based_datasource import FileBasedDatasource
from ray.util.annotations import PublicAPI
import yaml

if TYPE_CHECKING:
    import pyarrow


class LabelTask(BaseModel):
    """
    LabelTask
    """
    task_type: str
    task_name: str
    anno_key: int
    categories: dict


@PublicAPI
class LabelYamlDatasource(FileBasedDatasource):
    """Text datasource, for reading and writing text files."""

    def __init__(
            self,
            paths: List[str],
            *,
            encoding: str = "utf-8",
            **file_based_datasource_kwargs
    ):
        super().__init__(paths, **file_based_datasource_kwargs)

        self.encoding = encoding

    def _parse_yaml(self, data):
        tasks = data['tasks']

        # 将 YAML 数据转换为 pyarrow Table
        res = []
        for task in tasks:
            task_type = task['task_type']
            if task_type != 'image_classification':
                continue
            task_name = task['task_name']
            anno_key = task['anno_key']
            categories = task['categories']
            labelTask = LabelTask(
                task_type=task_type,
                task_name=task_name,
                anno_key=anno_key,
                categories=categories

            )
            res.append(labelTask.dict())

        return res

    def _read_stream(self, f: "pyarrow.NativeFile", path: str) -> Iterator[Block]:
        data = f.readall()
        # 将字节数据解码为字符串
        yaml_content = data.decode('utf-8')

        # 解析 YAML 内容
        parsed_data = yaml.safe_load(yaml_content)
        tasks = self._parse_yaml(data=parsed_data)
        builder = DelegatingBlockBuilder()

        item = {'task': tasks}
        builder.add(item)
        block = builder.build()

        yield block
