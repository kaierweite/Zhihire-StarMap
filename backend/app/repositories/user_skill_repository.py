"""用户技能关联仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.skill import Skill  # 技能字典 ORM
from app.models.entities.user_skill import UserSkill  # 用户技能关联 ORM


async def list_by_user(db: AsyncSession, user_id: int) -> list[tuple[UserSkill, Skill]]:
    """查询某用户的全部技能关联，并 JOIN 取回技能元信息。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。

    Returns:
        list[tuple[UserSkill, Skill]]: (关联实例, 技能实例) 列表。
    """
    stmt = (
        select(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .where(
            UserSkill.user_id == user_id,
            UserSkill.deleted_at == "0",
            Skill.deleted_at == "0",
        )
    )
    result = await db.execute(stmt)
    return [(us, sk) for us, sk in result.all()]


async def list_active_skill_ids(db: AsyncSession, user_id: int) -> list[int]:
    """查询某用户当前未软删的技能主键列表。

    用于更新时与目标集做差集比较。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。

    Returns:
        list[int]: 当前关联的技能主键列表。
    """
    stmt = select(UserSkill.skill_id).where(
        UserSkill.user_id == user_id,
        UserSkill.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def find_active_by_skill(db: AsyncSession, user_id: int, skill_id: int) -> UserSkill | None:
    """查询某用户某技能的当前关联记录。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。
        skill_id: 技能主键。

    Returns:
        UserSkill | None: 命中返回实例，否则返回 None。
    """
    stmt = select(UserSkill).where(
        UserSkill.user_id == user_id,
        UserSkill.skill_id == skill_id,
        UserSkill.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_skill: UserSkill) -> UserSkill:
    """新增用户技能关联并刷新主键。

    Args:
        db: 异步数据库会话。
        user_skill: 待新增的 UserSkill 实例。

    Returns:
        UserSkill: 已写入数据库、含主键的实例。
    """
    db.add(user_skill)
    await db.flush()
    return user_skill


async def soft_delete(db: AsyncSession, user_skill: UserSkill) -> None:
    """软删除用户技能关联（设置 deleted_at='1'）。

    Args:
        db: 异步数据库会话。
        user_skill: 待软删的 UserSkill 实例。
    """
    user_skill.deleted_at = "1"
    await db.flush()
