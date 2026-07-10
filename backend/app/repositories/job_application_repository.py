"""简历投递仓储模块。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.job_application import JobApplication


async def create(db: AsyncSession, application: JobApplication) -> JobApplication:
    """新增投递记录。"""
    db.add(application)
    await db.flush()
    await db.refresh(application)
    return application


async def get_by_user_and_job(db: AsyncSession, user_id: int, job_id: int) -> JobApplication | None:
    """查询用户对某岗位的投递记录。"""
    stmt = select(JobApplication).where(
        JobApplication.user_id == user_id,
        JobApplication.job_id == job_id,
        JobApplication.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_user(db: AsyncSession, user_id: int, page: int = 1, size: int = 20) -> tuple[list[JobApplication], int]:
    """查询用户的投递列表。"""
    base_cond = [JobApplication.user_id == user_id, JobApplication.deleted_at == "0"]

    count_stmt = select(JobApplication.id).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    stmt = (
        select(JobApplication)
        .where(*base_cond)
        .order_by(JobApplication.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def list_by_job(db: AsyncSession, job_id: int) -> list[JobApplication]:
    """查询某岗位的所有投递记录。"""
    stmt = (
        select(JobApplication)
        .where(JobApplication.job_id == job_id, JobApplication.deleted_at == "0")
        .order_by(JobApplication.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, application_id: int) -> JobApplication | None:
    """按 ID 查询投递记录。"""
    stmt = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_status(db: AsyncSession, application_id: int, status: str) -> JobApplication | None:
    """更新投递状态。"""
    stmt = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.deleted_at == "0",
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    if app is None:
        return None
    app.status = status
    await db.flush()
    return app


async def list_by_job_paginated(
    db: AsyncSession, job_id: int, page: int = 1, size: int = 20,
) -> tuple[list[tuple], int]:
    """分页查询某岗位的投递记录，JOIN user 获取投递人信息。"""
    from app.models.entities.user import User

    base_cond = [
        JobApplication.job_id == job_id,
        JobApplication.deleted_at == "0",
    ]

    # Count
    count_stmt = select(JobApplication.id).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    # Query with JOIN
    stmt = (
        select(JobApplication, User.username, User.email, User.phone)
        .join(User, JobApplication.user_id == User.id)
        .where(*base_cond)
        .order_by(JobApplication.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [(r[0], r[1], r[2], r[3]) for r in rows], total
