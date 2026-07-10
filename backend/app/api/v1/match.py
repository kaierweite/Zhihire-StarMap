"""匹配推荐 API 路由。

端点：
- POST /api/match/trigger - 触发简历匹配分析
- GET /api/match/resume/{resume_id} - 查询简历匹配结果列表
- GET /api/match/resume/{resume_id}/job/{job_id} - 查询单个匹配明细
- GET /api/match/skill-gap/{job_id} - 分析用户与岗位的技能差距
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.matching import MatchRequest
from app.models.schemas.result import PageResult, Result
from app.services import matching_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/match", tags=["匹配推荐"])


@router.post("/trigger", summary="触发匹配分析")
async def trigger_match(
    req: MatchRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """为当前用户的简历执行岗位匹配分析并缓存结果。"""
    try:
        results = await matching_service.match_resume_to_jobs(
            db, current_user.id, req.resume_id, req.job_ids,
        )
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=results, message="匹配分析完成")


@router.get("/resume/{resume_id}", summary="查询匹配结果列表")
async def list_matched_jobs(
    resume_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    min_score: float | None = Query(None, ge=0, le=100),
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """查询某简历的匹配结果列表。"""
    try:
        items, total = await matching_service.get_matched_jobs_for_resume(
            db, current_user.id, resume_id, page, size, min_score,
        )
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


@router.get("/resume/{resume_id}/job/{job_id}", summary="查询匹配明细")
async def get_match_detail(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """查询某简历与某岗位的匹配明细。"""
    try:
        detail = await matching_service.get_single_match_detail(
            db, current_user.id, resume_id, job_id,
        )
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=detail)


@router.get("/skill-gap/{job_id}", summary="技能差距分析")
async def analyze_skill_gap(
    job_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """分析当前用户与某岗位的技能差距。"""
    try:
        analysis = await matching_service.analyze_skill_gap_for_job(db, current_user.id, job_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=analysis)
