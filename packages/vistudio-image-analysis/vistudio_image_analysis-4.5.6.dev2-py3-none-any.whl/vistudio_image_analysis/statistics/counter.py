#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
counter.py
"""
import ray

@ray.remote
class ImageAnnotationCounter:
    """
    ImageAnnotationCounter
    """
    def __init__(self):
        self.image_count = 0
        self.annotation_count = 0

    def add_image_count(self, count: int = 1):
        """
        增加图片数量。
        """
        self.image_count += count
        return self.image_count

    def add_annotation_count(self, count: int = 1):
        """
        增加标注数量。
        """
        self.annotation_count += count
        return self.annotation_count

    def get_image_count(self):
        """
        获取图片数量
        """
        return self.image_count

    def get_annotation_count(self):
        """
        获取标注数量
        """
        return self.annotation_count

    def get_counts(self):
        """
        获取当前图片数量和标注数量。
        """
        return {
            "image_count": self.image_count,
            "annotation_count": self.annotation_count
        }
