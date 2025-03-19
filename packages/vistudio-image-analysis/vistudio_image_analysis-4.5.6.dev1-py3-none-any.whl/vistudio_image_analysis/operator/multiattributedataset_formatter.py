#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   imagenet_formatter.py
"""
import time
from typing import Union, Dict, Any, List
import numpy as np
import ray
from pandas import DataFrame
import pandas as pd

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.util import string
import os

from vistudio_image_analysis.util.label import convert_annotation_labels, convert_annotation_labels_id, \
    merge_labels_with_attr, convert_labels_id_attr_dict


class MultiAttributeDatasetFormatter(object):
    """
    ImageNetFormatter
    """

    def __init__(self,
                 annotation_labels: Union[List] = list,
                 data_types: Union[List] = None,
                 data_uri: str = None,
                 multi_attribute_labels: Union[List] = None,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 user_id: str = None,
                 org_id: str = None,
                 tag: Union[Dict] = None,
                 merge_labels: Union[Dict] = None,
                 counter: ImageAnnotationCounter = None
                 ):
        self.annotation_labels = annotation_labels
        self.data_types = data_types
        self.data_uri = data_uri
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag
        self.multi_attribute_labels = multi_attribute_labels
        self.annotation_label_dict = convert_labels_id_attr_dict(labels=self.annotation_labels)
        self.annotation_label_id_dict = convert_annotation_labels_id(labels=self.annotation_labels)
        self.multi_attribute_labels_dict = convert_annotation_labels_id(labels=self.multi_attribute_labels)
        self.image_uri_prefix = self._get_image_uri()
        self.merge_labels = merge_labels
        self.merge_annotation_labels = merge_labels_with_attr(labels=self.annotation_labels,
                                                              merge_labels=self.merge_labels)
        self.counter = counter

    def _convert_labels_dict(self):
        """
        _convert_labels_dict
        """
        label_dict = {}
        for label in self.annotation_labels:
            attributes = label.get("labels", None)
            attr_dict = {}
            if attributes is not None and len(attributes) > 0:
                for attr in attributes:
                    attr_dict[str(attr.get('displayName'))] = str(attr.get('localName'))

            label_dict[str(label.get('displayName'))] = {
                str(label.get('localName')): attr_dict
            }
        return label_dict

    def _convert_multi_attribute_labels(self):
        """
        _convert_multi_attribute_labels， 可以通过anno_key 快速找到对应的标签
        {
            "1": {
                "display_name": "安全帽",
                "attributes": [
                    {"local_name": "0", "display_name": "未带安全帽"},
                    {"local_name": "1", "display_name": "带安全帽"}
                ]
            },
            "2": {
                "display_name": "工服",
                "attributes": [
                    {"local_name": "0", "display_name": "未穿工服"},
                    {"local_name": "1", "display_name": "穿工服"}
                ]
            }
        }
        """
        if self.multi_attribute_labels is None:
            return None
        result = {item["anno_key"]: {"display_name": item["display_name"], "attributes": item["attributes"]} for item in
                  self.multi_attribute_labels}
        return result

    def _get_image_uri(self):
        if self.data_types is None:
            return None

        if len(self.data_types) == 2 and "image" in self.data_types and "annotation" in self.data_types:
            image_uri_prefix = os.path.join(self.data_uri, "images")
        else:
            image_uri_prefix = ''
        return image_uri_prefix

    def _fill_image_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_image_info_vistudio
        :param row: dict
        :return: dict
        """
        annotation_text = row['text']
        parts = annotation_text.split(' ')
        file_uri = parts[0]
        if "S3" not in file_uri:
            s3_file_uri = os.path.join(self.image_uri_prefix, file_uri)
        item = {}
        item['file_uri'] = s3_file_uri
        item['width'] = 0
        item['height'] = 0
        image_name = file_uri.split("/")[-1]
        item['image_name'] = image_name
        item['image_id'] = string.generate_md5(item['image_name'])
        item['annotation_set_id'] = self.annotation_set_id
        item['annotation_set_name'] = self.annotation_set_name
        item['user_id'] = self.user_id
        item['org_id'] = self.org_id
        item['created_at'] = time.time_ns()
        item['data_type'] = 'Image'
        if self.tag is not None and len(self.tag) > 0:
            item['tags'] = self.tag
        return item

    def _fill_annotation_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_annotation_info_vistudio
        :param row:
        :return:
        """
        annotation_text = row['text']
        parts = annotation_text.split(' ')
        file_uri = parts[0]
        image_name = file_uri.split("/")[-1]
        item = dict()
        item['image_id'] = string.generate_md5(image_name)
        item['user_id'] = self.user_id
        item['created_at'] = time.time_ns()
        item['data_type'] = 'Annotation'
        item['annotation_set_id'] = self.annotation_set_id
        item['task_kind'] = "Manual"
        item['artifact_name'] = ""
        item['job_name'] = ""
        annotations = list()
        for index, part in enumerate(parts):
            if index == 0 or str(part) == "-1":
                continue
            anno_key = str(index)
            multi_attribute_label = self.multi_attribute_labels_dict.get(anno_key)
            if multi_attribute_label is None:
                continue

            task_name = multi_attribute_label.get('display_name')
            task_categories = multi_attribute_label.get('attributes')
            task_dict = self.annotation_label_dict.get(task_name, None)
            if task_dict is None:
                continue
            label_id = task_dict.get("local_name")
            attr_dict = task_dict.get("attributes")
            attr_name = task_categories.get(str(part))
            attr_id = attr_dict.get(attr_name)
            annotations.append({
                'id': string.generate_random_digits(6),
                'labels': [{
                    "id": attr_id,
                    "name": attr_name,
                    "parent_id": label_id
                }]
            })

        item['annotations'] = annotations
        return item

    def to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        to_vistudio_v1
        :param ds:
        :return:
        """
        image_ds = ds.map(lambda row: self._fill_image_info_vistudio(row=row))
        annotation_ds = ds.map(lambda row: self._fill_annotation_info_vistudio(row=row))

        df = annotation_ds.to_pandas()
        df['annotations'] = df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        import pyarrow as pa
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(df))

        return {"image_ds": image_ds, "annotation_ds": annotation_ds}

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source: DataFrame
        :return: DataFrame
        """
        annotation_list = list()
        label_index_list = ["-1"] * (len(self.merge_annotation_labels))
        for source_index, source_row in source.iterrows():

            annotations_total = source_row.get('annotations')
            if annotations_total is None or len(annotations_total) == 0:
                continue
            file_name = source_row['file_uri']
            for image_annotation in annotations_total:
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue

                self.counter.add_image_count.remote()
                for annotation in annotations:
                    self.counter.add_annotation_count.remote()
                    labels = annotation['labels']
                    for label in labels:
                        attr_id = label['id']
                        label_id = label['parent_id']

                        merge_label_key = str(attr_id) + "_" + str(label_id)
                        if self.merge_labels is not None and merge_label_key in self.merge_labels.keys():
                            # 如果该属性 被合并了，那么跳过该属性
                            merge_label_value = self.merge_labels.get(merge_label_key)
                            attr_id = merge_label_value.split("_")[0]
                            label_id = merge_label_value.split("_")[1]

                        def find_key_index(d, key):
                            keys_list = list(d.keys())  # 将字典的键转换为列表
                            if key in keys_list:
                                return keys_list.index(key)
                            return -1

                        label_index = find_key_index(self.merge_annotation_labels, label_id)
                        if label_index == -1:
                            continue

                        attr_name = self.annotation_label_id_dict.get(label_id).get("attributes").get(attr_id)
                        attr_dict = self.merge_annotation_labels.get(label_id).get("attributes")
                        reversed_attributes = {v: k for k, v in attr_dict.items()}
                        attr_id = reversed_attributes.get(attr_name)
                        label_index_list[label_index] = attr_id

            annotation_list.append(("{} {}").format(file_name, ' '.join(label_index_list)))
        item = {"item": annotation_list}
        return pd.DataFrame(item)
