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




async def list_by_ids(db: AsyncSession, file_ids: list[int]) -> dict[int, str]:
    """Batch query file id -> original name mapping."""
    if not file_ids:
        return {}
    stmt = select(UploadFile).where(UploadFile.id.in_(file_ids), UploadFile.deleted_at == '0')
    result = await db.execute(stmt)
    return {f.id: f.original_name for f in result.scalars().all()}

async def soft_delete(db: AsyncSession, obj: UploadFile) -> None:
    obj.deleted_at = '1'
    await db.flush()
