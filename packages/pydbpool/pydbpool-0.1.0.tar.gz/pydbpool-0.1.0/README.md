
# PyDBPool - Python Database Connection Pool

[![PyPI Version](https://img.shields.io/pypi/v/pydbpool)](https://pypi.org/project/pydbpool/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pydbpool)](https://pypi.org/project/pydbpool/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**PyDBPool** 是一个高性能、通用的数据库连接池实现，支持主流关系型数据库，提供完善的连接生命周期管理和监控功能。

## 特性

- 🚀 **多数据库支持**：PostgreSQL、MySQL、SQLite 等
- 🔒 **线程安全**：严格的锁机制保证高并发安全
- 📊 **实时监控**：内置连接池指标统计
- 🩺 **健康检查**：自动心跳检测与失效连接剔除
- ⚡ **异步就绪**：支持协程环境（需异步驱动）
- 🔌 **智能调度**：动态扩缩容与最小空闲维持
- 🛠️ **扩展接口**：钩子函数与自定义策略支持

## 安装

```bash
# 基础安装
pip install pydbpool

# 按需选择数据库驱动
pip install pydbpool[postgres]   # PostgreSQL支持
pip install pydbpool[mysql]      # MySQL支持
```

## 快速开始

### 基本用法

```python
from pydbpool import DBPool
import psycopg2

# 初始化连接池
pool = DBPool(
    factory=lambda: psycopg2.connect(
        dbname="test",
        user="postgres",
        password="secret"
    ),
    min_idle=3,
    max_size=10,
    idle_timeout=300
)

# 使用连接
with pool.connection() as conn:
    cursor = conn.raw.cursor()
    cursor.execute("SELECT version()")
    print(cursor.fetchone())
```

### 监控指标

```python
print(pool.metrics)
# 输出示例：
# {
#   'total': 5,
#   'active': 2,
#   'idle': 3,
#   'max_size': 10,
#   'min_idle': 3
# }
```

## 高级功能

### 钩子函数

```python
# 注册连接获取钩子
@pool.hooks['post_acquire'].append
def log_connection(conn):
    print(f"Acquired connection {conn.meta.created_at}")

# 注册健康检查钩子
@pool.hooks['health_check'].append
def health_monitor(conn):
    if not conn.meta.is_healthy:
        send_alert(f"Unhealthy connection: {conn}")
```

### Web框架集成（Flask示例）

```python
from flask import Flask, g
from pydbpool import DBPool

app = Flask(__name__)
pool = DBPool(...)

@app.before_request
def get_connection():
    g.db_conn = pool.acquire()

@app.teardown_request
def release_connection(exc):
    if hasattr(g, 'db_conn'):
        pool.release(g.db_conn)

@app.route("/users")
def list_users():
    with g.db_conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
        return {"users": cur.fetchall()}
```

## 配置选项

| 参数            | 默认值 | 描述                          |
|-----------------|--------|-------------------------------|
| `min_idle`      | 3      | 最小空闲连接数                |
| `max_size`      | 20     | 最大连接数                    |
| `idle_timeout`  | 300    | 空闲连接超时时间（秒）        |
| `max_lifetime`  | 3600   | 连接最大生命周期（秒）        |
| `ping_query`    | SELECT 1 | 健康检查SQL                 |

## 性能建议

1. **连接数配置**：
   ```python
   # 推荐公式
   max_size = (avg_concurrent_requests × avg_query_time) + buffer
   ```

2. **监控集成**：
   ```python
   # Prometheus示例
   from prometheus_client import Gauge

   ACTIVE_GAUGE = Gauge('db_pool_active', 'Active connections')
   @pool.hooks['post_acquire'].append
   def update_metrics(_):
       ACTIVE_GAUGE.set(pool.metrics['active'])
   ```

## 开发指南

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest test/

# 生成文档
cd docs && make html
```

## 贡献

欢迎通过 [GitHub Issues](https://github.com/yourusername/pydbpool/issues) 报告问题或提交 Pull Request

## 许可证

[MIT License](LICENSE)

---

### 关键要素说明

1. **徽章系统**：显示版本、Python兼容性和许可证信息
2. **多代码块**：使用不同语言标签实现语法高亮
3. **配置表格**：清晰展示主要参数
4. **Web集成示例**：展示与Flask的整合
5. **监控集成**：提供Prometheus对接示例
6. **开发工作流**：明确贡献者指南

建议配合以下内容增强文档：
1. 添加架构图（使用Mermaid语法）
2. 性能基准测试数据
3. 与常用框架（Django、FastAPI）的集成示例
4. 故障排除指南
5. 版本更新日志