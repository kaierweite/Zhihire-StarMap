"""岗位业务服务模块。

编排岗位的 CRUD、搜索、技能关联等 8 个端点对应的业务逻辑。
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.job import Job
from app.models.entities.job_skill import JobSkill
from app.models.schemas.job import (
    AddJobSkillRequest,
    AddJobSkillResult,
    CreateJobRequest,
    CreateJobResult,
    JobDetail,
    JobItem,
    JobSkillItem,
    UpdateJobRequest,
)
from app.repositories import (
    company_repository,
    job_repository,
    job_skill_repository,
    occupation_role_repository,
    skill_repository,
)
from app.services.errors import BusinessError


async def create_job(
    db: AsyncSession,
    user_id: int,
    req: CreateJobRequest,
) -> CreateJobResult:
    """创建岗位。"""
    company = await company_repository.get_by_user_id(db, user_id)
    if company is None:
        raise BusinessError(403, "企业不存在，无权限发布岗位")
    if company.audit_status != "VERIFIED":
        raise BusinessError(403, "企业未通过审核，无法发布岗位")

    job = Job(
        company_id=company.id,
        occupation_role_id=req.occupation_role_id,
        title=req.title,
        city=req.city,
        education_requirement=req.education_requirement,
        experience_min=req.experience_min,
        salary_min=req.salary_min,
        salary_max=req.salary_max,
        job_type=req.job_type,
        description=req.description,
        benefits=req.benefits,
    )
    job = await job_repository.create(db, job)
    await db.commit()
    return CreateJobResult(id=job.id, title=job.title)
