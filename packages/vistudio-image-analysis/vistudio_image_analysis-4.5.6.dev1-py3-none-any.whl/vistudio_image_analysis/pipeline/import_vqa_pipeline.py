#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File: import_vqa_pipeline.py
"""
import ray.data
import argparse
import bcelogger

from vistudio_image_analysis.pipeline.base_import_pipeline import BaseImportPipline
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.operator.reader import Reader
from vistudio_image_analysis.processor.importer.zip.zip_preprocessor import ZipFormatPreprocessor
from vistudio_image_analysis.processor.importer.annotation.vqa_preprocessor import VQAFormatPreprocessor


class ImportVQAPipeline(BaseImportPipline):
    """
    ImportVQAPipeline
    """
    def __init__(self, args):
        super().__init__(args)
        self.only_anno = False

    def _import_annotation(self):
        """
        导入标注文件
        :return:
        """
        # 读取json 文件
        vqa_reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)
        if self.file_format == 'zip':
            zip_file_uris = vqa_reader.get_zip_file_uris(data_uri=self.data_uri)
            if len(zip_file_uris) > 0:
                zip_formatter = ZipFormatPreprocessor(config=self.config)
                self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_

        file_uris = vqa_reader.get_file_uris(
            data_uri=self.data_uri,
            data_types=self.data_types,
            annotation_format=self.annotation_format
        )
        if len(file_uris) == 0:
            self.update_annotation_job("未找到标注文件")
            raise Exception("未获取到相关文件，请检查文件")

        try:
            ds = vqa_reader.read_multijson(file_uris)
            bcelogger.info("import VQA annotation count = {}".format(ds.count()))
        except Exception as e:
            self.update_annotation_job("文件解析错误")
            raise e

        # 处理ds
        vqa_preprocessor = VQAFormatPreprocessor(
            config=self.config,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            data_uri=self.data_uri,
            tag=self.tag
        )
        final_ds_dict = vqa_preprocessor.fit(ds).stats_

        # 写入ds
        image_ds = final_ds_dict.get("image_ds", None)
        if image_ds is not None and self.only_anno is False:
            bcelogger.info("Start write image ...")
            image_ds.write_mongo(
                uri=self.mongo_uri,
                database=self.config.mongodb_database,
                collection=self.config.mongodb_collection
            )

        annotation_ds = final_ds_dict.get("annotation_ds", None)
        if annotation_ds is not None:
            bcelogger.info("Start write annotation ...")
            annotation_ds.write_mongo(
                uri=self.mongo_uri,
                database=self.config.mongodb_database,
                collection=self.config.mongodb_collection
            )

    def run(self):
        """
        run this piepline
        :return:
        """
        if len(self.data_types) == 1 and self.data_types[0] == "image":
            self._import_image()
        else:
            if len(self.data_types) == 1 and self.data_types[0] == "annotation":
                self.only_anno = True
            self._import_annotation()


def run(args):
    """
    pipeline run
    :param args:
    :return:
    """
    pipeline = ImportVQAPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Import')
    args = arg_parser.parse_args()
    run(args)
