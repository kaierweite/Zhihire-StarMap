"""\u80fd\u529b\u56fe\u8c31\u8def\u7531\u6a21\u5757\u3002
GET /api/graph/user - \u7528\u6237\u4e2a\u4eba\u80fd\u529b\u56fe\u8c31
GET /api/graph/job/{job_id} - \u5c97\u4f4d\u80fd\u529b\u8c31\u56fe
POST /api/graph/reload - \u7ba1\u7406\u5458\u91cd\u5efa\u56fe\u8c31
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.graph import GraphResult, UserGraphResult
from app.models.schemas.result import Result
from app.services.graph_service import analyze_gap_with_role, get_job_graph, get_user_graph, reload_graph_endpoint
from app.services.errors import BusinessError

router = APIRouter(prefix="/graph", tags=["\u80fd\u529b\u56fe\u8c31"])


@router.get("/user", summary="\u7528\u6237\u4e2a\u4eba\u80fd\u529b\u56fe\u8c31")
async def read_user_graph(
    role_id: int | None = Query(None, description="\u76ee\u6807\u89d2\u8272ID\uff0c\u7528\u4e8e\u8ba1\u7b97\u7f3a\u53e3\u6280\u80fd"),
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[UserGraphResult]:
    try:
        result = await get_user_graph(db, current_user.id)
        if role_id is not None:
            gaps = await analyze_gap_with_role(db, current_user.id, role_id)
            result.gap_skills = gaps
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="\u83b7\u53d6\u7528\u6237\u56fe\u8c31\u6210\u529f")


@router.get("/job/{job_id}", summary="\u5c97\u4f4d\u80fd\u529b\u8c31\u56fe")
async def read_job_graph(
    job_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[GraphResult]:
    try:
        result = await get_job_graph(db, job_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="\u83b7\u53d6\u5c97\u4f4d\u56fe\u8c31\u6210\u529f")


@router.post("/reload", summary="\u624b\u52a8\u91cd\u5efa\u56fe\u8c31")
async def reload_graph(
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result[None]:
    try:
        await reload_graph_endpoint(db)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(message="\u56fe\u8c31\u91cd\u5efa\u6210\u529f")
