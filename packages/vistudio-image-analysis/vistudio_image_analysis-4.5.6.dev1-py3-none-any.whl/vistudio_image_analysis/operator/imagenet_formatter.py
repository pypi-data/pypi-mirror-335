#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   imagenet_formatter.py
"""
import time
from typing import Union, Dict, Any
import numpy as np
import ray

from vistudio_image_analysis.util import string


class ImageNetFormatter(object):
    """
    ImageNetFormatter
    """

    def __init__(self,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 user_id: str = None,
                 org_id: str = None,
                 tag: Union[Dict] = None
                 ):
        self._labels = labels
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag

    def _fill_image_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_image_info_vistudio
        :param row: dict
        :return: dict
        """
        row['file_uri'] = row['image']
        row['width'] = 0
        row['height'] = 0
        image_name = row['image'].split("/")[-1]
        row['image_name'] = image_name
        row['image_id'] = string.generate_md5(row['image_name'])
        row['annotation_set_id'] = self.annotation_set_id
        row['annotation_set_name'] = self.annotation_set_name
        row['user_id'] = self.user_id
        row['org_id'] = self.org_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Image'
        row['infer_state'] = 'UnInfer'
        if self.tag is not None and len(self.tag) > 0:
            row['tags'] = self.tag
        return row

    def _fill_annotation_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_annotation_info_vistudio
        :param row:
        :return:
        """
        image_name = row['image'].split("/")[-1]
        row['image_id'] = string.generate_md5(image_name)
        row['user_id'] = self.user_id
        row['created_at'] = time.time_ns()
        row['data_type'] = 'Annotation'
        row['annotation_set_id'] = self.annotation_set_id
        row['task_kind'] = "Manual"
        row['artifact_name'] = ""
        row['job_name'] = ""
        label_name = row['label']
        annotation_label_info = self._labels.get(label_name)
        if annotation_label_info is None:
            return row
        annotation_label_id = annotation_label_info.get("local_name")
        annotations = list()
        annotations.append({
            'id': string.generate_random_digits(6),
            'labels': [{
                "id": annotation_label_id
            }]
        })
        row['annotations'] = annotations
        return row

    def to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        to_vistudio_v1
        :param ds:
        :return:
        """
        image_ds = ds.map(lambda row: self._fill_image_info_vistudio(row=row)).drop_columns(cols=['image', 'label'])
        annotation_ds = ds.map(lambda row: self._fill_annotation_info_vistudio(row=row)).drop_columns(
            cols=['image', 'label'])

        df = annotation_ds.to_pandas()
        df['annotations'] = df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        import pyarrow as pa
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(df))

        return {"image_ds": image_ds, "annotation_ds": annotation_ds}


