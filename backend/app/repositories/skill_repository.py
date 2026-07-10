"""技能字典仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.skill import Skill  # 技能字典 ORM


async def get_by_id(db: AsyncSession, skill_id: int) -> Skill | None:
    """按主键查询未删除的技能。

    Args:
        db: 异步数据库会话。
        skill_id: 技能主键。

    Returns:
        Skill | None: 命中返回实例，否则返回 None。
    """
    stmt = select(Skill).where(
        Skill.id == skill_id,
        Skill.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Skill | None:
    """按技能名称精确匹配查询未删除且非合并状态的技能。

    Args:
        db: 异步数据库会话。
        name: 技能名称。

    Returns:
        Skill | None: 命中返回实例，否则返回 None。
    """
    stmt = select(Skill).where(
        Skill.name == name,
        Skill.deleted_at == "0",
        Skill.status != "MERGED",  # 已合并技能不再独立使用
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_names(db: AsyncSession, names: list[str]) -> dict[str, Skill]:
    """批量按技能名称查询，返回名称到技能实例的映射。

    Args:
        db: 异步数据库会话。
        names: 需要查询的技能名称列表。

    Returns:
        dict[str, Skill]: 名称 -> 技能实例 的映射；未命中的名称不在其中。
    """
    if not names:
        return {}
    stmt = select(Skill).where(
        Skill.name.in_(names),
        Skill.deleted_at == "0",
        Skill.status != "MERGED",
    )
    result = await db.execute(stmt)
    return {s.name: s for s in result.scalars().all()}


async def create(db: AsyncSession, skill: Skill) -> Skill:
    """新增技能并刷新主键。

    Args:
        db: 异步数据库会话。
        skill: 待新增的 Skill 实例。

    Returns:
        Skill: 已写入数据库、含主键的技能实例。
    """
    db.add(skill)
    await db.flush()
    return skill
