#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Authors: chujianfei
Date:    2024/02/22-11:56 AM
"""
import argparse


class ArgParser(object):
    """
     arg parser
    """

    def __init__(self, kind: str):
        self._parser = argparse.ArgumentParser()
        self._add_common_args()

        if kind == 'Import':
            self._add_import_args()
        elif kind == 'Export':
            self._add_export_args()
        elif kind == 'Statistic':
            self._add_statistic_args()
        elif kind == 'BatchUpdate':
            self._add_batch_update_args()
        elif kind == 'DataProcessing':
            self._add_data_processing_args()
        elif kind == 'BatchAcceptInfer':
            self._add_batch_accept_infer_args()

    def _add_common_args(self):
        self._parser.add_argument(
            "--mongo-host",
            dest="mongo_host",
            required=True,
            default="10.27.240.45",
            help="mongo host",
        )

        self._parser.add_argument(
            "--mongo-port",
            dest="mongo_port",
            required=True,
            default="8718",
            help="mongo port",
        )

        self._parser.add_argument(
            "--mongo-user",
            dest="mongo_user",
            required=True,
            default="root",
            help="mongo user",
        )

        self._parser.add_argument(
            "--mongo-password",
            dest="mongo_password",
            required=True,
            default="",
            help="mongo password",
        )

        self._parser.add_argument(
            "--mongo-db",
            dest="mongo_database",
            required=True,
            default="",
            help="mongo database",
        )

        self._parser.add_argument(
            "--mongo-collection",
            dest="mongo_collection",
            required=True,
            default="",
            help="mongo collection",
        )

        self._parser.add_argument(
            "--windmill-endpoint",
            dest="windmill_endpoint",
            required=True,
            default="",
            help="windmill endpoint",
        )

        self._parser.add_argument(
            "--filesystem-name",
            dest="filesystem_name",
            required=True,
            default="",
            help="filesystem name",
        )

        self._parser.add_argument(
            "--job-name",
            dest="job_name",
            required=True,
            default="",
            help="windmill job name",
        )

        self._parser.add_argument(
            "--vistudio-endpoint",
            dest="vistudio_endpoint",
            required=True,
            default="http://10.27.240.49:8322",
            help="vistudio annotation endpoint",
        )

        self._parser.add_argument(
            "--annotation-set-name",
            dest="annotation_set_name",
            required=True,
            default="",
            help="Annotation set id, example: as01",
        )
        self._parser.add_argument(
            "--org-id",
            dest="org_id",
            required=True,
            default="",
            help="Org Id",
        )
        self._parser.add_argument(
            "--user-id",
            dest="user_id",
            required=True,
            default="",
            help="User Id",
        )
        self._parser.add_argument(
            "--mongo-shard-password",
            dest="mongo_shard_password",
            required=False,
            default="",
            help="mongo shard password",
        )

        self._parser.add_argument(
            "--mongo-shard-username",
            dest="mongo_shard_username",
            required=False,
            default="",
            help="mongo shard uasename",
        )

        self._parser.add_argument(
            "--q",
            dest="q",
            required=False,
            default="",
            help="Mongo query sql",
        )

    def _add_export_args(self):
        self._parser.add_argument(
            "--annotation-format",
            dest="annotation_format",
            required=True,
            default="COCO",
            help="Annotation format. Example: Coco",
        )

        self._parser.add_argument(
            "--export-to",
            dest="export_to",
            required=True,
            default="Dataset",
            help="Dataset or Filesystem",
        )
        self._parser.add_argument(
            "--dataset",
            dest="dataset",
            required=False,
            default="",
            help="create dataset request",
        )

        self._parser.add_argument(
            "--merge-labels",
            dest="merge_labels",
            required=False,
            default="",
            help="need merge label,key is dest label, value is need merge labels",
        )

        self._parser.add_argument(
            "--split",
            dest="split",
            required=False,
            default="",
            help="split image",
        )

        self._parser.add_argument(
            "--data-types",
            dest="data_types",
            required=False,
            default="",
            help="Image,Annotation",
        )

        self._parser.add_argument(
            "--file-name",
            dest="file_name",
            required=False,
            default="",
            help="export file name",
        )

    def _add_data_processing_args(self):
        self._parser.add_argument(
            "--operators",
            dest="operators",
            required=True,
            default="",
            help="operator params",
        )

    def _add_import_args(self):
        self._parser.add_argument(
            "--data-uri",
            dest="data_uri",
            required=True,
            default="",
            help="Only Image、Only Annotation、Image + Annotation",
        )

        self._parser.add_argument(
            "--data-types",
            dest="data_types",
            required=True,
            default="",
            help="Data type. Example: image,annotation",
        )

        self._parser.add_argument(
            "--file-format",
            dest="file_format",
            required=False,
            default="",
            help="File format. Example: zip,file,folder",
        )

        self._parser.add_argument(
            "--tag",
            dest="tag",
            required=False,
            default="",
            help="tag",
        )

        self._parser.add_argument(
            "--annotation-format",
            dest="annotation_format",
            required=False,
            default="",
            help="Annotation format. Example: Coco",
        )

    def _add_statistic_args(self):
        self._parser.add_argument(
            "--iou-threshold",
            dest="iou_threshold",
            required=False,
            default="",
            help="IoU threshold",
        )

    def _add_batch_update_args(self):
        self._parser.add_argument(
            "--object-type",
            dest="object_type",
            required=True,
            default=[],
            help="Exclude image ids",
        )
        self._parser.add_argument(
            "--updates",
            dest="updates",
            required=True,
            default='',
            help="Updates content",
        )

    def _add_batch_accept_infer_args(self):
        """
        batch accept infer args
        """
        self._parser.add_argument(
            "--artifact-names",
            dest="artifact_names",
            required=False,
            default='',
            help="model artifacts to infer",
        )
        self._parser.add_argument(
            "--policy",
            dest="policy",
            required=True,
            default='',
            help="Cover or Add",
        )
        self._parser.add_argument(
            "--infer-job-name",
            dest="infer_job_name",
            required=False,
            default='',
            help="annojob-xxxxx",
        )

    def parse_args(self):
        """
        parse args
        :return:
        """
        args = self._parser.parse_args()
        self._args = vars(args)
        return self._args

    def get_args(self):
        """
        get args
        :return:
        """
        return self._args