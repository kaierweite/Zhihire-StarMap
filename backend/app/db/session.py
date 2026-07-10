"""数据库会话模块。

基于 SQLAlchemy 2.0 async 构建异步引擎与会话工厂，
并提供 FastAPI 路由使用的 `get_db` 依赖。

注意：引擎在创建时不会真正连接数据库，`/api/ping` 端点不依赖数据库，
因此在数据库尚未初始化时骨架仍可启动。
"""
from collections.abc import AsyncGenerator  # 异步生成器类型注解

from sqlalchemy.ext.asyncio import (  # 异步引擎与扩展会话工具
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings  # 全局配置单例


# 配置连接池参数：pool_size、max_overflow、recycle 均来自配置
# echo 关闭以避免日志噪音；future=True 确保使用 SQLAlchemy 2.0 行为
async_engine = create_async_engine(
    settings.database_url,  # KingbaseES 兼容 PostgreSQL，asyncpg 驱动
    pool_size=settings.db_pool_size,  # 常驻连接数
    max_overflow=settings.db_max_overflow,  # 溢出连接数
    pool_recycle=settings.db_pool_recycle,  # 连接回收周期（秒）
    echo=False,  # 不打印 SQL 日志
    future=True,  # 启用 2.0 行为
    pool_pre_ping=True,  # 使用前探测连接，避免拿到失效连接
)


# 异步会话工厂：绑定上述引擎，禁用自动提交以显式控制事务
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定异步引擎
    class_=AsyncSession,  # 会话类
    autoflush=False,  # 关闭自动 flush，减少隐式 SQL
    expire_on_commit=False,  # 提交后不过期，便于读取已提交对象
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的 FastAPI 依赖。

    以生成器形式提供，确保请求结束后会话被正确关闭，
    即便中途抛出异常也能进入 finally 释放连接。

    Yields:
        AsyncSession: 当前请求范围内的异步数据库会话。
    """
    # 为每个请求创建独立会话
    async with AsyncSessionLocal() as session:
        # 交出会话供路由使用
        yield session
        # 作用域结束时自动关闭并归还连接


async def check_db_connection() -> bool:
    """检查数据库连接是否可用。

    执行 `SELECT 1` 探测，用于健康检查或启动自检。
    注意：此函数会真正访问数据库，仅在库已初始化时使用。

    Returns:
        bool: 连接成功返回 True，失败返回 False。
    """
    # 使用文本 SQL 执行探测
    from sqlalchemy import text  # 延迟导入，避免顶层依赖

    try:
        # 打开连接并执行 SELECT 1
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True  # 探测成功
    except Exception:
        # 任何异常均视为不可用，交由调用方决定是否降级
        return False