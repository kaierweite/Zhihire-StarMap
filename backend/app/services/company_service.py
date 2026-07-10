 """企业业务服务模块。

 编排企业信息查询、编辑、Dashboard 首页统计等业务流程。
 调用公司仓储层进行数据操作。
 """
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.company import Company
from app.models.schemas.company import (
    CompanyDashboardResponse,
    CompanyInfoResponse,
    CompanyUpdateRequest,
    DashboardApplicationItem,
    DashboardJobItem,
    DashboardStats,
)
from app.repositories import company_repository as repo
from app.services.errors import BusinessError


async def get_company_info(db: AsyncSession, user_id: int) -> CompanyInfoResponse:
    """获取当前用户的企业信息。"""
    company = await repo.get_by_user_id(db, user_id)
    if company is None:
        raise BusinessError(404, "企业信息不存在")
    return CompanyInfoResponse.model_validate(company)


async def update_company_info(
    db: AsyncSession, user_id: int, req: CompanyUpdateRequest,
) -> CompanyInfoResponse:
    """更新企业信息，重置审核状态为 PENDING。"""
    company = await repo.get_by_user_id(db, user_id)
    if company is None:
        raise BusinessError(404, "企业信息不存在")

    # 提取非 None 字段进行更新
    values = req.model_dump(exclude_none=True)
    if not values:
        raise BusinessError(400, "没有需要更新的字段")

    updated = await repo.update(db, company.id, **values)
    if updated is None:
        raise BusinessError(500, "更新企业信息失败")
    return CompanyInfoResponse.model_validate(updated)


async def get_dashboard(db: AsyncSession, user_id: int) -> CompanyDashboardResponse:
    """组装企业首页 Dashboard 统计与最近动态。"""
    company = await repo.get_by_user_id(db, user_id)
    if company is None:
        raise BusinessError(404, "企业信息不存在")

    company_id = company.id

    # 并行收集统计数据
    total_jobs = await repo.count_jobs(db, company_id)
    active_jobs = await repo.count_active_jobs(db, company_id)
    total_apps = await repo.count_received_resumes(db, company_id)

    stats = DashboardStats(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_apps,
    )

    # 并行收集最近动态
    jobs = await repo.recent_jobs(db, company_id, limit=5)
    recent_jobs = [DashboardJobItem.model_validate(j) for j in jobs]

    app_rows = await repo.recent_applications(db, company_id, limit=5)
    recent_apps = []
    for row in app_rows:
        app, job_title, username = row
        recent_apps.append(DashboardApplicationItem(
            id=app.id,
            job_id=app.job_id,
            job_title=job_title,
            user_id=app.user_id,
            applicant_name=username,
            status=app.status,
            created_at=app.created_at,
        ))

    return CompanyDashboardResponse(
        stats=stats,
        recent_jobs=recent_jobs,
        recent_applications=recent_apps,
    )
