# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2024 Baidu.com, Inc. All Rights Reserved
"""
ShardedMongoDatasource
"""
import re
import bson
from typing import Dict, List, Optional, Callable
from pymongo import MongoClient
import pymongo
import pymongoarrow.api
import bcelogger

from ray.util.annotations import PublicAPI
from ray.data.datasource.datasource import Datasource
from ray.data.block import Block, BlockMetadata
from ray.data.datasource.datasource import ReadTask
from ray.data.datasource.mongo_datasource import MongoDatasource, _validate_database_collection_exist

from vistudio_image_analysis.config.old_config import Config


@PublicAPI(stability="alpha")
class ShardedMongoDatasource(MongoDatasource):
    """Datasource for reading from and writing to MongoDB."""

    def __init__(
            self,
            uri: str,
            database: str,
            collection: str,
            pipeline: Optional[List[Dict]] = None,
            pipeline_func: Optional[Callable[[], Block]] = None,
            schema: Optional["pymongoarrow.api.Schema"] = None,
            shard_username: str = None,
            shard_password: str = None,
            **mongo_args,
    ):
        """
        Args:
        uri: The URI of the MongoDB cluster.
        database: The database to read from.
        collection: The collection to read from.
        pipeline: The aggregation pipeline to apply.
        pipeline_func: A function that takes a pymongo.MongoClient and returns a Block.
        schema: The schema to use for reading.
        mongo_args: Additional arguments to pass to the pymongo.MongoClient constructor.
        """
        self._pipeline_func = pipeline_func
        super().__init__(uri, database, collection, pipeline=pipeline, schema=schema, **mongo_args)
        self._shard_username = shard_username
        self._shard_password = shard_password
        self.set_shard()

    def set_shard(self):
        """
            设置分片。
        如果集合不存在或已删除，则将其标记为未分片。
        如果集合的键包含多个字段或包含"hashed"值，则将其标记为未分片。

        Args:
            无参数。

        Returns:
            无返回值，直接修改了类实例的属性 _shard。
        """
        client = pymongo.MongoClient(self._uri)
        _validate_database_collection_exist(client, self._database, self._collection)

        config_database = client["config"]
        config_collections = config_database["collections"]
        config_collection_metadata = config_collections.find_one(filter={'_id': f"{self._database}.{self._collection}"})

        self._shard = True
        if config_collection_metadata is None:
            self._shard = False
        else:
            if 'dropped' in config_collection_metadata and config_collection_metadata["dropped"]:
                self._shard = False

            key_doc = config_collection_metadata["key"]
            if len(key_doc) > 1:
                self._shard = False

            elif "hashed" in key_doc.values():
                self._shard = False



    def get_collection(self):
        """
        get mongo pipeline
        :return:
        """
        user, password, host, port = parse_mongo_uri(self._uri)
        mongo_client = MongoClient(host=host, port=port, username=user, password=password)
        mongo_db = mongo_client[self._database][self._collection]
        return mongo_db

    def get_read_tasks(self, parallelism: int) -> List[ReadTask]:
        """
            获取读取任务列表，如果当前节点是分片节点则调用get_shard_read_tasks方法，否则继承自DataReader的方法。
        参数parallelism（int）- 并行度，即同时读取多少个文件。
        返回值（List[ReadTask]）- 包含所有读取任务的列表，每个元素都是一个ReadTask对象。
        """
        if self._shard:
            return self.get_shard_read_tasks(parallelism)
        return super().get_read_tasks(parallelism)

    def get_shard_read_tasks(self, parallelism: int) -> List[ReadTask]:
        """
            获取读取任务列表，每个任务对应一个分片。该函数会根据配置的并行度`parallelism`来生成相应数量的任务。
        每个任务都需要执行一次查询操作，将结果返回给Block。

        Args:
            parallelism (int): 并行度，即同时执行多少个任务。

        Returns:
            List[ReadTask]: 包含了每个分片的读取任务列表，元素类型为ReadTask。

        Raises:
            ValueError: 如果集合没有被分片或者已经被删除，则会引发ValueError异常。
        """

        def make_block(
                uri: str,
                database: str,
                collection: str,
                pipeline: List[Dict],
                pipeline_func: Optional[Callable[[], Block]],
                shard_match: Dict,
                shard_hosts: List[str],
                schema: "pymongoarrow.api.Schema",
                kwargs: dict,
                shard_username: str = None,
                shard_password: str = None,
        ) -> Block:
            from pymongo.uri_parser import parse_uri
            from pymongoarrow.api import aggregate_arrow_all

            # A range query over the partition.
            match = [
                {
                    "$match": shard_match,
                }
            ]

            uri_info = parse_uri(uri)
            uri_info["nodelist"] = shard_hosts
            shard_uri = _to_mongo_uri(uri_info, shard_username, shard_password)
            client = pymongo.MongoClient(shard_uri)

            if pipeline_func is not None:
                return pipeline_func(client[database][collection], shard_match=match, schema=schema, **kwargs)

            return aggregate_arrow_all(
                client[database][collection], match + pipeline, schema=schema, **kwargs
            )

        def _to_mongo_uri(uri_info: Dict, shard_username: str = None, shard_password: str = None) -> str:
            nodelist = uri_info.get('nodelist', [])
            username = shard_username
            if username is None or username == "":
                username = uri_info.get('username', None)

            password = shard_password
            if password is None or password == "":
                password = uri_info.get('password', None)

            database = uri_info.get('database', None)
            collection = uri_info.get('collection', None)
            options = uri_info.get('options', {})
            fqdn = uri_info.get('fqdn', None)

            host_port_str = ",".join(nodelist)

            credentials_str = ''
            if username is not None and password is not None:
                credentials_str = f"{username}:{password}@"

            db_collection_str = ''
            if database is not None and collection is not None:
                db_collection_str = f"/{database}/{collection}"

            options_str = ''
            if options:
                options_str = "?" + "&".join([f"{key}={value}" for key, value in options.items()])

            if fqdn is not None:
                args = "retryWrites=false&tls=true&tlsAllowInvalidCertificates=false&tlsAllowInvalidHostnames=false"
                mongo_uri = f"mongodb+srv://{credentials_str}{host_port_str}/{db_collection_str}{options_str}?{args}"
            else:
                mongo_uri = f"mongodb://{credentials_str}{host_port_str}/{db_collection_str}{options_str}"

            bcelogger.info("mongo_uri===={}".format(mongo_uri))
            return mongo_uri

        self._get_or_create_client()
        coll = self._client[self._database][self._collection]
        match_query = self._get_match_query(self._pipeline)

        config_database = self._client["config"]
        config_collections = config_database["collections"]
        config_collection_metadata = config_collections.find_one(
            filter={'_id': f"{self._database}.{self._collection}"})

        if config_collection_metadata is None:
            raise ValueError(f"{self._collection} is not sharded, please use precise parallelism")

        if 'dropped' in config_collection_metadata and config_collection_metadata["dropped"]:
            raise ValueError(f"{self._collection} has been dropped, please use precise parallelism")

        key_doc = config_collection_metadata["key"]
        if len(key_doc) > 1:
            raise ValueError("Invalid partitioner strategy. The Sharded partitioner does not support compound "
                             "shard keys.")
        elif "hashed" in key_doc.values():
            raise ValueError("Invalid partitioner strategy. The Sharded partitioner does not support hashed shard "
                             "keys.")

        ns_condition = {"ns": config_collection_metadata["_id"]}
        uuid_condition = {"uuid": config_collection_metadata["uuid"]}
        chunk_collections = config_database["chunks"]

        chunks = [chunk for chunk in
                  chunk_collections.find({'$or': [ns_condition, uuid_condition]},
                                         projection={"min": True, "max": True, "shard": True})
                  .sort("min", pymongo.ASCENDING)]

        shard_map = {}
        for shard in config_database["shards"].find({}, projection={"_id": True, "host": True}):
            host_ports = []
            for host_port in shard["host"].split(','):
                host_ports.append(host_port.split('/')[-1])

            shard_map[shard["_id"]] = host_ports

        # input partition has two element, first is query condition, second is shard host list
        input_partitions = []
        for chunk in chunks:
            chunk_min = chunk["min"]
            chunk_max = chunk["max"]
            # chunk min size must equals chunk max size
            query_condition = {}
            for key in chunk_min.keys():
                query_condition[key] = {
                    '$gte': chunk_min.get(key, bson.min_key),
                    '$lt': chunk_max.get(key, bson.max_key)
                }

            shard = chunk["shard"]
            input_partitions.append((query_condition, shard_map[shard]))

        read_tasks: List[ReadTask] = []
        for i, input_partition in enumerate(input_partitions):
            count_result = list(coll.aggregate(
                [
                    {"$match": {'$and': [match_query, input_partition[0]]}},
                    {'$group': {'_id': None, 'count': {'$sum': 1}}}
                ],
                allowDiskUse=True,
            ))
            count = count_result[0]['count'] if count_result else 0
            metadata = BlockMetadata(
                num_rows=count,
                size_bytes=int(count * self._avg_obj_size),
                schema=None,
                input_files=None,
                exec_stats=None,
            )
            make_shard_block_args = (
                self._uri,
                self._database,
                self._collection,
                self._pipeline,
                self._pipeline_func,
                input_partition[0],
                input_partition[1],
                self._schema,
                self._mongo_args,
                self._shard_username,
                self._shard_password
            )

            read_task = ReadTask(
                lambda args=make_shard_block_args: [make_block(*args)],
                metadata,
            )
            read_tasks.append(read_task)
        return read_tasks    


def get_mongo_uri(host='localhost', port=27017, user='root', password=''):
    """
    Get MongoDB URI string.
    Args:
        host (str): Host name or IP address of the server.
        port (int): Port number. Default is 27017.
    Returns:
        str: MongoDB URI string.
    """
    return "mongodb://{}:{}@{}:{}".format(
            user,
            password,
            host,
            port
        )


def parse_mongo_uri(uri):
    """
    Parse MongoDB URI and extract host, port, username, and password.
    Args:
        mongo_uri (str): MongoDB URI string.

    Returns:
        tuple: A tuple containing (host, port, username, password).
    """
    if uri is None:
        return None, None, None, None
    pattern = r"mongodb://([^:]+):([^@]+)@([^:]+):(\d+)"
    match = re.match(pattern, uri)

    if match:
        name = match.group(1)
        password = match.group(2)
        host = match.group(3)
        port = match.group(4)
        return name, password, host, int(port),
    else:
        raise ValueError("Failed to parse MongoDB URI")


def _mongodb_collection(host='localhost',
                        port=8717, username='root',
                        password='',
                        database='annotation',
                        collection='annotation'):
    """
        初始化mongodb连接
        """
    from pymongo import MongoClient
    mongo_client = MongoClient(host=host, port=port, username=username, password=password)
    mongo_db = mongo_client[database][collection]
    return mongo_db


def get_mongo_collection(config: Config):
    """
    get_mongo_collection
    :param config:
    :return:
    """
    mongo_user, mongo_password, mongo_host, mongo_port = parse_mongo_uri(config.mongo_uri)
    mongodb = _mongodb_collection(host=mongo_host,
                                  port=mongo_port,
                                  username=mongo_user,
                                  password=mongo_password,
                                  database=config.mongodb_database,
                                  collection=config.mongodb_collection)
    return mongodb


def _get_exist_images(config: Config, annotation_set_id: str):
    """
    获取当前标注集已有图像的image ids
    :return:
    """
    mongodb = get_mongo_collection(config=config)

    exist_image_ids = set()
    query = {
        "annotation_set_id": annotation_set_id,
        "data_type": "Image"
    }
    exist_images = mongodb.find(query, ["image_id"])
    for image in exist_images:
        exist_image_ids.add(image["image_id"])
    bcelogger.info("The existing image ids are: {}".format(exist_image_ids))
    return exist_image_ids


def _get_exist_annotation(config: Config, annotation_set_id: str, task_kind: str = "Manual"):
    """
    获取当前标注集有标注图像的image ids
    :return:
    """
    mongodb = get_mongo_collection(config=config)
    exist_annotation_ids = set()
    query = {
        "annotation_set_id": annotation_set_id,
        "data_type": "Annotation",
        "task_kind": task_kind
    }
    exist_annos = mongodb.find(query, ["image_id"])
    for anno in exist_annos:
        exist_annotation_ids.add(anno["image_id"])

    bcelogger.info("The existing anno ids are: {}".format(exist_annotation_ids))
    return exist_annotation_ids


def get_mongo_datasource(config: Config, pipeline, schema) -> Datasource:
    """
    get mongo datasource
    :return: Datasource
    """
    source = ShardedMongoDatasource(
        uri=config.mongo_uri,
        database=config.mongodb_database,
        collection=config.mongodb_collection,
        pipeline=pipeline,
        schema=schema,
        shard_username=config.mongodb_shard_username,
        shard_password=config.mongodb_shard_password

    )
    return source


def _example_read(item):
    """Example for reading data from ShardedMongoDatasource."""
    name = item["name"]
    float_field = item["float_field"]
    int_field = item["int_field"]
    print(f"name: {name}, float_field: {float_field}, int_field: {int_field}")

    return {
        "name": name,
        "float_field": float_field,
        "int_field": int_field
    }


import ray


@ray.remote
def _example_pipeline():
    """Example for using ShardedMongoDatasource by mongo pipeline."""
    from ray.data.read_api import read_datasource
    from pymongoarrow.api import Schema
    import pyarrow as pa

    uri = "mongodb://root:mongo123#@10.27.240.45:8719"
    db_name = "lyw"
    collection_name = "test"
    schema = Schema({"name": pa.string(), "float_field": pa.float64(), "int_field": pa.int32()})

    source = ShardedMongoDatasource(
        uri=uri,
        database=db_name,
        collection=collection_name,
        pipeline=[{"$match": {"name": {"$exists": True}}}],
        schema=schema)
    ds = read_datasource(source, parallelism=10)

    ds = ds.map(_example_read)
    ds.show(1)


@ray.remote
def _example_pipeline_func():
    """Example for using ShardedMongoDatasource by custom pipeline function."""
    from ray.data.read_api import read_datasource
    from pymongoarrow.api import Schema
    import pyarrow as pa

    uri = "mongodb://root:mongo123#@10.27.240.45:8719"
    db_name = "lyw"
    collection_name = "test"
    schema = Schema({"name": pa.string(), "float_field": pa.float64(), "int_field": pa.int32()})

    def pipeline_func(collection, shard_match, schema=None, **kwargs):
        from pymongoarrow.api import aggregate_arrow_all

        pipeline = [{"$match": {"name": {"$exists": True}}}]
        return aggregate_arrow_all(collection, shard_match + pipeline, schema=schema, **kwargs)

    source = ShardedMongoDatasource(
        uri=uri,
        database=db_name,
        collection=collection_name,
        pipeline_func=pipeline_func,
        schema=schema)
    ds = read_datasource(source, parallelism=10)

    ds = ds.map(_example_read)
    ds.show(1)


if __name__ == "__main__":
    ray.init(address="ray://10.27.240.45:8887")
    ray.get(_example_pipeline.remote())
    ray.get(_example_pipeline_func.remote())
    ray.shutdown()