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
import logging
from typing import Any, Optional

from src.pydbpool.base import BaseConnection, DBConnMeta
from src.pydbpool.errors import ConnectionAttributeError

logger = logging.getLogger("pydbpool")


class DBPoolConnection(BaseConnection):
    """稳定的数据库连接封装"""

    def __init__(
            self,
            raw_conn,
            pool: "DBPool",  # type: ignore
    ) -> None:
        """
        初始化稳定连接

        Args:
            raw_conn: 原始数据库连接对象
            pool: 连接池实例
        """
        super().__init__(raw_conn, pool)
        self.meta = DBConnMeta()

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def cursor(self):
        return self._conn.cursor()

    @property
    def ping_query(self) -> str:
        return "SELECT 1 FROM (SELECT 1) AS TEMP"  # noqa E501

    def ping(self) -> bool:
        """
        执行探活检测
        Returns:
            bool: 连接是否存活
        """
        with self._lock:
            try:
                # 优先使用原生ping方法
                if hasattr(self._conn, 'ping'):
                    try:
                        alive = self._conn.ping(False)
                    except TypeError:
                        try:
                            alive = self._conn.ping()
                        except Exception:  # noqa S110
                            # 降级使用查询检测
                            with self._conn.cursor() as cursor:
                                cursor.execute(self.ping_query)
                                alive = True

                    if alive is None:
                        alive = True

            except Exception as e:
                logger.warning(f"Ping failed: {str(e)}")
                alive = False

            return alive

    def close(self) -> None:
        """安全关闭连接"""
        with self._lock:
            try:
                self._conn.close()
                self.meta.update_close()
            except AttributeError:
                raise ConnectionAttributeError(f"Connection class ：{type(self._conn)} has no close-method")
            except Exception:  # noqa S110
                pass

    def __enter__(self) -> "DBPoolConnection":
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        self._pool.release_connection(self)  # 退出上下文时自动归还
