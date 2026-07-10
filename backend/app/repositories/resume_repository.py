"""?????????????????"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.resume import Resume


async def get_by_id(db: AsyncSession, resume_id: int) -> Resume | None:
    stmt = select(Resume).where(Resume.id == resume_id, Resume.deleted_at == '0')
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_user_and_id(db: AsyncSession, resume_id: int, user_id: int) -> Resume | None:
    stmt = select(Resume).where(
        Resume.id == resume_id, Resume.user_id == user_id, Resume.deleted_at == '0')
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_user(db: AsyncSession, user_id: int, page: int = 1, size: int = 20) -> tuple[list[Resume], int]:
    base = select(Resume).where(Resume.user_id == user_id, Resume.deleted_at == '0')
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    offset = (page - 1) * size
    stmt = base.order_by(Resume.created_at.desc()).offset(offset).limit(size)
    result = await db.execute(stmt)
    rows = list(result.scalars().all())
    return rows, total


async def create(db: AsyncSession, obj: Resume) -> Resume:
    db.add(obj)
    await db.flush()
    return obj


async def update(db: AsyncSession, obj: Resume) -> Resume:
    await db.flush()
    return obj


async def soft_delete(db: AsyncSession, obj: Resume) -> None:
    obj.deleted_at = '1'
    await db.flush()
