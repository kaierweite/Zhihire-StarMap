"""?????????

???????????
- GET /api/parse/task/{task_id} ? ??????
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities.user import User
from app.models.schemas.resume import TaskStatus
from app.models.schemas.result import Result
from app.services import resume_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/parse", tags=["????"])


@router.get("/task/{task_id}", summary="????????")
async def get_task_status(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Result[TaskStatus]:
    """????????????

    ????????? 2 ?????? SUCCESS ? FAILED?
    """
    try:
        status = await resume_service.get_task_status(db, task_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=status)
