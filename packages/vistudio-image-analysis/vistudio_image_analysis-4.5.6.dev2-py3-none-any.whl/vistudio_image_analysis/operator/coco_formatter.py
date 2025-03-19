#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   coco_formatter.py
"""
import time
from typing import Union, Dict, Any, List
import os
import bcelogger
import numpy as np
import ray
from ray.data import Dataset
from pandas import DataFrame
import pandas as pd
import pyarrow as pa

from vistudio_image_analysis.table.image import ANNOTATION_STATE_ANNOTATED
from vistudio_image_analysis.util import string
from vistudio_image_analysis.util.label import merge_labels
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class CocoFormatter(object):
    """
    CocoFormatter
    """

    def __init__(
            self,
            labels: Union[Dict],
            merge_labels: Union[Dict] = None,
            annotation_set_id: str = None,
            annotation_set_name: str = None,
            data_uri: str = None,
            data_types: list() = None,
            user_id: str = None,
            org_id: str = None,
            tag: Union[Dict] = None,
            annotation_set_category: str = None,
            import_labels: Union[Dict] = None,
            counter: ImageAnnotationCounter = None
    ):
        self._labels = labels
        self.merge_labels = merge_labels
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.data_uri = data_uri
        self.data_types = data_types
        self.user_id = user_id
        self.org_id = org_id
        self.tag = tag
        self.annotation_set_category = annotation_set_category
        self.import_labels = import_labels
        self.counter = counter

    def images_from_vistudio_v1(self, source: DataFrame) -> list():
        """
        image_from_vistudio_v1
        :param source:
        :return:
        """
        images = list()
        filenames = list()
        for source_index, source_row in source.iterrows():
            file_name = source_row['file_uri']
            image_height = source_row['height']
            image_width = source_row['width']
            annotation_state = source_row['annotation_state']
            if annotation_state != ANNOTATION_STATE_ANNOTATED:
                continue
            filenames.append(file_name)

            image_id = int(source_row['image_id'], 16)
            images.append({
                "file_name": file_name,
                "height": int(image_height),
                "width": int(image_width),
                "id": image_id
            })
            if self.counter is not None:
                self.counter.add_image_count.remote()
        return images

    def annotations_from_vistudio_v1(self, source: DataFrame) -> list:
        """
        annotation_from_vistudio_v1
        :param source:
        :return:
        """
        results = list()
        for source_index, source_row in source.iterrows():
            image_id = int(source_row['image_id'], 16)
            for image_annotation in source_row.get('annotations'):
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue

                for annotation in annotations:
                    if self.counter is not None:
                        self.counter.add_annotation_count.remote()
                    labels = annotation['labels']
                    if labels is None or len(labels) == 0:
                        continue

                    label_id = str(labels[0]['id'])
                    if label_id not in self._labels:
                        continue

                    if self.merge_labels is not None and label_id in self.merge_labels:
                        label_id = self.merge_labels[label_id]

                    n_bbox = []
                    n_seg = [[]]

                    bbox = annotation.get('bbox')
                    if bbox is not None and len(bbox) > 0:
                        n_bbox = [int(element) for element in bbox]

                    area = annotation.get('area')
                    if area is None:
                        area = 0

                    seg = annotation.get('segmentation')
                    if seg is not None and len(seg) > 0:
                        n_seg = [[int(element) for element in seg]]

                    rle = annotation.get('rle')
                    if rle is not None and isinstance(rle, dict):
                        n_seg = rle

                    md5_data = {
                        "image_id": image_id,
                        "time": time.time_ns()
                    }
                    results.append({
                        "id": int(string.generate_md5(str(md5_data)), 16),
                        "image_id": image_id,
                        "bbox": n_bbox,
                        "area": int(area),
                        "iscrowd": 0,
                        "category_id": int(label_id),
                        "segmentation": n_seg,
                    })

        return results

    def categories_from_vistudio_v1(self):
        """
        categories_from_vistudio_v1
        :return:
        """
        merged_labels = merge_labels(self._labels, self.merge_labels)
        return [{'id': int(k), 'name': v} for k, v in sorted(merged_labels.items(), key=lambda item: int(item[0]))]

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source: DataFrame
        :return: DataFrame
        """
        images = self.images_from_vistudio_v1(source=source)
        annotations = self.annotations_from_vistudio_v1(source=source)
        results = [{
            "images": images,
            "annotations": annotations,
            "categories": []
        }]
        return pd.DataFrame(results)

    def merge(self, rows: DataFrame) -> DataFrame:
        """
        merge
        :param rows: DataFrame
        :return: DataFrame
        """
        images = rows['images'].sum()
        annotations = rows['annotations'].sum()
        categories = self.categories_from_vistudio_v1()
        results = [{
            "images": images,
            "annotations": annotations,
            "categories": categories,
        }]
        return pd.DataFrame(results)

    def _get_image_uri(self):
        if len(self.data_types) == 2 and "image" in self.data_types and "annotation" in self.data_types:
            image_uri_prefix = os.path.join(self.data_uri, "images")
        else:
            image_uri_prefix = ''
        return image_uri_prefix

    @staticmethod
    def _flat(row: Dict[str, Any], col: str) -> List[Dict[str, Any]]:
        """
         Expand the col column
        :param col:
        :return: List
        """
        # ray.util.pdb.set_trace()
        return row[col]

    def _group_by_image_id(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        group bu image_id
        :param group:
        :return:
        """
        image_id = group["image_id"][0]
        ids = group["id"].tolist()
        annotations = list()
        for i in range(len(ids)):
            id = ids[i]
            bbox = group["bbox"].tolist()[i]
            segmentation = group["segmentation"].tolist()[i]
            rle = {}
            if 'rle' in group:
                rle = group["rle"].tolist()[i]
            seg_arr = []
            if type(segmentation) == list:
                try:
                    seg_arr = np.array(segmentation).flatten()
                except Exception as e:
                    bcelogger.error("flatten_coco_seg err.segmentation={}".format(segmentation), e)
            elif type(segmentation) == dict:
                rle_counts = segmentation.get('counts', None)
                if rle_counts is not None:
                    rle = segmentation

            area = group["area"].tolist()[i]
            cate = group["category_id"].tolist()[i]
            iscrowd = group["iscrowd"].tolist()[i]

            labels = []
            label_name = self.import_labels.get(str(cate))
            if label_name is not None:
                annotation_label_id = self._labels.get(label_name).get("local_name")
                if annotation_label_id is not None:
                    labels.append(
                        {
                            "id": annotation_label_id,
                            "confidence": 1
                        }
                    )

            anno = {
                "id": string.generate_random_string(6),
                "bbox": bbox,
                "segmentation": seg_arr,
                "area": area,
                "iscrowd": iscrowd,
            }
            if len(labels) > 0:
                anno['labels'] = labels
            if rle is not None and len(rle) > 0:
                anno['rle'] = rle
            if self.annotation_set_category == 'Image/OCR':
                ocr = {}
                if "attributes" in group:
                    attributes = group["attributes"].tolist()[i]
                    word = attributes.get("文字", "")
                    ocr['word'] = word
                    ocr['direction'] = ''

                if len(ocr) > 0:
                    anno['ocr'] = ocr
                    anno['quadrangle'] = anno['segmentation']
                    anno.pop('segmentation')
            annotations.append(anno)

        annotation_res = {
            "image_id": image_id,
            "user_id": self.user_id,
            "created_at": time.time_ns(),
            "annotations": [annotations],
            "data_type": "Annotation",
            "annotation_set_id": self.annotation_set_id,
            "task_kind": "Manual",
            "artifact_name": "",
            "job_name": ""
        }
        return pd.DataFrame(annotation_res)

    def _fill_image_info_coco(self, row: Dict[str, Any], image_uri_prefix: str):
        """
        fill coco image info
        :param row:
        :param image_ids:
        :return:
        """
        image_name = os.path.basename(row['file_name'])
        image_dict = {
            "image_name": image_name,
            "image_id": string.generate_md5(image_name),
            "annotation_set_id": self.annotation_set_id,
            "annotation_set_name": self.annotation_set_name,
            "user_id": self.user_id,
            "created_at": time.time_ns(),
            "data_type": 'Image',
            "infer_state": 'UnInfer',
            "file_uri": os.path.join(image_uri_prefix, row['file_name']),
            "org_id": self.org_id,
            "annotation_state": "Annotated"
        }
        if self.tag is not None and len(self.tag) > 0:
            image_dict['tags'] = self.tag
        return image_dict

    @staticmethod
    def _fill_data(row: Dict[str, Any]) -> Dict[str, Any]:
        row["segmentation"] = row.get("segmentation", [])
        row["bbox"] = row.get("bbox", [])
        row["area"] = row.get("area", '')
        row["iscrowd"] = row.get("area", '')

        return row

    def to_vistudio_v1(self, ds: Dataset) -> Dict[str, Dataset]:

        """
        _fit_coco
        :param ds: Dataset
        :return: Dataset
        """
        image_uri_prefix = self._get_image_uri()
        # 展开 images
        image_ds = ds.flat_map(lambda row: self._flat(row=row, col="images"))
        bcelogger.info("import coco flat image.original_image_ds count={}".format(image_ds.count()))

        ori_df = image_ds.to_pandas().drop_duplicates(subset=['file_name'])
        image_drop_duplicates_ds = ray.data.from_pandas(ori_df)
        bcelogger.info(
            "import coco flat image.image_drop_duplicates_ds count={}".format(image_drop_duplicates_ds.count()))

        fill_image_ds = image_drop_duplicates_ds.map(
            lambda row: self._fill_image_info_coco(row=row, image_uri_prefix=image_uri_prefix)
        )

        # 展开 annotations
        annotation_ds_flat = ds.flat_map(lambda row: self._flat(row=row, col="annotations"))
        if len(annotation_ds_flat.take_all()) == 0:
            return {"image_ds": fill_image_ds, "annotation_ds": None}
        annotation_ds = annotation_ds_flat.map(lambda row: self._fill_data(row=row))
        bcelogger.info("import coco flat annotation.origin_annotation_ds count={}".format(annotation_ds.count()))

        # merge image_ds and annotation_ds on annotation_ds.image_id = image_ds.id
        drop_id_annotation_ds = annotation_ds.drop_columns(cols=['id'])
        image_df = image_drop_duplicates_ds.to_pandas()
        annotation_df = drop_id_annotation_ds.to_pandas()
        merged_df = pd.merge(annotation_df, image_df, left_on='image_id', right_on='id')

        bboxes = merged_df['bbox'].tolist()
        segmentation = merged_df['segmentation'].tolist()
        if bboxes is not None:
            normal_bbox_list = [arr.tolist() for arr in bboxes if arr is not None]
            if len(normal_bbox_list) > 0:
                merged_df['bbox'] = normal_bbox_list

        if segmentation is not None:
            normal_segmentation_list = list()
            for seg in segmentation:
                if seg is None:
                    continue
                if type(seg) == list or type(seg) == np.ndarray:
                    normal_segmentation_list.append(seg.tolist())
                elif type(seg) == dict:
                    normal_segmentation_list.append(seg)
            if len(normal_segmentation_list) > 0:
                merged_df['segmentation'] = normal_segmentation_list

        merged_df['image_id'] = merged_df['file_name'].apply(lambda x: string.generate_md5(x))
        merged_df = merged_df.drop(columns=['file_name', 'height', 'width'])

        dropped_annotation_ds = ray.data.from_pandas(merged_df)
        # groupby and map_groups
        group_data = dropped_annotation_ds.groupby("image_id")
        group_anno_ds = group_data.map_groups(lambda g: self._group_by_image_id(g))
        bcelogger.info("import coco flat annotation.final_annotation_ds count={}".format(group_anno_ds.count()))

        df = group_anno_ds.to_pandas()
        df['annotations'] = df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(df))

        bcelogger.info("import coco flat image.final_image_ds count={}".format(fill_image_ds.count()))
        return {"image_ds": fill_image_ds, "annotation_ds": annotation_ds}
