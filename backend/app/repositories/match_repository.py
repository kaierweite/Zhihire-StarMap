"""匹配结果仓储模块（遵循 Day06 开发规范命名）。

只做原子数据库操作。
"""
from sqlalchemy import select, func, update
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
    db: AsyncSession, resume_id: int,
) -> list[MatchResult]:
    """查询某简历的所有匹配结果（不分页）。"""
    stmt = (
        select(MatchResult)
        .where(MatchResult.resume_id == resume_id, MatchResult.deleted_at == "0")
        .order_by(MatchResult.score.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_by_job(
    db: AsyncSession, job_id: int,
) -> list[MatchResult]:
    """查询某岗位的所有匹配结果（不分页）。"""
    stmt = (
        select(MatchResult)
        .where(MatchResult.job_id == job_id, MatchResult.deleted_at == "0")
        .order_by(MatchResult.score.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def upsert(db: AsyncSession, resume_id: int, job_id: int, score: float,
                 match_detail: dict | None = None) -> MatchResult:
    """如果存在则更新，不存在则创建匹配结果。"""
    existing = await get_by_resume_and_job(db, resume_id, job_id)
    if existing:
        existing.score = score
        if match_detail is not None:
            existing.match_detail = match_detail
        existing.is_stale = False
        await db.flush()
        await db.refresh(existing)
        return existing
    return await create(
        db,
        MatchResult(
            resume_id=resume_id,
            job_id=job_id,
            score=score,
            match_detail=match_detail,
            is_stale=False,
        ),
    )


async def mark_stale(db: AsyncSession, resume_id: int | None = None, job_id: int | None = None) -> int:
    """标记匹配结果为过期（简历/岗位技能变更时触发）。

    Args:
        db: 数据库会话。
        resume_id: 指定简历 ID，标记所有包含该简历的匹配。
        job_id: 指定岗位 ID，标记所有包含该岗位的匹配。

    Returns:
        int: 受影响行数。
    """
    conditions = [MatchResult.deleted_at == "0"]
    if resume_id is not None:
        conditions.append(MatchResult.resume_id == resume_id)
    if job_id is not None:
        conditions.append(MatchResult.job_id == job_id)

    stmt = (
        update(MatchResult)
        .where(*conditions)
        .values(is_stale=True)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount or 0


async def soft_delete(db: AsyncSession, match_result: MatchResult) -> None:
    """软删除匹配结果。"""
    match_result.deleted_at = "1"
    await db.flush()
