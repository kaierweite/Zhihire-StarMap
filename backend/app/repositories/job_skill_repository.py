"""岗位-技能关联仓储模块。"""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.job_skill import JobSkill
from app.models.entities.skill import Skill


async def create(db: AsyncSession, job_skill: JobSkill) -> JobSkill:
    """新增岗位-技能关联。"""
    db.add(job_skill)
    await db.flush()
    await db.refresh(job_skill)
    return job_skill


async def get_by_job_and_skill(db: AsyncSession, job_id: int, skill_id: int) -> JobSkill | None:
    """按岗位和技能查询关联。"""
    stmt = select(JobSkill).where(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id,
        JobSkill.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_job(db: AsyncSession, job_id: int) -> list[tuple[JobSkill, Skill]]:
    """查询岗位的所有技能关联（含技能实体）。"""
    stmt = (
        select(JobSkill, Skill)
        .join(Skill, JobSkill.skill_id == Skill.id)
        .where(JobSkill.job_id == job_id, JobSkill.deleted_at == "0", Skill.deleted_at == "0")
    )
    result = await db.execute(stmt)
    return [(js, sk) for js, sk in result.all()]


async def soft_delete(db: AsyncSession, job_skill: JobSkill) -> None:
    """软删除岗位-技能关联。"""
    job_skill.deleted_at = "1"
    await db.flush()


async def delete_by_job_and_skill(db: AsyncSession, job_id: int, skill_id: int) -> bool:
    """硬删除岗位-技能关联。CASCADE 安全。返回是否删除。"""
    stmt = delete(JobSkill).where(
        JobSkill.job_id == job_id,
        JobSkill.skill_id == skill_id,
    )
    result = await db.execute(stmt)
    return result.rowcount > 0
