# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : base.py
@Project  : 
@Time     : 2025/3/18 10:57
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import time
from dataclasses import dataclass
from typing import Iterable, Optional, Set, Dict, Any
import threading


@dataclass
class ConnectionMeta:
    """连接元数据管理"""
    created_at: float = time.time()
    last_active: float = time.time()
    is_alive: bool = True
    usage_count: int = 0
    total_usage_time: float = 0.0
    last_error: Optional[str] = None
    error_count: int = 0

    def update_activity(self):
        self.last_active = time.time()

    def record_error(self, error: str):
        self.last_error = error
        self.error_count += 1

    def record_usage(self, duration: float):
        self.total_usage_time += duration
        self.usage_count += 1

    @property
    def avg_usage_time(self) -> float:
        return self.total_usage_time / self.usage_count if self.usage_count > 0 else 0.0


class ConnectionPoolMeta:
    """连接池元数据"""

    def __init__(self):
        self.created_at = time.time()
        self.last_active = time.time()
        self.total_count = 0
        self.borrow_count = 0
        self.free_count = 0
        self.error_count = 0
        self.wait_count = 0
        self.error_history = []  # 记录错误历史
        self.wait_times = []  # 记录等待时间
        self.usage_times = []  # 记录使用时间
        self._lock = threading.RLock()

    def record_wait(self, wait_time: float) -> None:
        """记录等待时间"""
        with self._lock:
            self.wait_count += 1
            self.wait_times.append(wait_time)
            # 只保留最近1000个等待时间记录
            if len(self.wait_times) > 1000:
                self.wait_times.pop(0)

    def record_usage(self, usage_time: float) -> None:
        """记录使用时间"""
        with self._lock:
            self.usage_times.append(usage_time)
            # 只保留最近1000个使用时间记录
            if len(self.usage_times) > 1000:
                self.usage_times.pop(0)

    def record_error(self, error_msg: str = None) -> None:
        """记录错误"""
        with self._lock:
            self.error_count += 1
            if error_msg:
                self.error_history.append({
                    'timestamp': time.time(),
                    'message': error_msg
                })
                # 只保留最近100个错误记录
                if len(self.error_history) > 100:
                    self.error_history.pop(0)

    def update_activity(self, count: int = 1, active_conns: Set = None) -> None:
        """更新活动连接数"""
        with self._lock:
            self.last_active = time.time()
            if active_conns is not None:
                self.free_count = self.total_count - len(active_conns)

    def record_borrow(self) -> None:
        """记录连接借用"""
        with self._lock:
            self.borrow_count += 1

    def record_return(self) -> None:
        """记录连接归还"""
        with self._lock:
            self.borrow_count -= 1

    def clear(self) -> None:
        """清理元数据"""
        with self._lock:
            self.total_count = 0
            self.borrow_count = 0
            self.free_count = 0
            self.error_count = 0
            self.wait_count = 0
            self.error_history.clear()
            self.wait_times.clear()
            self.usage_times.clear()

    def as_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        with self._lock:
            return {
                'created_at': self.created_at,
                'last_active': self.last_active,
                'total_count': self.total_count,
                'borrow_count': self.borrow_count,
                'free_count': self.free_count,
                'error_count': self.error_count,
                'wait_count': self.wait_count,
                'error_history': self.error_history,
                'wait_times': self.wait_times,
                'usage_times': self.usage_times,
                'avg_wait_time': sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0,
                'avg_usage_time': sum(self.usage_times) / len(self.usage_times) if self.usage_times else 0,
                'max_wait_time': max(self.wait_times) if self.wait_times else 0,
                'max_usage_time': max(self.usage_times) if self.usage_times else 0,
                'total_wait_time': sum(self.wait_times),
                'total_usage_time': sum(self.usage_times)
            }
