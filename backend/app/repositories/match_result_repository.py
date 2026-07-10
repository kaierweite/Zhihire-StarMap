"""匹配结果仓储模块。

只做原子数据库操作。
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.match_result import MatchResult


async def create(db: AsyncSession, match_result: MatchResult) -> MatchResult:
    """新增匹配结果记录。"""
    db.add(match_result)
    await db.flush()
    await db.refresh(match_result)
    return match_result


async def get_by_resume_and_job(db: AsyncSession, resume_id: int, job_id: int) -> MatchResult | None:
    """按简历和岗位查询匹配结果。"""
    stmt = select(MatchResult).where(
        MatchResult.resume_id == resume_id,
        MatchResult.job_id == job_id,
        MatchResult.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, match_id: int) -> MatchResult | None:
    """按主键查询匹配结果。"""
    stmt = select(MatchResult).where(
        MatchResult.id == match_id,
        MatchResult.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_resume(
    db: AsyncSession, resume_id: int, page: int = 1, size: int = 20,
) -> tuple[list[MatchResult], int]:
    """查询某简历的所有匹配结果。"""
    base_cond = [MatchResult.resume_id == resume_id, MatchResult.deleted_at == "0"]

    count_stmt = select(func.count()).select_from(MatchResult).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    stmt = (
        select(MatchResult)
        .where(*base_cond)
        .order_by(MatchResult.score.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def list_by_job(
    db: AsyncSession, job_id: int, page: int = 1, size: int = 20,
) -> tuple[list[MatchResult], int]:
    """查询某岗位的所有匹配结果。"""
    base_cond = [MatchResult.job_id == job_id, MatchResult.deleted_at == "0"]

    count_stmt = select(func.count()).select_from(MatchResult).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    stmt = (
        select(MatchResult)
        .where(*base_cond)
        .order_by(MatchResult.score.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def upsert(db: AsyncSession, resume_id: int, job_id: int, score: float, match_detail: dict | None = None) -> MatchResult:
    """如果存在则更新，不存在则创建匹配结果。"""
    existing = await get_by_resume_and_job(db, resume_id, job_id)
    if existing:
        existing.score = score
        if match_detail is not None:
            existing.match_detail = match_detail
        await db.flush()
        await db.refresh(existing)
        return existing
    return await create(
        db,
        MatchResult(resume_id=resume_id, job_id=job_id, score=score, match_detail=match_detail),
    )


async def soft_delete(db: AsyncSession, match_result: MatchResult) -> None:
    """软删除匹配结果。"""
    match_result.deleted_at = "1"
    await db.flush()
