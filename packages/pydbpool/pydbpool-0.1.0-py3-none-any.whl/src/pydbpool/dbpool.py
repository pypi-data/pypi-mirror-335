# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : dbpool.py
@Project  : 
@Time     : 2025/3/18 11:03
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import random
import threading
import time
import logging
from functools import wraps
from typing import Any, Callable, Deque, Dict, Set, Optional
from collections import deque
from contextlib import contextmanager

from base import ConnectionPoolMeta
from exceptions import ConnectionFailedError, PoolExhaustedError
from pydbpool.dbconnection import SteadyConnection

# 类型定义
ConnectionFactory = Callable[[], Any]
HookFunc = Callable[["SteadyConnection", "DBPool"], None]

logger = logging.getLogger("pydbpool")


def meta_operator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = func(self, *args, **kwargs)
        with self._lock:
            self._active_conns.add(conn)
            self.meta.free_count = len(self._idle_conns)
            self.meta.record_borrow()  # 记录连接借用
            self.meta.update_activity(1, self._active_conns)
        return conn

    return wrapper


class DBPool:

    def __init__(self,
                 creator: Callable,
                 minsize: int = 1,
                 maxsize: int = 2,
                 max_retries: int = 3,
                 max_usage: int = None,
                 ping_query: Optional[str] = None,
                 idle_timeout: Optional[int] = None,
                 wait_timeout: Optional[int] = None,
                 auto_increase: Optional[int] = True,
                 health_check_interval: int = 3600,
                 **kwargs
                 ):
        """
        初始化连接池

        Args:
            creator: 创建数据库连接的函数
            minsize: 最小连接数，默认为1
            maxsize: 最大连接数，默认为2
            max_retries: 连接失败最大重试次数，默认为3
            max_usage: 单个连接最大使用次数，默认为None（无限制）
            ping_query: 探活查询语句，默认为None
            idle_timeout: 空闲连接超时时间（秒），默认为None（无限制）
            wait_timeout: 获取连接等待超时时间（秒），默认为None（无限制）
            auto_increase: 是否允许自动增加连接，默认为True
            health_check_interval: 健康检查间隔（秒），默认为3600
            **kwargs: 传递给creator的其他参数
        """
        # 参数验证和规范化
        if minsize < 1:
            raise ValueError("minsize must be greater than 0")
        if maxsize < minsize:
            raise ValueError("maxsize must be greater than or equal to minsize")
        if max_retries < 1:
            raise ValueError("max_retries must be greater than 0")
        if health_check_interval < 1:
            raise ValueError("health_check_interval must be greater than 0")
        if wait_timeout is not None and wait_timeout < 0:
            raise ValueError("wait_timeout must be non-negative")
        if idle_timeout is not None and idle_timeout < 0:
            raise ValueError("idle_timeout must be non-negative")

        # 基本配置
        self.minsize = minsize
        self.maxsize = maxsize
        self.idle_timeout = idle_timeout
        self.wait_timeout = wait_timeout
        self.auto_increase = auto_increase
        self.ping_query = ping_query
        self.max_retries = max_retries
        self.max_usage = max_usage
        self.health_check_interval = health_check_interval

        # 连接创建相关
        self.creator = creator
        self.creator_kwargs = kwargs

        # 连接池状态
        self.meta = ConnectionPoolMeta()
        self._idle_conns: Deque[SteadyConnection] = deque()
        self._active_conns: Set[SteadyConnection] = set()

        # 线程安全
        self._lock = threading.RLock()
        self._cond = threading.Condition(self._lock)

        # 初始化连接池
        self._init_pool()

        # 启动健康检查线程
        self._health_check_thread = threading.Thread(target=self._health_check, daemon=True)
        self._health_check_thread.start()

    def _init_pool(self):
        """初始化连接池"""
        success_count = 0
        for _ in range(self.minsize):
            try:
                conn = self._create_conn()
                if conn.heartbeat():
                    conn.meta.is_alive = True
                    conn.meta.created_at = time.time()
                    self._idle_conns.append(conn)
                    success_count += 1
                else:
                    conn.meta.is_alive = False
                    conn.close()
            except Exception as e:
                logger.error(f"Failed to create initial connection: {e}")
                self.meta.record_error()
                time.sleep(1)
                continue

        if success_count == 0:
            logger.warning("No initial connections available, retrying...")
            time.sleep(1)
            self._init_pool()
        elif success_count < self.minsize:
            logger.warning(f"Only {success_count}/{self.minsize} initial connections created")
            self._init_pool()

    @contextmanager
    def connection(self) -> SteadyConnection:
        conn = self._get_conn()
        try:
            yield conn
        finally:
            self.release(conn)

    def get_connection(self) -> SteadyConnection:
        return self._get_conn()

    @meta_operator
    def _get_conn(self):
        """获取连接（带精确超时控制）"""
        start_time = time.monotonic()
        deadline = start_time + (self.wait_timeout or 0)

        with self._cond:
            while True:
                # 尝试获取空闲连接
                if self._idle_conns:
                    conn = self._idle_conns.popleft()
                    try:
                        if conn.meta.is_alive and conn.heartbeat():
                            wait_time = time.monotonic() - start_time
                            self.meta.record_wait(wait_time)
                            conn.meta.update_activity()
                            return conn
                        conn.meta.is_alive = False
                        conn.close()
                    except Exception as e:
                        logger.error(f"Error checking connection health: {e}")
                        conn.meta.record_error(str(e))
                        conn.meta.is_alive = False
                        conn.close()
                    continue

                # 尝试创建新连接
                current_size = len(self._active_conns) + len(self._idle_conns)
                if current_size < self.maxsize:
                    try:
                        conn = self._create_conn()
                        if conn.heartbeat():
                            wait_time = time.monotonic() - start_time
                            self.meta.record_wait(wait_time)
                            conn.meta.update_activity()
                            return conn
                        conn.meta.is_alive = False
                        conn.close()
                    except Exception as e:
                        logger.error(f"Failed to create new connection: {e}")
                        self.meta.record_error()
                        if not self.auto_increase:
                            if current_size < self.minsize:
                                logger.warning(
                                    f"Connection creation failed but below minsize ({current_size}/{self.minsize})")
                                time.sleep(1)
                                continue
                            raise PoolExhaustedError("Pool is exhausted and auto_increase is disabled")
                        time.sleep(1)
                        continue

                if self.wait_timeout:

                    # 检查总超时
                    if time.monotonic() >= deadline:
                        self.meta.record_error()
                        raise PoolExhaustedError(f"Timeout waiting for connection after {self.wait_timeout}s")

                    # 等待可用连接
                    timeout = deadline - time.monotonic()
                else:
                    timeout = None
                if not self._cond.wait_for(lambda: bool(self._idle_conns), timeout=timeout):
                    if not self.auto_increase:
                        if current_size < self.minsize:
                            logger.warning(f"Connection wait timeout but below minsize ({current_size}/{self.minsize})")
                            time.sleep(1)
                            continue
                        self.meta.record_error()
                        raise PoolExhaustedError("Pool is exhausted and auto_increase is disabled")
                    continue

    def release(self, conn):
        """放回连接"""
        if not conn:
            return

        start_time = time.monotonic()
        try:
            with self._cond:
                # 检查连接是否仍然有效
                if not conn.meta.is_alive or not conn.heartbeat():
                    conn.meta.is_alive = False
                    conn.close()
                    self.meta.total_count -= 1  # 减少总连接数
                    return

                # 检查使用次数
                if self.max_usage and conn.meta.usage_count >= self.max_usage:
                    conn.meta.is_alive = False
                    conn.close()
                    self.meta.total_count -= 1  # 减少总连接数
                    return

                # 更新连接状态
                conn.meta.update_activity()
                conn.meta.usage_count += 1
                usage_time = time.monotonic() - start_time
                conn.meta.record_usage(usage_time)
                self.meta.record_usage(usage_time)  # 记录到连接池元数据

                # 放回连接池
                self._idle_conns.append(conn)
                self._active_conns.remove(conn)
                self.meta.free_count = len(self._idle_conns)
                self.meta.update_activity(-1, self._active_conns)
                self.meta.record_return()  # 记录连接归还
                self._cond.notify_all()
        except Exception as e:
            logger.error(f"Error releasing connection: {e}")
            conn.meta.record_error(str(e))
            self.meta.record_error(str(e))  # 记录到连接池元数据
            conn.meta.is_alive = False
            conn.close()
            self.meta.total_count -= 1  # 减少总连接数

    def close(self):
        """关闭所有连接"""
        with self._cond:
            try:
                # 关闭所有空闲连接
                for conn in list(self._idle_conns):
                    try:
                        conn.meta.is_alive = False
                        conn.close()
                    except Exception as e:
                        logger.error(f"Error closing idle connection: {e}")
                        self.meta.record_error()
                self._idle_conns.clear()

                # 关闭所有活动连接
                for conn in list(self._active_conns):
                    try:
                        conn.meta.is_alive = False
                        conn.close()
                    except Exception as e:
                        logger.error(f"Error closing active connection: {e}")
                        self.meta.record_error()
                self._active_conns.clear()

                # 清理元数据
                self.meta.clear()

                # 通知所有等待线程
                self._cond.notify_all()
            except Exception as e:
                logger.error(f"Error during pool closure: {e}")
                self.meta.record_error()

    def _create_conn(self) -> SteadyConnection:
        """创建新连接"""
        retries = 3  # 最大重试次数
        retry_delay = 1.0  # 重试延迟（秒）

        for attempt in range(retries):
            try:
                raw_conn = self.creator(**self.creator_kwargs)
                conn = SteadyConnection(raw_conn, pool=self, ping_query=self.ping_query, max_retries=self.max_retries)
                conn.meta.is_alive = True  # 设置初始状态
                conn.meta.created_at = time.time()  # 记录创建时间
                self.meta.total_count += 1
                return conn
            except Exception as e:
                if attempt < retries - 1:  # 如果不是最后一次尝试
                    logger.warning(f"Connection attempt {attempt + 1}/{retries} failed: {str(e)}")
                    time.sleep(retry_delay)
                    continue
                else:  # 最后一次尝试失败
                    self.meta.record_error()
                    raise ConnectionFailedError(
                        f"Failed to create connection after {retries} attempts: {str(e)}") from e

    def _health_check(self):
        """后台维护任务"""
        while True:
            try:
                time.sleep(self.health_check_interval)
                now = time.time()

                with self._cond:
                    # 使用临时列表避免修改原队列
                    temp_idle = list(self._idle_conns)
                    self._idle_conns.clear()

                    # 清理过期连接
                    healthy = []
                    for conn in temp_idle:
                        try:
                            # 检查连接状态
                            if not conn.meta.is_alive:
                                conn.close()
                                continue

                            # 检查空闲超时
                            if self.idle_timeout and (now - conn.meta.last_active > self.idle_timeout):
                                conn.meta.is_alive = False
                                conn.close()
                                continue

                            # 检查使用次数
                            if self.max_usage and conn.meta.usage_count >= self.max_usage:
                                conn.meta.is_alive = False
                                conn.close()
                                continue

                            # 使用heartbeat检查连接是否存活
                            if not conn.heartbeat():
                                conn.close()
                                continue

                            healthy.append(conn)
                        except Exception as e:
                            logger.error(f"Error checking connection health: {e}")
                            conn.meta.record_error(str(e))
                            conn.meta.is_alive = False
                            conn.close()

                    # 重新填充空闲连接
                    self._idle_conns.extend(healthy)

                    # 动态调整连接池大小
                    current_size = len(self._active_conns) + len(self._idle_conns)
                    if current_size < self.minsize:
                        # 补充最小空闲连接
                        while len(self._idle_conns) < self.minsize and current_size < self.maxsize:
                            try:
                                conn = self._create_conn()
                                if conn.heartbeat():
                                    conn.meta.is_alive = True
                                    self._idle_conns.append(conn)
                                    current_size += 1
                                else:
                                    conn.meta.is_alive = False
                                    conn.close()
                            except ConnectionFailedError as e:
                                logger.error(f"Failed to create connection during health check: {e}")
                                self.meta.record_error()
                                break
                            except Exception as e:
                                logger.error(f"Unexpected error during health check: {e}")
                                self.meta.record_error()
                                time.sleep(1)
                                continue
                    elif current_size > self.maxsize:
                        # 清理多余的空闲连接
                        while len(self._idle_conns) > self.minsize and current_size > self.maxsize:
                            conn = self._idle_conns.pop()
                            conn.meta.is_alive = False
                            conn.close()
                            current_size -= 1

                    # 更新元数据
                    self.meta.free_count = len(self._idle_conns)
                    self.meta.total_count = current_size
                    self._cond.notify_all()

                    # 记录健康检查结果
                    logger.debug(f"Health check completed: {current_size} connections, {len(self._idle_conns)} idle")
            except Exception as e:
                logger.error(f"Error in health check: {e}")
                self.meta.record_error()
                time.sleep(1)

    @property
    def metrics(self) -> Dict[str, Any]:
        """获取池监控指标"""
        with self._lock:
            # 计算当前连接状态
            current_active = len(self._active_conns)
            current_idle = len(self._idle_conns)
            current_total = current_active + current_idle

            # 计算等待时间统计
            wait_times = self.meta.wait_times
            avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
            max_wait_time = max(wait_times) if wait_times else 0

            # 计算使用时间统计
            usage_times = self.meta.usage_times
            avg_usage_time = sum(usage_times) / len(usage_times) if usage_times else 0
            max_usage_time = max(usage_times) if usage_times else 0

            # 计算连接状态统计
            active_connections = [
                {
                    "id": id(conn),
                    "created_at": conn.meta.created_at,
                    "last_active": conn.meta.last_active,
                    "usage_count": conn.meta.usage_count,
                    "total_usage_time": conn.meta.total_usage_time,
                    "error_count": conn.meta.error_count,
                    "is_alive": conn.meta.is_alive
                }
                for conn in self._active_conns
            ]

            idle_connections = [
                {
                    "id": id(conn),
                    "created_at": conn.meta.created_at,
                    "last_active": conn.meta.last_active,
                    "usage_count": conn.meta.usage_count,
                    "total_usage_time": conn.meta.total_usage_time,
                    "error_count": conn.meta.error_count,
                    "is_alive": conn.meta.is_alive
                }
                for conn in self._idle_conns
            ]

            return {
                # 连接池配置
                "maxsize": self.maxsize,
                "minsize": self.minsize,
                "wait_timeout": self.wait_timeout,
                "idle_timeout": self.idle_timeout,
                "health_check_interval": self.health_check_interval,

                # 当前连接状态
                "total": current_total,
                "active": current_active,
                "idle": current_idle,
                "active_connections": active_connections,
                "idle_connections": idle_connections,

                # 等待时间统计
                "wait_count": self.meta.wait_count,
                "avg_wait_time": round(avg_wait_time, 3),
                "max_wait_time": round(max_wait_time, 3),
                "total_wait_time": round(sum(wait_times), 3),

                # 使用时间统计
                "borrow_count": self.meta.borrow_count,
                "avg_usage_time": round(avg_usage_time, 3),
                "max_usage_time": round(max_usage_time, 3),
                "total_usage_time": round(sum(usage_times), 3),

                # 错误统计
                "error_count": self.meta.error_count,
                "error_history": self.meta.error_history,

                # 连接池生命周期
                "created_at": self.meta.created_at,
                "last_active": self.meta.last_active,
                "uptime": round(time.time() - self.meta.created_at, 3),

                # 性能指标
                "connection_creation_rate": round(self.meta.total_count / (time.time() - self.meta.created_at), 3),
                "connection_reuse_rate": round(self.meta.borrow_count / self.meta.total_count,
                                               3) if self.meta.total_count > 0 else 0,
                "error_rate": round(self.meta.error_count / self.meta.borrow_count,
                                    3) if self.meta.borrow_count > 0 else 0
            }


def exec_sql(p: DBPool, text, idx):
    _con = p.get_connection()
    _cur = _con.raw.cursor()
    _cur.execute(text)
    print(f'sleep===>{idx}:', _cur.fetchall()[0])
    p.release(_con)


def split_total(total: int, parts: int) -> list[int]:
    # 生成 (parts-1) 个分割点，范围在 [1, total-1]
    dividers = sorted(random.sample(range(1, total), parts - 1))
    # 计算每个区间的长度（即每个部分的值）
    result = [dividers[0]]  # 第一个数
    for i in range(1, parts - 1):
        result.append(dividers[i] - dividers[i - 1])  # 中间数
    result.append(total - dividers[-1])  # 最后一个数
    return result


def monitor(p: DBPool):
    text = """select count(*) from information_schema.PROCESSLIST;"""
    while True:
        time.sleep(1)
        print(p.meta.as_dict())


if __name__ == '__main__':
    import pymysql

    sql = """SHOW FULL PROCESSLIST;"""
    pool = DBPool(
        creator=pymysql.connect,
        host="127.0.0.1",
        port=3306,
        user="root",
        password="2012516nwdytL!",
        database="lamtun_dev",
        minsize=1,
        maxsize=3,
        # wait_timeout=6,
        auto_increase=False,
        health_check_interval=2
    )

    threading.Thread(target=monitor, args=(pool,), daemon=True).start()

    texts = [f"select sleep({i});" for i in split_total(30, 30)]
    print(texts)
    for i, t in enumerate(texts, start=1):
        threading.Thread(target=exec_sql, args=(pool, t, i), daemon=True).start()

    time.sleep(3600)
