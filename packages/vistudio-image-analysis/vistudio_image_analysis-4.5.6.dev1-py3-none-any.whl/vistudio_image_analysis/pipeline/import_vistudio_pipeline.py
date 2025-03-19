#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
@File: import_vistudio_pipeline.py
"""
import ray.data
import bcelogger
import pandas as pd

from vistudio_image_analysis.pipeline.base_import_pipeline import BaseImportPipline
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.operator.reader import Reader
from vistudio_image_analysis.processor.importer.label.label_preprocessor import LabelFormatPreprocessor
from vistudio_image_analysis.processor.importer.annotation.vistudio_preprocessor import VistudioFormatPreprocessor
from vistudio_image_analysis.processor.importer.zip.zip_preprocessor import ZipFormatPreprocessor


class ImportVistudioPipeline(BaseImportPipline):
    """
    导入Vistudio标注数据
    """
    def __init__(self, args):
        super().__init__(args)
        self.only_anno = False

    def _import_annotation(self):
        """
        导入标注
        """
        # 读文件
        vistudio_reader = Reader(filesystem=self.config.filesystem, annotation_set_id=self.annotation_set_id)
        if self.file_format == 'zip':
            zip_file_uris = vistudio_reader.get_zip_file_uris(data_uri=self.data_uri)
            if len(zip_file_uris) > 0:
                zip_formatter = ZipFormatPreprocessor(config=self.config)
                self.data_uri = zip_formatter.fit(ds=ray.data.from_items(zip_file_uris)).stats_

        file_uris = vistudio_reader.get_file_uris(
            data_uri=self.data_uri,
            data_types=self.data_types,
            annotation_format=self.annotation_format
        )

        if len(file_uris) == 0:
            self.update_annotation_job("未找到标注文件")
            raise Exception("未找到标注文件")

        # 兼容预警导入过来的数据
        if all(uri.endswith('image.jsonl') for uri in file_uris):
            self.data_types = ['image']

        ds = vistudio_reader.read_json(file_uris)
        bcelogger.info("Import vistudio annotation count = {}".format(ds.count()))

        label_formatter = LabelFormatPreprocessor(
            config=self.config,
            labels=self.labels,
            annotation_format=self.annotation_format,
            annotation_set_category=self.annotation_set_category
        )
        label_dict = label_formatter.fit(ds).stats_
        import_labels_list = label_dict.get("import_labels")
        need_add_labels = label_dict.get("need_add_labels")
        bcelogger.info(f"import coco need add labels:{need_add_labels}")

        if need_add_labels is not None and len(need_add_labels) > 0:
            self.import_labels(need_add_labels=need_add_labels)
            self._get_labels()

        vistudio_preprocessor = VistudioFormatPreprocessor(
            config=self.config,
            annotation_set_id=self.annotation_set_id,
            annotation_set_name=self.annotation_set_name,
            data_uri=self.data_uri,
            labels=self.labels,
            import_labels=import_labels_list,
            data_types=self.data_types,
            tag=self.tag,
            annotation_set_category=self.annotation_set_category
        )
        final_ds_dict = vistudio_preprocessor.fit(ds).stats_

        if not self.only_anno:
            image_ds = final_ds_dict.get("image_ds")
            bcelogger.info("Start write image ...")
            image_ds.write_mongo(
                uri=self.mongo_uri,
                database=self.config.mongodb_database,
                collection=self.config.mongodb_collection
            )

        annotation_ds = final_ds_dict.get("annotation_ds")
        bcelogger.info("Start write annotation ...")
        annotation_ds.write_mongo(
            uri=self.mongo_uri,
            database=self.config.mongodb_database,
            collection=self.config.mongodb_collection
        )

        prediction_ds = final_ds_dict.get("prediction_ds")
        bcelogger.info("Start write prediction ...")
        prediction_ds.write_mongo(
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
    pipeline = ImportVistudioPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Import')
    args = arg_parser.parse_args()
    run(args)
