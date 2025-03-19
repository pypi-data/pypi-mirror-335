# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
image_datasource.py
Authors: chujianfei
Date:    2024/3/5 7:18 下午
"""
import io
import logging
import time
from typing import TYPE_CHECKING, Iterator, List, Optional, Tuple, Union

import numpy as np

from ray.data._internal.delegating_block_builder import DelegatingBlockBuilder
from ray.data._internal.util import _check_import
from ray.data.block import Block, BlockMetadata
from ray.data.datasource.file_based_datasource import FileBasedDatasource
from ray.data.datasource.file_meta_provider import DefaultFileMetadataProvider
from ray.util.annotations import DeveloperAPI
import cv2

from vistudio_image_analysis.util import file, polygon, string

if TYPE_CHECKING:
    import pyarrow

logger = logging.getLogger(__name__)

# The default size multiplier for reading image data source.
# This essentially is using image on-disk file size to estimate
# in-memory data size.
IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT = 1

# The lower bound value to estimate image encoding ratio.
IMAGE_ENCODING_RATIO_ESTIMATE_LOWER_BOUND = 0.5


@DeveloperAPI
class CityscapesImageDatasource(FileBasedDatasource):
    """A datasource that lets you read images."""

    _WRITE_FILE_PER_ROW = True
    _FILE_EXTENSIONS = ["png", "jpg", "jpeg", "tif", "tiff", "bmp", "gif"]
    # Use 8 threads per task to read image files.
    _NUM_THREADS_PER_TASK = 8

    def __init__(
            self,
            paths: Union[str, List[str]],
            size: Optional[Tuple[int, int]] = None,
            mode: Optional[str] = None,
            **file_based_datasource_kwargs,
    ):
        super().__init__(paths, **file_based_datasource_kwargs)

        _check_import(self, module="PIL", package="Pillow")

        if size is not None and len(size) != 2:
            raise ValueError(
                "Expected `size` to contain two integers for height and width, "
                f"but got {len(size)} integers instead."
            )

        if size is not None and (size[0] < 0 or size[1] < 0):
            raise ValueError(
                f"Expected `size` to contain positive integers, but got {size} instead."
            )

        self.size = size
        self.mode = mode

        meta_provider = file_based_datasource_kwargs.get("meta_provider", None)
        if isinstance(meta_provider, _ImageFileMetadataProvider):
            self._encoding_ratio = self._estimate_files_encoding_ratio()
            meta_provider._set_encoding_ratio(self._encoding_ratio)
        else:
            self._encoding_ratio = IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT

    def _read_stream(
            self,
            f: "pyarrow.NativeFile",
            path: str,
    ) -> Iterator[Block]:
        from PIL import Image, UnidentifiedImageError

        data = f.readall()

        try:
            image = Image.open(io.BytesIO(data))
        except UnidentifiedImageError as e:
            raise ValueError(f"PIL couldn't load image file at path '{path}'.") from e

        if self.size is not None:
            height, width = self.size
            image = image.resize((width, height), resample=Image.BILINEAR)
        if self.mode is not None:
            image = image.convert(self.mode)

        builder = DelegatingBlockBuilder()
        array = np.array(image)
        image_name = path.split("/")[-1]

        item = {"image": array, "image_name": image_name}
        builder.add(item)
        block = builder.build()

        yield block

    def _rows_per_file(self):
        return 1

    def estimate_inmemory_data_size(self) -> Optional[int]:
        """
        estimate_inmemory_data_size
        :return:
        """
        total_size = 0
        for file_size in self._file_sizes():
            # NOTE: check if file size is not None, because some metadata provider
            # such as FastFileMetadataProvider does not provide file size information.
            if file_size is not None:
                total_size += file_size
        return total_size * self._encoding_ratio

    def _estimate_files_encoding_ratio(self) -> float:
        """Return an estimate of the image files encoding ratio."""
        start_time = time.perf_counter()
        # Filter out empty file to avoid noise.
        non_empty_path_and_size = list(
            filter(lambda p: p[1] > 0, zip(self._paths(), self._file_sizes()))
        )
        num_files = len(non_empty_path_and_size)
        if num_files == 0:
            logger.warn(
                "All input image files are empty. "
                "Use on-disk file size to estimate images in-memory size."
            )
            return IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT

        if self.size is not None and self.mode is not None:
            # Use image size and mode to calculate data size for all images,
            # because all images are homogeneous with same size after resizing.
            # Resizing is enforced when reading every image in `ImageDatasource`
            # when `size` argument is provided.
            if self.mode in ["1", "L", "P"]:
                dimension = 1
            elif self.mode in ["RGB", "YCbCr", "LAB", "HSV"]:
                dimension = 3
            elif self.mode in ["RGBA", "CMYK", "I", "F"]:
                dimension = 4
            else:
                logger.warn(f"Found unknown image mode: {self.mode}.")
                return IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT
            height, width = self.size
            single_image_size = height * width * dimension
            total_estimated_size = single_image_size * num_files
            total_file_size = sum(p[1] for p in non_empty_path_and_size)
            ratio = total_estimated_size / total_file_size
        else:
            # TODO(chengsu): sample images to estimate data size
            ratio = IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT

        sampling_duration = time.perf_counter() - start_time
        if sampling_duration > 5:
            logger.warn(
                "Image input size estimation took "
                f"{round(sampling_duration, 2)} seconds."
            )
        logger.debug(f"Estimated image encoding ratio from sampling is {ratio}.")
        return max(ratio, IMAGE_ENCODING_RATIO_ESTIMATE_LOWER_BOUND)


class _ImageFileMetadataProvider(DefaultFileMetadataProvider):
    def _set_encoding_ratio(self, encoding_ratio: int):
        """Set image file encoding ratio, to provide accurate size in bytes metadata."""
        self._encoding_ratio = encoding_ratio

    def _get_block_metadata(
            self,
            paths: List[str],
            schema: Optional[Union[type, "pyarrow.lib.Schema"]],
            *,
            rows_per_file: Optional[int],
            file_sizes: List[Optional[int]],
    ) -> BlockMetadata:
        metadata = super()._get_block_metadata(
            paths, schema, rows_per_file=rows_per_file, file_sizes=file_sizes
        )
        if metadata.size_bytes is not None:
            metadata.size_bytes = int(metadata.size_bytes * self._encoding_ratio)
        return metadata


@DeveloperAPI
class PaddleOCRRecognImageDatasource(FileBasedDatasource):
    """A datasource that lets you read images."""

    _WRITE_FILE_PER_ROW = True
    _FILE_EXTENSIONS = ["png", "jpg", "jpeg", "tif", "tiff", "bmp", "gif"]
    # Use 8 threads per task to read image files.
    _NUM_THREADS_PER_TASK = 8

    def __init__(
            self,
            paths: Union[str, List[str]],
            size: Optional[Tuple[int, int]] = None,
            mode: Optional[str] = None,
            points: List = None,
            **file_based_datasource_kwargs,
    ):
        super().__init__(paths, **file_based_datasource_kwargs)

        _check_import(self, module="PIL", package="Pillow")
        self.points = points
        if size is not None and len(size) != 2:
            raise ValueError(
                "Expected `size` to contain two integers for height and width, "
                f"but got {len(size)} integers instead."
            )

        if size is not None and (size[0] < 0 or size[1] < 0):
            raise ValueError(
                f"Expected `size` to contain positive integers, but got {size} instead."
            )

        self.size = size
        self.mode = mode

        meta_provider = file_based_datasource_kwargs.get("meta_provider", None)
        if isinstance(meta_provider, _ImageFileMetadataProvider):
            self._encoding_ratio = self._estimate_files_encoding_ratio()
            meta_provider._set_encoding_ratio(self._encoding_ratio)
        else:
            self._encoding_ratio = IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT

    @staticmethod
    def get_rotate_crop_image(img, points):
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
        assert len(points) == 4, "shape of points must be 4*2"
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3])))
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2])))
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

    def _read_stream(
            self,
            f: "pyarrow.NativeFile",
            path: str,
    ) -> Iterator[Block]:
        from PIL import Image, UnidentifiedImageError

        data = f.readall()

        # 读取数据为 OpenCV 可用的格式
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

        # 检查图像读取是否成功
        if image is None:
            raise ValueError(f"cv2 couldn't load image file at path '{path}'.")

        h, w, _ = image.shape  # 获取图像高度、宽度和通道数
        builder = DelegatingBlockBuilder()
        image_name = path.split("/")[-1]
        for point in self.points:
            print("image quadrangle{} type:{}".format(point, type(point)))
            point_2d = polygon.convert_1d_to_2d_pairs(point)
            img_suffix = string.generate_md5(str(point))  # 旋转裁剪图像
            cropped_image = self.get_rotate_crop_image(image, np.float32(point_2d))
            cropped_image_name = image_name.split(".")[0] + "_" + str(img_suffix) + ".jpg"
            array = np.array(cropped_image)
            item = {"image": [array], "image_name": cropped_image_name}
            builder.add(item)

        block = builder.build()

        yield block

    def _rows_per_file(self):
        return 1

    def estimate_inmemory_data_size(self) -> Optional[int]:
        """
        estimate_inmemory_data_size
        :return:
        """
        total_size = 0
        for file_size in self._file_sizes():
            # NOTE: check if file size is not None, because some metadata provider
            # such as FastFileMetadataProvider does not provide file size information.
            if file_size is not None:
                total_size += file_size
        return total_size * self._encoding_ratio

    def _estimate_files_encoding_ratio(self) -> float:
        """Return an estimate of the image files encoding ratio."""
        start_time = time.perf_counter()
        # Filter out empty file to avoid noise.
        non_empty_path_and_size = list(
            filter(lambda p: p[1] > 0, zip(self._paths(), self._file_sizes()))
        )
        num_files = len(non_empty_path_and_size)
        if num_files == 0:
            logger.warn(
                "All input image files are empty. "
                "Use on-disk file size to estimate images in-memory size."
            )
            return IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT

        if self.size is not None and self.mode is not None:
            # Use image size and mode to calculate data size for all images,
            # because all images are homogeneous with same size after resizing.
            # Resizing is enforced when reading every image in `ImageDatasource`
            # when `size` argument is provided.
            if self.mode in ["1", "L", "P"]:
                dimension = 1
            elif self.mode in ["RGB", "YCbCr", "LAB", "HSV"]:
                dimension = 3
            elif self.mode in ["RGBA", "CMYK", "I", "F"]:
                dimension = 4
            else:
                logger.warn(f"Found unknown image mode: {self.mode}.")
                return IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT
            height, width = self.size
            single_image_size = height * width * dimension
            total_estimated_size = single_image_size * num_files
            total_file_size = sum(p[1] for p in non_empty_path_and_size)
            ratio = total_estimated_size / total_file_size
        else:
            # TODO(chengsu): sample images to estimate data size
            ratio = IMAGE_ENCODING_RATIO_ESTIMATE_DEFAULT

        sampling_duration = time.perf_counter() - start_time
        if sampling_duration > 5:
            logger.warn(
                "Image input size estimation took "
                f"{round(sampling_duration, 2)} seconds."
            )
        logger.debug(f"Estimated image encoding ratio from sampling is {ratio}.")
        return max(ratio, IMAGE_ENCODING_RATIO_ESTIMATE_LOWER_BOUND)
