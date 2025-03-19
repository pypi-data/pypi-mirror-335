# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/7/26
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : calculate_image_size_script.py
# @Software: PyCharm
"""

import os
import time
import ray
import pandas as pd
import pyarrow as pa
import bcelogger
from pymongoarrow.api import Schema
from ray.data.read_api import read_datasource
from datetime import datetime, timedelta
from pandas import DataFrame
from mongoengine import connect
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.datasource.sharded_mongo_datasource import get_mongo_datasource
from vistudio_image_analysis.operator.webp_generator import get_project_name
from vistudio_image_analysis.table.image import ImageData, DATA_TYPE_IMAGE
from windmillcomputev1.client.compute_client import ComputeClient
from windmillcomputev1.filesystem import blobstore


def calculate_image_size_pipeline(config, parallelism=10):
    """
    Main function to calculate image sizes and update MongoDB.
    """
    bcelogger.info(f"Start calculate image size pipeline with parallelism: {parallelism}")

    # 当前时间
    current_time = datetime.now()

    # 一个月前的时间
    one_month_ago = current_time - timedelta(days=30)

    # 格式化成指定的字符串格式
    one_month_ago_ns = int(one_month_ago.timestamp() * 1e9)

    # 第一步 查找size不存在的数据且创建时间小于一个月
    pipeline = [
        {"$match": {
            "data_type": "Image",
            "size": {"$exists": False},
            "created_at": {"$gte": one_month_ago_ns},
        }},
        {"$sort": {"created_at": -1}},
    ]
    schema = Schema({
        "image_id": pa.string(),
        "annotation_set_id": pa.string(),
        "annotation_set_name": pa.string(),
        "file_uri": pa.string(),
        "org_id": pa.string(),
        "user_id": pa.string(),
        "size": pa.float64(),
    })

    datasource = get_mongo_datasource(config=config, pipeline=pipeline, schema=schema)
    ds = read_datasource(datasource, parallelism=parallelism)

    if ds.count() <= 0:
        bcelogger.info(f"No images to calculate, returning.")
        return
    image_size_ds = generate_size(source=ds.to_pandas(), windmill_endpoint=config.windmill_endpoint)
    updated_ds = update_image_size(image_size_ds, config)
    bcelogger.info(f"Calculated image size count: {updated_ds.count()}")


def generate_size(source: DataFrame, windmill_endpoint) -> DataFrame:
    """
    generate size
    """
    results = []
    for source_index, source_row in source.iterrows():
        bcelogger.info(f"---start calculate image size: {source_row.to_dict()}---")
        try:
            # cache blobstore
            pj_name, ws_id = get_project_name(source_row['annotation_set_name'])
            org_id = source_row['org_id']
            user_id = source_row['user_id']
            bs_client = get_bs(pj_name, ws_id, org_id, user_id, windmill_endpoint)

            # read image
            file_uri = source_row['file_uri']
            image_bytes = bs_client.read_raw(path=file_uri)
            size = len(image_bytes)

            results.append({
                "image_id": source_row['image_id'],
                "annotation_set_id": source_row['annotation_set_id'],
                "size": size,
            })

            bcelogger.info("calculate image size success")
        except Exception as e:
            results.append({
                "image_id": source_row['image_id'],
                "annotation_set_id": source_row['annotation_set_id'],
                "size": -1,
            })
            bcelogger.info("calculate image size error: {}".format(e))

    return pd.DataFrame(results)


def get_bs(pj_name, ws_id, org_id, user_id, windmill_endpoint):
    """
    get blob store
    :return:
    """
    compute_client = ComputeClient(endpoint=windmill_endpoint,
                                   context={"OrgID": org_id, "UserID": user_id})

    try:
        fs = compute_client.suggest_first_filesystem(workspace_id=ws_id, guest_name=pj_name)
        return blobstore(filesystem=fs)
    except Exception as e:
        bcelogger.info(f"suggest filesystem error: {e}")


def update_image_size(source: DataFrame, config) -> DataFrame:
    """
    update size
    """
    connect(host=config.mongo_uri, db=config.mongodb_database)
    for source_index, source_row in source.iterrows():
        if source_row['size'] == -1:
            ImageData.objects(
                image_id=source_row['image_id'],
                annotation_set_id=source_row['annotation_set_id'],
                data_type=DATA_TYPE_IMAGE
            ).update_one(
                set__size=0,
                set__updated_at=time.time_ns()
            )
        else:
            ImageData.objects(
                image_id=source_row['image_id'],
                annotation_set_id=source_row['annotation_set_id'],
                data_type=DATA_TYPE_IMAGE
            ).update_one(
                set__updated_at=time.time_ns(),
                set__size=source_row['size']
            )

    return source


def main():
    """
    Main function to execute the pipeline.
    """
    args = {
        "mongo_user": os.environ.get('MONGO_USER', 'root'),
        "mongo_password": os.environ.get('MONGO_PASSWORD', 'mongo123#'),
        "mongo_host": os.environ.get('MONGO_HOST', '10.27.240.45'),
        "mongo_port": int(os.environ.get('MONGO_PORT', 8719)),
        "mongo_database": os.environ.get('MONGO_DB', 'annotation'),
        "mongo_collection": os.environ.get('MONGO_COLLECTION', 'annotation'),
        "windmill_endpoint": os.environ.get('WINDMILL_ENDPOINT', 'http://10.27.240.45:8340')
    }
    config = Config(args)

    # os.environ["RAY_ADDRESS"] = "ray://10.27.240.45:8892"
    ray.init()

    calculate_image_size_pipeline(config=config, parallelism=10)


if __name__ == '__main__':
    main()
