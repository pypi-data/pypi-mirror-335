#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/12
# @Author  : yanxiaodong
# @File    : swift_Formatter.py
"""
from typing import Dict, List, Any
import time
import os

from ray.data import Dataset
import pyarrow as pa
import numpy as np
import ray

import bcelogger
import pandas as pd

from vistudio_image_analysis.util import string
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class SWIFTFormatter(object):
    """
    SWIFTFormatter
    """
    def __init__(
            self,
            annotation_set_id: str = None,
            annotation_set_name: str = None,
            data_uri: str = None,
            data_types: List = None,
            user_id: str = None,
            org_id: str = None,
            tag: Dict = None,
            annotation_set_category: str = None,
            counter: ImageAnnotationCounter = None
    ):
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag
        self.annotation_set_category = annotation_set_category
        self.counter = counter

    def _get_image_uri(self):
        if self.data_types is not None and \
                len(self.data_types) == 2 and "image" in self.data_types and "annotation" in self.data_types:
            image_uri_prefix = self.data_uri
        else:
            image_uri_prefix = ''
        return image_uri_prefix

    def _fill_image_info_vistudio(self, row: Dict[str, Any], image_uri_prefix: str):
        """
        _fill_image_info_vistudio
        """
        # 不支持多图片对话，只取第一张图片
        image_name = os.path.basename(row["images"][0])

        row["image_id"] = string.generate_md5(image_name)
        row["image_name"] = image_name
        row["width"] = 0
        row["height"] = 0
        row["annotation_set_id"] = self.annotation_set_id
        row["annotation_set_name"] = self.annotation_set_name
        row["user_id"] = self.user_id
        row["org_id"] = self.org_id
        row["created_at"] = time.time_ns()
        row["data_type"] = 'Image'
        row["infer_state"] = 'UnInfer'
        row["file_uri"] = os.path.join(image_uri_prefix, row["images"][0])

        if self.tag is not None and len(self.tag) > 0:
            row['tags'] = self.tag

        return row

    def _fill_annotation_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_annotation_info_vistudio
        :param row:
        :return:
        """
        image_name = os.path.basename(row["images"][0])

        row["image_id"] = string.generate_md5(image_name)
        row["user_id"] = self.user_id
        row["created_at"] = time.time_ns()
        row["data_type"] = "Annotation"
        row["annotation_set_id"] = self.annotation_set_id
        row["task_kind"] = "Manual"
        row["artifact_name"] = ""
        row["job_name"] = ""
        annotations = [{
            "question_id": string.generate_random_digits(6),
            "question": row["query"],
            "answer": row["response"]
        }]
        row["annotations"] = annotations

        return row

    def to_vistudio_v1(self, ds: Dataset) -> Dict[str, Dataset]:
        """
        A dataset to vistudio v1 dataset
        """
        image_uri_prefix = self._get_image_uri()

        # 展开 images
        image_ds = ds.map(lambda row: self._fill_image_info_vistudio(row=row, image_uri_prefix=image_uri_prefix))
        image_ds = image_ds.drop_columns(cols=["query", "response", "images"])

        # 展开 annotations
        annotation_ds = ds.map(lambda row: self._fill_annotation_info_vistudio(row=row))
        annotation_ds = annotation_ds.drop_columns(cols=["query", "response", "images"])
        df = annotation_ds.to_pandas()
        df['annotations'] = df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(df))

        return {"image_ds": image_ds, "annotation_ds": annotation_ds}

    def _to_swift(self, row):
        annotations_total = row.get('annotations')
        if annotations_total is None or len(annotations_total) == 0:
            return {}

        self.counter.add_image_count.remote()
        questions = []
        answers = []

        for image_annotation in annotations_total:
            task_kind = image_annotation['task_kind']
            if task_kind != "Manual":
                continue
            annotations = image_annotation['annotations']
            if annotations is None or len(annotations) == 0:
                continue

            for annotation in annotations:
                question = annotation.get("question")
                answer = annotation.get("answer")
                if question is None or answer is None:
                    continue
                questions.append(f"{len(questions) + 1}.{question}")
                answers.append(answer)

                self.counter.add_annotation_count.remote()

        return {
            "images": [row['file_uri']],
            "query": ''.join(questions),
            "response": ''.join(answers),
        }

    def from_vistudio_v1(self, ds: "Dataset"):
        """
        vistudio_v1 to swift
        :param ds:
        :return:
        """
        return ds.map(lambda row: self._to_swift(row))
