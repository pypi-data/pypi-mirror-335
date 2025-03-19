#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_coco_pipeline.py
"""

import bcelogger
import ray
from ray.data.read_api import read_datasource

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.util.label import convert_annotation_labels_id
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.processor.exporter.coco.coco_preprocessor import CocoFormatPreprocessor, \
    CocoMergePreprocessor
from vistudio_image_analysis.processor.cutter.cut_preprocessor import VistudioCutterPreprocessor
from vistudio_image_analysis.operator.writer import Writer


class ExportCocoPipeline(BaseExportPipeline):
    """
    exporter coco pipeline
    """

    def __init__(self, args):
        super().__init__(args)
        self.counter = ImageAnnotationCounter.remote()

    def run(self, parallelism: int = 10):
        """
        pipeline_coco
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
        label_dict = convert_annotation_labels_id(labels=self.labels, ignore_parent_id=True)
        coco_format_preprocessor = CocoFormatPreprocessor(
            labels=label_dict,
            merge_labels=self.merge_labels,
            counter=self.counter
        )
        format_ds = coco_format_preprocessor.transform(ds)
        # bcelogger.info("format dataset.dataset count = {}".format(format_ds.count()))

        coco_merge_preprocessor = CocoMergePreprocessor(labels=label_dict, merge_labels=self.merge_labels)
        merge_ds = coco_merge_preprocessor.fit(format_ds).stats_
        # bcelogger.info("merge dataset.dataset count = {}".format(merge_ds.count()))
        # 4: writer
        path = location[len("s3://"):].strip("/")
        writer = Writer(self.config.filesystem)
        writer.write_json_file(ds=merge_ds, base_path=path, file_name="annotation.json")

        image_count, annotation_count = ray.get([
            self.counter.get_image_count.remote(),
            self.counter.get_annotation_count.remote()
        ])

        bcelogger.info("Get_Image_Annotation_Count image_count:{} annotation_count:{}"
                       .format(image_count, annotation_count))

        artifact_metadata = {'statistics': {'imageCount': int(image_count), 'annotationCount': int(annotation_count)},
                             'paths': [location + "/"]}

        # 5: create dataset
        self.create_dataset(location=location, artifact_metadata=artifact_metadata)


def run(args):
    """
    main
    :param args:
    :return:
    """
    pipeline = ExportCocoPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
