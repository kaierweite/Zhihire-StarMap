"""Notification API routes (Day09)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.enums.role import RoleEnum
from app.models.schemas.notification import NotificationItem, UnreadCountResponse
from app.models.schemas.result import PageResult, Result
from app.services import notification_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/notification", tags=["通知"])


@router.get("/list", summary="分页查询用户通知")
async def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(RoleEnum.USER, RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
):
    try:
        items, total = await notification_service.get_list(
            db, current_user.id, page=page, size=size
        )
    except BusinessError as e:
        return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(
        data=PageResult(
            records=[i.model_dump() for i in items],
            total=total,
            page=page,
            size=size,
        )
    )


@router.put("/{notification_id}/read", summary="标记单条已读")
async def mark_read(
    notification_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER, RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
):
    try:
        await notification_service.mark_read(db, current_user.id, notification_id)
    except BusinessError as e:
        return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(message="已标记已读")


@router.put("/read-all", summary="全部已读")
async def mark_all_read(
    current_user: User = Depends(require_role(RoleEnum.USER, RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
):
    try:
        await notification_service.mark_all_read(db, current_user.id)
    except BusinessError as e:
        return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(message="已全部标记已读")


@router.get("/unread-count", summary="未读通知数")
async def unread_count(
    current_user: User = Depends(require_role(RoleEnum.USER, RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
):
    try:
        r = await notification_service.get_unread_count(db, current_user.id)
    except BusinessError as e:
        return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(data=r.model_dump())
