#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   LiangpinFormatter.py
"""
import time
from typing import Dict, Any
from ray.data import Dataset


class BackGroundFormatter(object):
    """
    BackGroundFormatter
    """
    def __init__(self):
        super().__init__()

    def generator_background_annotation(self, image_ds: Dataset, annotation_ds: Dataset) -> Dataset:
        """
        generator_background_annotation
        """
        if image_ds is None:
            return annotation_ds
        annotations_ds_image_ids = [] if annotation_ds is None else annotation_ds.unique(column='image_id')
        background_annotation_ds = image_ds.filter(lambda row: row['image_id'] not in annotations_ds_image_ids).map(
            lambda row: self._fill_background_annotation(row=row))
        return background_annotation_ds.union(annotation_ds)

    @staticmethod
    def _fill_background_annotation(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_background_annotation
        """
        return {
            'image_id': row['image_id'],
            'image_created_at': row['created_at'],
            'artifact_name': "",
            'annotations': [],
            'task_kind': 'Manual',
            'task_id': "",
            'job_name': "",
            'data_type': "Annotation",
            'user_id': row['user_id'],
            'annotation_set_id': row['annotation_set_id'],
            'created_at': row['created_at']
        }