#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   annotation.py
"""
from typing import List
import numpy as np
import sys
from pycocotools import mask as maskUtils


def rle_area(rle):
    """
    计算rle的面积
    params:  rle: size[h, w]  counts: [0的个数, 1的个数, ……] (按列编码)
    """
    compressed_rle = maskUtils.frPyObjects(rle, rle.get('size')[0], rle.get('size')[1])
    return maskUtils.area(compressed_rle)


def rle_bbox(rle):
    """
    计算rle的外接框
    params:  rle: size[h, w]  counts: [0的个数, 1的个数, ……] (按列编码)
    return:  bbox: xmin, ymin, xmax, ymax
    """
    compressed_rle = maskUtils.frPyObjects(rle, rle.get('size')[0], rle.get('size')[1])
    return maskUtils.toBbox(compressed_rle)


def rle_to_mask(rle):
    """
    convert rle to mask
    """
    compressed_rle = maskUtils.frPyObjects(rle, rle.get('size')[0], rle.get('size')[1])
    return maskUtils.decode(compressed_rle)


def mask_to_rle(img):
    '''
    Args:
        -img: numpy array, 1 - mask, 0 - background, mask位置的值可以不是1，但必须完全相同
    Returns:
        -rle.txt
    该函数返回单个图片的标注信息，所有的标注视为整体，因此适用于单个标注的图片
    例如: img  1 0 0 1 1 1 0      rle.txt 0 1 2 3 1
    '''
    # 为了按列扫描，需要先转置一下
    img = img.T
    pixels = img.flatten()
    pixels = np.concatenate([[0], pixels, [0]])
    # 获取像素变化的坐标
    runs = np.where(pixels[1:] != pixels[:-1])[0]
    # 计算0 1 连续出现的数量
    runs = np.concatenate([[0], runs, [pixels.shape[0] - 2]])
    runs[1:] -= runs[:-1]
    # 如果最后一位为0， 去除
    if runs[-1] == 0:
        runs = runs[:-1]
    return runs[1:].tolist()


def rle2mask(rle, gray=255):
    """
    计算rle的mask
    params:
        rle: size[h, w]  counts: [0的个数, 1的个数, ……] (按行编码)
    Returns:
        -mask: rle对应的mask
    """
    height, width = rle["size"]
    mask = np.zeros(height * width).astype(np.uint8)
    start = 0
    pixel = 0
    for num in rle["counts"]:
        stop = start + num
        mask[start:stop] = pixel
        pixel = gray - pixel
        start = stop
    return mask.reshape(height, width)


def polygon_area(polygon: List[float]) -> float:
    """
    计算polygon的面积
    """
    x, y = np.array(polygon[::2]), np.array(polygon[1::2])
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def polygon_bbox_with_wh(polygon):
    """
    获取polygon的外接框。
    params:  polygon: 多边形。
    return:  bbox: 边界框 x, y, w, h
    """
    ymin, ymax, xmin, xmax = polygon_bbox(polygon)
    return xmin, ymin, xmax - xmin, ymax - ymin


def polygon_bbox(polygon):
    """
    获取polygon的外接框
    """
    xmin, ymin = sys.maxsize, sys.maxsize
    xmax, ymax = 0, 0
    for i in range(0, len(polygon), 2):
        x, y = int(polygon[i]), int(polygon[i + 1])
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)
    return ymin, ymax, xmin, xmax


def bbox_overlaps(bboxes1, bboxes2, mode='iou'):
    """Calculate the ious between each bbox of bboxes1 and bboxes2.

    Args:
        bboxes1(ndarray): shape (n, 4)
        bboxes2(ndarray): shape (k, 4)
        mode(str): iou (intersection over union) or iof (intersection
            over foreground)

    Returns:
        ious(ndarray): shape (n, k)
    """

    assert mode in ['iou', 'iof']

    bboxes1 = bboxes1.astype(np.float32)
    bboxes2 = bboxes2.astype(np.float32)
    rows = bboxes1.shape[0]
    cols = bboxes2.shape[0]
    ious = np.zeros((rows, cols), dtype=np.float32)
    if rows * cols == 0:
        return ious
    exchange = False
    if bboxes1.shape[0] > bboxes2.shape[0]:
        bboxes1, bboxes2 = bboxes2, bboxes1
        ious = np.zeros((cols, rows), dtype=np.float32)
        exchange = True
    area1 = (bboxes1[:, 2] - bboxes1[:, 0] + 1) * (
            bboxes1[:, 3] - bboxes1[:, 1] + 1)
    area2 = (bboxes2[:, 2] - bboxes2[:, 0] + 1) * (
            bboxes2[:, 3] - bboxes2[:, 1] + 1)
    for i in range(bboxes1.shape[0]):
        x_start = np.maximum(bboxes1[i, 0], bboxes2[:, 0])
        y_start = np.maximum(bboxes1[i, 1], bboxes2[:, 1])
        x_end = np.minimum(bboxes1[i, 2], bboxes2[:, 2])
        y_end = np.minimum(bboxes1[i, 3], bboxes2[:, 3])
        overlap = np.maximum(x_end - x_start + 1, 0) * np.maximum(
            y_end - y_start + 1, 0)
        if mode == 'iou':
            union = area1[i] + area2 - overlap
        else:
            union = area2 if not exchange else area1[i]
        ious[i, :] = overlap / union
    if exchange:
        ious = ious.T
    return ious


def convert_1d_to_2d_pairs(array_1d):
    """
    convert_1d_to_2d_pairs
    """
    if len(array_1d) % 2 != 0:
        raise ValueError("The length of the array must be even to form pairs.")

    # 将一维数组转换为二维数组，每两个数一组
    array_2d = np.array(array_1d).reshape((-1, 2))
    return array_2d


def convert_cvat_bbox_rle(cvt_rle_counts: list(), img_height, img_width, x_min, y_min, box_width, box_height):
    """
    convert_cvat_bbox_rle
    """
    mask = np.zeros((img_height, img_width))
    rle = {
        'counts': cvt_rle_counts,
        'size': [box_height, box_width]
    }
    mask[y_min: y_min + box_height, x_min:x_min + box_width] = rle2mask(rle=rle)
    return mask_to_rle(mask)
