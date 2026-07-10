"""认证模块请求/响应模型。

定义注册、登录、当前用户信息等接口所需的 Pydantic 模型，
供应商层与路由层做参数校验和数据序列化。
"""
from datetime import datetime  # 时间类型注解

from pydantic import BaseModel, ConfigDict, Field, field_validator  # 模型基类与校验

from app.models.enums.role import RoleEnum  # 角色枚举


class RegisterForm(BaseModel):
    """注册请求表单。

    求职者与企业统一使用本表单，通过 `role` 区分；
    企业注册时需附带 `company_name` 等企业字段。

    Attributes:
        username: 用户名（必填）。
        password: 密码（必填，明文上行，后端 bcrypt 加密）。
        role: 角色（必填，仅允许 USER 或 COMPANY，禁止注册 ADMIN）。
        email: 邮箱（可选）。
        phone: 手机号（可选）。
        company_name: 企业名称（role=COMPANY 时必填）。
        contact_email: 企业联系邮箱（可选）。
        contact_phone: 企业联系电话（可选）。
    """

    # 允许从 ORM 等属性对象构造
    model_config = ConfigDict(from_attributes=True)

    # 用户名：必填，长度 3~64
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    # 密码：必填，长度 6~64，明文传输后端加密
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    # 角色：必填，仅允许 USER/COMPANY，ADMIN 不可注册
    role: str = Field(..., description="角色：USER 或 COMPANY")
    # 邮箱：可选
    email: str | None = Field(None, max_length=128, description="邮箱")
    # 手机号：可选
    phone: str | None = Field(None, max_length=32, description="手机号")
    # 企业名称：role=COMPANY 时必填
    company_name: str | None = Field(None, max_length=128, description="企业名称")
    # 企业联系邮箱：可选
    contact_email: str | None = Field(None, max_length=128, description="企业联系邮箱")
    # 企业联系电话：可选
    contact_phone: str | None = Field(None, max_length=32, description="企业联系电话")

    @field_validator("role")
    @classmethod
    def _validate_role(cls, v: str) -> str:
        """校验角色：仅允许 USER 或 COMPANY，禁止注册 ADMIN。"""
        # 归一化为大写
        v = v.strip().upper()
        # ADMIN 不允许自行注册
        if v == RoleEnum.ADMIN.value:
            raise ValueError("管理员角色不可注册")
        # 必须属于合法角色集合
        if v not in (RoleEnum.USER.value, RoleEnum.COMPANY.value):
            raise ValueError("角色必须为 USER 或 COMPANY")
        return v


class LoginForm(BaseModel):
    """登录请求表单。

    Attributes:
        username: 用户名。
        password: 密码（明文，后端 bcrypt 比对）。
    """

    username: str = Field(..., min_length=1, max_length=64, description="用户名")
    password: str = Field(..., min_length=1, max_length=64, description="密码")


class LoginResult(BaseModel):
    """登录成功响应数据。

    Attributes:
        token: JWT 访问令牌。
        role: 用户角色（大写字符串）。
        username: 用户名。
    """

    token: str = Field(..., description="JWT 访问令牌")
    role: str = Field(..., description="用户角色")
    username: str = Field(..., description="用户名")


class UserInfo(BaseModel):
    """当前用户完整信息。

    用于 `GET /api/auth/me` 的响应数据。

    Attributes:
        id: 用户主键。
        username: 用户名。
        role: 角色。
        email: 邮箱（可能为空）。
        phone: 手机号（可能为空）。
        status: 账号状态。
        created_at: 创建时间。
    """

    # 允许从 ORM User 实例直接构造
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户主键")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="角色")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, description="手机号")
    status: str = Field(..., description="账号状态")
    created_at: datetime | None = Field(None, description="创建时间")
