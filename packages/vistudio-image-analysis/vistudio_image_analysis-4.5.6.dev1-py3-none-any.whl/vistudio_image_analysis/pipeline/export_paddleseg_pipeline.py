#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_pipeline.py
"""
import sys
import os
import bcelogger
import ray
from ray.data import read_datasource

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.processor.cutter.cut_preprocessor import VistudioCutterPreprocessor
from vistudio_image_analysis.processor.exporter.paddleseg.cityscape_preprocessor import PaddleSegFormatPreprocessor
from vistudio_image_analysis.operator.writer import Writer


class ExportPaddleSegPipeline(BaseExportPipeline):
    """
    exporter PaddleClas pipeline
    """

    def __init__(self, args: dict()):
        super().__init__(args)
        self.counter = ImageAnnotationCounter.remote()

    def run(self, parallelism: int = 10):
        """
        pipeline_cityscape
        :return:
        """
        # 1: datasource
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
        paddleseg_format_preprocessor = PaddleSegFormatPreprocessor(
            merge_labels=self.merge_labels,
            label_index_map=label_index_map,
            counter=self.counter
        )
        format_ds = paddleseg_format_preprocessor.transform(ds)
        # bcelogger.info("format dataset.dataset count = {}".format(format_ds.count()))

        # 4: write
        path = location[len("s3://"):].strip("/")

        writer = Writer(filesystem=self.config.filesystem)

        label_images_ds = format_ds.flat_map(lambda row: row["label_images"])
        writer.write_image_file(ds=label_images_ds, base_path=path + "/labels/")

        annotations_ds = format_ds.flat_map(lambda row: row["annotations"])
        writer.write_txt_file(ds=annotations_ds, base_path=path, file_name="annotation.txt")

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
    pipeline = ExportPaddleSegPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
