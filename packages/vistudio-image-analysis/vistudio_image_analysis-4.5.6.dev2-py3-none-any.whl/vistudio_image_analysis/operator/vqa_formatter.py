#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   vqa_formatter.py
"""
import time
from typing import Union, Dict
import os
import bcelogger
import ray
from ray.data import Dataset
import pandas as pd

from vistudio_image_analysis.util import string, filter


class VQAFormatter(object):
    """
    VQAFormatter
    """
    def __init__(
        self,
        annotation_set_id: str = None,
        annotation_set_name: str = None,
        data_uri: str = None,
        user_id: str = None,
        org_id: str = None,
        tag: Union[Dict] = None,
    ):
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag

    def _fill_image_info_vqa(self, row) -> dict:
        """
        fill image info
        """
        file_name = row.get("image")
        image_name = os.path.basename(file_name)

        item = {
            "annotation_set_id": self.annotation_set_id,
            "image_id": string.generate_md5(image_name),
            "data_type": "Image",
            "annotation_set_name": self.annotation_set_name,
            "file_uri": os.path.join(self.data_uri, "images", file_name),
            "image_name": image_name,
            "height": 0,
            "width": 0,
            "infer_state": "UnInfer",
            "org_id": self.org_id,
            "user_id": self.user_id,
            "created_at": time.time_ns(),
        }
        if self.tag is not None and len(self.tag) > 0:
            item['tags'] = self.tag
        return item

    def _fill_annotation_info_vistudio(self, group: pd.DataFrame) -> dict:
        """
        fill annotation info
        """
        file_name = group['image'].iloc[0]
        image_name = os.path.basename(file_name)

        annotations = []
        question_set = set()
        for _, row in group.iterrows():
            if len(annotations) >= 10:
                break

            if row.get('question') is None or row.get('answer') is None or row.get('question') is None:
                continue

            if row["question_id"] < 0 or row["question"] == "" or row["answer"] == "":
                continue

            if row["question"] in question_set:
                continue

            annotation = {
                "id": string.generate_random_digits(6),
                "question_id": row["question_id"],
                "question": row["question"],
                "answer": row["answer"]
            }
            annotations.append(annotation)
            question_set.add(row["question"])

        item = {
            "annotation_set_id": [self.annotation_set_id],
            "image_id": [string.generate_md5(image_name)],
            "data_type": ["Annotation"],
            "artifact_name": [""],
            "job_name": [""],
            "annotations": [annotations],
            "task_kind": ["Manual"],
            "user_id": [self.user_id],
            "created_at": [time.time_ns()],
        }
        return pd.DataFrame(item)

    def to_vistudio_v1(self, ds: Dataset):
        """
        convert vqa to vistudio v1
        """
        # image ds
        image_ds = ds.select_columns(["image"])
        image_df = filter.drop_duplicates(source=image_ds.to_pandas(), cols=['image'])
        image_ds = ray.data.from_pandas(image_df)
        final_image_ds = image_ds.map(lambda row: self._fill_image_info_vqa(row=row))

        # annotation ds
        df = filter.drop_duplicates(source=ds.to_pandas(), cols=['question_id'])
        final_ds = ray.data.from_pandas(df).groupby(['image'])
        final_anno_ds = final_ds.map_groups(self._fill_annotation_info_vistudio)

        return {"image_ds": final_image_ds, "annotation_ds": final_anno_ds}
