#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File: import_multiattributedataset_pipeline.py
"""
import pandas as pd
import ray.data
import sys
import os
import bcelogger
from windmillcomputev1.filesystem import blobstore, init_py_filesystem

work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, work_dir)

from vistudio_image_analysis.processor.importer.annotation.multiattributedataset_preprocessor import \
    MultiAttributeDatasetFormatPreprocessor
from vistudio_image_analysis.processor.importer.zip.zip_preprocessor import ZipFormatPreprocessor
from vistudio_image_analysis.processor.importer.label.label_preprocessor import LabelFormatPreprocessor
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.operator.reader import Reader
from vistudio_image_analysis.pipeline.base_import_pipeline import BaseImportPipline


class ImportMultiAttributeDatasetPipeline(BaseImportPipline):
    """
    ImportMultiAttributeDatasetPipeline
    """

    def __init__(self, args):
        super().__init__(args)
        self.bs = blobstore(self.config.filesystem)
        self._py_fs = init_py_filesystem(self.config.filesystem)

    def _import_annotation(self):
        """
        导入标注文件
        :return:
        """
        # 读取json 文件
        reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)

        zip_file_uris = reader.get_zip_file_uris(data_uri=self.data_uri)
        if len(zip_file_uris) > 0:
            zip_formatter = ZipFormatPreprocessor(config=self.config)
            self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_

        file_uris = reader.get_file_uris(
            data_uri=self.data_uri,
            data_types=self.data_types,
            annotation_format=self.annotation_format
        )
        txt_files = [file for file in file_uris if file.endswith('.txt')]
        label_files = [file for file in file_uris if file.endswith('.yaml')]
        if label_files is None or len(label_files) == 0:
            self.update_annotation_job(err_msg="缺少标签描述文件")
            raise Exception("缺少标签描述文件")

        label_ds = reader.read_label_yaml(label_file_uris=label_files).flat_map(lambda row: row['task'])
        if not self._check_label(label_ds):
            self.update_annotation_job(err_msg="标签描述文件不合格，anno_key必须大于等于1")
            raise Exception("标签描述文件不合格，anno_key必须大于等于1")

        label_len = len(label_ds.take_all())
        ds = ray.data.read_text(paths=txt_files, filesystem=self._py_fs)
        bcelogger.info("import multiattributedataset annotation dataset count = {}".format(ds.count()))
        anno_len = len(ds.take(1)[0].get("text").split(' '))
        if label_len != (anno_len - 1):
            self.update_annotation_job(err_msg="标注文件不合格")
            raise Exception("标注文件不合格")

        label_formatter = LabelFormatPreprocessor(
            config=self.config,
            labels=self.labels,
            annotation_format=self.annotation_format
        )

        # 处理 ds，获取annotation
        label_dict = label_formatter.fit(label_ds).stats_
        need_add_labels = label_dict.get("need_add_labels")
        bcelogger.info(f"import multiattributedataset need add labels:{need_add_labels}")

        if need_add_labels is not None and len(need_add_labels) > 0:
            self.import_labels(need_add_labels)
            self._get_labels()

        multi_attr_preprocessor = MultiAttributeDatasetFormatPreprocessor(
            config=self.config,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            annotation_labels=self.labels,
            multi_attribute_labels=label_dict.get("import_labels"),
            tag=self.tag,
            data_types=self.data_types,
            data_uri=self.data_uri)
        final_ds_dict = multi_attr_preprocessor.fit(ds).stats_
        image_ds = final_ds_dict.get("image_ds")
        annotation_ds = final_ds_dict.get("annotation_ds")
        # 数据入库
        image_ds.write_mongo(uri=self.mongo_uri,
                             database=self.config.mongodb_database,
                             collection=self.config.mongodb_collection)
        annotation_ds.write_mongo(uri=self.mongo_uri,
                                  database=self.config.mongodb_database,
                                  collection=self.config.mongodb_collection)

    @staticmethod
    def _check_label(label_ds):
        """
        check label
        """
        for row in label_ds.iter_rows():
            if row['anno_key'] <= 0:
                return False
        return True

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
    pipeline = ImportMultiAttributeDatasetPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Import')
    args = arg_parser.parse_args()
    run(args)
