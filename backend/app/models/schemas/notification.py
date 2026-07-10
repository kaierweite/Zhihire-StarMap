"""Notification module Pydantic request/response models."""
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationItem(BaseModel):
    """Single notification record returned by list endpoints."""
    id: int
    user_id: int
    title: str
    content: str | None = None
    type: str = "SYSTEM"
    is_read: bool = False
    created_at: datetime


class NotificationListQuery(BaseModel):
    """Query parameters for paginated notification list."""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class UnreadCountResponse(BaseModel):
    """Unread notification count."""
    count: int = 0
