#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   paddleseg_formatter.py
"""
from typing import Union, Dict, Any, List
from pandas import DataFrame
import ray.data
import numpy as np
import os
import bcelogger
import pandas as pd
import pycocotools.mask as mask_utils
from ray.data import Dataset

from windmillcomputev1.filesystem import init_py_filesystem

from vistudio_image_analysis.datasink.filename_provider import MultiFilenameProvider
from vistudio_image_analysis.datasink.paddleocr_image_datasink import PaddleOCRImageDatasink
from vistudio_image_analysis.datasource.image_datasource import PaddleOCRRecognImageDatasource
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.util import file, string


class PaddleOCRRecognFormatter(object):
    """
    文本识别
    PaddleOCRRecognFormatter
    """

    def __init__(
            self,
            filesystem: Union[Dict] = dict,
            location: str = None,
            counter: ImageAnnotationCounter = None
    ):

        self._filesystem = filesystem
        self._py_fs = init_py_filesystem(filesystem)
        self.location = location
        self.counter = counter

    def images_from_vistudio_v1(self, source: DataFrame) -> Dataset:
        """
        images_from_vistudio_v1
        :param source:
        :return:
        """
        image_ds_list = list()
        image_ds_first = None
        for source_index, source_row in source.iterrows():
            file_uri = source_row['file_uri']
            annotations_total = source_row.get('annotations')
            annotation_state = source_row.get('annotation_state')
            print("file_uri:{}, annotation_status:{}".format(file_uri,
                                                             annotation_state))
            if annotations_total is None or len(annotations_total) == 0:
                continue

            self.counter.add_image_count.remote()
            segmentations = list()
            for image_annotation in annotations_total:
                if annotation_state != 'Annotated':
                    continue
                task_kind = image_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = image_annotation['annotations']
                if annotations is None or len(annotations) == 0:
                    continue

                for annotation in annotations:
                    seg = annotation.get("quadrangle", None)
                    if seg is None:
                        continue
                    if type(seg) == np.ndarray:
                        seg = seg.tolist()
                    segmentations.append(seg)
                    self.counter.add_annotation_count.remote()

            if len(segmentations) < 0:
                continue
            paddleocr_recogn_datasource = PaddleOCRRecognImageDatasource(paths=file_uri,
                                                                         filesystem=self._py_fs,
                                                                         points=segmentations)
            image_ds = ray.data.read_datasource(datasource=paddleocr_recogn_datasource)
            image_ds_list.append(image_ds)

        if len(image_ds_list) > 0:
            image_ds_first = image_ds_list[0]
            if len(image_ds_list) == 1:
                return image_ds_first
            return image_ds_first.union(image_ds_list[1:])
        return image_ds_first

    def ocr_from_vistudio_v1(self, source: DataFrame) -> DataFrame():
        """
        ocr_from_vistudio_v1
        :param source:
        :return:
        """
        ocr_recogn = []
        for source_index, source_row in source.iterrows():
            file_uri = source_row['file_uri']
            annotations_total = source_row.get('annotations', None)
            if annotations_total is None:
                continue

            for manual_annotation in annotations_total:
                task_kind = manual_annotation['task_kind']
                if task_kind != "Manual":
                    continue

                annotations = manual_annotation.get("annotations", None)
                if annotations is None or len(annotations) == 0:
                    continue

                for annotation in annotations:
                    ocr = annotation.get("ocr", None)
                    if ocr is None:
                        continue
                    seg = annotation.get("quadrangle", None)
                    if seg is None:
                        continue
                    img_suffix = string.generate_md5(str(seg.tolist()))
                    print("txt quadrangle：{} type:{}".format(seg, type(seg)))
                    image_name = file_uri.split("/")[-1]
                    cropped_image_name = image_name.split(".")[0] + "_" + str(img_suffix) + ".jpg"
                    crop_img_file_uri = self.location + "/labels/" + cropped_image_name
                    word = ocr.get("word")
                    item_value = '{}\t{}'.format(crop_img_file_uri, word)
                    item = {"item": item_value}
                    ocr_recogn.append(item)

        return pd.DataFrame(ocr_recogn)

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source:
        :param merge_labels:
        :param location:
        :return:
        """
        image_ds = self.images_from_vistudio_v1(source=source)

        filename_provider = MultiFilenameProvider(is_full_file_name=False)
        bcelogger.info("paddleseg formatter.upload mask.location={}".format(self.location))
        # self._py_fs.create_dir(self.location + "/labels/")
        if image_ds is not None and image_ds.count() > 0:
            datasink = PaddleOCRImageDatasink(
                path=self.location + "/labels/",
                file_format="png",
                column="image",
                filesystem=self._py_fs,
                filename_provider=filename_provider,
                try_create_dir=True

            )
            image_ds.write_datasink(datasink=datasink)

        return self.ocr_from_vistudio_v1(source=source)

    def merge(self, rows: DataFrame) -> DataFrame:
        """
        merge
        :param rows:  DataFrame
        :return: DataFrame
        """
        item_list = rows['item'].to_list()
        return pd.DataFrame(item_list)
