# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : dbconnection.py
@Project  : 
@Time     : 2025/3/18 11:02
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from __future__ import annotations

import threading
import logging
from contextlib import suppress
from typing import Any, Optional, Protocol, runtime_checkable

from pydbpool.base import ConnectionMeta

logger = logging.getLogger("pydbpool")


@runtime_checkable
class DatabaseConnection(Protocol):
    """数据库连接协议"""

    def ping(self, reconnect: bool = True) -> bool:
        """检查连接是否存活"""
        ...

    def cursor(self) -> Any:
        """获取游标"""
        ...

    def close(self) -> None:
        """关闭连接"""
        ...


class SteadyConnection:
    """稳定的数据库连接封装"""

    def __init__(
            self,
            raw_conn,
            pool: "DBPool",
            ping_query: Optional[str] = None,
            max_retries: int = 3,
            retry_delay: float = 1.0
    ) -> None:
        """
        初始化稳定连接

        Args:
            raw_conn: 原始数据库连接对象
            pool: 连接池实例
            ping_query: 探活查询语句
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间(秒)
        """
        self.raw = raw_conn
        self._pool = pool
        self.ping_query = ping_query or "SELECT 1 FROM (SELECT 1) AS TEMP"  # noqa
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.meta = ConnectionMeta()
        self._lock = threading.RLock()

    def ping(self) -> bool:
        """
        执行探活检测

        Returns:
            bool: 连接是否存活
        """
        try:
            # 优先使用原生ping方法
            if hasattr(self.raw, 'ping'):
                try:
                    return bool(self.raw.ping(False))
                except TypeError:
                    return bool(self.raw.ping())

            # 降级使用查询检测
            with self.raw.cursor() as cursor:
                cursor.execute(self.ping_query)
                return True

        except Exception as e:
            logger.warning(f"Ping failed: {str(e)}")
            return False

    def heartbeat(self) -> bool:
        """
        执行心跳检测
        
        Returns:
            bool: 连接是否存活
        """
        with self._lock:
            try:
                # 优先使用原生ping方法
                if hasattr(self.raw, 'ping'):
                    try:
                        is_alive = self.raw.ping(False)
                    except TypeError:
                        is_alive = self.raw.ping()

                    if is_alive is None:
                        is_alive = True

                else:
                    # 降级使用查询检测
                    with self.raw.cursor() as cursor:
                        cursor.execute(self.ping_query)
                        is_alive = True

                # 更新连接状态
                self.meta.is_alive = is_alive
                if is_alive:
                    self.meta.update_activity()
                return is_alive

            except Exception as e:
                logger.warning(f"Heartbeat failed: {str(e)}")
                self.meta.record_error(str(e))
                self.meta.is_alive = False
                return False

    def close(self) -> None:
        """安全关闭连接"""
        with self._lock:
            with suppress(Exception):
                self.raw.close()
            self.meta.is_alive = False

    def __enter__(self) -> SteadyConnection:
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        self._pool.release(self)  # 退出上下文时自动归还
