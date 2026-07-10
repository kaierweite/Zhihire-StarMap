"""???????????????????"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.parse_task import ParseTask


async def get_by_id(db: AsyncSession, task_id: int) -> ParseTask | None:
    stmt = select(ParseTask).where(ParseTask.id == task_id, ParseTask.deleted_at == '0')
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_file_and_user(db: AsyncSession, file_id: int, user_id: int) -> ParseTask | None:
    stmt = select(ParseTask).where(
        ParseTask.file_id == file_id, ParseTask.user_id == user_id, ParseTask.deleted_at == '0')
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, obj: ParseTask) -> ParseTask:
    db.add(obj)
    await db.flush()
    return obj


async def update(db: AsyncSession, obj: ParseTask) -> ParseTask:
    await db.flush()
    return obj
