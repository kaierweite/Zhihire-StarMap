"""企业仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.company import Company
from app.models.entities.job import Job
from app.models.entities.job_application import JobApplication
from app.models.entities.user import User


async def create(db: AsyncSession, company: Company) -> Company:
    """新增企业记录并刷新主键。

    Args:
        db: 异步数据库会话。
        company: 待新增的 Company 实例。

    Returns:
        Company: 已写入数据库、含主键的企业实例。
    """
    db.add(company)
    await db.flush()
    return company


async def get_by_user_id(db: AsyncSession, user_id: int) -> Company | None:
    """按关联用户主键查询未删除的企业记录。

    Args:
        db: 异步数据库会话。
        user_id: 关联的用户主键。

    Returns:
        Company | None: 命中返回实例，否则返回 None。
    """
    stmt = select(Company).where(
        Company.user_id == user_id,
        Company.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def search_names(db: AsyncSession, keyword: str, limit: int = 10) -> list[str]:
    """按关键字模糊搜索企业名称，返回去重名称列表。

    Args:
        db: 异步数据库会话。
        keyword: 搜索关键字（区分大小写 ILIKE）。
        limit: 返回条数上限。

    Returns:
        List[str]: 匹配的企业名称列表。
    """
    stmt = select(Company.company_name).where(
        Company.company_name.ilike(f"%{keyword}%"),
        Company.deleted_at == "0",
    ).distinct().limit(limit)
    result = await db.execute(stmt)
    return [row[0] for row in result.fetchall()]


async def get_by_company_id(db: AsyncSession, company_id: int) -> Company | None:
    """按企业主键查询未删除的企业。"""
    stmt = select(Company).where(
        Company.id == company_id,
        Company.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update(db: AsyncSession, company_id: int, **values) -> Company | None:
    """更新企业字段，同时重置 audit_status 为 PENDING 并清空驳回原因。"""
    company = await get_by_company_id(db, company_id)
    if company is None:
        return None
    for key, value in values.items():
        if hasattr(company, key) and value is not None:
            setattr(company, key, value)
    company.audit_status = "PENDING"
    company.audit_reason = None
    company.updated_at = datetime.now()
    await db.flush()
    return company


async def count_jobs(db: AsyncSession, company_id: int) -> int:
    """统计企业岗位总数（含所有状态）。"""
    stmt = select(func.count()).select_from(Job).where(
        Job.company_id == company_id,
        Job.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def count_active_jobs(db: AsyncSession, company_id: int) -> int:
    """统计企业已发布（OPEN）岗位数。"""
    stmt = select(func.count()).select_from(Job).where(
        Job.company_id == company_id,
        Job.status == "OPEN",
        Job.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def count_received_resumes(db: AsyncSession, company_id: int) -> int:
    """统计企业收到的简历投递总数。"""
    stmt = (
        select(func.count())
        .select_from(JobApplication)
        .join(Job, JobApplication.job_id == Job.id)
        .where(
            Job.company_id == company_id,
            Job.deleted_at == "0",
            JobApplication.deleted_at == "0",
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def recent_jobs(db: AsyncSession, company_id: int, limit: int = 5) -> list[Job]:
    """获取企业最近发布的岗位。"""
    stmt = (
        select(Job)
        .where(Job.company_id == company_id, Job.deleted_at == "0")
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def recent_applications(db: AsyncSession, company_id: int, limit: int = 5) -> list:
    """获取企业最近收到的投递，含岗位标题与投递人用户名。"""
    stmt = (
        select(JobApplication, Job.title, User.username)
        .join(Job, JobApplication.job_id == Job.id)
        .join(User, JobApplication.user_id == User.id)
        .where(
            Job.company_id == company_id,
            Job.deleted_at == "0",
            JobApplication.deleted_at == "0",
        )
        .order_by(JobApplication.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [(r[0], r[1], r[2]) for r in rows]
