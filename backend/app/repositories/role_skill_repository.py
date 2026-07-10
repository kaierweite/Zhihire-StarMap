"""角色-技能关联仓储模块。
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.role_skill import RoleSkill
from app.models.entities.skill import Skill


async def list_by_role(db: AsyncSession, role_id: int) -> list[tuple[RoleSkill, Skill]]:
    stmt = (
        select(RoleSkill, Skill)
        .join(Skill, RoleSkill.skill_id == Skill.id)
        .where(RoleSkill.role_id == role_id, RoleSkill.deleted_at == "0", Skill.deleted_at == "0")
    )
    result = await db.execute(stmt)
    return [(rs, sk) for rs, sk in result.all()]


async def list_by_skill_ids(db: AsyncSession, skill_ids: list[int]) -> list[RoleSkill]:
    if not skill_ids:
        return []
    stmt = select(RoleSkill).where(RoleSkill.skill_id.in_(skill_ids), RoleSkill.deleted_at == "0")
    result = await db.execute(stmt)
    return list(result.scalars().all())
