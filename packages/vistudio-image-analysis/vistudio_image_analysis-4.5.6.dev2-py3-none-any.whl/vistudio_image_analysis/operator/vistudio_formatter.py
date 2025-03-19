#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File:  vistudio_formatter.py
"""
import os
import bcelogger
import ray.data
from ray.data import DataContext
import time
from typing import Union, Dict, Any
import numpy as np
import bson

from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.util import string
from vistudio_image_analysis.util.filter import drop_duplicates
from vistudio_image_analysis.util.label import convert_annotation_labels, convert_annotation_labels_id, \
    convert_labels_id_attr_dict

ctx = DataContext.get_current()
ctx.enable_tensor_extension_casting = False


class VistudioFormatter(object):
    """
    VistudioFormatter
    """
    def __init__(
        self,
        config: Config = None,
        labels: Union[Dict] = None,
        annotation_set_id: str = None,
        annotation_set_name: str = None,
        data_uri: str = None,
        data_types: list() = None,
        tag: Union[Dict] = None,
        import_labels: Union[Dict] = None,
        annotation_set_category: str = None
    ):
        self.config = config
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.labels = labels
        self.tag = tag
        self.import_labels = import_labels
        self.annotation_set_category = annotation_set_category

    def _fill_image_info_vistudio(self, row: Dict[str, Any]):
        """
        fill vistudio image info
        :param row:
        :return:
        """
        image_name = row['image_name']

        if len(self.data_types) > 1:
            # 导入图像+标注, file_uri需要根据图像的s3地址重新生成
            file_uri = f"{self.data_uri}/images/{image_name}"
        else:
            # 导入标注, file_uri为标注文件内写的地址，且需要是一个s3地址
            if "s3://" in row['file_uri']:
                file_uri = row['file_uri']
            else:
                file_uri = ''

        item = {
            "annotation_set_id": self.annotation_set_id,
            "image_id": string.generate_md5(os.path.basename(image_name)),
            "data_type": "Image",
            "annotation_set_name": self.annotation_set_name,
            "file_uri": file_uri,
            "image_name": image_name,
            "height": 0,
            "width": 0,
            "org_id": self.config.org_id,
            "user_id": self.config.user_id,
            "created_at": time.time_ns(),
        }

        tags = row.get("tags")
        # tags在mongo里面如果是空object，导出时会被读成[]，而不是{}
        if not isinstance(tags, dict):
            tags = {}
        if self.tag is not None and len(self.tag) > 0:
            tags = tags | self.tag
        if tags is not None and len(tags) > 0:
            item["tags"] = tags

        return item

    def _fill_annotation_info_vistudio(self, row):
        """
        fill annotation info
        :param row:
        """
        if self.annotation_set_category != 'Image/ImageClassification/MultiTask':
            new_annos = self._convert_labels_without_attr(row['annotations'])
        else:
            new_annos = self._convert_labels_with_attr(row['annotations'])

        item = {
            "annotation_set_id": self.annotation_set_id,
            "image_id": string.generate_md5(row['image_name']),
            "data_type": "Annotation",
            "artifact_name": row['artifact_name'],
            "job_name": row['job_name'],
            "infer_config": {
                'temperature': 0,
                'top_p': 0,
                'repetition_penalty': 0
            },
            "job_created_at": 0,
            "annotations": new_annos,
            "task_kind": row['task_kind'],
            "user_id": self.config.user_id,
            "created_at": time.time_ns(),
        }

        if row['task_kind'] == 'Model':
            if row.get('job_created_at') is not None and not np.isnan(row.get('job_created_at')):
                item['job_created_at'] = bson.Int64(int(row['job_created_at']))
            if row.get('infer_config') is not None and isinstance(row.get('infer_config'), dict):
                item['infer_config'] = row['infer_config']
        return item

    def _convert_labels_without_attr(self, annotations):
        """
        :param labels:
        :return:
        """
        new_annos = []
        for anno in annotations:
            new_labels = []
            for label in anno['labels']:
                label_id = label["id"]
                label_name = self.import_labels.get(label_id)
                if label_name is None:
                    continue
                new_label_id = self.labels.get(label_name).get("local_name")
                new_label = {"id": new_label_id}
                confidence = label.get("confidence")
                if confidence is not None and isinstance(confidence, float):
                    new_label["confidence"] = confidence

                new_labels.append(new_label)

            anno["labels"] = new_labels
            new_annos.append(anno)

        return new_annos

    def _convert_labels_with_attr(self, annotations):
        new_annos = []
        for anno in annotations:
            new_labels = []
            for label in anno['labels']:
                parent_id = label["parent_id"]
                if parent_id is None or parent_id == "":
                    continue

                # 获取导入标签的信息
                import_label = self.import_labels.get(parent_id)
                if import_label is None:
                    continue
                task_name = import_label.get('display_name')
                task_categories = import_label.get('attributes')

                # 获取导入标签对应标注集标签的信息
                task_dict = self.labels.get(task_name, None)
                if task_dict is None:
                    continue
                label_id = task_dict.get("local_name")
                attr_dict = task_dict.get("attributes")

                attr_name = task_categories.get(label["id"])
                attr_id = attr_dict.get(attr_name)

                new_label = {
                    "id": attr_id,
                    "parent_id": label_id
                }
                confidence = label.get("confidence")
                if confidence is not None and isinstance(confidence, float):
                    new_label["confidence"] = confidence
                new_labels.append(new_label)

            anno["labels"] = new_labels
            new_annos.append(anno)

        return new_annos

    @staticmethod
    def standardize_annotations(batch):
        """
        标准化 'annotations' 中的 'labels' 字段
        """
        for item in batch['annotations'].tolist():
            for annotation in item:
                if annotation.get('labels') is None:
                    annotation['labels'] = []
        return batch

    def to_vistudio_v1(self, ds: "Dataset") -> "Dataset":
        """
        to_vistudio_v1
        :param ds: Dataset
        :return: Dataset
        """
        # image ds
        image_ds = ds.filter(lambda row: row["data_type"] == "Image")
        image_df = drop_duplicates(source=image_ds.to_pandas(), cols=['image_name'])
        image_ds = ray.data.from_pandas(image_df)
        final_image_ds = image_ds.map(
            lambda row: self._fill_image_info_vistudio(row=row)
        ).filter(lambda x: x['file_uri'] != '')

        # annotation ds
        all_anno_ds = ds.filter(lambda row: (row['data_type'] == 'Annotation')).\
            map_batches(self.standardize_annotations)

        if len(all_anno_ds.take_all()) == 0:
            return {"image_ds": final_image_ds, "annotation_ds": all_anno_ds, "prediction_ds": all_anno_ds}

        image_id_ds = ds.filter(lambda row: row["data_type"] == "Image").select_columns(["image_id", "image_name"])
        image_id_df = drop_duplicates(source=image_id_ds.to_pandas(), cols=['image_name'])

        # 共同的image_id的行会被提取合并
        merge_df = image_id_df.merge(all_anno_ds.to_pandas(), on='image_id', how='inner')
        anno_ds = ray.data.from_pandas(merge_df)

        if self.annotation_set_category != 'Image/ImageClassification/MultiTask':
            self.labels = convert_annotation_labels(self.labels)
            self.import_labels = {item['local_name']: item['display_name'] for item in self.import_labels}
        else:
            self.labels = convert_labels_id_attr_dict(labels=self.labels)
            self.import_labels = convert_annotation_labels_id(labels=self.import_labels)

        anno_ds = anno_ds.map(lambda row: self._fill_annotation_info_vistudio(row))

        final_anno_ds = anno_ds.filter(lambda row: row['task_kind'] == 'Manual')
        final_pred_ds = anno_ds.filter(lambda row: row['task_kind'] == 'Model')
        return {"image_ds": final_image_ds, "annotation_ds": final_anno_ds, "prediction_ds": final_pred_ds}

    @staticmethod
    def from_vistudio_v1(ds: "Dataset"):
        """
        from_vistudio_v1
        :param ds: Dataset
        """
        def filter_annotations(row, task_kind):
            annotations_list = row['annotations']
            filtered_annotations = []
            for annotation in annotations_list:
                if annotation.get("task_kind") == task_kind:
                    filtered_annotations.append(annotation)
            return filtered_annotations

        image_ds = ds.map_batches(
            lambda batch: {k: v for k, v in batch.items() if k != "annotations"}
        )
        anno_ds = ds.flat_map(
            lambda row: filter_annotations(row, "Manual")
        )
        pred_ds = ds.flat_map(
            lambda row: filter_annotations(row, "Model")
        )

        return image_ds, anno_ds, pred_ds


