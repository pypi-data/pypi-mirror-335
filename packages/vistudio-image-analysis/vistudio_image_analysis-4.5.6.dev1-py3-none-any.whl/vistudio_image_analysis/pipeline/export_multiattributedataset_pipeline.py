#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   export_multiattributedataset_pipeline.py
"""
import ray
from ray.data.read_api import read_datasource
import os
import bcelogger
import yaml

from vistudio_image_analysis.statistics.counter import ImageAnnotationCounter
from vistudio_image_analysis.api.multiattributedataset import Task, Tasks
from vistudio_image_analysis.processor.exporter.multiattributedataset.multiattributedataset_preprocessor import \
    MultiAttributeDatasetFormatExportPreprocessor
from vistudio_image_analysis.util.label import merge_labels_with_attr
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.operator.writer import Writer


class ExportMultiAttributeDatasetPipeline(BaseExportPipeline):
    """
    exporter MultiAttributeDataset pipeline
    """

    def __init__(self, args):
        super().__init__(args)
        self.merge_annotation_labels = merge_labels_with_attr(labels=self.labels, merge_labels=self.merge_labels)
        self.counter = ImageAnnotationCounter.remote()

    def convert_label_to_tasks(self) -> Tasks:
        """
        convert_label_to_tasks
        """
        task_list = list()
        for index, (label_id, label_dict) in enumerate(self.merge_annotation_labels.items()):
            task_type = "image_classification"
            task_name = label_dict.get("display_name")
            anno_key = index + 1
            categories = dict
            attrbutes = label_dict.get("attributes", None)
            if attrbutes is None or len(attrbutes) == 0:
                continue

            task = Task(
                task_type=task_type,
                task_name=task_name,
                anno_key=anno_key,
                categories=attrbutes
            )
            task_list.append(task)

        tasks = Tasks(
            tasks=task_list
        )

        return tasks

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

        # 第二步 merger 算子 和 formatter 算子
        tasks = self.convert_label_to_tasks()
        mulattrdataset_format_preprocessor = MultiAttributeDatasetFormatExportPreprocessor(
            annotation_labels=self.labels,
            merge_labels=self.merge_labels,
            counter=self.counter
        )
        formater_ds = mulattrdataset_format_preprocessor.transform(ds)

        # 第三步 writer 算子
        path = os.path.join(location[len("s3://"):].strip("/"), "annotations")
        writer = Writer(filesystem=self.config.filesystem)
        writer.write_txt_file(ds=formater_ds, base_path=path, file_name="annotation.txt")

        yaml_content = yaml.dump(tasks.dict(), default_flow_style=False, allow_unicode=True)
        yaml_full_path = os.path.join(location, "annotations", "label_description.yaml")
        self.bs.write_raw(path=yaml_full_path, content_type="text/yaml", data=yaml_content.encode("utf-8"))

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
    pipeline = ExportMultiAttributeDatasetPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
