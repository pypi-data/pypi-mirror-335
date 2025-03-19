#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File:  import_imagnet_pipeline.py
"""
import pandas as pd
import ray.data
import sys
import os
import argparse
import bcelogger

work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, work_dir)

from vistudio_image_analysis.util.label import convert_annotation_labels
from vistudio_image_analysis.processor.importer.zip.zip_preprocessor import ZipFormatPreprocessor
from vistudio_image_analysis.processor.importer.annotation.imagenet_preprocessor import ImageNetFormatPreprocessor
from vistudio_image_analysis.processor.importer.label.label_preprocessor import LabelFormatPreprocessor
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.operator.reader import Reader
from vistudio_image_analysis.pipeline.base_import_pipeline import BaseImportPipline


class ImportImageNetPipeline(BaseImportPipline):
    """
    ImportImageNetPipeline
    """

    def __init__(self, args):
        super().__init__(args)

    def _import_annotation(self):
        """
        导入标注文件
        :return:
        """
        # 读取json 文件
        imagenet_reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)

        if self.file_format == 'zip':
            zip_file_uris = imagenet_reader.get_zip_file_uris(data_uri=self.data_uri)
            if len(zip_file_uris) > 0:
                zip_formatter = ZipFormatPreprocessor(config=self.config)
                self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_

        file_uris = imagenet_reader.get_file_uris(
            data_uri=self.data_uri,
            data_types=self.data_types,
            annotation_format=self.annotation_format
        )
        if len(file_uris) == 0:
            self.update_annotation_job("未找到标注文件")
            raise Exception("未获取到相关文件，请检查文件")

        ds = ray.data.from_pandas(pd.DataFrame(file_uris))
        bcelogger.info("import imagenet annotation count = {}".format(ds.count()))

        # 处理ds
        label_formatter = LabelFormatPreprocessor(
            config=self.config,
            labels=self.labels,
            annotation_format=self.annotation_format
        )
        need_add_labels = label_formatter.fit(ds).stats_.get("need_add_labels")
        bcelogger.info(f"import imagenet need add labels:{need_add_labels}")
        if need_add_labels is not None and len(need_add_labels) > 0:
            self.import_labels(need_add_labels)
            self._get_labels()

        imagenet_preprocessor = ImageNetFormatPreprocessor(config=self.config,
                                                           annotation_set_id=self.annotation_set_id,
                                                           annotation_set_name=self.annotation_set_name,
                                                           labels=convert_annotation_labels(self.labels),
                                                           tag=self.tag)
        final_ds_dict = imagenet_preprocessor.fit(ds).stats_
        image_ds = final_ds_dict.get("image_ds")
        annotation_ds = final_ds_dict.get("annotation_ds")
        # 数据入库
        image_ds.write_mongo(uri=self.mongo_uri,
                             database=self.config.mongodb_database,
                             collection=self.config.mongodb_collection)
        annotation_ds.write_mongo(uri=self.mongo_uri,
                                  database=self.config.mongodb_database,
                                  collection=self.config.mongodb_collection)

    def run(self):
        """
        run this piepline
        :return:
        """
        if len(self.data_types) == 1 and self.data_types[0] == "image":
            self._import_image()
        elif len(self.data_types) == 2 and "image" in self.data_types and "annotation" in self.data_types:
            self._import_annotation()
        else:
            raise Exception("The data_types: '{}' is not support.".format(self.data_types))


def run(args):
    """
    pipeline run
    :param args:
    :return:
    """
    pipeline = ImportImageNetPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Import')
    args = arg_parser.parse_args()
    run(args)
