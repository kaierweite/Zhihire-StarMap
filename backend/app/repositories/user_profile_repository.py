"""用户档案仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.user_profile import UserProfile  # 用户档案 ORM


async def get_by_user_id(db: AsyncSession, user_id: int) -> UserProfile | None:
    """按关联用户主键查询未删除的档案记录。

    Args:
        db: 异步数据库会话。
        user_id: 关联的用户主键。

    Returns:
        UserProfile | None: 命中返回实例，否则返回 None。
    """
    stmt = select(UserProfile).where(
        UserProfile.user_id == user_id,
        UserProfile.deleted_at == "0",  # 库约定：'0' 未删除
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, profile: UserProfile) -> UserProfile:
    """新增用户档案并刷新主键。

    Args:
        db: 异步数据库会话。
        profile: 待新增的 UserProfile 实例。

    Returns:
        UserProfile: 已写入数据库、含主键的档案实例。
    """
    db.add(profile)
    await db.flush()
    return profile


async def update(db: AsyncSession, profile: UserProfile) -> UserProfile:
    """更新已存在的用户档案实例。

    Args:
        db: 异步数据库会话。
        profile: 已在会话中加载的 UserProfile 实例（修改后直接传入）。

    Returns:
        UserProfile: 更新后的档案实例。
    """
    # 实例已绑定到会话，flush 即可同步到数据库
    await db.flush()
    return profile
