"""鉴权依赖模块。

提供 FastAPI 通用依赖：
- `oauth2_scheme`：从 Authorization 头解析 Bearer 令牌
- `get_current_user`：解析 JWT 并从数据库加载真实用户，校验账号状态
- `require_role`：按角色进行访问控制

day01 接入用户表后，`get_current_user` 返回真实 ORM User 实例，
并校验账号状态（封禁/停用拒绝访问）。
"""
from typing import Any  # 任意类型

from fastapi import Depends, HTTPException, status  # FastAPI 依赖与异常
from fastapi.security import OAuth2PasswordBearer  # Bearer 令牌解析
from jose import JWTError, jwt  # JWT 解码与异常
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.config.settings import settings  # 全局配置（JWT 密钥与算法）
from app.db.session import get_db  # 数据库会话依赖
from app.models.entities.user import User  # 用户 ORM
from app.models.enums.role import RoleEnum, VALID_ROLES  # 角色枚举与合法集合
from app.models.enums.status import UserStatusEnum  # 用户状态枚举
from app.repositories import user_repository  # 用户仓储


# OAuth2 Bearer 方案：tokenUrl 指向登录端点，仅用于 OpenAPI 文档展示
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT 解析凭证并从数据库加载真实用户。

    Args:
        token: 请求头中的 Bearer 令牌，由 oauth2_scheme 提取。
        db: 异步数据库会话，由 get_db 注入。

    Returns:
        User: 当前用户的 ORM 实例。

    Raises:
        HTTPException: token 无效/过期/claim 缺失(401)、用户不存在(401)、账号封禁/停用(403)。
    """
    # 准备鉴权失败的统一异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT，验证签名与过期时间
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret,  # 签名密钥
            algorithms=[settings.jwt_algorithm],  # 允许的算法
        )
        # 取出用户主键
        user_id = payload.get("sub")
        # 取出角色（统一大写），仅用于前置校验
        role = payload.get("role")
        # 任一关键 claim 缺失即视作无效 token
        if user_id is None or role is None:
            raise credentials_exception
        # 角色必须属于合法枚举集合
        if role not in VALID_ROLES:
            raise credentials_exception
    except JWTError:
        # 解码或签名校验失败
        raise credentials_exception

    # 从数据库加载真实用户
    user = await user_repository.get_by_id(db, int(user_id))
    # token 有效但用户不存在（已删除）
    if user is None:
        raise credentials_exception

    # 账号状态校验：封禁
    if user.status == UserStatusEnum.BANNED.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被封禁")
    # 账号状态校验：停用
    if user.status == UserStatusEnum.DISABLED.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被停用")

    # 返回真实用户实例
    return user


def require_role(*roles: RoleEnum):
    """生成角色守卫依赖。

    用法：`Depends(require_role(RoleEnum.ADMIN, RoleEnum.COMPANY))`，
    仅允许指定角色访问。

    Args:
        *roles: 允许通过的角色枚举。

    Returns:
        Callable: FastAPI 依赖函数，校验通过返回当前用户，否则抛 403。
    """
    # 将允许的角色枚举转为大写字符串集合，便于匹配
    allowed: set[str] = {r.value for r in roles}
    # 若调用方未传任何角色，等价于不做角色限制
    if not allowed:
        allowed = set(VALID_ROLES)

    async def _checker(current_user: User = Depends(get_current_user)) -> User:
        """角色校验闭包。

        Args:
            current_user: 当前用户实例，由 get_current_user 注入。

        Returns:
            User: 校验通过返回当前用户。

        Raises:
            HTTPException: 角色不在允许集合内时抛 403。
        """
        # 当前用户角色未在白名单中，拒绝访问
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        # 角色匹配，放行
        return current_user

    # 返回可被 Depends 使用的协程依赖
    return _checker
