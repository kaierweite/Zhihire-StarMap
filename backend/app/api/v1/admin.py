# -*- coding: utf-8 -*-
"""管理员 API 路由。

提供后台管理相关端点，统一使用 require_role(RoleEnum.ADMIN) 守卫。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.admin import (
    AuditRequest,
    JobStatusRequest,
    SkillAuditRequest,
    UserStatusRequest,
    AiProviderCreateRequest,
    AiProviderUpdateRequest
)
from app.models.schemas.result import Result
from app.services import admin_service
from app.repositories import operation_log_repository

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.get("/stat", summary="后台首页实时聚合统计")
async def get_admin_stat(
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取后台首页的实时聚合统计数据。"""
    stat = await admin_service.get_stat(db)
    return Result.success(data=stat.model_dump(mode="json"))


@router.get("/user", summary="用户管理分页列表")
async def list_users(
    keyword: str | None = Query(None, max_length=100, description="搜索关键词"),
    role: str | None = Query(None, description="按角色筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取用户管理分页列表，支持关键词搜索和角色筛选。"""
    result = await admin_service.list_users(db, keyword, role, page, size)
    return Result.success(data=result.model_dump(mode="json"))


@router.put("/user/{user_id}/status", summary="封禁/解封用户")
async def update_user_status(
    user_id: int,
    req: UserStatusRequest,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """封禁或解封指定用户。"""
    user_item = await admin_service.set_user_status(db, user_id, req.status)
    # 记录操作日志
    action_label = "封禁用户" if req.status == "BANNED" else "解封用户"
    await operation_log_repository.create_log(
        db,
        user_id=current_user.id,
        module="用户管理",
        action=action_label,
        detail={"target_user_id": user_id, "target_username": user_item.username},
        ip=current_user.avatar_url,  # placeholder, real IP from request if needed
    )
    return Result.success(
        data=user_item.model_dump(mode="json"),
        message=f"用户已{'封禁' if req.status == 'BANNED' else '解封'}",
    )


@router.get("/company/audit", summary="待审核企业列表")
async def list_company_audit(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取待审核企业列表。"""
    result = await admin_service.list_companies_pending(db, page, size)
    return Result.success(data=result.model_dump(mode="json"))


@router.put("/company/{company_id}/audit", summary="审核企业（通过/驳回）")
async def audit_company(
    company_id: int,
    req: AuditRequest,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """审核企业注册申请，通过或驳回。"""
    company_item = await admin_service.audit_company(db, company_id, req.action, req.reason)
    action_label = "审核通过" if req.action == "pass" else "审核驳回"
    await operation_log_repository.create_log(
        db,
        user_id=current_user.id,
        module="企业审核",
        action=f"{action_label}企业",
        detail={"company_id": company_id, "company_name": company_item.company_name, "reason": req.reason},
    )
    return Result.success(
        data=company_item.model_dump(mode="json"),
        message=f"企业{action_label}",
    )


@router.get("/log", summary="操作日志分页列表")
async def list_logs(
    log_type: str | None = Query(None, description="日志类型"),
    keyword: str | None = Query(None, max_length=100, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取操作日志分页列表。"""
    result = await admin_service.list_operation_logs(db, log_type, keyword, page, size)
    return Result.success(data=result.model_dump(mode="json"))


@router.put("/job/{job_id}/status", summary="强制下架/恢复岗位")
async def update_job_status(
    job_id: int,
    req: JobStatusRequest,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """强制下架违规岗位或恢复岗位。"""
    job_item = await admin_service.set_job_status(db, job_id, req.status)
    action_label = "强制下架" if req.status == "CLOSED" else "恢复上架"
    await operation_log_repository.create_log(
        db,
        user_id=current_user.id,
        module="岗位管理",
        action=f"{action_label}岗位",
        detail={"job_id": job_id, "job_title": job_item.title},
    )
    return Result.success(
        data=job_item.model_dump(mode="json"),
        message=f"岗位已{action_label}",
    )


@router.get("/skill/audit", summary="待审核技能列表")
async def list_skill_audit(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取待审核候选技能列表。"""
    result = await admin_service.list_skill_audit(db, page, size)
    return Result.success(data=result.model_dump(mode="json"))


@router.put("/skill/{skill_id}/audit", summary="审核技能（通过/驳回/合并）")
async def audit_skill(
    skill_id: int,
    req: SkillAuditRequest,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """审核候选技能：通过（可选合并到目标技能）或驳回（软删除）。"""
    skill_item = await admin_service.audit_skill(db, skill_id, req.action, req.target_id)
    action_label = "审核通过" if req.action == "approve" else "审核驳回"
    await operation_log_repository.create_log(
        db,
        user_id=current_user.id,
        module="字典审核",
        action=f"{action_label}技能",
        detail={"skill_id": skill_id, "skill_name": skill_item.name, "target_id": req.target_id},
    )
    return Result.success(
        data=skill_item.model_dump(mode="json"),
        message=f"技能{action_label}",
    )




@router.get("/ai-config", summary="Get all AI providers")
async def list_ai_providers(
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    providers = await admin_service.list_ai_providers(db)
    return Result.success(data=[p.model_dump(mode="json") for p in providers])


@router.post("/ai-config", summary="Create AI provider")
async def create_ai_provider(
    req: AiProviderCreateRequest,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    provider = await admin_service.create_ai_provider(db, req)
    return Result.success(data=provider.model_dump(mode="json"), message="Created")


@router.put("/ai-config/{provider_id}", summary="Update AI provider")
async def update_ai_provider(
    provider_id: int,
    req: AiProviderUpdateRequest,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    provider = await admin_service.update_ai_provider(db, provider_id, req)
    return Result.success(data=provider.model_dump(mode="json"), message="Updated")


@router.post("/ai-config/{provider_id}/test", summary="Test AI provider")
async def test_ai_provider(
    provider_id: int,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    result = await admin_service.test_ai_connection(db, provider_id)
    return Result.success(data=result.model_dump(mode="json"))


@router.delete("/ai-config/{provider_id}", summary="Delete AI provider")
async def delete_ai_provider(
    provider_id: int,
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    await admin_service.delete_ai_provider(db, provider_id)
    return Result.success(message="Deleted")