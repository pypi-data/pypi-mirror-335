# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
batch_delete.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/18 3:55 下午
"""

import base64
import json
import bcelogger
import pymongo
from mongoengine import connect

from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.table.image import ImageData
from vistudio_image_analysis.pipeline.query_pipeline import query_mongo
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name


def batch_delete(base_conf: Config, annotation_set_name, query_pipeline):
    """
    批量删除
    :param base_conf:
    :param annotation_set_name:
    :param query_pipeline
    :return:
    """
    # 连接Mongo
    client = pymongo.MongoClient(base_conf.mongo_uri)
    db = client[base_conf.mongodb_database]
    collection = db[base_conf.mongodb_collection]

    # 获取 annotation_set_id
    annotation_client = AnnotationClient(
        context=base_conf.bce_client_context,
        endpoint=base_conf.vistudio_endpoint
    )

    as_name = parse_annotation_set_name(annotation_set_name)
    annotation_set = annotation_client.get_annotation_set(as_name.workspace_id, as_name.project_name,
                                                          as_name.local_name)
    bcelogger.info("annotation_set: {}".format(annotation_set))
    annotation_set_id = annotation_set.id
    bcelogger.info("annotation_set_id: {}".format(annotation_set_id))

    # 获取需要更新的 image_id
    results = query_mongo(query_pipeline, collection)
    delete_image_ids = results.get("image_ids", [])
    bcelogger.info("delete_image_ids: {}".format(delete_image_ids))

    # 通过 mongo 删除
    ImageData.objects(
        annotation_set_id=annotation_set_id,
        image_id__in=delete_image_ids
    ).delete()


if __name__ == '__main__':
    bcelogger.info("start batch delete")
    arg_parser = ArgParser(kind='BatchDelete')
    args = arg_parser.parse_args()
    config = Config(args)
    bcelogger.info(f"args: {args}")
    q = args.get("q")
    q = base64.b64decode(q)
    bcelogger.info(f"query: {q}")
    q = json.loads(q)

    connect(host=config.mongo_uri, db=args.get("mongo_database"))

    batch_delete(config, args.get("annotation_set_name"), q)
