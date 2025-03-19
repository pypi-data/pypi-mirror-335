#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_pipeline.py
"""

from ray.data.read_api import read_datasource
import ray
import bcelogger

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.processor.exporter.paddleocr.paddleocr_preprocessor import \
    PaddleOCRRecognFormatPreprocessor
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.operator.writer import Writer


class ExportPaddleOCRRecognPipeline(BaseExportPipeline):
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
        # 第一步 datasource 算子
        ds = read_datasource(self.datasource, parallelism=parallelism)
        bcelogger.info("read data from mongo.dataset count = {}".format(ds.count()))
        if ds.count() <= 0:
            return

        location = self.create_dataset_location()
        bcelogger.info("create windmill location. location= {}".format(location))

        label_path = location + "/labels/empty_file.txt"
        labels_list = []
        self.bs.write_raw(path=label_path, content_type="text/plain", data=''.join(labels_list))

        # 第二步 formatter 算子
        paddleocr_format_preprocessor = PaddleOCRRecognFormatPreprocessor(
            config=self.config,
            location=location,
            counter=self.counter
        )
        formater_ds = paddleocr_format_preprocessor.transform(ds)
        # bcelogger.info("format dataset.dataset count = {}".format(formater_ds.count()))

        # 第三步 writer 算子
        # 写入 annotation.txt
        path = location[len("s3://"):].strip("/")
        writer = Writer(filesystem=self.config.filesystem)
        writer.write_txt_file(ds=formater_ds, base_path=path, file_name="annotation.txt")

        # 第四步 生成dataset
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
    pipeline = ExportPaddleOCRRecognPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
