"""企业模块 Pydantic 请求/响应模型。

包含企业信息查询、更新、Dashboard 首页统计的请求与响应模型。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ========== 响应模型 ==========


class CompanyInfoResponse(BaseModel):
    """企业信息响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    industry: str | None = None
    scale: str | None = None
    company_type: str | None = None
    website: str | None = None
    logo_url: str | None = None
    description: str | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    audit_status: str
    audit_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class DashboardJobItem(BaseModel):
    """Dashboard 最近岗位项。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: str
    city: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str
    views: int
    created_at: datetime


class DashboardApplicationItem(BaseModel):
    """Dashboard 最近投递项。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    job_title: str | None = None
    user_id: int
    applicant_name: str | None = None
    status: str
    created_at: datetime


class DashboardStats(BaseModel):
    """Dashboard 统计数字。"""
    total_jobs: int = 0
    active_jobs: int = 0
    total_applications: int = 0


class CompanyDashboardResponse(BaseModel):
    """企业首页 Dashboard 响应。"""
    stats: DashboardStats
    recent_jobs: list[DashboardJobItem] = []
    recent_applications: list[DashboardApplicationItem] = []


# ========== 请求模型 ==========


class CompanyUpdateRequest(BaseModel):
    """编辑企业信息请求（所有字段可选）。
    更新后 audit_status 将自动重置为 PENDING，需重新审核。
    """
    company_name: str | None = Field(None, max_length=200)
    industry: str | None = Field(None, max_length=100)
    scale: str | None = Field(None, max_length=50)
    company_type: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=500)
    logo_url: str | None = Field(None, max_length=500)
    description: str | None = None
    address: str | None = Field(None, max_length=500)
    contact_name: str | None = Field(None, max_length=50)
    contact_phone: str | None = Field(None, max_length=20)
    contact_email: str | None = Field(None, max_length=100)
