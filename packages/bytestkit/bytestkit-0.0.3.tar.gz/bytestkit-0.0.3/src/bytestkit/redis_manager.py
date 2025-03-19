#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from typing import Any, Dict, List, Optional

import redis

from ._internal_utils import singleton
from .logger import get_logger


@singleton
class RedisManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        """
        Redis 连接管理器，提供封装的 Redis 操作方法，并支持多实例管理。

        :param host: Redis 服务器地址
        :param port: Redis 端口
        :param db: Redis 数据库索引
        :param password: Redis 认证密码（如果需要）
        """
        self.logger = get_logger()
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self._connect()

    def _connect(self):
        """初始化 Redis 连接"""
        try:
            self._pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=True)
            self.client = redis.Redis(connection_pool=self._pool)
        except redis.ConnectionError as e:
            self.logger.fatal(f"Redis 连接失败, e: {repr(e)}")
            raise
        except redis.TimeoutError as e:
            self.logger.fatal(f"Redis 连接超时, e: {repr(e)}")
            raise

    def switch_db(self, db: int):
        """切换 Redis 数据库"""
        self.db = db
        self._connect()

    def ping(self) -> bool:
        """检查 Redis 连接状态"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    def set(self, key: str, value: Any, expire_time: Optional[int] = None, **kwargs) -> bool:
        """设置字符串键值"""
        return self.client.set(key, value, ex=expire_time, **kwargs)

    def get(self, key: str) -> Optional[str]:
        """获取字符串值"""
        return self.client.get(key)

    def delete(self, key: str) -> int:
        """删除键"""
        return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.client.exists(key) > 0

    def hset(self, name: str, key: str, value: Any) -> bool:
        """设置哈希表字段"""
        return self.client.hset(name, key, value) == 1

    def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希表字段值"""
        return self.client.hget(name, key)

    def hgetall(self, name: str) -> Dict[str, str]:
        """获取哈希表所有字段"""
        return self.client.hgetall(name)

    def lpush(self, key: str, value: Any) -> int:
        """左侧插入列表"""
        return self.client.lpush(key, value)

    def rpush(self, key: str, value: Any) -> int:
        """右侧插入列表"""
        return self.client.rpush(key, value)

    def lpop(self, key: str) -> Optional[str]:
        """移除并返回列表左侧元素"""
        return self.client.lpop(key)

    def rpop(self, key: str) -> Optional[str]:
        """移除并返回列表右侧元素"""
        return self.client.rpop(key)

    def sadd(self, key: str, value: Any) -> int:
        """添加集合元素"""
        return self.client.sadd(key, value)

    def srem(self, key: str, value: Any) -> int:
        """移除集合元素"""
        return self.client.srem(key, value)

    def smembers(self, key: str) -> set:
        """获取集合所有元素"""
        return self.client.smembers(key)

    def zadd(self, key: str, members: Dict[str, float]) -> int:
        """添加有序集合元素"""
        return self.client.zadd(key, members)

    def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> List:
        """获取有序集合范围"""
        return self.client.zrange(key, start, end, withscores=withscores)

    def expire(self, key: str, time: int) -> bool:
        """设置键的过期时间"""
        return self.client.expire(key, time)

    def keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配指定模式的所有键

        :param pattern: 匹配模式，默认为 '*'（获取所有键）
        :return: 符合条件的键列表
        """
        return self.client.keys(pattern)

    def pipeline(self):
        """获取 Redis 事务 pipeline"""
        return self.client.pipeline()

    def close(self):
        """关闭连接"""
        self.client.close()
