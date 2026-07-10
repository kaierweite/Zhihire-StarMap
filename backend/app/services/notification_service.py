"""Notification service — business logic."""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.notification import Notification
from app.models.schemas.notification import NotificationItem, UnreadCountResponse
from app.repositories import notification_repository
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)


async def get_list(
    db: AsyncSession, user_id: int, page: int = 1, size: int = 20
) -> tuple[list[NotificationItem], int]:
    """Get paginated notification list for a user."""
    records, total = await notification_repository.list_by_user(
        db, user_id, page=page, size=size
    )
    items = [
        NotificationItem(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            content=n.content,
            type=n.type,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in records
    ]
    return items, total


async def mark_read(db: AsyncSession, user_id: int, notification_id: int) -> None:
    """Mark one notification as read."""
    n = await notification_repository.get_by_id(db, notification_id)
    if n is None or n.user_id != user_id:
        raise BusinessError(404, "通知不存在")
    await notification_repository.mark_read(db, notification_id, user_id)
    await db.commit()


async def mark_all_read(db: AsyncSession, user_id: int) -> None:
    """Mark all user notifications as read."""
    await notification_repository.mark_all_read(db, user_id)
    await db.commit()


async def get_unread_count(
    db: AsyncSession, user_id: int
) -> UnreadCountResponse:
    """Get unread notification count."""
    count = await notification_repository.count_unread(db, user_id)
    return UnreadCountResponse(count=count)


async def send_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    type_: str = "SYSTEM",
    content: str | None = None,
) -> Notification:
    """Send a notification to a user (internal helper)."""
    n = await notification_repository.create(
        db, user_id=user_id, title=title, type_=type_, content=content
    )
    await db.commit()
    logger.info("Notification sent: user=%d type=%s title=%s", user_id, type_, title)
    return n
