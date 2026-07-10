"""Alembic 迁移环境配置（async 版本）。

配套 SQLAlchemy 2.0 async 引擎，使用 psycopg v3 异步驱动迁移 KingbaseES（兼容 PostgreSQL）。
连接串从 `app.config.settings` 注入，并在离线/在线两种模式下均通过 async 执行迁移。
Windows 上需切换事件策略以兼容 psycopg async 驱动。
"""
import asyncio  # 异步事件循环
import sys  # 平台检测
from logging.config import fileConfig  # 日志配置加载

# Windows 上 psycopg async 需要 SelectorEventLoop 而非 ProactorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from alembic import context  # Alembic 迁移上下文
from sqlalchemy import pool  # 连接池工具
from sqlalchemy.engine import Connection  # 同步连接类型注解
from sqlalchemy.ext.asyncio import async_engine_from_config  # 从配置创建异步引擎

from app.config.settings import settings  # 全局配置（含数据库连接串）

# KingbaseES 兼容性补丁：必须在引擎连接前加载，否则版本识别抛 AssertionError
from app.db import compat  # noqa: F401

# 导入实体包触发所有模型向 Base.metadata 注册，以便 autogenerate 捕获表结构
from app.models.entities import Base  # noqa: F401  声明式基类与模型注册

# Alembic 配置对象
config = context.config

# 注入数据库连接串：覆盖 alembic.ini 中的空值
config.set_main_option("sqlalchemy.url", settings.database_url)

# 日志配置（如 alembic.ini 中存在）
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# 全局目标 MetaData：autogenerate 据此生成差异
_target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以离线模式生成 SQL 脚本，无需连接数据库。

    将 MetaData 的变更渲染为 SQL 语句输出。
    """
    # 离线模式直接用 URL 创建引擎占位（不实际连接）
    url = config.get_main_option("sqlalchemy.url")
    # 渲染迁移为 SQL，而非真正执行
    context.configure(
        url=url,  # 连接串
        target_metadata=_target_metadata,  # ORM MetaData
        literal_binds=True,  # 将参数内联为字面量
        dialect_opts={"paramstyle": "named"},  # 命名参数风格
        compare_type=True,  # 比较列类型以检测变更
    )
    # 执行迁移脚本渲染
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """在已有连接上执行迁移。"""
    # 绑定连接并执行迁移
    context.configure(connection=connection, target_metadata=_target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """以在线 async 模式执行迁移。"""
    # 从配置创建异步引擎，复用连接池策略
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 迁移过程无需连接池，使用空池
    )
    try:
        # 获取同步连接包装并执行迁移
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        # 关闭释放引擎
        await connectable.dispose()


def run_migrations_online() -> None:
    """以在线模式执行迁移，交给 async 事件循环驱动。"""
    # 委托给事件循环执行 async 迁移
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    # 离线模式渲染 SQL
    run_migrations_offline()
else:
    # 在线模式真正执行
    run_migrations_online()
