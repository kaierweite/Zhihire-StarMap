"""职业规划模块 Pydantic 请求/响应模型。

用于职业规划生成与查询的请求参数与响应结构。
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any


class AiPlanGenerateRequest(BaseModel):
    """AI 职业规划生成请求。

    Attributes:
        input_type: 输入类型：PROFESSION（专业名称）/ JOB_DESCRIPTION（岗位 JD）/ JOB_URL（招聘链接）。
        target_text: 目标专业名称或 JD 内容，最长 5000 字符。
    """
    input_type: str = Field(
        ...,
        description="输入类型: PROFESSION / JOB_DESCRIPTION / JOB_URL",
        pattern=r"^(PROFESSION|JOB_DESCRIPTION|JOB_URL)$",
    )
    target_text: str = Field(
        ...,
        description="目标专业名称或 JD 内容",
        max_length=5000,
    )


class MindMapNode(BaseModel):
    """思维导图节点（递归树形结构）。

    Attributes:
        name: 节点名称。
        children: 子节点列表。
    """
    name: str
    children: list["MindMapNode"] = []


class GapSkillItem(BaseModel):
    """缺口技能条目。"""
    skill_name: str
    requirement_level: str  # MUST / NICE / BONUS


class LearningPathItem(BaseModel):
    """学习路径条目。"""
    skills: list[str]


class CareerPlanGenerateRequest(BaseModel):
    """生成职业规划请求。"""
    target_role_id: int = Field(..., description="目标职业角色主键")


class CareerPlanResponse(BaseModel):
    """职业规划响应。"""
    target_role: str
    gap_skills: list[GapSkillItem] = []
    learning_path: list[LearningPathItem] = []
    graph_hints: list[str] = []
    rationale: str = ""
    score: float = 0.0
    source: str = "PROACTIVE"


class CareerPlanRecord(BaseModel):
    """已保存的职业规划记录（含主键时间）。"""
    id: int
    target_role: str
    target_role_id: int
    plan_content: str | None = None
    source: str
    created_at: str | None = None
    updated_at: str | None = None


class AiSuggestion(BaseModel):
    """AI 建议项。"""
    title: str
    icon: str | None = None


class StrengthWeakness(BaseModel):
    """优势与不足分析。"""
    strengths: list[str] = []
    weaknesses: list[str] = []


class CareerStage(BaseModel):
    """职业发展阶段。"""
    stage: str
    title: str
    icon: str | None = None


class SkillGapWithProgress(BaseModel):
    """带进度的技能缺口。"""
    skill_name: str
    requirement_level: str  # MUST / NICE / BONUS
    current_level: int = 0
    target_level: int = 100
    description: str | None = None


class GrowthCurvePoint(BaseModel):
    """成长曲线点。"""
    label: str
    value: int


class LearningResource(BaseModel):
    """推荐学习资源。"""
    id: int
    title: str
    cover: str | None = None
    rating: float = 0.0
    duration: str | None = None
    type: str | None = None


class EmploymentOutlook(BaseModel):
    """就业前景预测。"""
    salary_range: str = ""
    demand_level: str = ""
    growth_rate: str = ""
    trend: str = "up"


class LearningStats(BaseModel):
    """学习数据概览。"""
    total_hours: int = 0
    completed_courses: int = 0
    planned_courses: int = 0
    certificates: int = 0
    completion_rate: int = 0
    target_completion_rate: int = 0


class AiPlanResponse(BaseModel):
    """AI 职业规划响应。

    Attributes:
        target_role: 目标角色/专业名称。
        analysis_summary: AI 分析总结。
        match_score: 匹配度（0-100）。
        has_resume: 是否使用了简历数据。
        ai_suggestions: AI 建议列表。
        strength_weakness: 优势与不足分析。
        career_stages: 职业发展阶段列表。
        gap_skills: 缺口技能列表（带进度）。
        growth_curve: 能力成长曲线数据。
        learning_resources: 推荐学习资源列表。
        employment_outlook: 就业前景预测。
        learning_stats: 学习数据概览。
        mind_map: 思维导图树形数据。
    """
    target_role: str
    analysis_summary: str = ""
    match_score: float = 0.0
    has_resume: bool = False
    ai_suggestions: list[AiSuggestion] = []
    strength_weakness: StrengthWeakness = StrengthWeakness()
    career_stages: list[CareerStage] = []
    gap_skills: list[SkillGapWithProgress] = []
    growth_curve: list[GrowthCurvePoint] = []
    learning_resources: list[LearningResource] = []
    employment_outlook: EmploymentOutlook = EmploymentOutlook()
    learning_stats: LearningStats = LearningStats()
    mind_map: dict | None = None
