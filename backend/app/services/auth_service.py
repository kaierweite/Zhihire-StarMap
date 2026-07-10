"""认证业务服务模块。

编排注册、登录、当前用户查询等业务流程：
- 注册：用户名查重、bcrypt 加密、入库；企业角色附带创建企业记录
- 登录：用户名查找、状态校验、bcrypt 比对、签发 JWT
- me：按主键加载用户并返回完整信息

事务提交由本层负责，仓储层仅做原子数据访问。
"""
from datetime import datetime, timedelta, timezone  # 时间计算与时区

from jose import jwt  # JWT 编码
from passlib.context import CryptContext  # bcrypt 哈希上下文
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.config.settings import settings  # 全局配置（JWT 密钥、有效期、算法）
from app.models.entities.company import Company  # 企业 ORM
from app.models.entities.user import User  # 用户 ORM
from app.models.enums.role import RoleEnum  # 角色枚举
from app.models.enums.status import (  # 状态枚举
    CompanyAuditStatusEnum,
    UserStatusEnum,
)
from app.models.schemas.auth import (  # 请求/响应模型
    LoginForm,
    LoginResult,
    RegisterForm,
    UserInfo,
)
from app.repositories import company_repository, user_repository  # 仓储层
from app.services.errors import BusinessError  # 业务异常


# bcrypt 哈希上下文：scheme 固定 bcrypt，自动标记旧算法弃用
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(plain: str) -> str:
    """对明文密码进行 bcrypt 加密。

    Args:
        plain: 明文密码。

    Returns:
        str: 哈希后的密码字符串。
    """
    # 调用 passlib 生成哈希
    return _pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。

    Args:
        plain: 明文密码。
        hashed: 数据库中存储的哈希。

    Returns:
        bool: 匹配返回 True，否则 False。
    """
    # passlib 内部处理常量时间比较，避免计时侧信道
    return _pwd_context.verify(plain, hashed)


def _create_access_token(user: User) -> str:
    """为指定用户签发 JWT 访问令牌。

    payload 包含 sub(用户主键)、role、username、exp(过期时间)。

    Args:
        user: 已通过认证的用户实例。

    Returns:
        str: 编码后的 JWT 字符串。
    """
    # 计算过期时间：当前时间 + 配置的有效期
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    # 组装 payload，sub 统一存为字符串
    payload = {
        "sub": str(user.id),  # 用户主键
        "role": user.role,  # 角色（大写）
        "username": user.username,  # 用户名
        "exp": expire,  # 过期时间
    }
    # 编码并返回 token
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def register(db: AsyncSession, form: RegisterForm) -> None:
    """用户注册。

    求职者与企业统一入口：企业角色需附带企业名称，并创建企业记录（审核状态未审核）。

    Args:
        db: 异步数据库会话。
        form: 注册表单。

    Raises:
        BusinessError: 用户名重复(409)、企业缺少名称(400)。
    """
    # 用户名查重：仅查未删除记录
    existing = await user_repository.get_by_username(db, form.username)
    if existing is not None:
        # 重复用户名返回 409
        raise BusinessError(409, "用户名已存在")

    # 企业角色必须填写企业名称
    if form.role == RoleEnum.COMPANY.value and not form.company_name:
        raise BusinessError(400, "企业注册必须填写企业名称")

    # bcrypt 加密明文密码
    password_hash = _hash_password(form.password)
    # 构造用户实例，状态默认正常
    user = User(
        username=form.username,
        password_hash=password_hash,
        role=form.role,
        email=form.email,
        phone=form.phone,
        status=UserStatusEnum.NORMAL.value,
    )
    # 写入数据库并取回主键
    user = await user_repository.create(db, user)

    # 企业角色：附带创建企业信息记录
    if form.role == RoleEnum.COMPANY.value:
        company = Company(
            user_id=user.id,
            company_name=form.company_name,
            audit_status=CompanyAuditStatusEnum.UNVERIFIED.value,
            contact_email=form.contact_email,
            contact_phone=form.contact_phone,
        )
        await company_repository.create(db, company)

    # 统一提交事务
    await db.commit()


async def login(db: AsyncSession, form: LoginForm) -> LoginResult:
    """用户登录。

    Args:
        db: 异步数据库会话。
        form: 登录表单。

    Returns:
        LoginResult: 包含 token、role、username 的登录结果。

    Raises:
        BusinessError: 用户不存在或密码错误(400)、账号封禁(403)、账号停用(403)。
    """
    # 按用户名查找用户
    user = await user_repository.get_by_username(db, form.username)
    if user is None:
        # 统一提示，避免泄露用户名是否存在
        raise BusinessError(400, "用户名或密码错误")

    # 账号状态校验：封禁
    if user.status == UserStatusEnum.BANNED.value:
        raise BusinessError(403, "账号已被封禁")
    # 账号状态校验：停用
    if user.status == UserStatusEnum.DISABLED.value:
        raise BusinessError(403, "账号已被停用")

    # bcrypt 比对密码
    if not _verify_password(form.password, user.password_hash):
        # 密码错误统一 400
        raise BusinessError(400, "用户名或密码错误")

    # 签发 JWT
    token = _create_access_token(user)
    # 组装登录结果
    return LoginResult(token=token, role=user.role, username=user.username)


async def me(db: AsyncSession, user_id: int) -> UserInfo:
    """查询当前用户完整信息。

    Args:
        db: 异步数据库会话。
        user_id: 当前用户主键（来自 JWT claim）。

    Returns:
        UserInfo: 当前用户完整信息。

    Raises:
        BusinessError: 用户不存在(404)。
    """
    # 按主键加载用户
    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        # token 有效但用户已被删除
        raise BusinessError(404, "用户不存在")
    # 从 ORM 实例构造响应模型
    return UserInfo.model_validate(user)
