import os

base = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\repositories'
p = os.path.join(base, 'company_repository.py')

with open(p, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace old imports with new ones
old_imports = '''"""企业仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `\\'0\\'/\\'1\\'` 标记，
查询时过滤 `deleted_at == \\'0\\'` 以获得未删除记录。
"""
from typing import List  # 列表类型注解

from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.company import Company  # 企业 ORM'''

new_imports = '''"""企业仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `\\'0\\'/\\'1\\'` 标记，
查询时过滤 `deleted_at == \\'0\\'` 以获得未删除记录。
"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.company import Company
from app.models.entities.job import Job
from app.models.entities.job_application import JobApplication
from app.models.entities.user import User'''

if old_imports in content:
    content = content.replace(old_imports, new_imports)
    print('Imports replaced')
else:
    print('WARNING: old imports not found!')
    # Debug: show first 400 chars
    print(repr(content[:400]))

# Append new functions after search_names
new_funcs = '''

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
        select(JobApplication, Job.title, User.nickname)
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
'''

# Find end of file (after search_names), append new functions after it
marker = "return [row[0] for row in result.fetchall()]"
pos = content.rfind(marker)
if pos == -1:
    print('ERROR: marker not found!')
    exit(1)

# Newline after the marker
end_pos = content.index('\n', pos) + 1
content = content[:end_pos] + new_funcs

with open(p, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! company_repository.py updated successfully.')
print(f'Final file size: {len(content)} bytes')
print(f'count_jobs present: {"count_jobs" in content}')
print(f'recent_applications present: {"recent_applications" in content}')
