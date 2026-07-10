"""技能字典仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import func, select, text  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.skill import Skill  # 技能字典 ORM
from app.models.enums.status import SkillStatusEnum


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
        Skill.deleted_at == text("'0'"),
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
        Skill.deleted_at == text("'0'"),
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
        Skill.deleted_at == text("'0'"),
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


async def list_active(db: AsyncSession) -> list[Skill]:
    """查询所有未删除且非合并状态的技能。

    Args:
        db: 异步数据库会话。

    Returns:
        list[Skill]: 技能列表。
    """
    stmt = select(Skill).where(
        Skill.deleted_at == text("'0'"),
        Skill.status != "MERGED",
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_ids(db: AsyncSession, skill_ids: list[int]) -> dict[int, Skill]:
    """批量按主键查询技能。

    Args:
        db: 异步数据库会话。
        skill_ids: 技能主键列表。

    Returns:
        dict[int, Skill]: ID -> 技能实例 的映射。
    """
    if not skill_ids:
        return {}
    stmt = select(Skill).where(
        Skill.id.in_(skill_ids),
        Skill.deleted_at == text("'0'"),
    )
    result = await db.execute(stmt)
    return {s.id: s for s in result.scalars().all()}

async def search_by_name(db: AsyncSession, keyword: str, limit: int = 20) -> list[Skill]:
    """按名称模糊搜索技能（ILIKE），用于前端技能下拉搜索。

    Args:
        db: 异步数据库会话。
        keyword: 搜索关键词。
        limit: 返回条数上限，默认 20。

    Returns:
        list[Skill]: 匹配的技能列表。
    """
    stmt = (
        select(Skill)
        .where(
            Skill.name.ilike(f"%{keyword}%"),
            Skill.deleted_at == text("'0'"),
            Skill.status != "MERGED",
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_candidates(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Skill], int]:
    """分页查询待审核候选技能（status == CANDIDATE）。"""
    base_cond = [
        Skill.deleted_at == text("'0'"),
        Skill.status == SkillStatusEnum.CANDIDATE.value,
    ]
    count_stmt = select(func.count()).select_from(Skill).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    query_stmt = (
        select(Skill)
        .where(*base_cond)
        .order_by(Skill.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query_stmt)
    records = list(result.scalars().all())
    return records, total


async def approve_skill(
    db: AsyncSession,
    skill_id: int,
    target_id: int | None = None,
) -> Skill | None:
    """审核通过候选技能。"""
    skill = await get_by_id(db, skill_id)
    if skill is None:
        return None
    if target_id is not None:
        skill.status = SkillStatusEnum.MERGED.value
    else:
        skill.status = SkillStatusEnum.ACTIVE.value
    await db.flush()
    return skill


async def reject_skill(db: AsyncSession, skill_id: int) -> Skill | None:
    """驳回候选技能（软删除）。"""
    skill = await get_by_id(db, skill_id)
    if skill is None:
        return None
    skill.deleted_at = "1"
    await db.flush()
    return skill
