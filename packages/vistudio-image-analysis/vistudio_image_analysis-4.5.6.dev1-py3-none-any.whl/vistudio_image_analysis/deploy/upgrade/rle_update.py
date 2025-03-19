# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   rle_update.py
"""
from pymongo import MongoClient
import numpy as np
import bcelogger
import os

# 线上 mongodb://root:mongo123#@10.27.240.5:8719
# test mongodb://root:mongo123#@10.27.240.49:8719
mongo_host = os.getenv("MONGO_HOST")
mongo_port = os.getenv("MONGO_PORT")
mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_db = os.getenv("MONGO_DB")
mongo_collection = os.getenv("MONGO_COLLECTION")
create_at_lt = os.getenv("CREATE_AT_LT", default="1726034584000000000")
mongo_uri = "mongodb://{}:{}@{}:{}".format(mongo_user, mongo_password, mongo_host, mongo_port)
bcelogger.info("mongo_uri:{}".format(mongo_uri))
client = MongoClient(mongo_uri)

db = client[mongo_db]
collection = db[mongo_collection]


def mask_to_rle(img):
    '''
    Args:
        -img: numpy array, 1 - mask, 0 - background, mask位置的值可以不是1，但必须完全相同
    Returns:
        -rle.txt
    该函数返回单个图片的标注信息，所有的标注视为整体，因此适用于单个标注的图片
    例如: img  1 0 0 1 1 1 0      rle.txt 0 1 2 3 1
    '''
    # 为了按列扫描，需要先转置一下
    img = img.T
    pixels = img.flatten()
    pixels = np.concatenate([[0], pixels, [0]])
    # 获取像素变化的坐标
    runs = np.where(pixels[1:] != pixels[:-1])[0]
    # 计算0 1 连续出现的数量
    runs = np.concatenate([[0], runs, [pixels.shape[0] - 2]])
    runs[1:] -= runs[:-1]
    # 如果最后一位为0， 去除
    if runs[-1] == 0:
        runs = runs[:-1]
    return runs[1:].tolist()


def rle2mask(rle, gray=255):
    """
    计算rle的mask
    params:
        rle: size[h, w]  counts: [0的个数, 1的个数, ……] (按行编码)
    Returns:
        -mask: rle对应的mask
    """
    height, width = rle["size"]
    mask = np.zeros(height * width).astype(np.uint8)
    start = 0
    pixel = 0
    for num in rle["counts"]:
        stop = start + num
        mask[start:stop] = pixel
        pixel = gray - pixel
        start = stop
    return mask.reshape(height, width)


def conver_rle(rle):
    """
    conver_rle
    """
    mask = rle2mask(rle)
    new_rle = mask_to_rle(mask)
    return new_rle


# 给定的 annotation_set_id 列表
# annotation_set_ids = ['as-y5h6hh2d']

# 查询 MongoDB 中所有包含 rle 且 annotation_set_id 在给定列表中的文档
query = {
    "annotations.rle": {"$exists": True},
    "data_type": "Annotation",
    "$or": [
        {"rle_update": {"$exists": False}},
        {"rle_update": "0"}
    ],
    "created_at": {"$lt": int(create_at_lt)}
}
docs_with_rle = collection.find(query)
docs_count = collection.count_documents(query)
bcelogger.info(f"满足条件的文档数量: {docs_count}")
# 遍历所有查询到的文档
for doc in docs_with_rle:
    # 遍历 annotations 以找到 rle
    try:
        updated = False
        for annotation in doc["annotations"]:
            if "rle" in annotation:
                old_rle = annotation["rle"]
                if old_rle is None or len(old_rle) == 0:
                    continue
                if 'counts' not in old_rle or 'size' not in old_rle:
                    bcelogger.info("rle 结构不符合，跳过。_id:{}".format(doc["_id"]))
                    continue
                # 调用方法A得到新的rle counts
                new_counts = conver_rle(old_rle)
                # 更新 counts
                annotation["rle"]["counts"] = new_counts
                updated = True

        # 如果有更新，保存回 MongoDB
        if updated:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "annotations": doc["annotations"],
                    "rle_update": "1"
                }}
            )
            bcelogger.info("更新成功，_id:{}".format(doc["_id"]))

    except Exception as e:
        bcelogger.error("转换出错 doc:{}".format(doc), e)

bcelogger.info("文档更新完成")
