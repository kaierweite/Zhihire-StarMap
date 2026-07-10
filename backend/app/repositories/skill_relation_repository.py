"""技能关系仓储模块。
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.skill_relation import SkillRelation


async def list_active(db: AsyncSession) -> list[SkillRelation]:
    stmt = select(SkillRelation).where(SkillRelation.deleted_at == "0")
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_by_skill(db: AsyncSession, skill_id: int) -> list[SkillRelation]:
    stmt = select(SkillRelation).where(
        ((SkillRelation.skill_id_a == skill_id) | (SkillRelation.skill_id_b == skill_id)),
        SkillRelation.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, relation: SkillRelation) -> SkillRelation:
    db.add(relation)
    await db.flush()
    return relation
