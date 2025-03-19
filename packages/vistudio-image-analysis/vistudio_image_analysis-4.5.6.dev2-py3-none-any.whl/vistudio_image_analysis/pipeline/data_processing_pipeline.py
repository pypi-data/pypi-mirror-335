#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    : data_processing_pipeline.py
"""

import sys
import os
import bcelogger
import json

from vistudio_image_analysis.util import string
from ray.data.read_api import read_datasource
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.processor.data_processor.inference_preprocessor import InferencePreprocessor
from vistudio_image_analysis.pipeline.base_data_processing_pipeline import BaseDataProcessingPipeline
from vistudio_image_analysis.processor.data_processor.merge_label_preprocessor import MergeLabelPreprocessor

__work_dir__ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, __work_dir__)


class DataProcessingPipeline(BaseDataProcessingPipeline):
    """
    DataProcessingPipeline
    """

    def __init__(self, args):
        super().__init__(args)

    def run(self, parallelism: int = 10):
        """
        pipeline_coco
        :return:
        """
        ds = read_datasource(self.datasource, parallelism=parallelism)
        bcelogger.info("read data from mongo.dataset count = {}".format(ds.count()))
        if ds.count() <= 0:
            return
        operator_params = json.loads(string.decode_from_base64(self.args.get("operators")))
        for params in operator_params:
            bcelogger.info(f"operator_name: {params.get('operator_name')}")
            if params.get("operator_name") == "infer":
                params["annotation_set_name"] = self.args.get("annotation_set_name")
                params["q"] = self.args.get("q")
                inference_preprocessor = InferencePreprocessor(self.config, params)
                inferd_ds = inference_preprocessor.fit(ds).stats_
                bcelogger.info(f"infer end")
            elif params.get("operator_name") == "merge_label":
                merge_generator = MergeLabelPreprocessor(self.config, params)
                merge_ds = merge_generator.transform(ds)
                bcelogger.info(f"merge_labels end, merge_ds.count:{merge_ds.take_all()}")


def run(args):
    """
    main
    :param args:
    :return:
    """

    pipeline = DataProcessingPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='DataProcessing')
    args = arg_parser.parse_args()
    run(args)
