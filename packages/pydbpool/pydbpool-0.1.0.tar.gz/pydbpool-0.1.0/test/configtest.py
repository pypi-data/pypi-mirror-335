# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : configtest.py
@Project  : 
@Time     : 2025/3/18 13:58
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from typing import Any

from pydbpool.dbpool import DBPool
from pydbpool.extra import PoolEventType, PoolEvent, EventBus


# 订阅事件（支持多种参数形式）
@EventBus.subscribe(PoolEventType.BEFORE_GET)
def handle_before_get(event: PoolEvent):
    print(f"Acquired connection from pool {id(event.pool)}")


@EventBus.subscribe(PoolEventType.BEFORE_PUT)
def handle_pre_put(pool: DBPool, conn: Any):
    print(f"Returning connection to pool {id(pool)}")

# 输出：
# Acquired connection from pool 1397160135424
# Returning connection to pool 1397160135424
