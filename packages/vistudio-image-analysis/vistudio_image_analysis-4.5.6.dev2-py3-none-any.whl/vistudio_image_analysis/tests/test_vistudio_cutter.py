# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
@File    : test_vistudio_cutter.py
@Author  : dongling01@baidu.com
@Time    : 2024/10/15 10:52
"""
import ray
import pandas as pd
import bcelogger
import os

from vistudio_image_analysis.tests.mock.mock_data import GET_LOCAL_FILESYSTEM
from vistudio_image_analysis.operator.vistudio_cutter import VistudioCutter


def test_vistudio_cutter():
    """
    测试切图
    """
    mock_fs = GET_LOCAL_FILESYSTEM
    mock_location = os.path.dirname(os.path.abspath(__file__)) + "/store/1"
    mock_split = {
        'width': 150,
        'height': 150,
        'overlap': 0,
        'padding': False
    }

    mock_cut_data = [
        {
            'file_uri': os.path.dirname(os.path.abspath(__file__)) + "/store/image/xinpian.jpg",
            'width': 300,
            'height': 300,
            'annotation_state': 'Annotated',
            'annotations': [
                {
                    'annotations': [
                        {
                            "area": 7158.201633849831,
                            "bbox": [38.4525, 74.52693, 67.28091, 113.99186],
                            "labels": [{"id": "1"}],
                            "segmentation": [105.30486270838438,182.09067147507045,72.3072201880243,188.51878365436136,
                                             38.45249604375883,180.80504903921224,40.166659291569744,78.812335794463,
                                             71.45013856411887,74.5269276749357,105.7334035203371,79.66941741836845]
                        },
                        {
                            "area": 3286,
                            "bbox": [117, 239, 73, 49],
                            "labels": [{"id": "1"}],
                            "rle": {
                                "size": [300,300],
                                "counts": [35364,11,280,23,273,30,268,34,264,37,262,39,259,41,259,42,257,43,256,45,255,
                                           45,254,46,253,48,252,48,251,49,251,49,251,49,251,49,251,49,251,49,251,49,252,
                                           48,252,48,252,48,252,48,252,48,252,48,252,48,251,49,251,49,251,49,251,48,252,
                                           48,252,48,252,47,253,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,
                                           48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,
                                           48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,48,252,47,253,47,253,
                                           47,253,46,255,45,256,43,258,41,261,38,266,33,292,6,33021]
                            },
                        },
                        {
                            "area": 7013.854913027673,
                            "bbox": [77.3409007409222, 161.54917028963325, 131.99057008144015, 53.13906068213828],
                            "labels": [{"id": "1"}]
                        }
                    ],
                    'task_kind': 'Manual'
                }
            ]
        }
    ]

    df = pd.DataFrame(mock_cut_data)
    operator = VistudioCutter(filesystem=mock_fs, location=mock_location, split_config=mock_split)
    df = operator.cut_images_and_annotations(source=df)

    ds = ray.data.from_pandas(df)
    bcelogger.info(f"VistudioCutter: {ds.take_all()}")


