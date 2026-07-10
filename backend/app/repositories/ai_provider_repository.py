"""AI Provider 仓储模块。"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.ai_provider import AiProvider


async def create(db: AsyncSession, provider: AiProvider) -> AiProvider:
    db.add(provider)
    await db.flush()
    await db.refresh(provider)
    return provider


async def get_by_id(db: AsyncSession, provider_id: int) -> AiProvider | None:
    stmt = select(AiProvider).where(
        AiProvider.id == provider_id,
        AiProvider.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> AiProvider | None:
    stmt = select(AiProvider).where(
        AiProvider.provider_name == name,
        AiProvider.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession) -> list[AiProvider]:
    stmt = (
        select(AiProvider)
        .where(AiProvider.deleted_at == "0")
        .order_by(AiProvider.order_no, AiProvider.id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update(db: AsyncSession, provider: AiProvider, values: dict) -> AiProvider:
    for key, value in values.items():
        if value is not None and hasattr(provider, key):
            setattr(provider, key, value)
    await db.flush()
    return provider


async def delete(db: AsyncSession, provider: AiProvider) -> None:
    provider.deleted_at = "1"
    await db.flush()
