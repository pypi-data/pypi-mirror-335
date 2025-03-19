# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@file: batch_accept_infer.py
@author: dongling01
@date: 2024/07/26
"""

import base64
import json
import bcelogger
import pymongo
import time
from mongoengine import connect
from pydantic import BaseModel

import windmilltrainingv1.client.training_api_job
from windmilltrainingv1.client.training_client import TrainingClient
from windmillcategoryv1.client.category_api import match

from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.table.annotation import AnnotationData, DATA_TYPE_ANNOTATION, TASK_KIND_MODEL, \
    TASK_KIND_MANUAL
from vistudio_image_analysis.table.image import ImageData, DATA_TYPE_IMAGE, ANNOTATION_STATE_ANNOTATED
from vistudio_image_analysis.pipeline.query_pipeline import query_mongo
from vistudio_image_analysis.client.annotation_client import AnnotationClient
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name

mongo_client = None
collection = None
vistudio_client = None
train_client = None


class BatchAcceptInferConfig(BaseModel):
    """
    定义更新任务的配置
    """
    job_name: str = ""
    infer_job_name: str = ""
    query_pipeline: list = []
    annotation_set_name: str = ""
    policy: str = ""
    artifact_names: list = []
    user_id: str = ""


def batch_accept_infer(config):
    """
    批量接受模型推理结果
    :param:
    :return:
    """
    # 获取 annotation_set_id
    as_name = parse_annotation_set_name(config.annotation_set_name)
    annotation_set = vistudio_client.get_annotation_set(as_name.workspace_id, as_name.project_name, as_name.local_name)
    annotation_set_category = annotation_set.category['category']
    annotation_set_id = annotation_set.id

    # 获取 job 对应的 user_id
    job_name = windmilltrainingv1.client.training_api_job.parse_job_name(config.job_name)
    job = train_client.get_job(job_name.workspace_id, job_name.project_name, job_name.local_name)

    # 获取需要更新的 image_id
    results = query_mongo(config.query_pipeline, collection)
    update_image_ids = results.get("image_ids", [])
    bcelogger.info(f"update_image_ids: {update_image_ids}")

    # 更新
    if config.policy == "Cover":
        accepted_image_count, unaccepted_image_count = cover_annotation(
            annotation_set_id, update_image_ids, annotation_set_category, config)
    elif config.policy == "Add":
        accepted_image_count, unaccepted_image_count = add_annotation(
            annotation_set_id, update_image_ids, annotation_set_category, config)

    # 更新job的tag
    tags = job.tags if job.tags is not None else {}
    tags["accepted_image_count"] = str(accepted_image_count)
    tags["unaccepted_image_count"] = str(unaccepted_image_count)
    resp = train_client.update_job(job_name.workspace_id, job_name.project_name, job_name.local_name, tags=tags)
    bcelogger.info("update job resp is {}".format(resp))


def cover_annotation(annotation_set_id, image_ids, annotation_set_category, config):
    """
    覆盖已有标注
    :return:
    """
    accepted_image_count = 0
    unaccepted_image_count = 0
    for image_id in image_ids:
        try:
            # 查找模型推理结果
            if config.infer_job_name is not None and config.infer_job_name != "":
                model_annos = AnnotationData.objects(
                    annotation_set_id=annotation_set_id, image_id=image_id,
                    data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MODEL, job_name=config.infer_job_name)
            elif len(config.artifact_names) > 0:
                model_annos = AnnotationData.objects(
                    annotation_set_id=annotation_set_id, image_id=image_id,
                    data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MODEL, artifact_name__in=config.artifact_names)
            else:
                model_annos = AnnotationData.objects(
                    annotation_set_id=annotation_set_id, image_id=image_id,
                    data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MODEL)

            if len(model_annos) == 0:
                continue

            # 删除原先的人工标注
            AnnotationData.objects(
                annotation_set_id=annotation_set_id, image_id=image_id,
                data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MANUAL).delete()

            # 插入模型推理结果
            insert_annotations = []
            for model_anno in model_annos:
                if model_anno.annotations is None:
                    continue
                for anno in model_anno.annotations:
                    for label in anno.labels:
                        if 'confidence' in label:
                            del label.confidence
                insert_annotations.extend(model_anno.annotations)

            image = ImageData.objects(data_type=DATA_TYPE_IMAGE, annotation_set_id=annotation_set_id,
                                      image_id=image_id).first()

            if len(insert_annotations) > 10 and match(annotation_set_category, "Multimodal"):
                    insert_annotations = insert_annotations[:10]

            AnnotationData(
                image_id=image_id,
                annotation_set_id=annotation_set_id,
                artifact_name="",
                task_kind=TASK_KIND_MANUAL,
                data_type=DATA_TYPE_ANNOTATION,
                annotations=insert_annotations,
                user_id=config.user_id,
                image_created_at=image.created_at,
                job_name=""
            ).save()

            # 如果存在模型标注记录，但它的annotations字段为空，则接受推理结果时，将其认为是良品，需要更新标注状态
            image.update(set__annotation_state=ANNOTATION_STATE_ANNOTATED, set__updated_at=time.time_ns())

            accepted_image_count += 1
        except Exception as e:
            bcelogger.error(f"image: {image_id}, accept infer error: {e}")
            unaccepted_image_count += 1
    return accepted_image_count, unaccepted_image_count


def add_annotation(annotation_set_id, image_ids, annotation_set_category, config):
    """
    新增标注
    :return:
    """
    accepted_image_count = 0
    unaccepted_image_count = 0
    for image_id in image_ids:
        try:
            covered_or_inserted = True

            # 查找模型推理结果
            if config.infer_job_name is not None and config.infer_job_name != "":
                model_annos = AnnotationData.objects(
                    annotation_set_id=annotation_set_id, image_id=image_id,
                    data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MODEL, job_name=config.infer_job_name)
            elif len(config.artifact_names) > 0:
                model_annos = AnnotationData.objects(
                    annotation_set_id=annotation_set_id, image_id=image_id,
                    data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MODEL, artifact_name__in=config.artifact_names)
            else:
                model_annos = AnnotationData.objects(
                    annotation_set_id=annotation_set_id, image_id=image_id,
                    data_type=DATA_TYPE_ANNOTATION, task_kind=TASK_KIND_MODEL)

            if len(model_annos) == 0:
                continue

            insert_annotations = []
            for a in model_annos:
                if a.annotations is None:
                    continue
                for anno in a.annotations:
                    for label in anno.labels:
                        if 'confidence' in label:
                            del label.confidence
                insert_annotations.extend(a.annotations)

            image = ImageData.objects(data_type=DATA_TYPE_IMAGE, annotation_set_id=annotation_set_id,
                                      image_id=image_id).first()

            # 查找是否有Manual记录
            manual_anno = AnnotationData.objects(data_type=DATA_TYPE_ANNOTATION, annotation_set_id=annotation_set_id,
                                                 task_kind=TASK_KIND_MANUAL, image_id=image_id).first()

            if manual_anno is None:
                # 如果没有，则插入
                if len(insert_annotations) > 10 and match(annotation_set_category, "Multimodal"):
                        insert_annotations = insert_annotations[:10]

                AnnotationData(
                    image_id=image_id,
                    annotation_set_id=annotation_set_id,
                    artifact_name="",
                    task_kind=TASK_KIND_MANUAL,
                    data_type=DATA_TYPE_ANNOTATION,
                    annotations=insert_annotations,
                    user_id=config.user_id,
                    image_created_at=image.created_at,
                    job_name=""
                ).save()
            else:
                # 如果有，则合并
                annos = manual_anno.annotations

                if match(annotation_set_category, "Multimodal"):
                    # 大模型：1只取前10个； 2判断提示词和人工标注提示词是否相同，相同需要覆盖
                    is_covered = False
                    for insert_anno in insert_annotations[:]:
                        if insert_anno.question is None:
                            continue
                        for anno in annos:
                            if anno.question is not None and insert_anno.question == anno.question:
                                anno.answer = insert_anno.answer
                                insert_annotations.remove(insert_anno)
                                is_covered = True

                    covered_or_inserted = (is_covered or len(annos) < 10)
                    if covered_or_inserted:
                        annos.extend(insert_annotations)
                        if len(annos) > 10:
                            annos = annos[:10]
                        manual_anno.update(set__annotations=annos, set__updated_at=time.time_ns())

                else:
                    annos.extend(insert_annotations)
                    manual_anno.update(set__annotations=annos, set__updated_at=time.time_ns())

            image.update(set__annotation_state=ANNOTATION_STATE_ANNOTATED, set__updated_at=time.time_ns())

            if covered_or_inserted:
                accepted_image_count += 1
            else:
                unaccepted_image_count += 1
        except Exception as e:
            bcelogger.error(f"image: {image_id}, accept infer error: {e}")
            unaccepted_image_count += 1
    return accepted_image_count, unaccepted_image_count


if __name__ == '__main__':
    bcelogger.info("start batch accept infer result")
    arg_parser = ArgParser(kind='BatchAcceptInfer')
    args = arg_parser.parse_args()
    config = Config(args)

    q = args.get("q")
    q = base64.b64decode(q)
    bcelogger.info(f"query: {q}")
    q = json.loads(q)

    accept_infer_config = BatchAcceptInferConfig(
        policy=args.get("policy"),
        query_pipeline=q,
        annotation_set_name=args.get("annotation_set_name"),
        artifact_names=args.get("artifact_names").split(","),
        infer_job_name=args.get("infer_job_name"),
        user_id=args.get("user_id"),
        job_name=args.get("job_name")
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

    # batch accept infer result
    batch_accept_infer(accept_infer_config)
