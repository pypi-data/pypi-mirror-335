#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   swift_preprocessor.py
"""
from ray.data.preprocessor import Preprocessor

from vistudio_image_analysis.operator.swift_formatter import SWIFTFormatter
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter


class SWIFTFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert vistudio_v1 to ms-swift
    """
    def __init__(
        self,
        counter: ImageAnnotationCounter = None
    ):
        self.counter = counter

    def _fit(self, ds: "Dataset") -> "Preprocessor":

        operator = SWIFTFormatter(counter=self.counter)
        format_ds = operator.from_vistudio_v1(ds)

        self.stats_ = format_ds
        return self



