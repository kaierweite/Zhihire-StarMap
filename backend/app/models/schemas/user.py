"""用户档案模块请求/响应模型。

定义求职者个人档案的读取与更新所需 Pydantic 模型。
多值字段（工作/项目/语言/证书）通过子表存储。
"""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SkillItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int = Field(..., description="技能主键")
    name: str = Field(..., description="技能名称")
    category: str | None = Field(None, description="技能领域")
    proficiency_level: float = Field(0.0, description="熟练度 0~5")


class WorkExperienceItem(BaseModel):
    title: str = Field(..., description="职位")
    company: str = Field(..., description="公司名称")
    period: str | None = Field(None, description="时间范围")
    description: str | None = Field(None, description="工作描述")


class ProjectExperienceItem(BaseModel):
    name: str = Field(..., description="项目名称")
    description: str | None = Field(None, description="项目描述")


class LanguageItem(BaseModel):
    name: str = Field(..., description="语言名称（如英语）")
    level: str | None = Field(None, description="熟练程度（如精通）")


class CertificateItem(BaseModel):
    name: str = Field(..., description="证书名称")


class UserProfileDTO(BaseModel):
    """用户档案完整信息响应模型。"""

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
    expected_position: str | None = Field(None, description="期望职位")
    expected_worktype: str | None = Field(None, description="工作类型")
    expected_industry: str | None = Field(None, description="期望行业")
    expected_salary_min: float | None = Field(None, description="期望薪资下限")
    expected_salary_max: float | None = Field(None, description="期望薪资上限")
    bio: str | None = Field(None, description="个人优势")
    work_experiences: list[WorkExperienceItem] = Field(default_factory=list, description="工作/实习经历")
    project_experiences: list[ProjectExperienceItem] = Field(default_factory=list, description="项目经历")
    languages: list[LanguageItem] = Field(default_factory=list, description="语言能力")
    certificates: list[CertificateItem] = Field(default_factory=list, description="证书")
    profile_completeness: int = Field(0, description="档案完成度 0~100")
    skills: list[SkillItem] = Field(default_factory=list, description="技能列表")
    created_at: datetime | None = Field(None, description="创建时间")


class UserProfileUpdateForm(BaseModel):
    """用户档案更新请求表单。

    所有字段可选，仅覆盖已提供的字段。
    薪资字段前端以 K（千）为单位发送（如 10 表示 10K），服务层转为实际值存储。
    多值字段全量替换（前端传完整数组，后端先删后插）。
    语言字段 `name` 对应 DB 的 `language` 列，`description` 对应 DB 的对应列。
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
    expected_position: str | None = Field(None, max_length=200, description="期望职位")
    expected_worktype: str | None = Field(None, max_length=20, description="工作类型")
    expected_industry: str | None = Field(None, max_length=100, description="期望行业")
    expected_salary_min: float | None = Field(None, ge=0, description="期望薪资下限（K 值/月）")
    expected_salary_max: float | None = Field(None, ge=0, description="期望薪资上限（K 值/月）")
    bio: str | None = Field(None, description="个人优势")
    work_experiences: list[dict[str, Any]] | None = Field(None, description="工作/实习经历（[{title, company, period, description}]）")
    project_experiences: list[dict[str, Any]] | None = Field(None, description="项目经历（[{name, description}]）")
    languages: list[dict[str, Any]] | None = Field(None, description="语言能力（[{name, level}]，name 对应 DB language 列）")
    certificates: list[dict[str, Any]] | None = Field(None, description="证书（[{name}]）")
    skills: list[str] | None = Field(None, description="技能名列表，服务层归一到 skill_id")
