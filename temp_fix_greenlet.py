import os, py_compile

filepath = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\job_service.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('\ufeff', '')

# Rebuild with top-level imports and proper signatures
new_file = r'''"""岗位业务服务模块。

编排岗位的 CRUD、搜索、技能关联等 8 个端点对应的业务逻辑。
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.job import Job
from app.models.entities.job_skill import JobSkill
from app.models.entities.job_application import JobApplication
from app.models.schemas.job import (
    ApplyJobResult,
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
    job_application_repository,
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


async def search_jobs(
    db: AsyncSession,
    keyword: str | None = None,
    city: str | None = None,
    education_requirement: str | None = None,
    experience_min: int | None = None,
    salary_min: float | None = None,
    salary_max: float | None = None,
    job_type: str | None = None,
    company_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[JobItem], int]:
    records, total = await job_repository.search_jobs(
        db, keyword=keyword, city=city,
        education_requirement=education_requirement,
        experience_min=experience_min, salary_min=salary_min,
        salary_max=salary_max, job_type=job_type, company_id=company_id,
        status=status, page=page, size=size,
    )
    company_ids = list({r.company_id for r in records})
    companies = {}
    for cid in company_ids:
        c = await company_repository.get_by_company_id(db, cid)
        if c:
            companies[cid] = c
    items = []
    for r in records:
        comp = companies.get(r.company_id)
        items.append(JobItem(
            id=r.id, company_id=r.company_id,
            company_name=comp.company_name if comp else None,
            title=r.title, city=r.city,
            education_requirement=r.education_requirement,
            experience_min=r.experience_min,
            salary_min=float(r.salary_min) if r.salary_min is not None else None,
            salary_max=float(r.salary_max) if r.salary_max is not None else None,
            job_type=r.job_type, status=r.status, views=r.views,
            benefits=r.benefits, occupation_role_id=r.occupation_role_id,
            created_at=r.created_at, updated_at=r.updated_at,
        ))
    return items, total


async def get_job_detail(
    db: AsyncSession,
    job_id: int,
    increment_view: bool = True,
) -> JobDetail:
    job, company = await job_repository.get_by_id_with_company(db, job_id)
    if job is None or company is None:
        raise BusinessError(404, "岗位不存在")
    if company.audit_status != "VERIFIED":
        raise BusinessError(404, "岗位不存在")
    if increment_view:
        await job_repository.increment_views(db, job.id)
        await db.commit()
    role_name = None
    if job.occupation_role_id:
        role = await occupation_role_repository.get_by_id(db, job.occupation_role_id)
        role_name = role.name if role else None
    skills = []
    skill_rows = await job_skill_repository.list_by_job(db, job_id)
    for js, sk in skill_rows:
        skills.append(JobSkillItem(
            id=js.id, job_id=js.job_id, skill_id=js.skill_id,
            skill_name=sk.name, skill_category=sk.category,
            importance=js.importance, required_level=js.required_level,
        ))
    return JobDetail(
        id=job.id, company_id=job.company_id,
        company_name=company.company_name,
        occupation_role_id=job.occupation_role_id,
        occupation_role_name=role_name,
        title=job.title, city=job.city,
        education_requirement=job.education_requirement,
        experience_min=job.experience_min,
        salary_min=float(job.salary_min) if job.salary_min is not None else None,
        salary_max=float(job.salary_max) if job.salary_max is not None else None,
        job_type=job.job_type, description=job.description,
        requirements=job.requirements, source=job.source,
        status=job.status, views=job.views + 1 if increment_view else job.views,
        benefits=job.benefits, skills=skills,
        created_at=job.created_at, updated_at=job.updated_at,
    )


async def update_job(
    db: AsyncSession,
    company_id: int,
    job_id: int,
    req: UpdateJobRequest,
) -> JobDetail:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    values: dict[str, Any] = {}
    for field in [
        "title", "city", "education_requirement", "experience_min",
        "salary_min", "salary_max", "job_type", "description",
        "occupation_role_id", "status", "benefits",
    ]:
        val = getattr(req, field, None)
        if val is not None:
            values[field] = val
    await job_repository.update_job(db, job, values)
    await db.commit()
    return await get_job_detail(db, job_id, increment_view=False)


async def delete_job(db: AsyncSession, company_id: int, job_id: int) -> None:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    await job_repository.soft_delete(db, job)
    await db.commit()


async def add_job_skill(
    db: AsyncSession,
    company_id: int,
    job_id: int,
    req: AddJobSkillRequest,
) -> AddJobSkillResult:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    skill = await skill_repository.get_by_id(db, req.skill_id)
    if skill is None:
        raise BusinessError(404, "技能不存在")
    existing = await job_skill_repository.get_by_job_and_skill(db, job_id, req.skill_id)
    if existing:
        raise BusinessError(409, "该技能已关联到此岗位")
    job_skill = JobSkill(job_id=job_id, skill_id=req.skill_id, importance=req.importance, required_level=req.required_level)
    job_skill = await job_skill_repository.create(db, job_skill)
    await db.commit()
    return AddJobSkillResult(id=job_skill.id, job_id=job_id, skill_id=req.skill_id, required_level=req.required_level)


async def list_job_skills(db: AsyncSession, job_id: int) -> list[JobSkillItem]:
    skill_rows = await job_skill_repository.list_by_job(db, job_id)
    items = []
    for js, sk in skill_rows:
        items.append(JobSkillItem(
            id=js.id, job_id=js.job_id, skill_id=js.skill_id,
            skill_name=sk.name, skill_category=sk.category,
            importance=js.importance, required_level=js.required_level,
        ))
    return items


async def remove_job_skill(
    db: AsyncSession, company_id: int, job_id: int, skill_id: int,
) -> None:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    deleted = await job_skill_repository.delete_by_job_and_skill(db, job_id, skill_id)
    if not deleted:
        raise BusinessError(404, "技能关联不存在")
    await db.commit()


async def apply_job(
    db: AsyncSession, user_id: int, job_id: int, resume_id: int | None = None,
) -> ApplyJobResult:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.status != "OPEN":
        raise BusinessError(404, "岗位不存在或已关闭")
    existing = await job_application_repository.get_by_user_and_job(db, user_id, job_id)
    if existing:
        raise BusinessError(409, "已投递过该岗位")
    application = JobApplication(user_id=user_id, job_id=job_id, resume_id=resume_id)
    application = await job_application_repository.create(db, application)
    await db.commit()
    return ApplyJobResult(id=application.id, user_id=user_id, job_id=job_id, status=application.status)


async def list_job_applications(
    db: AsyncSession, company_id: int, job_id: int, page: int = 1, size: int = 20,
) -> tuple[list, int]:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    rows, total = await job_application_repository.list_by_job_paginated(db, job_id, page=page, size=size)
    items = []
    for app, username, email, phone in rows:
        items.append(ApplyJobResult(id=app.id, job_id=app.job_id, user_id=app.user_id, status=app.status))
    return items, total
'''

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_file)

try:
    py_compile.compile(filepath, doraise=True)
    size = os.path.getsize(filepath)
    lines = new_file.count('\n') + 1
    funcs = [l.strip() for l in new_file.split('\n') if 'async def ' in l]
    print(f"OK: {size} bytes, {lines} lines")
    for fn in funcs:
        print(f"  {fn}")
    # Verify salary fix
    if 'is not None' in new_file:
        print("  salary fix: CONFIRMED")
except py_compile.PyCompileError as e:
    print(f"FAIL: {e}")