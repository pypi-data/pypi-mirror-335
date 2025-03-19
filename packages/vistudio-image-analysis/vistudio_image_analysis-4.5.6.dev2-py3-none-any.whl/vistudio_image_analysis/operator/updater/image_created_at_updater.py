#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File    :   image_created_at_updater.py
@Time    :   2024/03/13 16:49:57
@Author  :   <dongling01@baidu.com>
"""

import time
import bcelogger
from pandas import DataFrame

from vistudio_image_analysis.operator.updater.base_mongo_updater import BaseMongoUpdater
from vistudio_image_analysis.table.annotation import AnnotationData, DATA_TYPE_ANNOTATION, TASK_KIND_MANUAL
from vistudio_image_analysis.table.image import ImageData, DATA_TYPE_IMAGE, ANNOTATION_STATE_ANNOTATED


class ImageCreatedAtUpdater(BaseMongoUpdater):
    """
    ImageCreatedAtUpdater
    """
    def update_image_created_at(self, source: DataFrame) -> DataFrame:
        """
        update image_created_at
        """
        for source_index, source_row in source.iterrows():
            image = ImageData.objects(image_id=source_row['image_id'],
                                      annotation_set_id=source_row['annotation_set_id'],
                                      data_type=DATA_TYPE_IMAGE).first()
            if image is None:
                # 脏数据清理：如果这条标注记录(无图像对应)在库里存在时间超过三天，则清除掉
                if (time.time_ns() - source_row['created_at']) / 1e+9 > 3 * 24 * 60 * 60:
                    AnnotationData.objects(image_id=source_row['image_id'],
                                           annotation_set_id=source_row['annotation_set_id'],
                                           data_type=DATA_TYPE_ANNOTATION).delete()
                continue

            # 更新image_created_at
            AnnotationData.objects(image_id=source_row['image_id'], annotation_set_id=source_row['annotation_set_id'],
                                   data_type=DATA_TYPE_ANNOTATION).update(
                image_created_at=image.created_at, updated_at=time.time_ns())

            # 更新annotation_state
            if source_row['task_kind'] != TASK_KIND_MANUAL:
                continue

            if image.annotation_state is None or image.annotation_state != ANNOTATION_STATE_ANNOTATED:
                ImageData.objects(image_id=source_row['image_id'],
                                  annotation_set_id=source_row['annotation_set_id'],
                                  data_type=DATA_TYPE_IMAGE).update(annotation_state=ANNOTATION_STATE_ANNOTATED)

        return source