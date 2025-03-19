#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@file: export_vistudio_pipeline.py
"""
import bcelogger
from ray.data.read_api import read_datasource
import ray
import pandas as pd
from datetime import datetime
import os
import tarfile
import shutil

from windmillcomputev1.filesystem import download_by_filesystem
from windmilltrainingv1.client.training_api_job import parse_job_name

from vistudio_image_analysis.pipeline.base_export_pipeline import BaseExportPipeline
from vistudio_image_analysis.config.arg_parser import ArgParser
from vistudio_image_analysis.processor.exporter.vistudio.vistudio_preprocessor import VistudioFormatPreprocessor

zip_extensions = ('.zip', '.tar.gz', '.tar', '.tgz')


class ExportVistudioPipeline(BaseExportPipeline):
    """
    exporter vistudio pipeline
    """

    def __init__(self, args):
        super().__init__(args)
        self.data_types = self._get_data_types()
        self.file_name = self.args.get('file_name')
        if not self.file_name.lower().endswith(zip_extensions):
            raise ValueError(f"无效的文件名: {self.file_name}")

        self.export_target = self.args.get('export_to')

    def _get_data_types(self):
        """
        get data types
        :return:
        """
        data_types = self.args.get('data_types').split(",")
        if not ((len(data_types) == 1 and data_types[0] in {"image", "annotation"}) or
                (len(data_types) == 2 and set(data_types) == {"image", "annotation"})):
            raise ValueError(f"无效的data_types: {data_types}")

        return data_types

    def run(self, parallelism: int = 10):
        """
        :return:
        """
        # datasource
        ds = read_datasource(self.datasource, parallelism=parallelism)
        if ds.count() <= 0:
            bcelogger.info("export ds count is 0")
            return

        if self.export_target == 'Dataset':
            self._export_to_dataset(ds)
        elif self.export_target == 'Filesystem':
            self._export_to_filesystem(ds)
        else:
            raise ValueError(f"Unsupported export target: {self.export_target}")

    def _export_to_dataset(self, ds):
        """
        :param ds:
        """
        location = self.create_dataset_location()
        bcelogger.info(f"export to dataset location: {location}")

        # vistudio formatter
        vs_preprocessor = VistudioFormatPreprocessor(
            config=self.config,
            labels=self.labels,
            annotation_set_name=self.annotation_set_name,
            location=location,
            split=self.split
        )
        vs_preprocessor.fit(ds).stats_

        # create dataset
        self.create_dataset(location=location)

    def _export_to_filesystem(self, ds):
        """
        :param ds:
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        export_uri = f"{self.annotation_uri}/export/{timestamp}"
        export_vs_location = f"{export_uri}/vistudioData"

        # vistudio formatter
        vs_preprocessor = VistudioFormatPreprocessor(
            config=self.config,
            labels=self.labels,
            annotation_set_name=self.annotation_set_name,
            location=export_vs_location,
            split=self.split
        )
        image_ds = vs_preprocessor.fit(ds).stats_

        # download
        dir_path = f"/export/{timestamp}/vistudioData"

        if "annotation" in self.data_types:
            # download annotation files
            download_by_filesystem(self.config.filesystem, export_vs_location, dir_path)

        if "image" in self.data_types:
            # download image files
            image_path = os.path.join(dir_path, "images")
            if not os.path.exists(image_path):
                os.makedirs(image_path, exist_ok=True)

            image_uris = image_ds.to_pandas()['file_uri'].tolist()
            for uri in image_uris:
                file_name = os.path.join(image_path, os.path.basename(uri))
                self.bs.download_file(path=uri, file_name=file_name)

        # tar and upload
        output_tar = os.path.join(dir_path, self.file_name)
        files_to_tar = os.listdir(dir_path)
        with tarfile.open(output_tar, 'w') as tar:
            for file in files_to_tar:
                full_path = os.path.join(dir_path, file)
                tar.add(full_path, arcname=file, recursive=os.path.isdir(full_path))

        upload_uri = f"{export_uri}/{self.file_name}"
        bcelogger.info(f"upload tar uri: {upload_uri}")
        self.bs.upload_file(output_tar, upload_uri)

        # update tag
        shutil.rmtree(dir_path)

        job_name = parse_job_name(self.config.job_name)
        job = self.windmill_client.get_job(job_name.workspace_id, job_name.project_name, job_name.local_name)
        tags = job.tags if job.tags is not None else {}
        tags["export_uri"] = upload_uri
        self.windmill_client.update_job(job_name.workspace_id, job_name.project_name, job_name.local_name, tags=tags)


def run(args):
    """
    main
    :param args:
    :return:
    """
    pipeline = ExportVistudioPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    arg_parser = ArgParser(kind='Export')
    args = arg_parser.parse_args()
    run(args)
