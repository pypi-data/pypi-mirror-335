#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import threading
from functools import wraps


def singleton(cls):
    """
    通用单例装饰器，保证类的实例在全局唯一
    根据传入的参数缓存不同的实例
    """
    instances = {}
    lock = threading.Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        key = (cls, args, frozenset(kwargs.items()))
        with lock:
            if key not in instances:
                instances[key] = cls(*args, **kwargs)
        return instances[key]

    return get_instance
