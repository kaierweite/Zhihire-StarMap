"""岗位 API 路由。

8 个端点：
- POST /api/job - 创建岗位（企业）
- GET /api/job - 分页搜索岗位
- GET /api/job/{job_id} - 岗位详情
- PUT /api/job/{job_id} - 更新岗位（企业）
- DELETE /api/job/{job_id} - 删除岗位（企业）
- POST /api/job/{job_id}/skills - 添加技能要求（企业）
- GET /api/job/{job_id}/skills - 查询技能要求
- DELETE /api/job/{job_id}/skills/{skill_id} - 移除技能要求（企业）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.job import (
    AddJobSkillRequest,
    CreateJobRequest,
    JobDetail,
    JobItem,
    JobSkillItem,
    UpdateJobRequest,
)
from app.models.schemas.result import PageResult, Result
from app.repositories import company_repository
from app.services import job_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/job", tags=["岗位"])


@router.post("", summary="创建岗位")
async def create_job(
    req: CreateJobRequest,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业创建岗位。"""
    try:
        result = await job_service.create_job(db, current_user.id, req)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="岗位创建成功")


@router.get("", summary="搜索岗位")
async def search_jobs(
    keyword: str | None = Query(None, max_length=200),
    city: str | None = Query(None, max_length=100),
    education_requirement: str | None = Query(None, max_length=50),
    experience_min: int | None = Query(None, ge=0),
    salary_min: float | None = Query(None),
    salary_max: float | None = Query(None),
    job_type: str | None = Query(None, max_length=20),
    company_id: int | None = Query(None),
    status: str | None = Query(None, max_length=20),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """分页搜索岗位。"""
    try:
        items, total = await job_service.search_jobs(
            db,
            keyword=keyword,
            city=city,
            education_requirement=education_requirement,
            experience_min=experience_min,
            salary_min=salary_min,
            salary_max=salary_max,
            job_type=job_type,
            company_id=company_id,
            status=status,
            page=page,
            size=size,
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


@router.get("/{job_id}", summary="岗位详情")
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取岗位详情（无需登录），自动增加浏览次数。"""
    try:
        detail = await job_service.get_job_detail(db, job_id, increment_view=True)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=detail)


@router.put("/{job_id}", summary="更新岗位")
async def update_job(
    job_id: int,
    req: UpdateJobRequest,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业更新岗位。"""
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        detail = await job_service.update_job(db, company.id, job_id, req)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=detail, message="岗位更新成功")


@router.delete("/{job_id}", summary="删除岗位")
async def delete_job(
    job_id: int,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业删除岗位（软删除）。"""
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        await job_service.delete_job(db, company.id, job_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(message="岗位已删除")


@router.post("/{job_id}/skills", summary="添加技能要求")
async def add_job_skill(
    job_id: int,
    req: AddJobSkillRequest,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业为岗位添加技能要求。"""
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        result = await job_service.add_job_skill(db, company.id, job_id, req)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="技能要求已添加")


@router.get("/{job_id}/skills", summary="查询技能要求")
async def list_job_skills(
    job_id: int,
    db: AsyncSession = Depends(get_db),
) -> Result:
    """查询岗位的技能要求列表。"""
    try:
        items = await job_service.list_job_skills(db, job_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=[i.model_dump() for i in items])


@router.delete("/{job_id}/skills/{skill_id}", summary="移除技能要求")
async def remove_job_skill(
    job_id: int,
    skill_id: int,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """企业移除岗位的技能要求。"""
    try:
        company = await company_repository.get_by_user_id(db, current_user.id)
        if company is None:
            return Result.error(403, "企业不存在")
        await job_service.remove_job_skill(db, company.id, job_id, skill_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(message="技能要求已移除")
