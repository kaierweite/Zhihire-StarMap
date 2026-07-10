"""???????????????????"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.upload_file import UploadFile


async def get_by_id(db: AsyncSession, file_id: int) -> UploadFile | None:
    stmt = select(UploadFile).where(UploadFile.id == file_id, UploadFile.deleted_at == '0')
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, obj: UploadFile) -> UploadFile:
    db.add(obj)
    await db.flush()
    return obj


async def soft_delete(db: AsyncSession, obj: UploadFile) -> None:
    obj.deleted_at = '1'
    await db.flush()
