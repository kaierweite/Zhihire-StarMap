"""能力图谱缓存仓储模块。
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.ability_graph import AbilityGraph


async def get_by_owner(db: AsyncSession, owner_type: str, owner_id: int) -> AbilityGraph | None:
    stmt = select(AbilityGraph).where(
        AbilityGraph.owner_type == owner_type,
        AbilityGraph.owner_id == owner_id,
        AbilityGraph.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def upsert(db: AsyncSession, owner_type: str, owner_id: int, graph_json: str) -> AbilityGraph:
    existing = await get_by_owner(db, owner_type, owner_id)
    if existing:
        existing.graph_json = graph_json
        await db.flush()
        return existing
    record = AbilityGraph(owner_type=owner_type, owner_id=owner_id, graph_json=graph_json)
    db.add(record)
    await db.flush()
    return record
