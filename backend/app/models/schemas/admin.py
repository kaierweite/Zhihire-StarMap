# -*- coding: utf-8 -*-
"""管理员模块请求/响应模型。

定义后台管理相关 Pydantic 模型，包括统计、用户管理、企业审核、操作日志等。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdminStatResponse(BaseModel):
    """后台首页统计数据响应模型。"""
    model_config = ConfigDict(from_attributes=True)
    user_count: int = Field(0, description="注册用户总数")
    company_count: int = Field(0, description="注册企业总数")
    job_count: int = Field(0, description="在招岗位总数")
    match_count: int = Field(0, description="匹配记录总数")
    parse_count: int = Field(0, description="解析任务总数")
    application_count: int = Field(0, description="简历投递总数")


class UserAdminItem(BaseModel):
    """用户管理列表项响应模型。"""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="用户主键")
    username: str = Field(..., description="用户名")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, description="手机号")
    role: str = Field(..., description="用户角色")
    status: str = Field(..., description="账号状态")
    avatar_url: str | None = Field(None, description="头像链接")
    created_at: datetime | None = Field(None, description="注册时间")
    updated_at: datetime | None = Field(None, description="更新时间")


class CompanyAuditItem(BaseModel):
    """企业审核列表项响应模型。"""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="企业主键")
    company_name: str = Field(..., description="企业名称")
    industry: str | None = Field(None, description="所属行业")
    scale: str | None = Field(None, description="企业规模")
    website: str | None = Field(None, description="企业网站")
    description: str | None = Field(None, description="企业介绍")
    address: str | None = Field(None, description="企业地址")
    contact_name: str | None = Field(None, description="联系人姓名")
    contact_phone: str | None = Field(None, description="联系人电话")
    contact_email: str | None = Field(None, description="联系人邮箱")
    audit_status: str = Field(..., description="审核状态")
    audit_reason: str | None = Field(None, description="审核驳回原因")
    created_at: datetime | None = Field(None, description="创建时间")


class AuditRequest(BaseModel):
    """企业审核操作请求模型。"""
    action: str = Field(..., description="审核动作：pass / reject", pattern="^(pass|reject)$")
    reason: str | None = Field(None, max_length=500, description="驳回原因，reject 时必填")


class UserStatusRequest(BaseModel):
    """用户状态更新请求模型。"""
    status: str = Field(..., description="目标状态：BANNED / NORMAL", pattern="^(BANNED|NORMAL)$")


class JobStatusRequest(BaseModel):
    """岗位状态更新请求模型。"""
    status: str = Field(..., description="目标状态：CLOSED / OPEN", pattern="^(CLOSED|OPEN)$")


class LogItem(BaseModel):
    """操作日志列表项响应模型。"""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="日志主键")
    user_id: int = Field(..., description="操作用户主键")
    module: str | None = Field(None, description="模块名")
    action: str | None = Field(None, description="操作动作")
    detail: dict[str, Any] | None = Field(None, description="扩展信息")
    ip: str | None = Field(None, description="客户端 IP")
    created_at: datetime | None = Field(None, description="操作时间")


class SkillAuditItem(BaseModel):
    """技能审核列表项响应模型。"""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="技能主键")
    name: str = Field(..., description="技能名称")
    category: str | None = Field(None, description="技能领域")
    status: str = Field(..., description="技能状态")
    created_at: datetime | None = Field(None, description="创建时间")


class SkillAuditRequest(BaseModel):
    """技能审核操作请求模型。"""
    action: str = Field(..., description="审核动作：approve / reject", pattern="^(approve|reject)$")
    target_id: int | None = Field(None, description="合并目标技能 ID（approve 时可选）")


class AdminServiceStatus(BaseModel):
    """后台服务状态卡片模型。"""
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态：UP / DOWN")
    latency_ms: int | None = Field(None, description="延迟毫秒数")


class JobAdminItem(BaseModel):
    """后台岗位管理列表项响应模型。"""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="岗位主键")
    title: str = Field(..., description="岗位名称")
    company_id: int = Field(..., description="所属企业主键")
    company_name: str | None = Field(None, description="企业名称")
    city: str | None = Field(None, description="工作城市")
    status: str = Field(..., description="岗位状态")
    views: int = Field(0, description="浏览次数")
    created_at: datetime | None = Field(None, description="发布时间")
    updated_at: datetime | None = Field(None, description="更新时间")
