#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   paddleseg_formatter.py
"""
from typing import Union, Dict
from pandas import DataFrame
import numpy as np
import os
import bcelogger
import pandas as pd
import pycocotools.mask as mask_utils

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.util import file


class PaddleSegFormatter(object):
    """
    PaddleSegFormatter
    """

    def __init__(
            self,
            label_index_map: Union[Dict] = dict,
            merge_labels: Union[Dict] = None,
            counter: ImageAnnotationCounter = None
    ):
        self.label_index_map = label_index_map
        self.merge_labels = merge_labels
        self.counter = counter

    @staticmethod
    def _get_bg_mask(source: DataFrame):
        """
        _get_bg_mask
        :param source:
        :return:
        """
        height = source['height'][0]
        width = source['width'][0]
        image_mask = np.zeros(shape=(height, width), dtype=np.uint8)
        return image_mask

    def mask_from_vistudio_v1(self, source: DataFrame):
        """
        Convert annotations from Vistudio to Mask.
        """
        height = source['height'][0]
        width = source['width'][0]
        annotations = source['annotations'][0]
        image_mask = np.zeros(shape=(height, width), dtype=np.uint8)

        for annotation in annotations:
            labels = annotation['labels']
            for label in labels:
                label_id = label['id']
                if self.merge_labels is not None and label_id in self.merge_labels:
                    label_id = self.merge_labels[label_id]
                index_info = self.label_index_map.get(label_id)
                if index_info is None:
                    bcelogger.warning("label_id: {} not found".format(label_id))
                    continue
                rle = annotation.get('rle', None)
                if rle is not None:
                    rle_obj = mask_utils.frPyObjects(rle, height, width)
                    mask = mask_utils.decode(rle_obj)
                    index = mask == 1
                    image_mask[index] = index_info['index']
                else:
                    polygon = annotation.get('segmentation', None)
                    if polygon is None or len(polygon) < 6:
                        continue
                    polygon_obj = mask_utils.frPyObjects([polygon], height, width)
                    mask = mask_utils.decode(mask_utils.merge(polygon_obj))
                    index = mask == 1
                    image_mask[index] = index_info['index']
            self.counter.add_annotation_count.remote()
        return image_mask

    def images_from_vistudio_v1(self, source: DataFrame) -> list():
        """
        images_from_vistudio_v1
        :param source:
        :return:
        """
        images = list()
        for source_index, source_row in source.iterrows():
            file_uri = source_row['file_uri']
            total_annotations = source_row.get('annotations')
            annotation_state = source_row.get('annotation_state')
            bcelogger.info(f"file_uri:{file_uri}, annotation_status:{annotation_state}")

            if total_annotations is None:
                continue
            if len(total_annotations) == 0:
                mask_data = {
                    "height": source_row['height'],
                    "width": source_row['width'],
                }
                mask = self._get_bg_mask(source=pd.DataFrame([mask_data]))
                png_file_name = file.change_file_ext(file_name=os.path.basename(file_uri), file_ext=".png")
                image_data = {"image": mask, "image_name": png_file_name}
                images.append(image_data)

            for anno_record in total_annotations:
                if annotation_state != 'Annotated':
                    continue
                task_kind = anno_record['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = anno_record['annotations']
                mask_data = {
                    "height": source_row['height'],
                    "width": source_row['width'],
                    "annotations": [annotations]
                }
                mask = self.mask_from_vistudio_v1(source=pd.DataFrame(mask_data))
                png_file_name = file.change_file_ext(file_name=os.path.basename(file_uri), file_ext=".png") \
                    .replace(" ", "")
                image_data = {"image": mask, "image_name": png_file_name}
                images.append(image_data)

                self.counter.add_image_count.remote()
        return images



    @staticmethod
    def labels_from_vistudio_v1(source: DataFrame) -> list():
        """
        labels_from_vistudio_v1
        :param source:
        :return:
        """
        labels = []
        for source_index, source_row in source.iterrows():
            file_uri = source_row['file_uri']
            png_file_name = file.change_file_ext(file_name=os.path.basename(file_uri), file_ext=".png").replace(" ", "")
            item_value = '{} {}'.format(file_uri, "labels/" + png_file_name)
            item = {"item": item_value}
            labels.append(item)

        return labels

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source:
        :return:
        """
        return pd.DataFrame([
            {
                'label_images': self.images_from_vistudio_v1(source=source),
                'annotations': self.labels_from_vistudio_v1(source=source),
            }
        ])

