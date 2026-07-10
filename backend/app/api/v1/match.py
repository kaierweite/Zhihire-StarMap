"""匹配推荐 API 路由（Day06 规范）。

4 个端点：
- GET  /api/match/jobs — 求职者推荐岗位（懒计算 + 缓存）
- GET  /api/match/candidates/{job_id} — 企业端候选人推荐
- POST /api/match/apply — 求职者投递
- POST /api/match/invite — 企业邀请面试
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.result import Result
from app.repositories import company_repository
from app.services import match_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/match", tags=["匹配推荐"])


# ========== 请求模型 ==========

class ApplyRequest(BaseModel):
    job_id: int
    resume_id: int


class InviteRequest(BaseModel):
    resume_id: int
    job_id: int


# ========== 端点 ==========


@router.get("/jobs", summary="求职者推荐岗位")
async def recommend_jobs(
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """求职者查看推荐岗位（懒计算 + 新鲜度缓存）。"""
    try:
        jobs = await match_service.get_job_recommendations(db, current_user.id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data={"jobs": jobs})


@router.get("/candidates/{job_id}", summary="企业候选人推荐")
async def recommend_candidates(
    job_id: int,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业查看某岗位的候选人推荐。"""
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        candidates = await match_service.get_candidate_recommendations(db, company.id, job_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data={"candidates": candidates})


@router.post("/apply", summary="投递岗位")
async def apply_job(
    req: ApplyRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """求职者投递岗位。"""
    try:
        result = await match_service.apply_job(db, current_user.id, req.job_id, req.resume_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="投递成功")


@router.post("/invite", summary="邀请面试")
async def invite_candidate(
    req: InviteRequest,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业邀请候选人面试。"""
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        result = await match_service.invite_candidate(db, company.id, req.job_id, req.resume_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="邀请已发送")
