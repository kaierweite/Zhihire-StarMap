"""岗位模块 Pydantic 请求/响应模型。

包含岗位 CRUD 与技能关联的操作模型。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ========== 请求模型 ==========


class CreateJobRequest(BaseModel):
    """创建岗位请求。"""
    title: str = Field(..., max_length=200)
    city: str = Field(..., max_length=100)
    education_requirement: str = Field(default="本科", max_length=50)
    experience_min: int = Field(default=0, ge=0)
    salary_min: float = Field(default=0)
    salary_max: float = Field(default=0)
    job_type: str = Field(default="FULL_TIME", max_length=20)
    description: str = Field(default="")
    company_id: int
    occupation_role_id: int | None = None
    benefits: list[str] | None = None


class UpdateJobRequest(BaseModel):
    """更新岗位请求（所有字段可选）。"""
    title: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=50)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = Field(None, max_length=20)
    description: str | None = None
    occupation_role_id: int | None = None
    status: str | None = Field(None, max_length=20)
    benefits: list[str] | None = None


class AddJobSkillRequest(BaseModel):
    """为岗位添加技能要求请求。"""
    skill_id: int
    importance: float = Field(default=0.5, ge=0, le=1)
    required_level: str = Field(default="MUST", max_length=10)


class JobSearchParams(BaseModel):
    """岗位搜索参数。"""
    keyword: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=50)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = Field(None, max_length=20)
    company_id: int | None = None
    status: str | None = Field(None, max_length=20)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


# ========== 响应模型 ==========


class JobSkillItem(BaseModel):
    """岗位技能关联信息。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    skill_id: int
    skill_name: str | None = None
    skill_category: str | None = None
    importance: float
    required_level: str


class JobItem(BaseModel):
    """岗位列表项。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    company_name: str | None = None
    title: str
    city: str
    education_requirement: str
    experience_min: int
    salary_min: float
    salary_max: float
    job_type: str
    status: str
    views: int
    benefits: list[str] | None = None
    occupation_role_id: int | None = None
    created_at: datetime
    updated_at: datetime


class JobDetail(BaseModel):
    """岗位详情。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    company_name: str | None = None
    occupation_role_id: int | None = None
    occupation_role_name: str | None = None
    title: str
    city: str
    education_requirement: str
    experience_min: int
    salary_min: float
    salary_max: float
    job_type: str
    description: str
    requirements: str | None = None
    source: str
    status: str
    views: int
    benefits: list[str] | None = None
    skills: list[JobSkillItem] = []
    created_at: datetime
    updated_at: datetime


class CreateJobResult(BaseModel):
    """创建岗位结果。"""
    id: int
    title: str


class AddJobSkillResult(BaseModel):
    """添加技能关联结果。"""
    id: int
    job_id: int
    skill_id: int
    required_level: str
