# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : extra.py
@Project  : 
@Time     : 2025/3/18 10:52
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List
from functools import wraps
import inspect

from pydbpool.dbconnection import SteadyConnection


class PoolEventType(Enum):
    """
    顺序不能改变

    获取连接前
    获取连接后
    归还连接前
    归还连接后
    连接创建时
    连接销毁时
    """
    BEFORE_GET = auto()
    AFTER_GET = auto()
    BEFORE_PUT = auto()
    AFTER_PUT = auto()
    CONN_CREATED = auto()
    CONN_DESTROYED = auto()


@dataclass
class PoolEvent:
    event_type: PoolEventType
    pool: Any = None
    conn: Any = None


class EventBus:
    _subscribers: Dict[PoolEventType, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: PoolEventType):
        def decorator(func: Callable):
            cls._subscribers.setdefault(event_type, []).append(func)
            return func

        return decorator

    @classmethod
    def publish(cls, event: PoolEvent):
        for callback in cls._subscribers.get(event.event_type, []):
            sig = inspect.signature(callback)
            kwargs = {}
            if "event" in sig.parameters:
                kwargs["event"] = event
            if "pool" in sig.parameters:
                kwargs["pool"] = event.pool
            if "conn" in sig.parameters:
                kwargs["conn"] = event.conn

            if event.pool:
                callback(event.pool, **kwargs)
            else:
                callback(**kwargs)


def event_handler(event_type: PoolEventType):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 触发前置事件
            EventBus.publish(PoolEvent(
                event_type=event_type,
                pool=self,
                conn=kwargs.get('conn')
            ))

            result = func(self, *args, **kwargs)

            # 自动识别后置事件类型
            post_event_type = PoolEventType(event_type.value + 1)
            EventBus.publish(PoolEvent(
                event_type=post_event_type,
                pool=self,
                conn=result if isinstance(result, SteadyConnection) else None
            ))

            return result

        return wrapper

    return decorator
