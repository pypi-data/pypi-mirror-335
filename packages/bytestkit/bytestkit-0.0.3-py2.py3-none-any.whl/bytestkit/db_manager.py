#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import concurrent.futures
from typing import Any, Dict, List, Optional, Tuple

import pymysql
from dbutils.pooled_db import PooledDB, PooledDedicatedDBConnection
from pymysql.cursors import DictCursor
from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from ._internal_utils import singleton
from .logger import get_logger


@singleton
class TinyDBManager:
    """
    TinyDB 通用管理类, 封装数据库的基本操作

    [使用示例]
    1. 初始化数据库
    db = TinyDBManager("database.json", table_name="demo")  # 传入文件路径, 持久化存储
    db = TinyDBManager()  # 使用内存数据库
    2. 插入数据
    data_id = db.insert({"name": "Tester", "age": 3})
    3. 查询数据
    data = db.get(db.q.name="Tester")
    4. 更新数据
    db.update({"age": 6}, db.q.name == "Tester")
    5. 统计符合条件的数据
    count = db.count(db.q.age > 3)
    6. 删除数据
    db.remove(db.q.name == "Tester")
    7. 关闭数据库
    db.close()
    8. 切换表
    db.switch_table("users")
    """

    def __init__(self, db_path: Optional[str] = None, table_name: Optional[str] = None):
        """
        初始化数据库管理器
        :param db_path: 数据库文件路径, 如果为 None, 则使用内存存储
        """
        self.logger = get_logger(__file__)

        self.db = TinyDB(db_path) if db_path else TinyDB(storage=MemoryStorage)
        self.table = self.db.table(table_name) if table_name else self.db.table("default")  # 默认表, 可在操作时指定不同表名
        self.q = Query()

    def switch_table(self, table_name: str):
        """
        切换表
        :param table_name: 要切换的表名
        """
        self.table = self.db.table(table_name)
        self.logger.info(f"✅ 已切换到数据表: {table_name}")

    def insert(self, data: Dict[str, Any], table_name: Optional[str] = None) -> int:
        """
        插入单条数据
        :param data: 要插入的数据字典
        :param table_name: 可选, 指定表名
        :return: 插入的文档 ID
        """
        table = self.db.table(table_name) if table_name else self.table
        return table.insert(data)

    def insert_multiple(self, data_list: List[Dict[str, Any]], table_name: Optional[str] = None) -> List[int]:
        """
        批量插入数据
        :param data_list: 数据列表, 每个元素为字典
        :param table_name: 可选, 指定表名
        :return: 插入的文档 ID 列表
        """
        table = self.db.table(table_name) if table_name else self.table
        return table.insert_multiple(data_list)

    def get(self, condition: Query, table_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取符合条件的第一条数据
        :param condition: 查询条件(使用 Query)
        :param table_name: 可选, 指定表名
        :return: 查询到的第一条数据(字典格式), 如果没有返回 None
        """
        table = self.db.table(table_name) if table_name else self.table
        return table.get(condition)

    def search(self, condition: Query, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        查询所有符合条件的数据
        :param condition: 查询条件(使用 Query)
        :param table_name: 可选, 指定表名
        :return: 查询到的数据列表
        """
        table = self.db.table(table_name) if table_name else self.table
        return table.search(condition)

    def update(self, updates: Dict[str, Any], condition: Query, table_name: Optional[str] = None) -> int:
        """
        更新符合条件的记录
        :param updates: 需要更新的数据
        :param condition: 查询条件(使用 Query)
        :param table_name: 可选, 指定表名
        :return: 更新的记录数量
        """
        table = self.db.table(table_name) if table_name else self.table
        return table.update(updates, condition)

    def remove(self, condition: Query, table_name: Optional[str] = None) -> int:
        """
        删除符合条件的记录
        :param condition: 查询条件(使用 Query)
        :param table_name: 可选, 指定表名
        :return: 删除的记录数量
        """
        table = self.db.table(table_name) if table_name else self.table
        return table.remove(condition)

    def count(self, condition: Query, table_name: Optional[str] = None) -> int:
        """
        统计符合条件的记录数
        :param condition: 查询条件(使用 Query)
        :param table_name: 可选, 指定表名
        :return: 记录数
        """
        table = self.db.table(table_name) if table_name else self.table
        return len(table.search(condition))

    def clear(self, table_name: Optional[str] = None) -> None:
        """
        清空指定表的数据
        :param table_name: 可选, 指定表名
        """
        table = self.db.table(table_name) if table_name else self.table
        table.truncate()

    def close(self) -> None:
        """关闭数据库"""
        self.db.close()
        self.logger.info("✅数据库连接已关闭")


@singleton
class MySQLManager:
    """
    MySQL 数据库管理类, 基于PooledDB连接池, 提供通用的数据库操作方法.

    实现特点:
    - 优雅的连接管理：支持 with 语句, 确保连接在使用后自动关闭
    - 通用查询方法：支持增删改查操作, 并提供事务支持
    - 支持批量插入
    - 异步查询(基于 `ThreadPoolExecutor`)
    - 支持切换数据库, 不需要重新实例化对象

    *! 不能用占位符 (%s) 代替表名, "%s" 只能用于值（如 WHERE 条件中的值），但不能用于表名或列名
    1. 支持with语句:
    with MySQLManager(**config) as db:
        data = db,fetch_one(...)
    """

    _pool = None  # 连接池实例(类变量)

    def __init__(self, host: str, username: str, password: str, database: Optional[str] = None, port: int = 3306, mincached: int = 1, maxcached: int = 5, maxconnections: int = 10, **kwargs):
        """
        初始化 MySQLManager, 并设置连接池。

        :param host: 数据库地址
        :param user: 数据库用户名
        :param password: 数据库密码
        :param database: 连接的数据库名称, 可选
        :param port: 数据库端口, 默认 3306
        :param mincached: 连接池最小空闲连接数
        :param maxcached: 连接池最大空闲连接数
        :param maxconnections: 允许的最大连接数
        """
        self.logger = get_logger(__file__)

        self.host = host
        self.user = username
        self.password = password
        self.database = database
        self.port = int(port)
        self._kw = kwargs

        self.connection = None

        if MySQLManager._pool is None:  # 只初始化一次连接池
            MySQLManager._pool = PooledDB(
                creator=pymysql,
                mincached=mincached,
                maxcached=maxcached,
                maxconnections=maxconnections,
                blocking=True,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=False,
                **self._kw,
            )

        self._pool = MySQLManager._pool

    def __enter__(self):
        """支持 with 语句, 在进入上下文时从连接池获取连接"""
        self._ensure_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """支持 with 语句, 在退出上下文时提交或回滚事务, 并释放连接"""
        self._close_connection(exc_type)
        if self.connection:
            if exc_type is None:
                self.connection.commit()  # 正常退出提交事务
            else:
                self.connection.rollback()  # 发生异常时回滚
            self.connection.close()  # 释放连接回池

    def _ensure_connection(self):
        """确保连接已建立（自动创建连接）"""
        if self.connection is None:
            self.connection: PooledDedicatedDBConnection = self._pool.connection()
            self.logger.info(f"✅ 初始化已连接到Mysql服务器:  {self.host}:{self.port}")

    def _close_connection(self, exc_type=None):
        """关闭连接并释放到连接池"""
        if self.connection:
            if exc_type is None:
                self.connection.commit()  # 正常退出提交事务
            else:
                self.connection.rollback()  # 发生异常时回滚
            self.connection.close()
            self.connection = None
            self.logger.info("✅数据库连接已关闭")

    def connect(self):
        """普通实例化方式时, 手动建立数据库连接"""
        self._ensure_connection()

    def switch_database(self, new_database: str):
        """
        切换当前使用的数据库。

        :param new_database: 新的数据库名称
        """
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(f"USE `{new_database}`")
        self.database = new_database

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        """
        执行增删改操作(INSERT、UPDATE、DELETE)。

        :param query: SQL 语句
        :param params: SQL 参数
        :return: 受影响的行数
        """
        self._ensure_connection()  # 确保连接已建立
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> dict:
        """
        执行查询并获取单行数据。

        :param query: SQL 语句
        :param params: SQL 参数
        :return: 查询结果(字典格式), 若无数据也会返回{}
        """
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if not result:
                result = dict()
            return result

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[dict]:
        """
        执行查询并获取所有数据。

        :param query: SQL 语句
        :param params: SQL 参数
        :return: 查询结果(字典格式列表)
        """
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            if not result:
                result = []
            return result

    def batch_insert(self, query: str, values: List[Tuple[Any, ...]]) -> int:
        """
        批量插入数据(INSERT INTO ... VALUES ...)。

        :param query: SQL 语句
        :param values: 批量数据
        :return: 受影响的行数
        """
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.executemany(query, values)
            return cursor.rowcount

    def async_fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[dict]:
        """
        异步执行查询(在后台线程执行)。

        :param query: SQL 语句
        :param params: SQL 参数
        :return: 查询结果(字典格式列表)
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.fetch_all, query, params)
            return future.result()

    def commit(self):
        """手动提交事务"""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """手动回滚事务"""
        if self.connection:
            self.connection.rollback()

    def close(self):
        """手动关闭数据库连接（释放到连接池）"""
        self._close_connection()
