"""企业 API 路由。

提供当前企业信息查询等端点。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.result import Result
from app.repositories import company_repository
from app.services.errors import BusinessError

router = APIRouter(prefix="/company", tags=["企业"])


@router.get("/me", summary="当前企业信息")
async def get_my_company(
    current_user: User = Depends(require_role(RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取当前登录企业用户的企业信息，包含 company_id。"""
    company = await company_repository.get_by_user_id(db, current_user.id)
    if company is None:
        return Result.error(404, "企业信息不存在")
    return Result.success(data={
        "id": company.id,
        "company_name": company.company_name,
        "industry": company.industry,
        "scale": company.scale,
        "description": company.description,
        "website": company.website,
        "logo_url": company.logo_url,
        "address": company.address,
        "contact_name": company.contact_name,
        "contact_phone": company.contact_phone,
        "contact_email": company.contact_email,
        "audit_status": company.audit_status,
    })
