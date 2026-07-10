"""推荐 API 路由。

端点：
- POST /api/recommend/trigger - 触发岗位推荐（基于当前用户技能）
- GET /api/recommend/list - 查询推荐记录列表
- POST /api/recommend/{record_id}/action - 标记推荐操作（点击/投递）
- GET /api/recommend/career-paths - 职业路径推荐
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.matching import RecommendClickRequest, RecommendRequest
from app.models.schemas.result import PageResult, Result
from app.services import recommend_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/recommend", tags=["岗位推荐"])


@router.post("/trigger", summary="触发岗位推荐")
async def trigger_recommend(
    req: RecommendRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """基于当前用户技能触发岗位推荐。"""
    try:
        results = await recommend_service.recommend_jobs_for_user(db, current_user.id, req.count)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=results, message="推荐完成")


@router.get("/list", summary="推荐记录列表")
async def list_recommendations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """查询当前用户的推荐记录列表。"""
    try:
        items, total = await recommend_service.get_recommendations(db, current_user.id, page, size)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(
        data=PageResult(
            records=[i.model_dump() for i in items],
            total=total,
            page=page,
            size=size,
        ),
    )


@router.post("/{record_id}/action", summary="标记推荐操作")
async def mark_action(
    record_id: int,
    req: RecommendClickRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """标记推荐记录为已点击或已投递。"""
    try:
        success = await recommend_service.mark_recommendation_action(
            db, current_user.id, record_id, req.action,
        )
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data={"success": success}, message="操作成功")


@router.get("/career-paths", summary="职业路径推荐")
async def recommend_career_paths(
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """基于用户技能推荐职业发展路径。"""
    try:
        paths = await recommend_service.recommend_career_paths(db, current_user.id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=[p.model_dump() for p in paths])
