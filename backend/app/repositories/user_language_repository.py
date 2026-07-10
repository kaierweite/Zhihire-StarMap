"""用户语言能力仓储模块。"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.user_language import UserLanguage


async def list_by_user(db: AsyncSession, user_id: int) -> list[UserLanguage]:
    stmt = select(UserLanguage).where(
        UserLanguage.user_id == user_id,
        UserLanguage.deleted_at == "0",
    ).order_by(UserLanguage.sort_order, UserLanguage.id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, obj: UserLanguage) -> UserLanguage:
    db.add(obj)
    await db.flush()
    return obj


async def soft_delete_all_by_user(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(UserLanguage)
        .where(UserLanguage.user_id == user_id, UserLanguage.deleted_at == "0")
        .values(deleted_at="1")
    )


async def find_active_by_language(
    db: AsyncSession, user_id: int, language: str,
) -> UserLanguage | None:
    """???????????????????"""
    stmt = select(UserLanguage).where(
        UserLanguage.user_id == user_id,
        UserLanguage.language == language,
        UserLanguage.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
