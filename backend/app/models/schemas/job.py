"""岗位模块 Pydantic 请求/响应模型。

包含岗位 CRUD 与技能关联的操作模型。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ========== 请求模型 ==========


class CreateJobRequest(BaseModel):
    """创建岗位请求。注意 company_id 从当前登录企业自动获取，请求中可省略。"""
    title: str = Field(..., max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=20)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str = Field(default="FULL_TIME", max_length=20)
    description: str | None = None
    company_id: int | None = None
    occupation_role_id: int | None = None
    is_campus: bool = False
    major: str | None = None
    job_category: str | None = None
    benefits: list[str] | None = None


class UpdateJobRequest(BaseModel):
    """更新岗位请求（所有字段可选）。"""
    title: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=20)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = Field(None, max_length=20)
    description: str | None = None
    occupation_role_id: int | None = None
    status: str | None = Field(None, max_length=20)
    is_campus: bool | None = None
    major: str | None = None
    job_category: str | None = None
    benefits: list[str] | None = None


class AddJobSkillRequest(BaseModel):
    """为岗位添加技能要求请求。"""
    skill_id: int
    importance: float = Field(default=3.0, ge=1, le=5)
    required_level: str = Field(default="NICE", max_length=20)


class BatchAddJobSkillRequest(BaseModel):
    """批量为岗位添加技能要求请求。"""
    skills: list[AddJobSkillRequest]


class JobSearchParams(BaseModel):
    """岗位搜索参数。"""
    keyword: str | None = Field(None, max_length=200)
    city: str | None = Field(None, max_length=100)
    education_requirement: str | None = Field(None, max_length=20)
    experience_min: int | None = Field(None, ge=0)
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = Field(None, max_length=20)
    major: str | None = Field(None, max_length=200)
    job_category: str | None = Field(None, max_length=100)
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
    industry: str | None = None
    scale: str | None = None
    company_type: str | None = None
    title: str
    city: str | None = None
    education_requirement: str | None = None
    experience_min: int | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str
    status: str
    views: int
    is_campus: bool = False
    major: str | None = None
    job_category: str | None = None
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
    city: str | None = None
    education_requirement: str | None = None
    experience_min: int | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str
    description: str | None = None
    requirements: str | None = None
    source: str | None = None
    status: str
    views: int
    is_campus: bool = False
    major: str | None = None
    job_category: str | None = None
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


class JobApplicationItem(BaseModel):
    """投递记录响应项（企业端查看某岗位的投递列表）。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    user_id: int
    applicant_name: str | None = None
    applicant_email: str | None = None
    phone: str | None = None
    resume_id: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ApplyJobRequest(BaseModel):
    """投递简历请求。"""
    resume_id: int | None = None


class ApplyJobResult(BaseModel):
    """投递简历结果。"""
    id: int
    user_id: int
    job_id: int
    status: str


class UpdateApplicationStatusRequest(BaseModel):
    """更新投递状态请求。"""
    status: str = Field(..., description="ACCEPTED / REJECTED")


class UpdateApplicationStatusResult(BaseModel):
    """更新投递状态结果。"""
    id: int
    status: str


class JdParseResult(BaseModel):
    """JD 解析结果。"""
    task_id: int
    status: str
    file_id: int
    title: str | None = None
    city: str | None = None
    education_requirement: str | None = None
    experience_min: int | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = None
    description: str | None = None
    benefits: list[str] | None = None
    skills: list[dict] = []
    parsed_at: datetime | None = None


class JdUploadResult(BaseModel):
    """JD 上传结果。"""
    file_id: int
    task_id: int
    file_name: str
