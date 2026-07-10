"""推荐记录仓储模块。

只做原子数据库操作。
"""
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.recommend_record import RecommendRecord


async def create(db: AsyncSession, record: RecommendRecord) -> RecommendRecord:
    """新增推荐记录。"""
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_by_id(db: AsyncSession, record_id: int) -> RecommendRecord | None:
    """按主键查询推荐记录。"""
    stmt = select(RecommendRecord).where(
        RecommendRecord.id == record_id,
        RecommendRecord.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_user_and_job(db: AsyncSession, user_id: int, job_id: int) -> RecommendRecord | None:
    """按用户和岗位查询推荐记录。"""
    stmt = select(RecommendRecord).where(
        RecommendRecord.user_id == user_id,
        RecommendRecord.job_id == job_id,
        RecommendRecord.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_user(
    db: AsyncSession, user_id: int, page: int = 1, size: int = 20,
) -> tuple[list[RecommendRecord], int]:
    """查询某用户的推荐列表。"""
    base_cond = [RecommendRecord.user_id == user_id, RecommendRecord.deleted_at == "0"]

    count_stmt = select(func.count()).select_from(RecommendRecord).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    stmt = (
        select(RecommendRecord)
        .where(*base_cond)
        .order_by(RecommendRecord.score.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def mark_clicked(db: AsyncSession, record_id: int) -> bool:
    """标记推荐记录为已点击。"""
    stmt = (
        update(RecommendRecord)
        .where(RecommendRecord.id == record_id, RecommendRecord.deleted_at == "0")
        .values(is_clicked=True)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


async def mark_applied(db: AsyncSession, record_id: int) -> bool:
    """标记推荐记录为已投递。"""
    stmt = (
        update(RecommendRecord)
        .where(RecommendRecord.id == record_id, RecommendRecord.deleted_at == "0")
        .values(is_applied=True)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0


async def soft_delete(db: AsyncSession, record: RecommendRecord) -> None:
    """软删除推荐记录。"""
    record.deleted_at = "1"
    await db.flush()


async def batch_create(db: AsyncSession, records: list[RecommendRecord]) -> list[RecommendRecord]:
    """批量创建推荐记录。"""
    for record in records:
        db.add(record)
    await db.flush()
    for record in records:
        await db.refresh(record)
    return records
