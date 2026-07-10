"""用户仓储模块。

只做原子数据库操作，不包含业务编排与事务提交。
事务提交由调用方（service 层）负责，仓储仅负责数据访问与刷新以取回主键。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.user import User  # 用户 ORM


async def create(db: AsyncSession, user: User) -> User:
    """新增用户并刷新主键。

    Args:
        db: 异步数据库会话。
        user: 待新增的 User 实例（调用方负责填充 password_hash 等字段）。

    Returns:
        User: 已写入数据库、含主键的用户实例。
    """
    # 加入会话
    db.add(user)
    # 刷新以取回数据库生成的主键与 server_default 字段
    await db.flush()
    return user


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    """按用户名查询未删除的用户。

    Args:
        db: 异步数据库会话。
        username: 用户名。

    Returns:
        User | None: 命中返回实例，否则返回 None。
    """
    # 构造查询：用户名匹配且未软删除
    stmt = select(User).where(
        User.username == username,
        User.deleted_at.is_(None),
    )
    # 执行并取第一条
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    """按主键查询未删除的用户。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。

    Returns:
        User | None: 命中返回实例，否则返回 None。
    """
    # 构造查询：主键匹配且未软删除
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    # 执行并取第一条
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
