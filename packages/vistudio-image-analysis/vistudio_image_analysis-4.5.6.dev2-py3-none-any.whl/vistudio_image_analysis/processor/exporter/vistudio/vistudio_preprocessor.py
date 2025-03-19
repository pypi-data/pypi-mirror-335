#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
vistudio_preprocessor.py
"""

from typing import Union, Dict, Any, List
import os
import json
from ray.data.preprocessor import Preprocessor

from windmillcomputev1.filesystem import blobstore

from vistudio_image_analysis.operator.vistudio_formatter import VistudioFormatter
from vistudio_image_analysis.operator.vistudio_cutter import VistudioCutter
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.operator.writer import Writer


class VistudioFormatPreprocessor(Preprocessor):
    """
    use this Preprocessor to convert to vistudio_v1
    """

    def __init__(
            self,
            config: Config,
            location: str = "",
            labels: Union[List] = None,
            annotation_set_name: str = "",
            split: Union[Dict] = None,
    ):
        self.location = location
        self.labels = labels
        self.annotation_set_name = annotation_set_name
        self.config = config
        self.split = split

        self.bs = blobstore(filesystem=self.config.filesystem)

    def _fit(self, ds: "Dataset") -> "Preprocessor":
        if self.split is not None:
            cut_operator = VistudioCutter(self.config.filesystem, self.location, self.split)
            ds = cut_operator.cut_images_and_annotations(source=ds.to_pandas())

        path = f"{self.location}/meta.json"
        self.save_vistudio_meta_json_file(file_path=path)

        vs_formatter = VistudioFormatter()
        image_ds, anno_ds, pred_ds = vs_formatter.from_vistudio_v1(ds)

        path = os.path.join(self.location[len("s3://"):], "jsonls")
        writer = Writer(self.config.filesystem)

        writer.write_json_file(ds=image_ds, base_path=path, file_name="image.jsonl")
        if anno_ds.count() > 0:
            writer.write_json_file(ds=anno_ds, base_path=path, file_name="annotation.jsonl")
        if pred_ds.count() > 0:
            writer.write_json_file(ds=pred_ds, base_path=path, file_name="prediction.jsonl")

        self.stats_ = image_ds
        return self

    def save_vistudio_meta_json_file(self, file_path: str):
        """
        save vistudio meta.json file
        :param file_path:
        :return:
        """
        vs_labels = list()
        if self.labels is not None:
            for label in self.labels:
                item = {
                    "id": label["local_name"],
                    "name": label["display_name"],
                    "parent_id": label["parent_id"]
                }
                vs_labels.append(item)

        meta = {
            "data_type": "Label",
            "annotation_set_name": self.annotation_set_name,
            "labels": vs_labels
        }

        data_json = json.dumps(meta)
        self.bs.write_raw(path=file_path, content_type="application/json", data=data_json)




