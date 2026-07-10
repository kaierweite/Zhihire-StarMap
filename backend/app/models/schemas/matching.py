"""匹配推荐模块 Pydantic 请求/响应模型。

包含人岗匹配、岗位推荐和职业规划的请求/响应模型。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ========== 匹配请求 ==========


class MatchRequest(BaseModel):
    """触发匹配请求。"""
    resume_id: int
    job_ids: list[int] | None = None  # None 表示匹配所有 OPEN 岗位


# ========== 匹配结果响应 ==========


class SkillMatchDetail(BaseModel):
    """技能匹配明细。"""
    skill_id: int
    skill_name: str
    skill_category: str | None = None
    required_level: str
    user_proficiency: float = 0.0
    matched: bool = False
    score_contribution: float = 0.0


class MatchDetail(BaseModel):
    """匹配明细。"""
    jaccard_score: float = 0.0
    weighted_skill_score: float = 0.0
    composite_score: float = 0.0
    total_score: float = 0.0
    matched_skills: list[int] = []
    missing_skills: list[int] = []
    required_met: bool = False
    skill_details: list[SkillMatchDetail] = []
    rationale: str | None = None


class MatchResultItem(BaseModel):
    """匹配结果项。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    job_id: int
    job_title: str | None = None
    company_name: str | None = None
    score: float = 0.0
    match_detail: dict | None = None
    created_at: datetime
    updated_at: datetime


# ========== 推荐请求/响应 ==========


class RecommendRequest(BaseModel):
    """请求为当前用户推荐岗位。"""
    count: int = Field(default=10, ge=1, le=50)


class RecommendItem(BaseModel):
    """推荐岗位项。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    job_title: str | None = None
    company_name: str | None = None
    score: float = 0.0
    is_clicked: bool = False
    is_applied: bool = False
    created_at: datetime


class RecommendClickRequest(BaseModel):
    """标记推荐记录已点击/已投递。"""
    action: str = Field(..., pattern=r"^(click|apply)$")


# ========== 技能差距分析 ==========


class GapSkillItem(BaseModel):
    """技能差距项。"""
    skill_name: str
    requirement_level: str  # MUST / NICE / BONUS


class SkillGapAnalysis(BaseModel):
    """技能差距分析结果。"""
    total_required: int
    matching_skills: int
    gap_skills: list[GapSkillItem] = []
    match_rate: float = 0.0
    suggestions: list[str] = []


# ========== 职业规划 ==========


class CareerPathItem(BaseModel):
    """职业路径推荐项。"""
    role_id: int
    role_name: str
    score: float = 0.0
    gap_skills: list[GapSkillItem] = []


class CareerPlanResult(BaseModel):
    """职业规划结果。"""
    current_skills: list[int] = []
    career_paths: list[CareerPathItem] = []
    target_role: str | None = None
    plan_content: dict | None = None
