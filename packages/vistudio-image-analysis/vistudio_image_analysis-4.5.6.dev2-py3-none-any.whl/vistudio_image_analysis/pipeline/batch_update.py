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
from pydantic import BaseModel

import windmilltrainingv1.client.training_api_job
from windmilltrainingv1.client.training_client import TrainingClient

from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.table.annotation import AnnotationData, Annotation, Label, DATA_TYPE_ANNOTATION, \
    TASK_KIND_MANUAL
from vistudio_image_analysis.table.image import ImageData, DATA_TYPE_IMAGE
from vistudio_image_analysis.pipeline.query_pipeline import query_mongo
from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name
from vistudio_image_analysis.util import string

mongo_client = None
collection = None
vistudio_client = None
train_client = None


class UpdateConfig(BaseModel):
    """
    定义更新任务的配置
    """
    job_name: str = ""
    query_pipeline: list = []
    annotation_set_name: str = ""
    object_type: str = ""
    updates: dict = {}


def batch_update(update_conf: UpdateConfig):
    """
    批量更新
    :param update_conf:
    :return:
    """
    # 获取 annotation_set_id
    annotation_set_name = parse_annotation_set_name(update_conf.annotation_set_name)
    annotation_set = vistudio_client.get_annotation_set(
        annotation_set_name.workspace_id, annotation_set_name.project_name, annotation_set_name.local_name)
    bcelogger.info("annotation_set: {}".format(annotation_set))
    annotation_set_id = annotation_set.id
    bcelogger.info("annotation_set_id: {}".format(annotation_set_id))

    # 获取 job 对应的 user_id
    job_name = windmilltrainingv1.client.training_api_job.parse_job_name(update_conf.job_name)
    job = train_client.get_job(job_name.workspace_id, job_name.project_name, job_name.local_name)
    bcelogger.info("job: {}".format(job))
    user_id = job.userID

    # 获取需要更新的 image_id
    results = query_mongo(update_conf.query_pipeline, collection)
    update_image_ids = results.get("image_ids", [])
    bcelogger.info(f"update_image_ids: {update_image_ids}")

    # 更新
    if update_conf.object_type == "Image":
        update_tags = update_conf.updates["tags"]
        update_image_tag(annotation_set_id, update_image_ids, update_tags)
    elif update_conf.object_type == "Annotation":
        update_labels = update_conf.updates["labels"]
        update_annotation_label(annotation_set_id, update_image_ids, update_labels, user_id)


def update_image_tag(annotation_set_id, image_ids, update_tags):
    """
    更新 image 的 tag
    :param annotation_set_id:
    :param image_ids:
    :param update_tags:
    :return:
    """
    update_field = dict()
    for key, value in update_tags.items():
        update_field[f"tags.{key}"] = value
    update = {"$set": update_field}
    ImageData.objects(data_type=DATA_TYPE_IMAGE, annotation_set_id=annotation_set_id, image_id__in=image_ids). \
        update(__raw__=update)


def update_annotation_label(annotation_set_id, image_ids, update_labels, user_id=""):
    """
    更新 annotation 的 label
    :param annotation_set_id:
    :param image_ids:
    :param update_labels:
    :param user_id:
    :return:
    """
    assert len(update_labels) >= 1

    # 先删除原先标注，再插入新的标注
    AnnotationData.objects(data_type=DATA_TYPE_ANNOTATION, annotation_set_id=annotation_set_id,
                           image_id__in=image_ids, task_kind=TASK_KIND_MANUAL).delete()

    # 计算需要新插入的 annotation
    new_labels = []
    for label in update_labels:
        label_data = Label(id=label["id"], parent_id=label.get("parent_id"))
        new_labels.append(label_data)

    insert_annotations = []
    for image_id in image_ids:
        annotation = AnnotationData(
            image_id=image_id,
            annotation_set_id=annotation_set_id,
            artifact_name="",
            task_kind=TASK_KIND_MANUAL,
            data_type=DATA_TYPE_ANNOTATION,
            annotations=[Annotation(id="anno-" + string.generate_random_string(8), labels=new_labels)],
            user_id=user_id,
        )
        insert_annotations.append(annotation)

    # 插入新的 annotation
    AnnotationData.objects.insert(insert_annotations)

    # 更新图片的标注状态
    ImageData.objects(data_type=DATA_TYPE_IMAGE, annotation_set_id=annotation_set_id, image_id__in=image_ids). \
        update(__raw__={"$set": {"annotation_state": "Annotated"}})


if __name__ == '__main__':
    bcelogger.info("start batch update")
    arg_parser = ArgParser(kind='BatchUpdate')
    args = arg_parser.parse_args()
    config = Config(args)

    q = args.get("q")
    q = base64.b64decode(q)
    bcelogger.info(f"query: {q}")
    q = json.loads(q)

    updates = args.get("updates")
    updates = base64.b64decode(updates)
    bcelogger.info(f"updates: {updates}")
    updates = json.loads(updates)

    update_config = UpdateConfig(
        job_name=args.get("job_name"),
        annotation_set_name=args.get("annotation_set_name"),
        query_pipeline=q,
        object_type=args.get("object_type"),
        updates=updates,
    )

    # init mongo client
    mongo_client = pymongo.MongoClient(config.mongo_uri)
    db = mongo_client[config.mongodb_database]
    collection = db[config.mongodb_collection]
    connect(host=config.mongo_uri, db=config.mongodb_database)

    # init vistudio client
    vistudio_client = AnnotationClient(
        context=config.bce_client_context,
        endpoint=config.vistudio_endpoint)

    # init train client
    train_client = TrainingClient(
        context=config.bce_client_context,
        endpoint=config.windmill_endpoint)

    # batch update
    batch_update(update_config)
