# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : exceptions.py
@Project  : 
@Time     : 2025/3/18 10:52
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""


class PoolBaseError(Exception):
    """连接池异常"""


class ConnectionBaseError(Exception):
    """连接异常"""


class ConnectionTimeoutError(ConnectionBaseError):
    """连接超时异常"""


class ConnectionClosedError(ConnectionBaseError):
    """连接已关闭异常"""


class ConnectionUnavailableError(ConnectionBaseError):
    """连接不可用异常"""


class ConnectionFailedError(ConnectionBaseError):
    """连接异常"""


class PoolClosedError(PoolBaseError):
    """连接池已关闭异常"""


class PoolExhaustedError(PoolBaseError):
    """连接池已耗尽异常"""


class PoolTimeoutError(PoolBaseError):
    """连接池获取超时异常"""


class NotSupportModule(PoolBaseError):
    """不支持模块"""
