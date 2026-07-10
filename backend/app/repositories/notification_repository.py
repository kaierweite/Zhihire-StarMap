"""Notification repository — atomic DB operations."""
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.notification import Notification


async def list_by_user(
    db: AsyncSession, user_id: int, page: int = 1, size: int = 20
) -> tuple[list[Notification], int]:
    """Paginated query of user notifications, newest first."""
    cond = [
        Notification.user_id == user_id,
        Notification.deleted_at == "0",
    ]
    total = (
        await db.execute(
            select(func.count()).select_from(Notification).where(*cond)
        )
    ).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(
        select(Notification)
        .where(*cond)
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    return list(result.scalars().all()), total


async def get_by_id(db: AsyncSession, nid: int) -> Notification | None:
    """Get a single notification by ID."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == nid, Notification.deleted_at == "0"
        )
    )
    return result.scalar_one_or_none()


async def mark_read(db: AsyncSession, nid: int, user_id: int) -> None:
    """Mark a single notification as read (owner guard)."""
    await db.execute(
        update(Notification)
        .where(
            Notification.id == nid,
            Notification.user_id == user_id,
            Notification.deleted_at == "0",
        )
        .values(is_read=True)
    )
    await db.flush()


async def mark_all_read(db: AsyncSession, user_id: int) -> None:
    """Mark all unread notifications as read for a user."""
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.deleted_at == "0",
        )
        .values(is_read=True)
    )
    await db.flush()


async def count_unread(db: AsyncSession, user_id: int) -> int:
    """Count unread notifications for a user."""
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.deleted_at == "0",
        )
    )
    return result.scalar() or 0


async def create(
    db: AsyncSession, user_id: int, title: str, type_: str = "SYSTEM", content: str | None = None
) -> Notification:
    """Create a notification."""
    n = Notification(
        user_id=user_id, title=title, type=type_, content=content
    )
    db.add(n)
    await db.flush()
    return n
