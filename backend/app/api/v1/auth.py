"""认证路由模块。

提供注册、登录、获取当前用户信息三个端点：
- POST /api/auth/register
- POST /api/auth/login
- GET  /api/auth/me

路由层只做参数校验、依赖注入与响应封装，业务逻辑下沉到 service 层。
"""
from fastapi import APIRouter, Depends, status  # 路由分组与依赖
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.api.deps import get_current_user  # 当前用户依赖
from app.db.session import get_db  # 数据库会话依赖
from app.models.entities.user import User  # 用户 ORM（类型注解）
from app.models.schemas.auth import (  # 请求/响应模型
    LoginForm,
    LoginResult,
    RegisterForm,
    UserInfo,
)
from app.models.schemas.result import Result  # 统一响应模型
from app.services import auth_service  # 认证业务服务
from app.services.errors import BusinessError  # 业务异常


# 路由实例，统一 tags 为「认证」
router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", summary="用户注册")
async def register(form: RegisterForm, db: AsyncSession = Depends(get_db)) -> Result[None]:
    """注册求职者或企业用户。

    Args:
        form: 注册表单。
        db: 异步数据库会话。

    Returns:
        Result[None]: 成功返回 code=200，data 为 null。
    """
    try:
        # 委托业务层完成注册
        await auth_service.register(db, form)
    except BusinessError as exc:
        # 业务可预期异常：按携带的状态码封装
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    # 成功返回空数据
    return Result.success(data=None, message="注册成功")


@router.post("/login", summary="用户登录")
async def login(form: LoginForm, db: AsyncSession = Depends(get_db)) -> Result[LoginResult]:
    """用户登录并签发 JWT。

    Args:
        form: 登录表单。
        db: 异步数据库会话。

    Returns:
        Result[LoginResult]: 成功返回登录结果（token/role/username）。
    """
    try:
        # 委托业务层完成登录
        result = await auth_service.login(db, form)
    except BusinessError as exc:
        # 业务异常封装为统一错误响应
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    # 成功返回登录结果
    return Result.success(data=result, message="登录成功")


@router.get("/me", summary="获取当前用户信息")
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Result[UserInfo]:
    """根据 JWT 获取当前用户完整信息。

    Args:
        current_user: 当前用户实例，由 get_current_user 注入。
        db: 异步数据库会话。

    Returns:
        Result[UserInfo]: 当前用户完整信息。
    """
    try:
        # 按当前用户主键加载完整信息
        info = await auth_service.me(db, current_user.id)
    except BusinessError as exc:
        # 用户已被删除等异常
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    # 成功返回用户信息
    return Result.success(data=info, message="success")
