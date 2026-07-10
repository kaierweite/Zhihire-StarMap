"""鉴权依赖模块。

提供 FastAPI 通用依赖：
- `oauth2_scheme`：从 Authorization 头解析 Bearer 令牌
- `get_current_user`：解析 JWT 并返回当前用户信息
- `require_role`：按角色进行访问控制

day00 阶段尚未接入用户表，此处基于 JWT claim 构造轻量用户对象，
day01 认证模块再接入数据库做真实用户加载。
"""
from typing import Any  # 任意类型

from fastapi import Depends, HTTPException, status  # FastAPI 依赖与异常
from fastapi.security import OAuth2PasswordBearer  # Bearer 令牌解析
from jose import JWTError, jwt  # JWT 解码与异常

from app.config.settings import settings  # 全局配置（JWT 密钥与算法）
from app.models.enums.role import RoleEnum, VALID_ROLES  # 角色枚举与合法集合


# OAuth2 Bearer 方案：tokenUrl 指向登录端点，仅用于 OpenAPI 文档展示
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


class CurrentUser:
    """当前用户轻量对象。

    day00 阶段仅承载 JWT claim 中可解析的字段，
    day01 接入用户表后将替换为真实 ORM 用户实例。

    Attributes:
        user_id: 用户主键。
        username: 用户名。
        role: 角色字符串（大写）。
    """

    def __init__(self, user_id: int, username: str, role: str) -> None:
        # 记录用户主键
        self.user_id = user_id
        # 记录用户名
        self.username = username
        # 记录角色（大写字符串）
        self.role = role


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """从 JWT 解析当前用户。

    Args:
        token: 请求头中的 Bearer 令牌，由 oauth2_scheme 提取。

    Returns:
        CurrentUser: 解析得到的当前用户对象。

    Raises:
        HTTPException: token 无效或过期、claim 缺失时抛 401。
    """
    # 准备鉴权失败时的统一异常
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
        # 取出用户名
        username = payload.get("username")
        # 取出角色（统一大写）
        role = payload.get("role")
        # 任一关键 claim 缺失即视作无效 token
        if user_id is None or username is None or role is None:
            raise credentials_exception
        # 角色必须属于合法枚举集合
        if role not in VALID_ROLES:
            raise credentials_exception
    except JWTError:
        # 解码或签名校验失败
        raise credentials_exception

    # 构造并返回当前用户对象
    return CurrentUser(user_id=int(user_id), username=str(username), role=str(role))


def require_role(*roles: RoleEnum):
    """生成角色守卫依赖。

    用法：`Depends(require_role(RoleEnum.ADMIN, RoleEnum.COMPANY))`，
    仅允许指定角色访问。day00 不强校验账号状态，交由 day01 完善。

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

    async def _checker(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        """角色校验闭包。

        Args:
            current: 当前用户，由 get_current_user 注入。

        Returns:
            CurrentUser: 校验通过返回当前用户。

        Raises:
            HTTPException: 角色不在允许集合内时抛 403。
        """
        # 当前用户角色未在白名单中，拒绝访问
        if current.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        # 角色匹配，放行
        return current

    # 返回可被 Depends 使用的协程依赖
    return _checker