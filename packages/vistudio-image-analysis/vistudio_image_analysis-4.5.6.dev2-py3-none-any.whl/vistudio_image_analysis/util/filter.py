#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   filter.py
"""

from typing import Union, Dict, Any, List
from pandas import DataFrame
import pandas as pd


def _filter_image_fn(row: Dict[str, Any], existed_images: set()) -> bool:
    """
    _filter_image_fn
    :param row:
    :param existed_images:
    :return:
    """
    if row['data_type'] == 'Annotation':
        return True
    elif row['data_type'] == 'Image':
        return row['image_id'] not in existed_images


def filter_image(source: "Dataset", existed_images: set()) -> "Dataset":
    """
    filter ds not in filter_list
    :param source:
    :param col:
    :param filter_list:
    :return:
    """
    if existed_images is None or len(existed_images) == 0:
        return source

    return source.filter(lambda x: _filter_image_fn(row=x, existed_images=existed_images))


def _filter_image_by_artifact_name_fn(row: Dict[str, Any], artifact_name: str):
    is_filter = True
    for image_annotation in row.get('annotations', []):
        task_kind = image_annotation['task_kind']
        if task_kind == "Manual":
            continue

        annotation_artifact_name = image_annotation['artifact_name']
        if annotation_artifact_name == artifact_name:
            is_filter = False
            break

    return is_filter


def filter_image_by_artifact_name(source: "Dataset", artifact_name: str) -> "Dataset":
    """
    filter ds not in filter_list
    :param source:
    :param col:
    :param filter_list:
    :return:
    """

    return source.filter(lambda x: _filter_image_by_artifact_name_fn(row=x, artifact_name=artifact_name))


def _filter_annotation_fn(row: Dict[str, Any], existed_annotations: set()):
    """
    _filter_annotation_fn
    :param row:
    :param existed_annotations:
    :return:
    """
    if row['data_type'] == 'Image':
        return True
    elif row['data_type'] == 'Annotation':
        return row['image_id'] not in existed_annotations


def filter_annotation(source: "Dataset", existed_annotations: set()) -> "Dataset":
    """
    filter ds not in filter_list
    :param source:
    :param existed_annotations:
    :return:
    """
    if existed_annotations is None or len(existed_annotations) == 0:
        return source

    return source.filter(lambda x: _filter_annotation_fn(row=x, existed_annotations=existed_annotations))


def filter_annotation_df(source: DataFrame, existed_annotations: set()) -> DataFrame:
    """
    filter ds not in filter_list
    :param source:
    :param existed_annotations:
    :return:
    """
    if existed_annotations is None or len(existed_annotations) == 0:
        return source

    anno_filtered_df = source[(~source['image_id'].isin(existed_annotations))]
    return anno_filtered_df


def drop_duplicates(source: DataFrame, cols: List[str], inplace: bool = False) -> DataFrame:
    """
    drop duplicate rows by cols
    :param source:
    :param cols:
    :return:
    """
    return source.drop_duplicates(subset=cols, inplace=inplace)
