"""用户档案路由模块。

提供求职者个人档案的读取与更新两个端点：
- GET /api/user/profile
- PUT /api/user/profile

路由层只做参数校验、依赖注入与响应封装，业务逻辑下沉到 service 层。
仅 USER 角色可访问。
"""
from fastapi import APIRouter, Depends  # 路由分组与依赖
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.api.deps import get_current_user, require_role  # 鉴权依赖
from app.db.session import get_db  # 数据库会话依赖
from app.models.entities.user import User  # 用户 ORM（类型注解）
from app.models.enums.role import RoleEnum  # 角色枚举
from app.models.schemas.result import Result  # 统一响应模型
from app.models.schemas.user import (  # 请求/响应模型
    UserProfileDTO,
    UserProfileUpdateForm,
)
from app.services import user_service  # 用户档案业务服务
from app.services.errors import BusinessError  # 业务异常


# 路由实例，统一 tags 为「用户档案」
router = APIRouter(prefix="/user", tags=["用户档案"])


@router.get("/profile", summary="获取个人档案")
async def get_profile(
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[UserProfileDTO]:
    """读取当前用户的完整档案。

    Args:
        current_user: 当前用户实例，由 require_role 注入。
        db: 异步数据库会话。

    Returns:
        Result[UserProfileDTO]: 完整档案信息。
    """
    try:
        # 委托业务层组装档案 DTO
        dto = await user_service.get_profile(db, current_user)
    except BusinessError as exc:
        # 业务可预期异常封装为统一错误响应
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=dto)


@router.put("/profile", summary="更新个人档案")
async def update_profile(
    form: UserProfileUpdateForm,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[UserProfileDTO]:
    """更新当前用户的档案信息（逐 section）。

    Args:
        form: 档案更新表单。
        current_user: 当前用户实例，由 require_role 注入。
        db: 异步数据库会话。

    Returns:
        Result[UserProfileDTO]: 更新后的完整档案信息。
    """
    try:
        # 委托业务层完成更新并返回最新档案
        dto = await user_service.update_profile(db, current_user, form)
    except BusinessError as exc:
        # 业务异常（如薪资区间非法）封装为统一错误响应
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=dto, message="更新成功")
