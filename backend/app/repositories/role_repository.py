"""职业角色仓储模块。
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.role import Role


async def get_by_id(db: AsyncSession, role_id: int) -> Role | None:
    stmt = select(Role).where(Role.id == role_id, Role.deleted_at == "0")
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Role | None:
    stmt = select(Role).where(Role.name == name, Role.deleted_at == "0")
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_active(db: AsyncSession) -> list[Role]:
    stmt = select(Role).where(Role.deleted_at == "0")
    result = await db.execute(stmt)
    return list(result.scalars().all())
