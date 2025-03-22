"""
数据库工具
"""

from .tools import now, time_next
from .tools import logger
from .tools import to_excel
from .tools import to_json
from .tools import read_json

__all__ = [
    "diskcache",
    "diskcache_deque",
    "duckdb",
    "mongodb",
    "mongo_create_index",
    "mongo_distinct",
    "mongo_dict",
    "mongo_from_jsonl",
    "mongo_insert",
    "mongo_id",
    "mongo_list_collection_names",
    "mongo_queue",
    "mongo_sample",
    "mongo_tongji",
    "mongo_to_csv",
    "mongo_to_jsonl",
    "mysql",
    "oss2_bucket",
    "oss2_find_file",
    "oss2_upload_content",
    "oss2_upload_file",
    "oss2_sign_url",
    "oss2_put_object_acl",
    "oss2_set_object_acl",
    "redisdb",
    "redis_queue",
]


def duckdb(query="select now()", *, db=None):
    """
    使用 DuckDB 执行 SQL 语句

    - query: SQL 语句
    - db: 数据库路径
    """
    try:
        import duckdb
    except Exception:
        print("DuckDB 导入失败, 请先安装 DuckDB")
        print("pip install duckdb")
        return

    if db:
        connect = duckdb.connect(db)
        return connect

    return duckdb.sql(query)


def diskcache(directory: str = None, timeout: int = 60):
    """
    通过 diskcache 实现缓存

    - directory: 缓存目录, 默认值为 temp 目录
    - timeout: SQLite 连接超时时间, 默认值为60秒
    """
    try:
        from diskcache import Cache
    except Exception:
        print("请先安装 diskcache")
        print("pip install diskcache")

    return Cache(directory, timeout)


def diskcache_deque(iterable=(), directory=None, maxlen=None):
    """
    通过 diskcache 实现 deque 序列化

    - iterable: 可迭代对象, 默认为空
    - directory: 缓存目录, 默认值为 temp 目录
    - maxlen: 最大长度, 默认值为 None
    """
    try:
        from diskcache import Deque
    except Exception:
        print("请先安装 diskcache")
        print("pip install diskcache")

    return Deque(iterable, directory=directory, maxlen=maxlen)


def oss2_bucket(
    endpoint: str,
    bucket_name: str,
    access_key_id: str,
    access_key_secret: str,
    proxies: dict = None,
):
    """
    oss2 连接 bucket

    - endpoint: oss 地址
    - bucket_name: oss bucket 名称
    - access_key_id: oss 访问密钥
    - access_key_secret: oss 访问密钥
    - proxies: 代理
    """
    import oss2

    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name, proxies=proxies)
    return bucket


def oss2_put_object_acl(
    bucket,
    key,
    content,
    acl: str = "default",
):
    """
    上传 content 到 oss, 并设置 acl

    - bucket: oss2.Bucket 对象
    - key: 上传到OSS的文件名
    - content: 本地内容content
    - acl: 权限, 支持 default, public-read, public-read-write, private
    """
    import oss2

    if acl == "default":
        permission = oss2.OBJECT_ACL_DEFAULT
    if acl == "public-read":
        permission = oss2.OBJECT_ACL_PUBLIC_READ
    if acl == "public-read-write":
        permission = oss2.OBJECT_ACL_PUBLIC_READ_WRITE
    if acl == "private":
        permission = oss2.OBJECT_ACL_PRIVATE

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    try:
        z = bucket.put_object(key, content, headers={"x-oss-object-acl": permission})
        logger.success(f"文件上传成功, 文件路径: {key}")
        return z
    except Exception as e:
        logger.error(f"oss2_put_object_acl 发生错误: {e}")


def oss2_set_object_acl(
    bucket,
    key,
    acl: str = "default",
):
    """
    上传 content 到 oss, 并设置 acl

    - bucket: oss2.Bucket 对象
    - key: 上传到OSS的文件名
    - acl: 权限, 支持 default, public-read, public-read-write, private
    """
    import oss2

    if acl == "default":
        permission = oss2.OBJECT_ACL_DEFAULT
    if acl == "public-read":
        permission = oss2.OBJECT_ACL_PUBLIC_READ
    if acl == "public-read-write":
        permission = oss2.OBJECT_ACL_PUBLIC_READ_WRITE
    if acl == "private":
        permission = oss2.OBJECT_ACL_PRIVATE

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    try:
        z = bucket.put_object_acl(key, permission=permission)
        logger.success(f"{key} 权限设置为 {acl}")
        return z
    except Exception as e:
        logger.error(f"oss2_put_object_acl 发生错误: {e}")


def oss2_upload_file(bucket, key, filepath, proxies: dict = None):
    """
    上传文件到 oss

    - bucket: oss2.Bucket 对象
    - key: 上传到OSS的文件名
    - filepath: 本地文件路径
    - proxies: 代理, dict
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    if proxies:
        bucket.proxies = proxies
    try:
        z = bucket.put_object_from_file(key, filepath)
        logger.success(f"文件 {filepath} 上传成功, 文件路径: {key}")
        return z
    except Exception as e:
        logger.error(f"oss2_upload_file 发生错误: {e}")
        return


def oss2_upload_content(bucket, key, content, proxies: dict = None):
    """
    上传 content 到 oss

    - bucket: oss2.Bucket 对象
    - key: 上传到OSS的文件名
    - content: 本地内容content
    - proxies: 代理
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    if proxies:
        bucket.proxies = proxies
    try:
        z = bucket.put_object(key, content)
        logger.success(f"文件上传成功, 文件路径: {key}")
        return z
    except Exception as e:
        logger.error(f"oss2_upload_content 发生错误: {e}")
        return


def oss2_sign_url(
    bucket,
    key,
    method="GET",
    expires: int = 300,
    headers: None = None,
    params: None = None,
    slash_safe: bool = False,
    additional_headers: None = None,
):
    """
    oss 生成签名的 url

    - bucket: oss2.Bucket 对象
    - key: 上传到OSS的文件名
    - method: GET, PUT, POST, DELETE, HEAD
    - expires: 过期时间, 单位为秒, 默认 300 秒
    - headers: 请求头, 字典
    - params: 请求参数, 字典
    - slash_safe: 是否安全, 默认 False
    - additional_headers: 附加请求头, 字典
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return

    try:
        url = bucket.sign_url(
            method,
            key,
            expires=expires,
            headers=headers,
            params=params,
            slash_safe=slash_safe,
            additional_headers=additional_headers,
        )
        logger.success(f"文件签名成功, url为: {url}")
        return url
    except Exception as e:
        logger.error(f"oss2_sign_url 发生错误: {e}")


def oss2_find_file(bucket, prefix: str, size1: int = 0, size2: int = None):
    """
    寻找 oss 文件, 指定 size1 和 size2 可以筛选特定大小的文件。默认单位为 KB。返回值为字典。

    可以通过 len 统计文件数量。可以通过 sum 统计返回值字典的 values 统计文件夹文件的总大小, 单位为KB。

    - bucket: oss2.Bucket 对象
    - prefix: 文件夹路径, 例如 'etl/atk'
    - size1: 文件大小下限, 单位为 KB, 默认0 KB
    - size2: 文件大小上限, 单位为 KB, 默认 None 表示不限制
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    d = {}
    for obj in oss2.ObjectIterator(bucket, prefix):
        t = obj.size / 1024
        if size2 is None:
            if size1 < t and not obj.is_prefix():
                print(f"文件名:{obj.key}  文件大小: {t:.2f} KB")
                d[obj.key] = t
        else:
            if size1 < t < size2 and not obj.is_prefix():
                print(f"文件名:{obj.key}  文件大小: {t:.2f} KB")
                d[obj.key] = t
    return d


def redisdb(
    host="localhost",
    port=6379,
    db=0,
    username=None,
    password=None,
    decode_responses=True,
    url=None,
    **kwargs,
):
    """
    ## 连接 redis 数据库

    - host: redis 主机
    - port: redis 端口
    - db: redis 数据库
    - password: redis 密码
    - decode_responses: 是否解码响应, 默认 True
    - url: 链接, 优先级高于 host, port, db, username, password

    #### url example

    - redis://[[username]:[password]]@localhost:6379/0
    - rediss://[[username]:[password]]@localhost:6379/0
    - unix://[username@]/path/to/socket.sock?db=0[&password=password]


    """
    import redis

    if url:
        return redis.Redis.from_url(url, decode_responses=decode_responses, **kwargs)

    return redis.Redis(
        host=host,
        port=port,
        db=db,
        username=username,
        password=password,
        decode_responses=decode_responses,
        **kwargs,
    )


def mongodb(host, database=None, port: int | None = None, **kwargs):
    """
    连接 MongoDB, 有 database 时返回指定 Database, 否则返回 Client。

    - host: mongo 链接
    - database: 数据库名称
    - port: mongo 端口

    host 有密码格式: "mongodb://username:password@192.168.0.1:27017/"
    host 无密码格式: "mongodb://192.168.0.1:27017/"
    """
    from pymongo import MongoClient

    try:
        client = MongoClient(host, port, **kwargs)
        if database:
            db = client[database]
            db.list_collection_names()
            logger.success(f"MongoDB 成功连接到 {database}")
            return db
        else:
            client.list_database_names()
            logger.success(f"MongoDB 成功连接到 {host}")
            return client
    except Exception as e:
        logger.error("MongoDB 连接失败:", str(e))
        return None


def mongo_sample(
    table,
    match: dict = {},
    *,
    size: int = 1000,
    excel: bool = True,
) -> list:
    """
    mongodb 随机样本抽样

    - table: mongo 表(集合), Collection 对象
    - match: 匹配条件，默认不筛选
    - size: 随机样本数量
    - excel: 是否导出 excel文件, 默认 True
    """
    results = list(
        table.aggregate([
            {"$match": match},
            {"$sample": {"size": size}},
        ])
    )
    if excel:
        import pandas as pd

        table_name = table.name
        filename = f"{now(7)}_{table_name}_sample_{size}.xlsx"
        df = pd.DataFrame(results)
        to_excel(df, filename)

    return results


def mongo_tongji(
    mongodb,
    prefix: str = "",
    tongji_table: str = "tongji",
) -> dict:
    """
    统计 mongodb 每个集合的`文档数量`

    - mongodb: mongo 库
    - prefix: mongo 表(集合)前缀, 默认空字符串可以获取所有表, 字段名称例如 `统计_20240101`。
    - tongji_table: 统计表名称，默认为 tongji
    """

    tongji = mongodb[tongji_table]
    key = prefix if prefix else f"统计_{now(7)}"
    collection_count_dict = {
        **(
            tongji.find_one({"key": key}).get("count")
            if tongji.find_one({"key": key})
            else {}
        ),
        **({
            i: mongodb[i].estimated_document_count()
            for i in mongodb.list_collection_names()
            if i.startswith(prefix)
        }),
    }
    tongji.update_one(
        {"key": prefix if prefix else f"统计_{now(7)}"},
        {"$set": {"count": collection_count_dict}},
        upsert=True,
    )
    return dict(sorted(collection_count_dict.items()))


def mongo_distinct(table, *fields):
    """
    mongo distinct 去重

    - table: mongo 表(集合), Collection 对象
    - fields: 字段名称，支持多个字段
    """
    pipeline = [{"$group": {"_id": {i: f"${i}" for i in fields}}}]
    agg_results = table.aggregate(pipeline)
    results = [i["_id"] for i in agg_results]
    return results


def mongo_id(oid: str | bytes | None = None):
    """
    Mongo 生成 id

    - oid: ObjectId, 默认为 None
    """
    from bson import ObjectId

    return ObjectId(oid)


def mongo_insert(
    table,
    data: list[dict] | dict,
    ordered=False,
    bypass_document_validation=False,
    session=None,
    comment=None,
):
    """
    mongo 批量插入

    - table: mongo 表(集合), Collection 对象
    - data: 数据列表，每个元素为一个字典
    - ordered: 是否按顺序插入，默认为False
    - bypass_document_validation: 是否绕过文档验证，默认为False
    - session: 事务会话
    - comment: 注释
    """
    try:
        if isinstance(data, dict):
            data = [data]
        results = table.insert_many(
            data,
            ordered=ordered,
            bypass_document_validation=bypass_document_validation,
            session=session,
            comment=comment,
        )
        logger.success(f"{table.name} 插入 {len(results.inserted_ids)} 条数据")

    except Exception as e:
        logger.success(f"{table.name} 插入 {e.details.get('nInserted')} 条数据")


def mongo_to_csv(table, output_file: str | None = None, batch_size: int = 1000):
    """
    从MongoDB集合中导出数据到CSV文件

    - table: MongoDB的集合名称或Collection对象
    - output_file: 导出的CSV文件路径, 默认值为`表名.csv`
    - batch_size: 批处理大小，默认为1000
    """
    import pymongo
    import csv

    if not isinstance(table, pymongo.collection.Collection):
        raise ValueError("table 必须是 MongoDB Collection对象")

    table_name = table.name

    if not output_file:
        output_file = f"{table_name}.csv"

    try:
        count_documents = table.estimated_document_count()
        logger.info(f"开始导出 {table_name}, 总数据量 {count_documents}")
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=1)
            cursor = table.find().batch_size(batch_size)
            header = table.find_one().keys() if table.find_one() else []
            writer.writerow(header)
            for doc in cursor:
                record = []
                for key in header:
                    if key not in doc:
                        record.append("")
                    else:
                        record.append(str(doc[key]))
                writer.writerow(record)
        logger.success(f"{table_name} 导出成功, 文件路径: {output_file}")
    except Exception as e:
        logger.error(f"{table_name} 导出发生错误: {e}")


def mongo_to_jsonl(table, output_file: str | None = None, batch_size: int = 1000):
    """
    mongo 导出 jsonl

    - table: mongo 表(集合), Collection 对象
    - output_file: 导出的 jsonl 文件名, 默认值为`表名.jsonl`
    - batch_size: 批处理大小，默认为1000
    """
    import pymongo
    import json

    if not isinstance(table, pymongo.collection.Collection):
        raise ValueError("table 必须是 MongoDB Collection对象")

    table_name = table.name

    if not output_file:
        output_file = f"{table_name}.jsonl"
    try:
        count_documents = table.estimated_document_count()
        logger.info(f"开始导出 {table_name}, 总数据量 {count_documents}")
        with open(output_file, "w", encoding="utf-8") as f:
            cursor = table.find().batch_size(batch_size)
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
        logger.success(f"{table_name} 导出成功, 文件路径: {output_file}")
    except Exception as e:
        logger.error(f"{table_name} 导出发生错误: {e}")


def mongo_from_jsonl(jsonl_file: str, table, batch_size: int = 1000):
    """
    从 JSONL 文件导入数据到 MongoDB 集合

    - jsonl_file: JSONL 文件路径
    - table: MongoDB 集合，Collection 对象
    - batch_size: 批处理大小，默认为 1000
    """
    import pymongo
    import json

    if not isinstance(table, pymongo.collection.Collection):
        raise ValueError("table 必须是 MongoDB Collection 对象")

    table_name = table.name

    try:
        logger.info(f"开始导入 {jsonl_file} 到集合 {table_name}")
        with open(jsonl_file, "r", encoding="utf-8") as f:
            batch = []
            for line in f:
                doc = json.loads(line)
                if "_id" in doc and isinstance(doc["_id"], str):
                    try:
                        doc["_id"] = mongo_id(doc["_id"])
                    except Exception:
                        pass
                batch.append(doc)
                if len(batch) >= batch_size:
                    mongo_insert(table, batch)
                    batch = []
            if batch:
                table.insert_many(batch)

        logger.info(f"导入完成，文件 {jsonl_file} 已成功导入到集合 {table_name}")
    except Exception as e:
        logger.error(f"导入发生错误: {e}")


def mysql(
    host="localhost",
    user="root",
    password="",
    database="",
    query="SELECT now()",
):
    """
    连接MySQL，查询返回结果

    - host: MySQL 主机
    - user: MySQL 用户名
    - password: MySQL 密码
    - database: MySQL 数据库名
    - query: 查询语句
    """
    import pymysql

    try:
        # 连接数据库
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        print(f"MySQL读取失败: {e}")
        return None


def redis_queue(redisdb, name, use_existing: bool = True):
    """
    redis 队列

    - redisdb: redis 数据库, redis.Redis 对象
    - name: 队列名称
    - use_existing: 是否使用已存在的队列, 默认为 True
    """

    class RedisQueue:
        def __init__(self, redisdb, name, use_existing):
            """
            redis 队列

            - redisdb: redis 数据库, redis.Redis 对象
            - name: 队列名称
            - use_existing: 是否使用已存在的队列, 默认为 True
            """
            self.redisdb = redisdb
            self.name = name
            self._index = 0
            self.use_existing = use_existing
            if not use_existing:
                self.redisdb.delete(self.name)

        def __len__(self):
            return self.redisdb.llen(self.name)

        def __getitem__(self, index):
            return read_json(self.redisdb.lindex(self.name, index))

        def push(self, item):
            self.redisdb.rpush(self.name, to_json(item))

        def pop(self):
            item = self.redisdb.lpop(self.name)
            return read_json(item) if item else None

        def clear(self):
            self.redisdb.delete(self.name)

        def __iter__(self):
            return self

        def __next__(self):
            if self._index >= len(self):
                self._index = 0
                raise StopIteration
            self._index += 1
            item = self[self._index - 1]
            if item is None:
                raise StopIteration
            return item

        def __repr__(self):
            return f"RedisQueue({self.name})"

        def __str__(self):
            return f"RedisQueue({self.name})"

    return RedisQueue(redisdb, name, use_existing)


def mongo_create_index(table, index_name, unique=False, background=True):
    """
    mongo 创建索引

    - table: mongo 表(集合), Collection 对象
    - index_name: 索引名称
    - unique: 是否唯一索引, 默认为 False
    - background: 是否后台创建索引, 默认为 True
    """
    return table.create_index(index_name, unique=unique, background=background)


def mongo_queue(table, use_existing: bool = True):
    """
    mongo 队列

    - table: mongo 表(集合), Collection 对象
    - use_existing: 是否使用已存在的队列, 默认为 True
    """

    class MongoQueue:
        def __init__(self, table, use_existing):
            """
            mongo 队列

            - table: mongo 表(集合), Collection 对象
            - use_existing: 是否使用已存在的队列, 默认为 True
            """
            self.table = table
            self.name = table.name
            self.use_existing = use_existing
            if not use_existing:
                self.table.delete_many({})

        def __len__(self):
            return self.table.count_documents({})

        def push(self, item):
            _id = mongo_id()
            self.table.insert_one({
                "_id": _id,
                "key": _id,
                "value": item,
                "time": now(1),
            })

        def pop(self):
            item = self.table.find_one_and_delete({})
            return item.get("value") if item else None

        def clear(self):
            self.table.delete_many({})

        def __iter__(self):
            cursor = self.table.find()
            for item in cursor:
                yield item

        def __repr__(self):
            return f"MongoQueue({self.name})"

        def __str__(self):
            return f"MongoQueue({self.name})"

    return MongoQueue(table, use_existing)


def mongo_dict(table):
    """
    mongo 字典

    - table: mongo 表(集合), Collection 对象
    """

    class MongoDict:
        def __init__(self, table):
            """
            mongo 字典

            - table: mongo 表(集合), Collection 对象
            """
            self.table = table
            self.table.create_index("key", unique=True, background=True)

        def __getitem__(self, key):
            item = self.table.find_one({"key": key})
            if item is not None:
                return item["value"]
            else:
                raise KeyError(f"Key '{key}' not found in {self.table.name}")

        def get(self, key, default=None):
            """
            获取值，如果不存在则返回默认值

            - key: 键
            - default: 默认值
            """
            item = self.table.find_one({"key": key})
            if item is not None:
                return item["value"]
            else:
                return default

        def __setitem__(self, key, value):
            self.table.update_one(
                {"key": key},
                {"$set": {"value": value, "time": now(1)}},
                upsert=True,
            )

        def __delitem__(self, key):
            self.table.delete_one({"key": key})

        def pop(self, key, default=None):
            """
            删除并返回值，如果不存在则返回默认值

            - key: 键
            - default: 默认值
            """
            item = self.table.find_one_and_delete({"key": key})
            if item is not None:
                return item["value"]
            else:
                return default

        def clear(self):
            """
            删除所有键值对
            """
            self.table.delete_many({})

        def keys(self):
            """
            返回所有键
            """
            return [item["key"] for item in self.table.find()]

        def values(self):
            """
            返回所有值
            """
            return [item["value"] for item in self.table.find()]

        def items(self):
            """
            返回所有键值对
            """
            return [(item["key"], item["value"]) for item in self.table.find()]

        def __contains__(self, key):
            return self.table.find_one({"key": key}) is not None

        def __len__(self):
            return self.table.count_documents({})

        def __iter__(self):
            cursor = self.table.find()
            for item in cursor:
                yield item

        def __repr__(self):
            return f"MongoDict({self.table.name})"

        def __str__(self):
            return f"MongoDict({self.table.name})"

    return MongoDict(table)


def mongo_list_collection_names(table, startswith="", before=0):
    """
    列出表名, 支持前缀和后缀日期过滤

    - table: mongo 表(集合), Collection 对象
    - startswith: 表名前缀, 默认为空
    - before: 后缀 %Y%m%d 日期过滤几天前, 默认为 0, 不过滤
    """
    return sorted([
        name
        for name in table.list_collection_names()
        if name.startswith(startswith)
        and name[-8:].isnumeric()
        and name[-8:] <= time_next(-before, fmt="%Y%m%d")
    ])
