"""操作日志仓储模块。

只做原子数据库操作。
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.operation_log import OperationLog


async def create(db: AsyncSession, log: OperationLog) -> OperationLog:
    """新增操作日志记录并刷新主键。"""
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def list_logs(
    db: AsyncSession,
    log_type: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[OperationLog], int]:
    """分页查询操作日志。

    Args:
        db: 异步数据库会话。
        log_type: 日志类型筛选（如 operation / login）。
        keyword: 搜索关键词（匹配 module / action）。
        page: 页码，从 1 开始。
        size: 每页条数。

    Returns:
        tuple[list[OperationLog], int]: 日志列表与总条数。
    """
    base_cond = [OperationLog.deleted_at == "0"]

    if keyword:
        keyword_filter = (
            OperationLog.module.ilike(f"%{keyword}%")
            | OperationLog.action.ilike(f"%{keyword}%")
        )
        base_cond.append(keyword_filter)

    count_stmt = select(func.count()).select_from(OperationLog).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    query_stmt = (
        select(OperationLog)
        .where(*base_cond)
        .order_by(OperationLog.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query_stmt)
    records = list(result.scalars().all())

    return records, total


async def create_log(
    db: AsyncSession,
    user_id: int,
    module: str,
    action: str,
    detail: dict[str, Any] | None = None,
    ip: str | None = None,
) -> OperationLog:
    """便捷方法：创建操作日志记录。"""
    log = OperationLog(
        user_id=user_id,
        module=module,
        action=action,
        detail=detail,
        ip=ip,
    )
    return await create(db, log)
