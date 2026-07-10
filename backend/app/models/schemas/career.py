"""职业规划模块 Pydantic 请求/响应模型。

用于职业规划生成与查询的请求参数与响应结构。
"""
from pydantic import BaseModel, Field


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