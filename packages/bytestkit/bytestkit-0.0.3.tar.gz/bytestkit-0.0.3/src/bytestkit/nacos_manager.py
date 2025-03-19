#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import logging
from typing import Callable, Optional

import nacos

from ._internal_utils import singleton
from .logger import get_logger


@singleton
class NacosManager:
    """
    Nacos 配置管理(Config Service)封装, 基于 nacos-sdk-python 2.0.1
    """

    def __init__(self, server_addresses: str, namespace: str = "public", username: Optional[str] = None, password: Optional[str] = None, **kwargs):
        """
        初始化 Nacos 客户端.

        :param server_addresses: Nacos 服务器地址, 格式为 'IP:PORT' 或 'IP1:PORT1,IP2:PORT2'.
        :param namespace: 命名空间 ID, 默认为 'public'.
        :param username: Nacos 用户名, 可选.
        :param password: Nacos 密码, 可选.
        :param kwargs: 其他可选参数, 例如:
            - ak: Access Key, 用于身份验证.
            - sk: Secret Key, 用于身份验证.
        """
        self.logger = get_logger("nacos")

        self.client = nacos.NacosClient(server_addresses=server_addresses, namespace=namespace, username=username, password=password, ak=kwargs.get("ak"), sk=kwargs.get("sk"), log_level=logging.INFO)
        self.logger.info(f"Nacos 客户端已连接到 {server_addresses}, 命名空间: {namespace}")

    def get_config(self, data_id: str, group: str, timeout: int = 10) -> Optional[str]:
        """
        获取配置.

        :param data_id: 配置的 Data ID.
        :param group: 配置的分组.
        :param timeout: 请求超时时间, 单位为秒.
        :return: 配置内容, 如果获取失败则返回 None.
        """
        try:
            config = self.client.get_config(data_id, group, timeout)
            self.logger.info(f"成功获取配置: Data ID={data_id}, Group={group}")
            return config
        except Exception as e:
            self.logger.error(f"获取配置失败: Data ID={data_id}, Group={group}, 错误信息: {e}")
            return None

    def publish_config(self, data_id: str, group: str, content: str) -> bool:
        """
        发布配置.

        :param data_id: 配置的 Data ID.
        :param group: 配置的分组.
        :param content: 配置内容.
        :return: 发布是否成功.
        """
        try:
            result = self.client.publish_config(data_id, group, content)
            if result:
                self.logger.info(f"成功发布配置: Data ID={data_id}, Group={group}")
            else:
                self.logger.warning(f"发布配置失败: Data ID={data_id}, Group={group}")
            return result
        except Exception as e:
            self.logger.error(f"发布配置异常: Data ID={data_id}, Group={group}, 错误信息: {e}")
            return False

    def delete_config(self, data_id: str, group: str) -> bool:
        """
        删除配置.

        :param data_id: 配置的 Data ID.
        :param group: 配置的分组.
        :return: 删除是否成功.
        """
        try:
            result = self.client.remove_config(data_id, group)
            if result:
                self.logger.info(f"成功删除配置: Data ID={data_id}, Group={group}")
            else:
                self.logger.warning(f"删除配置失败: Data ID={data_id}, Group={group}")
            return result
        except Exception as e:
            self.logger.error(f"删除配置异常: Data ID={data_id}, Group={group}, 错误信息: {e}")
            return False

    def add_config_listener(self, data_id: str, group: str, callback: Callable[[str], None]) -> None:
        """
        添加配置监听器.

        :param data_id: Data ID.
        :param group: Group.
        :param callback: 当配置变化时调用的回调函数, 接收新的配置内容作为参数.
        """

        def _callback(config):
            self.logger.info(f"配置发生变化: Data ID={data_id}, Group={group}")
            callback(config)

        self.client.add_config_watcher(data_id, group, callback)
        self.logger.info(f"已添加配置监听器: Data ID={data_id}, Group={group}")

    def remove_config_listener(self, data_id: str, group: str, callback: Callable[[str], None], remove_all: bool = False) -> None:
        """
        删除配置监听器.

        :param data_id: Data ID.
        :param group: Group.
        :param callback: 删除配置时的回调函数.
        :param remove_all: 删除该配置的所有监听器，而不考虑回调函数.
        """

        try:
            self.logger.info(f"删除配置监听器: Data ID={data_id}, Group={group}, remove_all={remove_all}")
            self.client.remove_config_watcher(data_id, group, callback, remove_all)
            self.logger.info(f"已删除配置监听器: Data ID={data_id}, Group={group}")
        except Exception as e:
            self.logger.error(f"删除配置监听器失败: {e}")
            raise
