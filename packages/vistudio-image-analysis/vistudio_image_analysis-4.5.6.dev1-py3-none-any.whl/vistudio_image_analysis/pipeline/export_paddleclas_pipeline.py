#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_paddleclas_pipeline.py
"""

from ray.data.read_api import read_datasource
import ray
import os
import bcelogger

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.processor.cutter.cut_preprocessor import VistudioCutterPreprocessor
from vistudio_image_analysis.processor.exporter.paddleclas.paddleclas_preprocessor import PaddleClasFormatPreprocessor
from vistudio_image_analysis.operator.writer import Writer


class ExportPaddleClasPipeline(BaseExportPipeline):
    """
    exporter PaddleClas pipeline
    """

    def __init__(self, args):
        super().__init__(args)
        self.counter = ImageAnnotationCounter.remote()

    def run(self, parallelism: int = 10):
        """
        pipeline_imagenet
        :return:
        """
        # 1: read datasource
        ds = read_datasource(self.datasource, parallelism=parallelism)
        bcelogger.info("read data from mongo.dataset count = {}".format(ds.count()))
        if ds.count() <= 0:
            return

        location = self.create_dataset_location()
        bcelogger.info("create windmill location. location= {}".format(location))

        # 2: split
        if self.split is not None:
            cut_preprocessor = VistudioCutterPreprocessor(self.config, location, self.split)
            ds = cut_preprocessor.transform(ds)

        # 3: transform
        label_index_map = self.build_label_index_map()
        paddleclas_format_preprocessor = PaddleClasFormatPreprocessor(
            label_index_map=label_index_map,
            merge_labels=self.merge_labels,
            counter=self.counter
        )
        formatter_ds = paddleclas_format_preprocessor.transform(ds)
        # bcelogger.info("format dataset.dataset count = {}".format(formatter_ds.count()))
        # 4: writer
        path = location[len("s3://"):].strip("/")
        writer = Writer(filesystem=self.config.filesystem)
        writer.write_txt_file(ds=formatter_ds, base_path=path, file_name="annotation.txt")

        label_txt_full_path = os.path.join(location, "labels.txt")
        self.save_label_file(file_path=label_txt_full_path, label_index_map=label_index_map)

        # 5: create dataset
        image_count, annotation_count = ray.get([
            self.counter.get_image_count.remote(),
            self.counter.get_annotation_count.remote()
        ])
        bcelogger.info(f"Get_Image_Annotation_Count image_count:{image_count} annotation_count:{annotation_count}")

        artifact_metadata = {'statistics': {'imageCount': int(image_count), 'annotationCount': int(annotation_count)},
                             'paths': [location + "/"]}
        self.create_dataset(location=location, artifact_metadata=artifact_metadata)


def run(args):
    """
    main
    :param args:
    :return:
    """
    pipeline = ExportPaddleClasPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
