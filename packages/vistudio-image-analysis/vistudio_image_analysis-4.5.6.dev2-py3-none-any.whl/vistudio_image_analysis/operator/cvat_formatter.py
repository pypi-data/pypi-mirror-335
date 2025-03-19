#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   imagenet_formatter.py
"""
import os.path
import time
from typing import Union, Dict, Any
from ray.data import DataContext, Dataset

from vistudio_image_analysis.util import string, polygon
from vistudio_image_analysis.util.annotation import convert_cvat_bbox_rle

ctx = DataContext.get_current()
ctx.enable_tensor_extension_casting = False


class CVATFormatter(object):
    """
    CVATFormatter
    """

    def __init__(self,
                 labels: Union[Dict] = dict,
                 annotation_set_id: str = None,
                 annotation_set_name: str = None,
                 user_id: str = None,
                 org_id: str = None,
                 data_uri: str = None,
                 tag: Union[Dict] = None
                 ):
        self._labels = labels
        self.annotation_set_id = annotation_set_id
        self.annotation_set_name = annotation_set_name
        self.user_id = user_id
        self.org_id = org_id
        self.data_uri = data_uri
        self.tag = tag

    def _fill_image_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_image_info_vistudio
        :param row: dict
        :return: dict
        """
        image_name = row['name']
        item = dict()
        item['file_uri'] = os.path.join(self.data_uri, "images", image_name)
        item['width'] = 0
        item['height'] = 0
        item['image_name'] = image_name
        item['image_id'] = string.generate_md5(image_name)
        item['annotation_set_id'] = self.annotation_set_id
        item['annotation_set_name'] = self.annotation_set_name
        item['user_id'] = self.user_id
        item['org_id'] = self.org_id
        item['created_at'] = time.time_ns()
        item['data_type'] = 'Image'
        item['infer_state'] = 'UnInfer'
        item['annotation_state'] = 'Annotated'
        if self.tag is not None and len(self.tag) > 0:
            item['tags'] = self.tag
        return item

    def _fill_annotation_info_vistudio(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        _fill_annotation_info_vistudio
        :param row:
        :return:
        """
        image_name = row['name']
        item = dict()
        item['image_id'] = string.generate_md5(image_name)
        item['user_id'] = self.user_id
        item['created_at'] = time.time_ns()
        item['data_type'] = 'Annotation'
        item['annotation_set_id'] = self.annotation_set_id
        item['task_kind'] = "Manual"
        item['artifact_name'] = ""
        item['job_name'] = ""
        item['annotations'] = []
        annotations = list()
        annotations_cvat = row.get('annotations', [])
        if annotations_cvat is None or len(annotations_cvat) == 0:
            return item
        for annotation_cvat in annotations_cvat:
            box_cvat_dict = annotation_cvat.get("box", None)
            polygon_cvat_dict = annotation_cvat.get("polygon", None)
            mask_cvat = annotation_cvat.get("mask", None)
            polyline_cvat_dict = annotation_cvat.get("polyline", None)
            points = annotation_cvat.get("points", None)
            tag_dict = annotation_cvat.get("tag", None)
            if box_cvat_dict is not None:
                bbox = polygon.calculate_bbox(box_cvat_dict)
                seg = polygon.bbox_to_polygon(box_cvat_dict)
                area = polygon.compute_polygon_area(polygon.bbox_to_polygon_2d_array(box_cvat_dict))
                label_name = box_cvat_dict.get("label")
                label_info = self._labels.get(label_name)
                if label_info is None:
                    continue
                label_id = label_info.get("local_name")
                label = {
                    "id": str(label_id)
                }
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "area": area,
                    "segmentation": seg,
                    "bbox": bbox,
                    "labels": [label],

                })
            elif polygon_cvat_dict is not None:
                seg = polygon.convert_vertices_to_1d_array(polygon_cvat_dict.get('points', ''))
                polygon_2d = polygon.convert_vertices_to_2d_array(polygon_cvat_dict.get('points', ''))
                bbox = polygon.polygon_to_bbox_cv2(polygon_2d)
                area = polygon.compute_polygon_area(polygon_2d)
                label_name = polygon_cvat_dict.get("label")
                label_info = self._labels.get(label_name)
                if label_info is None:
                    continue
                label_id = label_info.get("local_name")
                label = {
                    "id": str(label_id)
                }
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "area": area,
                    "segmentation": seg,
                    "bbox": bbox,
                    "labels": [label],

                })

            elif mask_cvat is not None:
                rle_str = mask_cvat.get('rle', '')
                left = mask_cvat.get('left', '0')
                top = mask_cvat.get('top', '0')
                width = mask_cvat.get('width', '0')
                height = mask_cvat.get('height', '0')
                rle_list = [int(x.strip()) for x in rle_str.split(',')]
                rle_counts = list()
                if len(rle_list) > 0:
                    rle_counts = convert_cvat_bbox_rle(cvt_rle_counts=rle_list,
                                                       img_height=int(row['height']),
                                                       img_width=int(row['width']),
                                                       x_min=int(left),
                                                       y_min=int(top),
                                                       box_width=int(width),
                                                       box_height=int(height))
                size = [int(row['height']), int(row['width']),]
                bbox = [int(left), int(top), int(width), int(height)]
                rle = {
                    "counts": rle_counts,
                    'size': size
                }
                label_name = mask_cvat.get("label")
                label_info = self._labels.get(label_name)
                if label_info is None:
                    continue
                label_id = label_info.get("local_name")
                label = {
                    "id": str(label_id)
                }
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "bbox": bbox,
                    "labels": [label],
                    "rle": rle

                })
            elif polyline_cvat_dict is not None:
                seg = polygon.convert_vertices_to_1d_array(polyline_cvat_dict.get('points', ''))
                polyline_2d = polygon.convert_vertices_to_2d_array(polyline_cvat_dict.get('points', ''))
                bbox = polygon.polygon_to_bbox_cv2(polyline_2d)
                area = polygon.compute_polygon_area(polyline_2d)
                label_name = polyline_cvat_dict.get("label")
                label_info = self._labels.get(label_name)
                if label_info is None:
                    continue
                label_id = label_info.get("local_name")
                label = {
                    "id": str(label_id)
                }
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "area": area,
                    "segmentation": seg,
                    "bbox": bbox,
                    "labels": [label],

                })
            elif tag_dict is not None:
                label_name = tag_dict.get('label')
                label_info = self._labels.get(label_name)
                if label_info is None:
                    continue
                label_id = label_info.get("local_name")
                label = {
                    "id": str(label_id)
                }
                annotations.append({
                    "id": string.generate_random_digits(6),
                    "labels": [label],

                })

        item['annotations'] = annotations
        return item

    def to_vistudio_v1(self, ds: Dataset) -> Dict[str, Dataset]:
        """
        to_vistudio_v1
        :param ds:
        :return:
        """
        image_info_ds = ds.flat_map(lambda row: row['images'])
        image_ds = image_info_ds.map(lambda row: self._fill_image_info_vistudio(row=row))
        annotation_ds = image_info_ds.map(lambda row: self._fill_annotation_info_vistudio(row=row))
        return {"image_ds": image_ds, "annotation_ds": annotation_ds}
