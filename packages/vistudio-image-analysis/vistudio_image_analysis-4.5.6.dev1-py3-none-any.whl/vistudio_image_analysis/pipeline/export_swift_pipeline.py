#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@file: export_swift_pipeline.py
"""
import bcelogger
from ray.data.read_api import read_datasource
import ray
import pandas as pd

from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.processor.exporter.swift.swift_preprocessor import SWIFTFormatPreprocessor
from vistudio_image_analysis.operator.writer import Writer
from vistudio_image_analysis.client.annotation_api_annotationset import parse_annotation_set_name


class ExportSWIFTPipeline(BaseExportPipeline):
    """
    export swift pipeline
    """

    def __init__(self, args):
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

        # 2: transform
        format_preprocessor = SWIFTFormatPreprocessor(self.counter)
        format_ds = format_preprocessor.fit(ds).stats_

        # 3: write
        path = location[len("s3://"):].strip("/")
        writer = Writer(filesystem=self.config.filesystem)
        writer.write_json_file(ds=format_ds, base_path=path, file_name="annotation.jsonl")

        # 4: create dataset
        image_count, annotation_count = ray.get([
            self.counter.get_image_count.remote(),
            self.counter.get_annotation_count.remote()
        ])
        bcelogger.info(f"Get_Image_Annotation_Count image_count:{image_count} annotation_count:{annotation_count}")

        artifact_metadata = {
            'statistics': {'imageCount': int(image_count), 'annotationCount': int(annotation_count)},
            'paths': [location + "/"],
            'instructions': self._get_instructions(),
        }
        self.create_dataset(location=location, artifact_metadata=artifact_metadata)

    def _get_instructions(self):
        try:
            as_name = parse_annotation_set_name(self.annotation_set_name)
            prompt_templates = self.annotation_client.list_prompt_template(
                workspace_id=as_name.workspace_id,
                project_name=as_name.project_name,
                annotation_set_name=as_name.local_name,
            )
        except Exception as e:
            bcelogger.error(f"list_prompt_template error: {e}")
            raise ValueError('failed to list prompt templates')

        instructions = []
        for pt in prompt_templates.result:
            if not pt.get('instructions'):
                continue
            instructions.extend(pt.get('instructions'))

        return instructions


def run(args):
    """
    main
    :param args:
    :return:
    """
    pipeline = ExportSWIFTPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
