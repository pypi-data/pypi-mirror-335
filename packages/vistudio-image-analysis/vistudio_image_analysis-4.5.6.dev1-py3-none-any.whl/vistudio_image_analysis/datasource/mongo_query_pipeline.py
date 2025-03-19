# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
"""
export_pipeline.py
Authors: xujian(xujian16@baidu.com)
Date:    2024/3/5 7:18 下午
"""
import json

import bcelogger
import pandas as pd
import pyarrow as pa
import pymongo

from vistudio_image_analysis.api import Vistudio
from vistudio_image_analysis.api.annotation import convert_dataframe

LOOKUP = "$lookup:"


def replace_nested_set_strings(value, m):
    """
    replace_nested_set_strings
    :param value:
    :param m:
    :return:
    """
    if isinstance(value, str) and value.startswith(LOOKUP):
        key = value[len(LOOKUP):]
        return m.get(key, value)
    elif isinstance(value, list):
        return [replace_nested_set_strings(item, m) for item in value]
    elif isinstance(value, dict):
        return {k: replace_nested_set_strings(v, m) for k, v in value.items()}
    return value


class Step:
    """
    Step
    """

    def __init__(self, aggregation, collection, default_query_result, query_result_mapping):
        self.aggregation = aggregation
        self.collection = collection
        self.default_query_result = default_query_result
        self.query_result_mapping = query_result_mapping
        # self.aggregation_json = json.dumps(aggregation)

    def append_shard_match(self, shard_match):
        """
        append_shard_match
        :param shard_match:
        :return:
        """
        new_aggregation = shard_match.copy()
        new_aggregation.extend(self.aggregation)
        self.aggregation = new_aggregation

    def aggregation_doc(self):
        """
        aggregation_doc
        :return:
        """
        return self.aggregation

    def collection_name(self):
        """
        collection_name
        :return:
        """
        return self.collection

    def run(self, coll):
        """
        run
        :param coll:
        :return:
        """

        # data_type_value = None
        # for stage in self.aggregation_doc():
        #     if '$match' in stage and 'data_type' in stage['$match']:
        #         data_type_value = stage['$match']['data_type']
        #         break
        # schema = None
        # if data_type_value == 'Image':
        #     schema = Image.to_pyarrow_schema()
        # elif data_type_value == 'Annotation':
        #     schema = Annotations.to_pyarrow_schema()
        cursor = coll.aggregate(self.aggregation_doc(), allowDiskUse=True)
        result = dict()
        for doc in cursor:
            # 查询结果映射
            for k, v in self.query_result_mapping.items():
                if v not in result:
                    result[v] = []

                if k == "":
                    result[v].append(doc)
                    continue

                if k in doc:
                    result[v].append(doc[k])
        return result


class Pipeline:
    """
    Pipeline
    """

    def __init__(self, steps):
        self.steps = [step for step in steps if step is not None]
        self.results = {}
        self.index = 0

    def append_shard_match(self, shard_match):
        """
        append_shard_match
        :param shard_match:
        :return:
        """
        for step in self.steps:
            step.append_shard_match(shard_match)

    def next_step(self):
        """
        next_step
        :return:
        """
        if self.index >= len(self.steps):
            return None
        query = self.steps[self.index]
        self.index += 1
        transformed_doc = replace_nested_set_strings(query.aggregation, self.results)
        query.aggregation = transformed_doc
        # query.aggregation_json = json.dumps(transformed_doc)
        # print("next_step aggregation: {}".format(query.aggregation))
        return query

    def set_query_result(self, result):
        """
        set_query_result
        :param result:
        :return:
        """
        default_query_result = self.steps[self.index - 1].default_query_result
        if default_query_result is None:
            default_query_result = {}
        if result is not None:
            default_query_result.update(result)
        self.results.update(default_query_result)

    def run(self, coll):
        """
        run
        :param coll:
        :return:
        """
        for i in range(len(self.steps)):
            step = self.next_step()
            step_result = step.run(coll)
            self.set_query_result(step_result)
        return self.results


def json_to_pipeline(steps_json):
    """
    json_to_pipeline
    :param steps_json:
    :return:
    """
    pipe_steps = []
    for s in steps_json:
        aggregation = s.get("aggregation", [])
        collection = s.get("collection", "")
        default_query_result = s.get("default_query_result", None)
        query_result_mapping = s.get("query_result_mapping", {})
        pipe_steps.append(Step(aggregation, collection, default_query_result, query_result_mapping))
    return Pipeline(pipe_steps)


def get_pipeline_func(query_json):
    """
    get_pipeline_func
    :param query_json:
    :return:
    """
    pipe = json_to_pipeline(query_json)

    def list_image_annotation(coll, shard_match=None, schema=None, **kwargs):
        """
        list_image_annotation
        :param coll:
        :param shard_match:
        :param schema:
        :param kwargs:
        :return:

        返回的格式示例
         {
              'width': 1920,
              'height': 1080,
              'image_id': '443dc43cc26e533a',
              'image_name': '4c74bb83b4e04ffeb968fcaa8e95b14f.jpeg',
              'annotation_set_id': 'as-eca7pczg',
              'annotation_set_name': 'workspaces/internal/projects/spiproject/annotationsets/as-BKCdsWSz',
              'user_id': '2c9533c3bb98459dbf4121dfab8c6023',
              'created_at': 1729820871810472994,
              'data_type': 'Image',
              'file_uri': 's3://windmill-pre/store//images/4c74bb83b4e04ffeb968fcaa8e95b14f.jpeg',
              'org_id': '8981e5ce5b3740cba841b692495d9baf',
              'tags': None,
              'image_state': {
                'webp_state': 'NotNeed',
                'thumbnail_state': 'Completed'
              },
              'updated_at': 1729820887554442176,
              'annotation_state': 'Annotated',
              'annotations': [
                {
                  'image_id': '443dc43cc26e533a',
                  'user_id': '2c9533c3bb98459dbf4121dfab8c6023',
                  'created_at': 1729820871308608419,
                  'annotations': [
                    {
                      'id': '0',
                      'bbox': [
                        757.0,
                        746.0,
                        62.0,
                        34.0
                      ],
                      'segmentation': [

                      ],
                      'quadrangle': None,
                      'rle': None,
                      'area': 2138.0,
                      'labels': [
                        {
                          'id': '0',
                          'name': None,
                          'confidence': 1.0,
                          'parent_id': None
                        }
                      ],
                      'ocr': None
                    },

                    {
                      'id': '0',
                      'bbox': [
                        157.0,
                        445.0,
                        468.0,
                        217.0
                      ],
                      'segmentation': [

                      ],
                      'quadrangle': None,
                      'rle': None,
                      'area': 101882.0,
                      'labels': [
                        {
                          'id': '0',
                          'name': None,
                          'confidence': 1.0,
                          'parent_id': None
                        }
                      ],
                      'ocr': None
                    }
                  ],
                  'data_type': 'Annotation',
                  'annotation_set_id': 'as-eca7pczg',
                  'task_kind': 'Manual',
                  'artifact_name': '',
                  'image_created_at': 1729820871810472994,
                  'updated_at': 1732795054842533494
                }
              ]
            }
            ]




        """
        pipe.append_shard_match(shard_match)
        results = pipe.run(coll)
        if 'images' not in results:
            df = pd.DataFrame()

            table = pa.Table.from_pandas(df)
            return table
        images = results['images']
        annotations = results.get('annotations', [])
        image_list = []
        image_id2index = {}
        for image in images:
            image_id = image['image_id']
            image_id2index[image_id] = len(image_list)
            image['annotations'] = []
            image_list.append(image)
        for annotation in annotations:
            image_id = annotation['image_id']
            image_list[image_id2index[image_id]]['annotations'].append(annotation)

        df = pd.DataFrame(image_list)
        pa_schema = Vistudio.to_pyarrow_schema()
        image_df = convert_dataframe(df=df, schema=pa_schema)
        table = pa.Table.from_pandas(image_df, schema=pa_schema)
        print("list_image_annotation result count: ", table.num_rows)
        return table

    return list_image_annotation





def test_json_to_pipeline():
    """
    test_json_to_pipeline
    :return:
    """
    json_str = """
        """
    json_str_without_space = json_str.replace(" ", "").replace("\n", "").replace('"', '\"')
    print(json_str_without_space)
    pipe_json = json.loads(json_str)
    pipeline = json_to_pipeline(pipe_json)
    print("test_json_to_pipeline: {}".format(pipeline))

    uri = "mongodb://root:mongo123#@10.27.240.45:8719"
    db_name = "annotation_dev_tiny"
    collection_name = "annotation"
    client = pymongo.MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    res = pipeline.run(collection)
    print("res", res)


if __name__ == '__main__':
    test_json_to_pipeline()