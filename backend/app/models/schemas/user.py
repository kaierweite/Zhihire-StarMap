"""用户档案模块请求/响应模型。

定义求职者个人档案的读取与更新所需 Pydantic 模型。
档案扩展表 `user_profile` 为单记录设计，教育经历内联为单条
（school/major/education），不复用独立子表。
"""
from datetime import date, datetime  # 日期与时间类型

from pydantic import BaseModel, ConfigDict, Field  # 模型基类与字段


class SkillItem(BaseModel):
    """用户技能条目（响应结构）。

    用于 GET /api/user/profile 返回的技能列表，
    兼具技能元信息与用户侧熟练度。

    Attributes:
        skill_id: 技能主键。
        name: 技能名称。
        category: 技能领域。
        proficiency_level: 熟练度 0~5。
    """

    model_config = ConfigDict(from_attributes=True)

    skill_id: int = Field(..., description="技能主键")
    name: str = Field(..., description="技能名称")
    category: str | None = Field(None, description="技能领域")
    proficiency_level: float = Field(0.0, description="熟练度 0~5")


class UserProfileDTO(BaseModel):
    """用户档案完整信息响应模型。

    GET /api/user/profile 与 PUT /api/user/profile 成功后均返回本结构。
    基本信息来自 user 表，档案字段来自 user_profile 表，
    技能列表来自 user_skill JOIN skill。

    Attributes:
        id: 用户主键。
        username: 用户名。
        avatar_url: 头像链接。
        real_name: 真实姓名。
        gender: 性别。
        birth_date: 出生日期。
        phone: 手机号。
        email: 邮箱。
        education: 学历。
        school: 毕业院校。
        major: 所学专业。
        work_years: 工作年限。
        current_city: 当前城市。
        expected_city: 期望城市。
        expected_salary_min: 期望薪资下限。
        expected_salary_max: 期望薪资上限。
        bio: 个人优势/自我介绍。
        profile_completeness: 档案完成度 0~100。
        skills: 技能列表。
        created_at: 创建时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户主键")
    username: str = Field(..., description="用户名")
    avatar_url: str | None = Field(None, description="头像链接")
    real_name: str | None = Field(None, description="真实姓名")
    gender: str | None = Field(None, description="性别")
    birth_date: date | None = Field(None, description="出生日期")
    phone: str | None = Field(None, description="手机号")
    email: str | None = Field(None, description="邮箱")
    education: str | None = Field(None, description="学历")
    school: str | None = Field(None, description="毕业院校")
    major: str | None = Field(None, description="所学专业")
    work_years: int | None = Field(None, description="工作年限")
    current_city: str | None = Field(None, description="当前城市")
    expected_city: str | None = Field(None, description="期望城市")
    expected_salary_min: float | None = Field(None, description="期望薪资下限")
    expected_salary_max: float | None = Field(None, description="期望薪资上限")
    bio: str | None = Field(None, description="个人优势")
    profile_completeness: int = Field(0, description="档案完成度 0~100")
    skills: list[SkillItem] = Field(default_factory=list, description="技能列表")
    created_at: datetime | None = Field(None, description="创建时间")


class UserProfileUpdateForm(BaseModel):
    """用户档案更新请求表单。

    PUT /api/user/profile 接收本结构，逐 section 更新。
    所有字段均为可选；填写的字段会覆盖原值，未填写的保持不变。

    Attributes:
        real_name: 真实姓名。
        gender: 性别。
        birth_date: 出生日期。
        phone: 手机号。
        email: 邮箱。
        education: 学历。
        school: 毕业院校。
        major: 所学专业。
        work_years: 工作年限。
        current_city: 当前城市。
        expected_city: 期望城市。
        expected_salary_min: 期望薪资下限。
        expected_salary_max: 期望薪资上限。
        bio: 个人优势。
        skills: 技能名列表，由服务层归一到 skill_id 后写入 user_skill。
    """

    real_name: str | None = Field(None, max_length=50, description="真实姓名")
    gender: str | None = Field(None, description="性别")
    birth_date: date | None = Field(None, description="出生日期")
    phone: str | None = Field(None, max_length=32, description="手机号")
    email: str | None = Field(None, max_length=128, description="邮箱")
    education: str | None = Field(None, description="学历")
    school: str | None = Field(None, max_length=100, description="毕业院校")
    major: str | None = Field(None, max_length=100, description="所学专业")
    work_years: int | None = Field(None, ge=0, le=99, description="工作年限")
    current_city: str | None = Field(None, max_length=100, description="当前城市")
    expected_city: str | None = Field(None, max_length=100, description="期望城市")
    expected_salary_min: float | None = Field(None, ge=0, description="期望薪资下限")
    expected_salary_max: float | None = Field(None, ge=0, description="期望薪资上限")
    bio: str | None = Field(None, description="个人优势")
    skills: list[str] | None = Field(None, description="技能名列表，服务层归一到 skill_id")
