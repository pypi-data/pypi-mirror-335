# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/10/11 17:36
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : mock_mongodb.py
# @Software: PyCharm
"""
from pymongo import MongoClient, IndexModel, ASCENDING
from pymongo.errors import OperationFailure
from vistudio_image_analysis.config.old_config import Config
import bcelogger


class MongoDBClient:
    def __init__(self, args):
        self.args = args
        self.config = Config(args)
        self.mongo_uri = self.config.mongo_uri
        self.database_name = self.config.mongodb_database
        self.collection_name = self.config.mongodb_collection
        self.client = None
        self.db = None
        self.collection = None

    def init(self):
        """初始化 MongoDB 数据库的collection"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            # 启用分片
            try:
                self.client.admin.command("enableSharding", self.database_name)
                bcelogger.info(f"Sharding enabled for database: {self.database_name}")
            except OperationFailure as e:
                bcelogger.info(f"Failed to enable sharding: {e}")

            # 设置 shard key
            shard_key = {"image_id": 1}  # 定义 shard_key
            try:
                self.client.admin.command("shardCollection", f"{self.database_name}.{self.collection_name}", key=shard_key)
                bcelogger.info(f"Sharding key set for collection: {self.collection_name}")
            except OperationFailure as e:
                bcelogger.info(f"Failed to set sharding key: {e}")

            # 创建集合
            self.collection = self.db[self.collection_name]

            # 创建索引
            index_models = [
                IndexModel([("image_id", ASCENDING), ("annotation_set_id", ASCENDING), ("data_type", ASCENDING),
                             ("artifact_name", ASCENDING)], unique=True),
                IndexModel(
                    [("annotation_set_id", ASCENDING), ("data_type", ASCENDING), ("image_created_at", ASCENDING)]),
            ]

            try:
                self.collection.create_indexes(index_models)
                bcelogger.info(f"Indexes created for collection: {self.collection_name}")
            except Exception as e:
                bcelogger.info(f"Failed to create indexes: {e}")
        except Exception as e:
            bcelogger.info(f"Could not connect to MongoDB: {e}")

    def insert(self, documents):
        """插入单条或多条文档到 MongoDB 集合"""
        try:
            if isinstance(documents, list):
                result = self.collection.insert_many(documents)
                bcelogger.info(f"Inserted multiple documents with IDs: {result.inserted_ids}")
            else:
                result = self.collection.insert_one(documents)
                bcelogger.info(f"Inserted single document with ID: {result.inserted_id}")
        except Exception as e:
            bcelogger.info(f"Failed to insert documents: {e}")

    def delete_collection(self):
        # 删除集合
        try:
            self.collection.drop()
            bcelogger.info(f"Collection {self.collection_name} dropped successfully.")
        except Exception as e:
            bcelogger.info(f"Failed to drop collection: {e}")

    def close(self):
        """关闭数据库连接"""
        self.client.close()
        bcelogger.info("MongoDB connection closed.")


# 使用示例
if __name__ == "__main__":
    # 假设 config 是一个包含 MongoDB 配置信息的模块
    args = {'mongo_host': '10.27.240.45',
            'mongo_port': '8719',
            'mongo_user': 'root',
            'mongo_password': 'mongo123#',
            'mongo_database': 'annotation_ut',
            'mongo_collection': 'annotation_ut'}

    mongo_client = MongoDBClient(args)

    # 示例操作
    mongo_client.init()
    # 删除集合
    mongo_client.delete_collection()

    # 关闭连接
    mongo_client.close()
