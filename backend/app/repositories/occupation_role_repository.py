"""职业角色仓储模块（occupation_role 表）。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.occupation_role import OccupationRole


async def get_by_id(db: AsyncSession, role_id: int) -> OccupationRole | None:
    """按主键查询未删除的职业角色。"""
    stmt = select(OccupationRole).where(
        OccupationRole.id == role_id,
        OccupationRole.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
