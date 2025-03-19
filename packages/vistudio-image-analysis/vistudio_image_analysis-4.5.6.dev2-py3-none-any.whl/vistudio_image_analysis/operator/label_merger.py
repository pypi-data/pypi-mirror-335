# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/23 11:49
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : label_merger.py
# @Software: PyCharm
"""
import bcelogger
import numpy as np
from pandas import DataFrame
from pymongo import MongoClient
from vistudio_image_analysis.operator.updater.base_mongo_updater import BaseMongoUpdater
from vistudio_image_analysis.table.annotation import AnnotationData, DATA_TYPE_ANNOTATION


class LabelMerger(BaseMongoUpdater):
    """
    LabelMerger
    """

    def __init__(self, config, operator_params):
        super().__init__(config=config)
        self.merge_labels = operator_params.get("merge_labels")
        self.collection = self._get_collection()

    def merge_label(self, source: DataFrame) -> DataFrame:
        """
        merge label for each annotation in the source DataFrame
        """
        bcelogger.info(f"Starting to merge labels for {len(source)} images")
        source['annotations'] = source['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        for source_index, source_row in source.iterrows():
            for image_annotation_index, image_annotation in enumerate(source_row.get('annotations')):
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue

                for annotation_index, annotation in enumerate(annotations):
                    new_labels = []
                    # 如果 annotation 的 labels 列表不存在或为空，跳过该 annotation
                    if len(annotation.get("labels")) == 0:
                        continue
                    # 遍历 labels 列表中的每个 dict
                    for label_index, label in enumerate(annotation["labels"]):
                        label_id = label.get("id", "")
                        parent_id = label.get("parent_id", "")

                        if f"{label_id}_{parent_id}" in self.merge_labels:
                            new_id_parent = self.merge_labels[f"{label_id}_{parent_id}"]
                            label_id, parent_id = new_id_parent.split("_")

                        # 处理只有 id，没有 parent_id 的情况
                        elif label_id in self.merge_labels:
                            label_id = self.merge_labels[label_id]
                            parent_id = label.get("parent_id")
                        new_labels.append({
                            "id": label_id,
                            "parent_id": parent_id,
                            "name": label.get("name"),
                            "confidence": label.get("confidence")
                        })
                    documents = self.collection.update_one(
                        {
                            "image_id": source_row["image_id"],
                            "annotation_set_id": image_annotation['annotation_set_id'],
                            "task_kind": image_annotation["task_kind"],
                            "data_type": DATA_TYPE_ANNOTATION,
                            "annotations.id": annotation['id']  # 匹配 annotations 中的特定 annotation
                        },
                        {
                            "$set": {
                                "annotations.$.labels": new_labels  # 使用 $ 操作符更新匹配的 annotation 的 labels
                            }
                        }
                    )
                    annotations[annotation_index]['labels'] = new_labels
                    source.at[source_index, 'annotations'][image_annotation_index]['annotations'] = annotations

                bcelogger.info(f"after merge source: {source.to_string()}")

        return source

    def _get_collection(self):
        """
        get collection from mongo
        """
        client = MongoClient(self.config.mongo_uri)
        db = client[self.config.mongodb_database]
        return db[self.config.mongodb_collection]
