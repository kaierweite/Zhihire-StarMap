"""岗位仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from datetime import datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.company import Company
from app.models.entities.job import Job
from app.models.entities.occupation_role import OccupationRole


async def create(db: AsyncSession, job: Job) -> Job:
    """新增岗位记录并刷新主键。"""
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


async def get_by_id(db: AsyncSession, job_id: int) -> Job | None:
    """按主键查询未删除的岗位。"""
    stmt = select(Job).where(Job.id == job_id, Job.deleted_at == "0")
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id_with_company(db: AsyncSession, job_id: int) -> tuple[Job, Company] | tuple[None, None]:
    """按主键查询岗位及其所属企业（仅 VERIFIED 企业）。"""
    stmt = (
        select(Job, Company)
        .join(Company, Job.company_id == Company.id)
        .where(Job.id == job_id, Job.deleted_at == "0", Company.deleted_at == "0")
    )
    result = await db.execute(stmt)
    row = result.one_or_none()
    if row is None:
        return None, None
    return row[0], row[1]


async def increment_views(db: AsyncSession, job_id: int) -> None:
    """岗位浏览次数 +1。"""
    stmt = (
        update(Job)
        .where(Job.id == job_id, Job.deleted_at == "0")
        .values(views=Job.views + 1)
    )
    await db.execute(stmt)


async def update_job(db: AsyncSession, job: Job, values: dict[str, Any]) -> Job:
    """部分更新岗位字段。"""
    for key, value in values.items():
        if hasattr(job, key) and value is not None:
            setattr(job, key, value)
    job.updated_at = datetime.now()
    await db.flush()
    return job


async def soft_delete(db: AsyncSession, job: Job) -> None:
    """软删除岗位。"""
    job.deleted_at = "1"
    await db.flush()


async def search_jobs(
    db: AsyncSession,
    keyword: str | None = None,
    city: str | None = None,
    education_requirement: str | None = None,
    experience_min: int | None = None,
    salary_min: float | None = None,
    salary_max: float | None = None,
    job_type: str | None = None,
    major: str | None = None,
    job_category: str | None = None,
    company_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Job], int]:
    """搜索岗位（仅展示已审核企业发布的有效岗位）。"""
    base_cond = [
        Job.deleted_at == "0",
        Company.deleted_at == "0",
        Company.audit_status == "VERIFIED",
    ]
    if status and status != "ALL":
        base_cond.append(Job.status == status)
    elif not status:
        base_cond.append(Job.status == "OPEN")
    if company_id is not None:
        base_cond.append(Job.company_id == company_id)
    if keyword:
        base_cond.append(Job.title.ilike(f"%{keyword}%"))
    if city:
        base_cond.append(Job.city.ilike(f"%{city}%"))
    if education_requirement:
        base_cond.append(Job.education_requirement == education_requirement)
    if experience_min is not None:
        base_cond.append(Job.experience_min <= experience_min)
    if salary_min is not None:
        base_cond.append(Job.salary_max >= salary_min)
    if salary_max is not None:
        base_cond.append(Job.salary_min <= salary_max)
    if job_type:
        base_cond.append(Job.job_type == job_type)

    count_stmt = (
        select(func.count()).select_from(Job)
        .join(Company, Job.company_id == Company.id)
        .where(*base_cond)
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    query_stmt = (
        select(Job)
        .join(Company, Job.company_id == Company.id)
        .where(*base_cond)
        .order_by(Job.updated_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query_stmt)
    records = list(result.scalars().all())

    return records, total


async def list_by_company(db: AsyncSession, company_id: int) -> list[Job]:
    """查询某企业所有未删除岗位。"""
    stmt = (
        select(Job)
        .where(Job.company_id == company_id, Job.deleted_at == "0")
        .order_by(Job.updated_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
