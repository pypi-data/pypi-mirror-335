# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
factory.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/5/23 8:17 下午
"""
from vistudio_image_analysis.pipeline.base import BasePipeline

import bcelogger


class PipelineFactory(object):
    """
    工厂类，用于创建pipeline实例
    """

    @classmethod
    def get_pipeline_instance(cls, pipeline_name, *args, **kwargs):
        """
        获取pipeline实例
        """
        subclasses = BasePipeline.get_all_subclasses()
        bcelogger.info("subclasses:{}".format(subclasses))
        return subclasses[pipeline_name](*args, **kwargs)


def test_get_pipeline_instance():
    """
    测试获取pipeline实例
    """
    pipeline_name = 'UpdateInferStatePipeline'
    constructor_kwargs = ("", {},)
    instance = PipelineFactory.get_pipeline_instance(pipeline_name, constructor_kwargs)
    print(instance)


if __name__ == '__main__':
    test_get_pipeline_instance()
