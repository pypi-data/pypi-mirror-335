# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
Vistudio Spec
"""
import re
from typing import List, Tuple, Optional, Dict
import pyarrow as pa
import pandas as pd
from pydantic import BaseModel


class Label(BaseModel):
    """Label"""
    id: int
    name: str
    confidence: float
    parent_id: str

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Label to pyarrow data type"""
        return pa.struct([
            pa.field("id", pa.string(), nullable=True),
            pa.field("name", pa.string(), nullable=True),
            pa.field("confidence", pa.float64(), nullable=True),
            pa.field("parent_id", pa.string(), nullable=True),
        ])


class OCR(BaseModel):
    """OCR"""
    word: str
    direction: str
    confidence: float

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """OCR to pyarrow data type"""
        return pa.struct([
            pa.field("direction", pa.string(), nullable=True),
            pa.field("confidence", pa.float32(), nullable=True),
            pa.field("word", pa.string(), nullable=True)
        ])


class RLE(BaseModel):
    """RLE"""
    counts: List[float]
    size: Tuple[float, float]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """RLE to pyarrow data type"""
        return pa.struct([
            pa.field("counts", pa.list_(pa.int32())),
            pa.field("size", pa.list_(pa.int32()))
        ])


class Instruction(BaseModel):
    """
    Instruction
    """
    name: str
    dataType: str
    kind: str

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Instruction to pyarrow data type"""

        return pa.struct([
            pa.field('name', pa.string()),
            pa.field('dataType', pa.string()),
            pa.field('kind', pa.string())
        ])


class Annotation(BaseModel):
    """Annotation"""
    id: str
    bbox: List[float]
    segmentation: List[float]
    quadrangle: List[float]
    rle: RLE
    area: float
    labels: List[Label]
    iscrowd: int
    ocr: OCR

    question_id: int
    question: str
    answer: str
    prompt: str
    instructions: List[Instruction]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Annotation to pyarrow data type"""
        return pa.struct([
            pa.field("id", pa.string()),
            pa.field("bbox", pa.list_(pa.float32())),
            pa.field("segmentation", pa.list_(pa.float32()), nullable=True),
            pa.field("quadrangle", pa.list_(pa.float32()), nullable=True),
            pa.field("rle", RLE.to_pyarrow_schema(), nullable=True),
            pa.field("area", pa.float32()),
            pa.field("labels", pa.list_(Label.to_pyarrow_schema())),
            pa.field("ocr", OCR.to_pyarrow_schema(), nullable=True),
            pa.field("question_id", pa.int64(), nullable=True),
            pa.field("question", pa.string(), nullable=True),
            pa.field("answer", pa.string(), nullable=True),
            pa.field("prompt", pa.string(), nullable=True),
            pa.field("instructions", pa.list_(Instruction.to_pyarrow_schema()), nullable=True),
        ])


class InferConfig(BaseModel):
    """
    InferConfig
    """
    temperature: float
    top_p: float
    repetition_penalty: float

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """InferConfig to pyarrow data type"""

        return pa.struct([
            pa.field('temperature', pa.float32()),
            pa.field('top_p', pa.float32()),
            pa.field('repetition_penalty', pa.float32())
        ])


class Annotations(BaseModel):
    """Annotations"""
    image_id: str
    annotations: List[Annotation]
    user_id: str
    created_at: int
    data_type: str
    annotation_set_id: str
    task_kind: str
    artifact_name: str
    image_created_at: int
    updated_at: int
    job_name: str
    job_created_at: int
    infer_config: InferConfig

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Annotations to pyarrow data type"""

        return pa.struct([
            pa.field('image_id', pa.string()),
            pa.field('user_id', pa.string(), nullable=True),
            pa.field('created_at', pa.int64()),
            pa.field('annotations', pa.list_(Annotation.to_pyarrow_schema())),
            pa.field('data_type', pa.string()),
            pa.field('annotation_set_id', pa.string()),
            pa.field('task_kind', pa.string()),
            pa.field('artifact_name', pa.string()),
            pa.field('image_created_at', pa.int64(), nullable=True),
            pa.field('updated_at', pa.int64(), nullable=True),
            pa.field('job_name', pa.string()),
            pa.field('job_created_at', pa.int64(), nullable=True),
            pa.field('infer_config', InferConfig.to_pyarrow_schema(), nullable=True)
        ])


class ImageState(BaseModel):
    """
    ImageState
    """
    webp_state: str
    thumbnail_state: str

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """ImageState to pyarrow data type"""

        return pa.struct([
            pa.field('webp_state', pa.string()),
            pa.field('thumbnail_state', pa.string())
        ])


class Image(BaseModel):
    """Image"""
    image_id: str
    image_name: str
    file_uri: str
    width: int
    height: int
    annotation_set_id: str
    annotation_set_name: str
    user_id: str
    created_at: int
    data_type: str
    org_id: str
    updated_at: int
    annotation_state: str
    tags: dict
    image_state: ImageState
    infer_state: str

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """
        Image to pyarrow data type
        这里tags 注释掉了，因为pymongoarrow 不支持pa.map_, 如果设置成pa.dictionary，要求k 必须是 integer ，所以无法兼容
        """
        return pa.schema([
            pa.field("width", pa.int32(), nullable=True),
            pa.field("height", pa.int32(), nullable=True),
            pa.field("image_id", pa.string()),
            pa.field("image_name", pa.string()),
            pa.field("annotation_set_id", pa.string()),
            pa.field("annotation_set_name", pa.string()),
            pa.field("user_id", pa.string(), nullable=True),
            pa.field("created_at", pa.int64()),
            pa.field("data_type", pa.string()),
            pa.field("file_uri", pa.string()),
            pa.field("org_id", pa.string()),
            pa.field("updated_at", pa.int64(), nullable=True),
            pa.field("annotation_state", pa.string(), nullable=True),
            pa.field("tags", pa.map_(pa.string(), pa.string()), nullable=True),
            pa.field("image_state", ImageState.to_pyarrow_schema(), nullable=True),
            pa.field("infer_state", pa.string(), nullable=True),
        ])


class Vistudio(BaseModel):
    """
    Vistudio
    """
    image_id: str
    image_name: str
    file_uri: str
    width: int
    height: int
    annotation_set_id: str
    annotation_set_name: str
    user_id: str
    created_at: int
    data_type: str
    org_id: str
    updated_at: int
    annotation_state: str
    tags: Optional[dict]
    image_state: ImageState
    annotations: List[Annotations]

    @classmethod
    def to_pyarrow_schema(cls) -> pa.DataType:
        """Vistudio to pyarrow data type"""
        return pa.schema([
            pa.field("width", pa.int32()),
            pa.field("height", pa.int32()),
            pa.field("image_id", pa.string()),
            pa.field("image_name", pa.string()),
            pa.field("annotation_set_id", pa.string()),
            pa.field("annotation_set_name", pa.string()),
            pa.field("user_id", pa.string(), nullable=True),
            pa.field("created_at", pa.int64()),
            pa.field("data_type", pa.string()),
            pa.field("file_uri", pa.string()),
            pa.field("org_id", pa.string()),
            pa.field("tags", pa.map_(pa.string(), pa.string()), nullable=True),  # tags 是一个键值对的 map 类型
            pa.field("image_state", ImageState.to_pyarrow_schema(), nullable=True),
            pa.field("updated_at", pa.int64(), nullable=True),
            pa.field("annotation_state", pa.string(), nullable=True),
            pa.field("annotations", pa.list_(Annotations.to_pyarrow_schema()))
        ])


def convert_dataframe(df, schema):
    """
    convert_dataframe
    """
    for field in schema:
        column = field.name
        dtype = field.type
        if column not in df.columns:
            df[column] = pd.NA  # 添加缺失字段并设置为 NA

    return df


if __name__ == "__main__":
    print(Vistudio.to_pyarrow_schema())
