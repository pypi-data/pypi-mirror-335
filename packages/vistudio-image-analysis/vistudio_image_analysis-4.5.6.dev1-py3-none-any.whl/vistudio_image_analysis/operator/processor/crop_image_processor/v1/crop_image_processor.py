"""
mongo_datasource.py
Authors: chujianfei
Date:    2024/12/10 8:59 下午
"""
import base64
import json
from typing import Optional, Dict, List
from urllib.parse import urlparse

import mysql.connector

import bcelogger
import pandas as pd
import ray
import numpy as np
import cv2
from pygraphv1.client.graph_api_operator import Operator
from ray.air.util.data_batch_conversion import BatchFormat
from ray.data import Dataset, read_datasource

from vistudio_image_analysis.config.config import Config
from vistudio_image_analysis.operator.processor.processor import Processor
from vistudio_image_analysis.util import string, polygon
from vistudio_image_analysis.operator.base_operator import OPERATOR


@OPERATOR.register_module(name="CropImageProcessorV1", version="1")
class CropImageProcessorV1(Processor):
    """
    MultiModalProcessorV1
    """

    def __init__(self,
                 config: Config,  # 公共参数
                 meta: Operator = None,
                 ):
        super().__init__(config=config, meta=meta)

        # TODO Metric Tricker

    def execute(self, ds_list: List[Dataset]) -> Optional[Dict[str, Dataset]]:
        """
        execute
        """

        return {self.meta.outputs[0].name: ds_list[0].map_batches(
            self._transform_pandas, batch_format=BatchFormat.PANDAS
        )}

    def _transform_pandas(self, df: "pd.DataFrame") -> "pd.DataFrame":
        """
        transform_pandas
        """
        crop_image_list = list()
        for source_index, source_row in df.iterrows():
            point_list = []
            bboxes = source_row["bboxes"]
            image_uri = source_row["image_uri"]
            image_name = image_uri.split("/")[-1]
            image_list = self._crop_image(image=source_row['image'],
                                          image_name=image_name,
                                          bboxes=bboxes,
                                          width_factor=self.meta.get_property("width_factor").value,
                                          height_factor=self.meta.get_property("height_factor").value)
            crop_image_list.append(image_list)
        return pd.DataFrame(crop_image_list)

    def _crop_image(self,
                    image: np.ndarray,
                    image_name: str,
                    bboxes: list(),
                    width_factor=None,
                    height_factor=None):
        crop_image_list = []
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # 检查图像读取是否成功
        if image is None:
            raise ValueError(f"cv2 couldn't load image file at path '{image_name}'.")

        h, w, _ = image.shape  # 获取图像高度、宽度和通道数

        def bbox_to_points(bbox):
            """
            根据 bbox 计算四个顶点坐标
            :param bbox: [x_min, y_min, width, height]
            :return: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] 四个顶点坐标
            """
            x_min, y_min, width, height = bbox
            points = [x_min, y_min, x_min + width, y_min,
                      x_min + width, y_min + height, x_min, y_min + height
                      ]
            return points

        point = bbox_to_points(bboxes)
        print("image quadrangle{} type:{}".format(point, type(point)))
        point_2d = polygon.convert_1d_to_2d_pairs(point)
        img_suffix = string.generate_md5(str(point))  # 旋转裁剪图像
        cropped_image = self._get_rotate_crop_image(img=image,
                                                    points=np.float32(point_2d),
                                                    image_name=image_name,
                                                    width_factor=width_factor,
                                                    height_factor=height_factor)
        cropped_image_name = image_name.split(".")[0] + "_" + str(img_suffix) + ".jpg"
        array = np.array(cropped_image)
        image_id = string.generate_md5(cropped_image_name)
        item = {
            "image": [array],
            "image_name": cropped_image_name,
            "bboxes": bboxes
        }
        crop_image_list.append(item)

        return crop_image_list

    @staticmethod
    def get_rotate_crop_image(img, points, image_name=None, width_factor=None, height_factor=None):
        '''
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        '''
        assert len(points) == 4, f"{image_name} shape of points must be 4*2"
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3])))

        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2])))

        if width_factor is not None:
            img_crop_width = int(img_crop_width * width_factor)
        if height_factor is not None:
            img_crop_height = int(img_crop_height * height_factor)

        pts_std = np.float32([[0, 0], [img_crop_width, 0],
                              [img_crop_width, img_crop_height],
                              [0, img_crop_height]])
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M, (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC)
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        # if dst_img_height * 1.0 / dst_img_width >= 1.5:
        #     dst_img = np.rot90(dst_img)
        return dst_img
