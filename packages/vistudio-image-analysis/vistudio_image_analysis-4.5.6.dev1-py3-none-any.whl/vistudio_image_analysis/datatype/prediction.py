# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
prediction.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/5 7:18 下午
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass
import json


class Segmentation(BaseModel):
    """
    Segmentation class
    """
    data: List[float] = Field(default_factory=list)

    def to_json(self) -> str:
        """
        Convert to json string
        """
        return self.json()

    @staticmethod
    def from_json(data: str) -> "Segmentation":
        """
        Convert from json string
        """
        return Segmentation.parse_raw(data)


@dataclass
class BBox:
    """
    Bounding box class
    """
    left: float
    top: float
    width: float
    height: float

    def is_overlap(self, other: "BBox") -> bool:
        """
        is_overlap
        """
        return not (
                self.left > other.left + other.width or
                other.left > self.left + self.width or
                self.top > other.top + other.height or
                other.top > self.top + self.height
        )


class Keypoint(BaseModel):
    """
    KeyPoint class
    """
    point: List[float]  # x, y
    confidence: float


class OCR(BaseModel):
    """
    OCR class
    """
    word: Optional[str]
    direction: Optional[str]
    confidence: Optional[float]


class Category(BaseModel):
    """
    Category class
    """
    id: str
    class_id: Optional[str]
    name: str
    confidence: float
    super_category: Optional[str]
    all_probs: Optional[List[float]]


class Prediction(BaseModel):
    """
    Prediction class
    """
    bbox: Optional[List[float]]  # [x, y, w, h]
    quadrangle: Optional[List[float]]  # [x1, y1, x2, y2, ...] (Clockwise or counterclockwise)
    key_points: Optional[List[Keypoint]]
    confidence: Optional[float]
    segmentation: Optional[List[float]]
    polygon: Optional[List[List[float]]]
    area: Optional[float]
    ocr: Optional[OCR]
    features: Optional[List[float]]
    bbox_id: Optional[int]
    track_id: Optional[int]
    categories: Optional[List[Category]]

    def get_bbox(self) -> BBox:
        """
        get_bbox
        """
        return BBox(
            left=self.bbox[0],
            top=self.bbox[1],
            width=self.bbox[2],
            height=self.bbox[3]
        )

    def to_json(self) -> str:
        """
        Convert to json string
        """
        return self.json()

    @staticmethod
    def from_json(data: str) -> "Prediction":
        """
        Convert from json string
        """
        return Prediction.parse_raw(data)


class PredictionList(BaseModel):
    """
    PredictionList class
    """
    predictions: List[Prediction] = Field(default_factory=list)

    def to_json(self) -> str:
        """
        Convert to json string
        """
        return self.json()

    @staticmethod
    def from_json(data: str) -> "PredictionList":
        """
        Convert from json string
        """
        return PredictionList.parse_raw(data)
