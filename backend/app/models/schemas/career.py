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


class AiPlanResponse(BaseModel):
    """AI 职业规划响应。

    Attributes:
        target_role: 目标角色/专业名称。
        analysis_summary: AI 分析总结。
        match_score: 匹配度（0-100）。
        has_resume: 是否使用了简历数据。
        gap_skills: 缺口技能列表。
        mind_map: 思维导图树形数据。
    """
    target_role: str
    analysis_summary: str = ""
    match_score: float = 0.0
    has_resume: bool = False
    gap_skills: list[dict] = []
    mind_map: dict | None = None


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
