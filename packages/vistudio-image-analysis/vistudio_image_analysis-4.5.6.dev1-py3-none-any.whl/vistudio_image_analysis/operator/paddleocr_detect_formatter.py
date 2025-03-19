#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   paddleocr_detect_formatter.py
"""
from typing import Union, Dict, Any
from pandas import DataFrame
import pandas as pd

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.util import polygon


class PaddleOCRDetectFormatter(object):
    """
    ImageNetFormatter
    """

    def __init__(self, counter: ImageAnnotationCounter = None):
        super().__init__()
        self.counter = counter

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source: DataFrame
        :return: DataFrame
        """
        paddleocr_detects = list()
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
                annotation_list = list()
                for annotation in annotations:

                    ocr = annotation.get("ocr", None)
                    if ocr is None:
                        continue
                    self.counter.add_annotation_count.remote()
                    word = ocr.get("word")
                    seg = annotation.get("quadrangle", None)
                    seg_2d = polygon.convert_1d_to_2d_pairs(seg)
                    detect_anno = {
                        "transcription": word,
                        "points": seg_2d,
                    }
                    annotation_list.append(detect_anno)

                paddleocr_detects.append(("{}\t{}").format(file_name, annotation_list))

        item = {"item": paddleocr_detects}
        return pd.DataFrame(item)

    def merge(self, rows: DataFrame) -> DataFrame:
        """
        merge
        :param rows: DataFrame
        :return: DataFrame
        """
        item_list = rows['item'].to_list()
        return pd.DataFrame(item_list)
