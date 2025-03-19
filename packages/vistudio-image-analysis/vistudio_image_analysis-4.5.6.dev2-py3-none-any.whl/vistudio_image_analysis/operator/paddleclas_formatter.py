#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   paddleclas_formatter.py
"""
from typing import Union, Dict
from pandas import DataFrame
import pandas as pd

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class PaddleClasFormatter(object):
    """
    PaddleClasFormatter
    """

    def __init__(
            self,
            label_index_map: Union[Dict] = dict,
            merge_labels: Union[Dict] = None,
            counter: ImageAnnotationCounter = None,
    ):
        self.label_index_map = label_index_map
        self.merge_labels = merge_labels
        self.counter = counter

    def from_vistudio_v1(self, source: DataFrame) -> DataFrame:
        """
        from_vistudio_v1
        :param source: DataFrame
        :return: DataFrame
        """
        annotation_list = []

        for source_index, source_row in source.iterrows():
            total_annotations = source_row.get('annotations')
            if total_annotations is None or len(total_annotations) == 0:
                continue
            file_name = source_row['file_uri']
            self.counter.add_image_count.remote(count=1)
            for anno_record in total_annotations:
                task_kind = anno_record['task_kind']
                if task_kind != "Manual":
                    continue
                annotations = anno_record['annotations']
                if annotations is None or len(annotations) == 0:
                    continue
                for annotation in annotations:
                    self.counter.add_annotation_count.remote()
                    labels = annotation['labels']
                    for label in labels:
                        label_id = label['id']
                        if self.merge_labels is not None and label_id in self.merge_labels:
                            label_id = self.merge_labels[label_id]

                        index_info = self.label_index_map.get(label_id)
                        if index_info is None:
                            continue

                        annotation_list.append(f"{file_name} {index_info['index']}")

        item = {"item": annotation_list}

        return pd.DataFrame(item)
