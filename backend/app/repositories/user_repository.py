"""用户仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.user import User  # 用户 ORM


async def create(db: AsyncSession, user: User) -> User:
    """新增用户并刷新主键。

    Args:
        db: 异步数据库会话。
        user: 待新增的 User 实例。

    Returns:
        User: 已写入数据库、含主键的用户实例。
    """
    db.add(user)
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
    stmt = select(User).where(
        User.username == username,
        User.deleted_at == "0",  # 库约定：'0' 未删除
    )
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
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at == "0",  # 库约定：'0' 未删除
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def list_by_role(db: AsyncSession, role: str) -> list[User]:
    """按角色查询未删除的用户列表。"""
    stmt = select(User).where(
        User.role == role,
        User.deleted_at == "0",
    ).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
