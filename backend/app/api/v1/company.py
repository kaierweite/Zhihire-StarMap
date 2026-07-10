"""企业 API 路由。

提供当前企业信息查询、编辑、Dashboard 首页统计等端点。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.company import CompanyUpdateRequest
from app.models.schemas.result import Result
from app.services import company_service

router = APIRouter(prefix="/company", tags=["企业"])


@router.get("/me", summary="当前企业信息")
async def get_my_company(
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取当前登录企业用户的企业信息，含 audit_status。"""
    info = await company_service.get_company_info(db, current_user.id)
    return Result.success(data=info.model_dump(mode="json"))


@router.put("/info", summary="编辑企业信息")
async def update_company(
    req: CompanyUpdateRequest,
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """编辑企业基本信息，更新后审核状态自动重置为 PENDING。"""
    info = await company_service.update_company_info(db, current_user.id, req)
    return Result.success(data=info.model_dump(mode="json"), message="企业信息已更新，请等待审核")


@router.get("/dashboard", summary="企业首页统计")
async def get_dashboard(
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取企业首页 Dashboard 统计数字与最近动态。"""
    dashboard = await company_service.get_dashboard(db, current_user.id)
    return Result.success(data=dashboard.model_dump(mode="json"))
