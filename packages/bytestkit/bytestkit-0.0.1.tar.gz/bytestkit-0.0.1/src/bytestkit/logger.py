#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import datetime
import logging
import weakref
from pathlib import Path

import colorlog

__all__ = ("get_logger", "logger")


LOG_FORMAT = "[%(levelname)s] - %(asctime)s %(filename)s -> %(funcName)s line:%(lineno)d : %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class LogColorConfig(dict):
    """日志颜色配置，允许自定义"""

    DEFAULT_COLORS = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "purple",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    def __init__(self, custom_colors=None):
        super().__init__(self.DEFAULT_COLORS)
        if custom_colors:
            self.update(custom_colors)


LOG_COLOR_CONFIG = LogColorConfig()


# filter `urllib3` logs
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("urllib3.util.retry").setLevel(logging.WARNING)


_loggers = weakref.WeakValueDictionary()


class ErrorDividerFormatter(colorlog.ColoredFormatter):
    """为 ERROR 和 CRITICAL 级别日志增加分隔符"""

    def format(self, record):
        if record.levelno >= logging.ERROR:
            divider0 = ">" * 40
            divider1 = "<" * 40
            message = f"{divider0}\n{super().format(record)}\n{divider1}"
            return message
        return super().format(record)


def get_logger(name=None, *, log_level: str = None, log_to_console=True, log_to_file=False, log_file_path: str = None, log_colors_config: dict = None) -> logging.Logger:
    """获取 Logger 实例，支持控制台彩色日志输出以及写入本地文件

    Args:
        name (str, optional): name of logger.
        log_level (str, optional): 日志级别, 可以传入字符串"INFO"
        log_to_console (bool, optional): 是否输出到控制台. Defaults to True.
        log_to_file (bool, optional): 是否输出到文件, 仅在本地运行case时有效. Defaults to True.
        log_colors_config (dict, optional): 自定义日志颜色.

    Returns:
        logging.Logger: logging.Logger
    """

    name = str(name) or __name__

    if _loggers.get(name):
        return _loggers.get(name)

    _logger = logging.getLogger(name)

    # 低于 LOG_LEVEL 的日志会直接被丢弃，不会传递给任何 Handler
    _logger.setLevel(logging.DEBUG)

    if log_level is None:
        log_level = logging.DEBUG
    elif isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.DEBUG)

    # 避免重复添加 handler
    if not _logger.handlers:
        # 输出到控制台
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            log_colors_config = log_colors_config or LOG_COLOR_CONFIG
            console_formatter = ErrorDividerFormatter("%(log_color)s" + LOG_FORMAT, datefmt=LOG_DATE_FORMAT, log_colors=log_colors_config)
            console_handler.setFormatter(console_formatter)
            _logger.addHandler(console_handler)

        # 输出到磁盘文件
        if log_to_file:
            if log_file_path is None:
                log_file_path = _get_log_file_path()

            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)  # 不使用颜色格式
            file_handler.setFormatter(file_formatter)
            _logger.addHandler(file_handler)

    _loggers[name] = _logger

    return _logger


def _get_log_file_path():
    log_root = Path(__file__).parent.parent.joinpath("logs")
    if not log_root.exists():
        log_root.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today()
    log_file = f"{today.year}_{today.month}_{today.day}.log"
    filename = log_root.joinpath(log_file)

    return filename


logger = get_logger("default", log_level="DEBUG", log_to_console=True, log_to_file=False)
