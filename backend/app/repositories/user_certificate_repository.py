"""用户证书仓储模块。"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.user_certificate import UserCertificate


async def list_by_user(db: AsyncSession, user_id: int) -> list[UserCertificate]:
    stmt = select(UserCertificate).where(
        UserCertificate.user_id == user_id,
        UserCertificate.deleted_at == "0",
    ).order_by(UserCertificate.sort_order, UserCertificate.id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, obj: UserCertificate) -> UserCertificate:
    db.add(obj)
    await db.flush()
    return obj


async def soft_delete_all_by_user(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(UserCertificate)
        .where(UserCertificate.user_id == user_id, UserCertificate.deleted_at == "0")
        .values(deleted_at="1")
    )


async def find_active_by_name(
    db: AsyncSession, user_id: int, name: str,
) -> UserCertificate | None:
    """???????????????????"""
    stmt = select(UserCertificate).where(
        UserCertificate.user_id == user_id,
        UserCertificate.name == name,
        UserCertificate.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
