#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   coco_data_update.py
"""

from pymongo import MongoClient

from vistudio_image_analysis.util import string

# 连接到 MongoDB
client = MongoClient("mongodb://root:mongo123#@10.224.41.107:8088")
db = client["annotation"]
collection = db["annotation"]

# 要查找和更新的参数
annotation_set_id = "as-9wjdr3de"  # 根据你的要求修改
data_type = "Image"

# 查询符合条件的文档
documents = collection.find(
    {"annotation_set_id": annotation_set_id,
     "data_type": data_type,
     }
)
for document in documents:
    if document and "image_name" in document:
        # 基于 image_name 生成新的 image_id
        image_name = document["image_name"]
        old_image_id = document["image_id"]
        new_image_id = string.generate_md5(image_name)

        document_anno = collection.find_one(
            {
                "annotation_set_id": annotation_set_id,
                "data_type": "Annotation",
                "image_id": old_image_id,
                "task_kind": "Manual"
            }
        )

        # 更新文档的 image_id
        result_image = collection.update_one(
            {"annotation_set_id": annotation_set_id, "data_type": "Image", "image_id": old_image_id},
            {"$set": {"image_id": new_image_id}}
        )

        result_anno = collection.update_one(
            {"annotation_set_id": annotation_set_id, "data_type": "Annotation", "image_id": old_image_id},
            {"$set": {"image_id": new_image_id}}
        )

        # 确认更新操作
        if result_image.modified_count > 0:
            print("Document updated successfully with new image_id.")
        else:
            print("No document was updated.")
    else:
        print("No document found with the specified annotation_set_id and data_type.")
