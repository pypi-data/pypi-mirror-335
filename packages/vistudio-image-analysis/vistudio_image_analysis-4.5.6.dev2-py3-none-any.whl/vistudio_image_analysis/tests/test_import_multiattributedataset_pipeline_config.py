# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/14 16:03
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : test_import_multiattributedataset_pipeline_config.py
# @Software: PyCharm
"""
MULTIATTRIBUTE_PIPELINE_ARGS = {'mongo_host': '10.27.240.45',
                                'mongo_port': '8719',
                                'mongo_user': 'root',
                                'mongo_password': 'mongo123#',
                                'mongo_database': 'test_annotation',
                                'mongo_collection': 'test_annotation',
                                'windmill_endpoint': 'http://10.27.240.45:0000',
                                'vistudio_endpoint': 'http://10.27.240.45:0000',
                                'filesystem_name': 'workspaces/public/filesystems/defaultfs',
                                'job_name': 'workspaces/public/projects/default/jobs/annoJob-azonn3Vv',
                                'annotation_set_name':
                                    'workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut',
                                'annotation_format': 'MultiAttributeDataset',
                                'org_id': '68b4691df5fd48a7a23742fed8d39c36',
                                'user_id': '20bbbb61e90e4e7fae27c2a05ec1ba59',
                                'mongo_shard_password': '',
                                'mongo_shard_username': '',
                                'data_uri':
                                    's3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/'
                                    'annotationsets/as-vistudio-ut/nt7Svx1B/data',
                                'data_types': 'annotation,image',
                                'file_format': 'zip',
                                'tag': ''}

MULTIATTRIBUTE_PIPELINE_DOCUMENTS = [
    {
        "_id": {"$oid": "6708e38ff3efaa4b7e9c3e01"},
        "file_uri": "s3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/"
                    "annotationsets/as-vistudio-ut/nt7Svx1B/data/multiattributedataset/images/worker.jpeg",
        "width": 500,
        "height": 755,
        "image_name": "worker.jpeg",
        "image_id": "1b61e2511666a2c7",
        "annotation_set_id": "as-n6jdhp8z",
        "annotation_set_name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
        "user_id": "20bbbb61e90e4e7fae27c2a05ec1ba59",
        "org_id": "68b4691df5fd48a7a23742fed8d39c36",
        "created_at": {"$numberLong": "1728635791404116090"},
        "data_type": "Image",
        "annotation_state": "Annotated",
        "image_state": {
            "webp_state": "NotNeed",
            "thumbnail_state": "Completed"
        },
        "updated_at": {"$numberLong": "1728635997561778007"},
        "size": 31258
    },
    {
        "_id": {"$oid": "6708e390aa660aee18704175"},
        "file_uri": "s3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut/"
                    "nt7Svx1B/data/multiattributedataset/images/safety_helmet.jpeg",
        "width": 750,
        "height": 500,
        "image_name": "safety_helmet.jpeg",
        "image_id": "b034024337ddf85a",
        "annotation_set_id": "as-n6jdhp8z",
        "annotation_set_name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
        "user_id": "20bbbb61e90e4e7fae27c2a05ec1ba59",
        "org_id": "68b4691df5fd48a7a23742fed8d39c36",
        "created_at": {"$numberLong": "1728635791447179366"},
        "data_type": "Image",
        "annotation_state": "Annotated",
        "image_state": {
            "webp_state": "NotNeed",
            "thumbnail_state": "Completed"
        },
        "updated_at": {"$numberLong": "1728635997538859676"},
        "size": 36588
    }
]

FILESYSTEM_INFO = {'name': 'workspaces/public/filesystems/defaultfs',
                   'localName': 'defaultfs',
                   'isDisabled': False,
                   'kind': 's3',
                   'host': 's3.bj.bcebos.com',
                   'endpoint': 'windmill-test/store',
                   'credential': {'accessKey': 'test-ak',
                                  'secretKey': 'test-sk',
                                  'token': ''},
                   'mountPath': '/home/paddleflow/storage/mnt',
                   'config': {'disableSSL': 'false',
                              'region': 'bj',
                              's3ForcePathStyle':
                                  'true'},
                   'tags': {},
                   'userID': '9b70ba591c554c28ae5b311f794a238c',
                   'orgID': '07e17c96439e4d5da9f9c9817e1d2ad5',
                   'workspaceID': 'public',
                   'createdAt': '2024-07-10T14:29:47.101Z',
                   'updatedAt': '2024-07-10T14:29:47.101Z'}


GET_ANNOTATION_SET_RESPONSE = {
    "id": "as-n6jdhp8z",
    "name": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
    "localName": "as-vistudio-ut",
    "displayName": "多属性安全帽",
    "description": "",
    "category": {
        "objectType": "annotationset",
        "objectName": "workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
        "parentType": "project",
        "parentName": "workspaces/default/projects/proj-vistudio-ut",
        "workspaceID": "default",
        "name": "workspaces/default/categories/category-b99zenmj",
        "localName": "category-b99zenmj",
        "category": "Image/ImageClassification/MultiTask",
        "createdAt": "2024-10-11T08:11:00.782Z",
        "updatedAt": "2024-10-11T08:11:00.782Z"
    },
    "labels": [
        {
            "localName": "0",
            "id": "╔",
            "displayName": "安全帽",
            "color": "#4764ec",
            "parentID": "",
            "confidence": 0,
            "annotationSetName": "as-vistudio-ut",
            "projectName": "proj-vistudio-ut",
            "workspaceID": "default",
            "createdAt": "2024-10-11T08:11:46.753Z",
            "updatedAt": "2024-10-11T08:11:46.753Z",
            "deletedAt": 0
        },
        {
            "localName": "0",
            "id": "╕",
            "displayName": "未戴安全帽",
            "color": "#098e47",
            "parentID": "0",
            "confidence": 0,
            "annotationSetName": "as-vistudio-ut",
            "projectName": "proj-vistudio-ut",
            "workspaceID": "default",
            "createdAt": "2024-10-11T08:11:46.791Z",
            "updatedAt": "2024-10-11T08:11:46.791Z",
            "deletedAt": 0
        },
        {
            "localName": "1",
            "id": "╖",
            "displayName": "戴安全帽",
            "color": "#ab783e",
            "parentID": "0",
            "confidence": 0,
            "annotationSetName": "as-vistudio-ut",
            "projectName": "proj-vistudio-ut",
            "workspaceID": "default",
            "createdAt": "2024-10-11T08:11:46.813Z",
            "updatedAt": "2024-10-11T08:11:46.813Z",
            "deletedAt": 0
        },
        {
            "localName": "1",
            "id": "╗",
            "displayName": "工服",
            "color": "#da335d",
            "parentID": "",
            "confidence": 0,
            "annotationSetName": "as-vistudio-ut",
            "projectName": "proj-vistudio-ut",
            "workspaceID": "default",
            "createdAt": "2024-10-11T08:11:46.842Z",
            "updatedAt": "2024-10-11T08:11:46.842Z",
            "deletedAt": 0
        },
        {
            "localName": "0",
            "id": "╘",
            "displayName": "未穿工服",
            "color": "#2579aa",
            "parentID": "1",
            "confidence": 0,
            "annotationSetName": "as-vistudio-ut",
            "projectName": "proj-vistudio-ut",
            "workspaceID": "default",
            "createdAt": "2024-10-11T08:11:46.883Z",
            "updatedAt": "2024-10-11T08:11:46.883Z",
            "deletedAt": 0
        },
        {
            "localName": "1",
            "id": "╙",
            "displayName": "工服",
            "color": "#54a2fb",
            "parentID": "1",
            "confidence": 0,
            "annotationSetName": "as-vistudio-ut",
            "projectName": "proj-vistudio-ut",
            "workspaceID": "default",
            "createdAt": "2024-10-11T08:11:46.911Z",
            "updatedAt": "2024-10-11T08:11:46.911Z",
            "deletedAt": 0
        }
    ],
    "imageCount": 2,
    "annotatedImageCount": 2,
    "inferedImageCount": 0,
    "size": "67.85kB",
    "uri": "s3://windmill/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut",
    "jobs": [],
    "orgID": "68b4691df5fd48a7a23742fed8d39c36",
    "userID": "20bbbb61e90e4e7fae27c2a05ec1ba59",
    "projectName": "proj-vistudio-ut",
    "workspaceID": "default",
    "createdAt": "2024-10-11T08:11:00.783Z",
    "updatedAt": "2024-10-12T09:14:54.251Z"
}


GET_FILESYSTEM_CREDENTIAL = {
    "name": "workspaces/public/filesystems/defaultfs",
    "localName": "defaultfs",
    "displayName": "",
    "description": "",
    "isDisabled": False,
    "kind": "s3",
    "parentName": "",
    "host": "s3.bj.bcebos.com",
    "endpoint": "windmill-test/store",
    "credential": {
        "accessKey": "test-ak",
        "secretKey": "test-sk",
        "token": ""
    },
    "mountPath": "/home/paddleflow/storage/mnt",
    "config": {
        "disableSSL": "false",
        "region": "bj",
        "s3ForcePathStyle": "true"
    },
    "tags": {},
    'raw_data': '{"name": "workspaces/public/filesystems/defaultfs", '
                '"localName": "defaultfs", "displayName": "", "description": "", '
                '"isDisabled": false, "kind": "s3", "parentName": "", "host": "s3.bj.bcebos.com", '
                '"endpoint": "windmill-test/store", "credential": {"accessKey": "test-ak", '
                '"secretKey": "test-sk", "token": ""}, '
                '"mountPath": "/home/paddleflow/storage/mnt", "config": {"disableSSL": "false", "region": '
                '"bj", "s3ForcePathStyle": "true"}, "tags": {}, "userID": "9b70ba591c554c28ae5b311f794a238c", '
                '"orgID": "07e17c96439e4d5da9f9c9817e1d2ad5", "workspaceID": "public", '
                '"createdAt": "2024-07-10T22:29:47.101Z", "updatedAt": "2024-07-10T22:29:47.101Z"}',
    "userID": "9b70ba591c554c28ae5b311f794a238c",
    "orgID": "07e17c96439e4d5da9f9c9817e1d2ad5",
    "workspaceID": "public",
    "createdAt": "2024-07-10T22:29:47.101Z",
    "updatedAt": "2024-07-10T22:29:47.101Z"
}


FILE_URIS = [
    's3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/as-vistudio-ut/'
    'nt7Svx1B/data/multiattribute_dataset/annotations/label_description.yaml',
    's3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/'
    'as-vistudio-ut/nt7Svx1B/data/multiattribute_dataset/annotations/train.txt'
]

ZIP_FILE_URI = ['s3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/'
                'annotationsets/as-vistudio-ut/nt7Svx1B/data/multiattribute_dataset.zip']

ZIP_DIR = 's3://windmill-test/store/workspaces/default/projects/proj-vistudio-ut/annotationsets/' \
                      'as-vistudio-ut/nt7Svx1B/data/multiattribute_dataset'
