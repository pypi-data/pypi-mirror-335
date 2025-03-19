# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/28 19:58
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : test_operator.py
# @Software: PyCharm
"""
import os.path
import pandas as pd
import ray

from vistudio_image_analysis.operator.background_formatter import BackGroundFormatter
from vistudio_image_analysis.operator.vistudio_formatter import VistudioFormatter
from windmillclient.client.mock import get_mock_server
from vistudio_image_analysis.tests.mock.mock_server import get_mock_server as get_mock_as_server
from vistudio_image_analysis.tests.test_export import data as mock_data
from vistudio_image_analysis.operator.coco_formatter import CocoFormatter

args = {
    'mongo_host': '10.27.240.45',
    'mongo_port': '8719',
    'mongo_user': 'root',
    'mongo_password': 'mongo123#',
    'mongo_database': 'annotation_ut',
    'mongo_collection': 'annotation_ut',
    'windmill_endpoint': get_mock_server(),
    'vistudio_endpoint': get_mock_as_server(),
    'filesystem_name': 'workspaces/public/filesystems/defaultfs',
    'job_name': 'workspaces/public/projects/default/jobs/annoJob-azonn3Vv',
    'annotation_set_name': 'workspaces/default/projects/pj-ut/annotationsets/as-ut',
    'annotation_format': '',
    'org_id': 'test-org-id',
    'user_id': 'test-user-id',
    'mongo_shard_password': '',
    'mongo_shard_username': '',
    'data_uri': os.path.dirname(os.path.abspath(__file__)) + "/testdata/",
    'data_types': 'annotation,image',
    'file_format': 'file',
}


def test_coco_formatter():
    coco_formatter = CocoFormatter(
        labels={'铁轨': {'local_name': '0', 'attributes': []}},
        annotation_set_id='as-01',
        annotation_set_name='workspaces/default/projects/pj-ut/annotationsets/as-ut',
        data_uri=args['data_uri'],
        data_types=args['data_types'],
        user_id=args['user_id'],
        org_id=args['org_id'],
        tag=None,
        annotation_set_category='Image/ImageClassification/MultiTask',
        import_labels={'0': '铁轨'},
        merge_labels={'0': '0'},
    )

    image_data = [
        {
            'file_name': 's3://data/1ecb1b30-05171.jpg',
            'height': 960,
            'width': 1280,
            'id': 1.7388440778424859e+19
        }
    ]
    # 将字典列表转换为 Ray Dataset
    image_drop_duplicates_ds = ray.data.from_items(image_data)
    # 去重，基于 'file_name'
    for row in image_drop_duplicates_ds.iter_rows():
        # 调用 _fill_image_info_coco 方法
        coco_formatter._fill_image_info_coco(
            row=row,
            image_uri_prefix='tests/testdata/images'
        )
    annotation_data = {
        "image_id": ["00accc09b0706dbf"],
        "bbox": [[327, 623, 167, 222]],
        "area": [0],
        "iscrowd": [0],
        "category_id": [0],
        "segmentation": [[]],
        "id": [1.738844e+19]
    }
    # 创建一个 DataFrame 作为分组的数据
    group_df = pd.DataFrame(annotation_data)
    coco_formatter._group_by_image_id(group_df)

    coco_operator = CocoFormatter(labels={'0': '铁轨'}, merge_labels={})
    source_df = pd.DataFrame(mock_data)
    coco_operator.from_vistudio_v1(source_df)


def test_liangpin_formatter():
    row = {
        "image_name": "05d1c7c1-cfe8-4579-ba1a-8fd75486bfbf.jpg",
        "image_id": "29f1e5b408618271",
        "annotation_set_id": "as-xkwgfgut",
        "annotation_set_name": "workspaces/wsyiiiad/projects/spiproject/annotationsets/as-QRj2fQtw",
        "user_id": "05c4100af26e4628ab527eecf184ab48",
        "created_at": {
            "$numberLong": "1730102381611791431"
        },
        "data_type": "Image",
        "infer_state": "UnInfer",
        "file_uri": "s3://windmill-online/store/workspaces/wsyiiiad/projects/spiproject/annotationsets/as-QRj2fQtw/CYRIkSUN/data/nahui/images/CVAT数据复核/nahui/双面坡/05d1c7c1-cfe8-4579-ba1a-8fd75486bfbf.jpg",
        "org_id": "7b7456100c1848ecad0ab8280674fe5a",
        "annotation_state": "Annotated",
        "image_state": {
            "webp_state": "NotNeed",
            "thumbnail_state": "Completed"
        },
        "updated_at": {
            "$numberLong": "1730102412873291496"
        },
        "height": 309,
        "size": 88251,
        "width": 550
    }
    bg_formatter = BackGroundFormatter()
    item = bg_formatter._fill_background_annotation(row=row)




