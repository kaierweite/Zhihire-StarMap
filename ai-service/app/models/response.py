"""
响应模型 — 定义各接口的出参结构
"""

from pydantic import BaseModel, Field


class ResultWrapper(BaseModel):
    """统一返回封装，与后端 Result<T> 对齐"""
    code: str = "OK"
    message: str = "success"
    data: object | None = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"


class ParseResult(BaseModel):
    """解析结果（简历 / JD 通用）"""
    raw_text: str = Field(default="", description="原始文本")
    skills: list[str] = Field(default_factory=list, description="提取的技能列表")
    parsed_data: dict = Field(default_factory=dict, description="结构化解析数据")


class MatchResultItem(BaseModel):
    """单条匹配结果"""
    candidate_id: int = Field(..., description="候选岗位 ID")
    score: float = Field(..., description="综合匹配分 0-100")
    breakdown: dict = Field(default_factory=dict, description="分项得分")
    rationale: str = Field(default="", description="匹配理由")
    graph_hints: list[str] = Field(default_factory=list, description="图谱提示")


class MatchResponse(BaseModel):
    """匹配评分响应"""
    results: list[MatchResultItem] = Field(default_factory=list)


class GraphData(BaseModel):
    """图谱数据（ECharts JSON 格式）"""
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)


class CareerPlanItem(BaseModel):
    """学习路径单项"""
    skill: str = Field(..., description="目标技能")
    priority: str = Field(default="medium", description="优先级")
    resources: list[str] = Field(default_factory=list, description="推荐学习资源")


class CareerAnalyzeResponse(BaseModel):
    """职业规划响应"""
    gap_skills: list[str] = Field(default_factory=list, description="差距技能")
    learning_path: list[CareerPlanItem] = Field(default_factory=list, description="学习路径")
    rationale: str = Field(default="", description="规划理由")
