"""图谱模块 Pydantic 请求/响应模型。
"""
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    name: str
    category: str | None = None
    level: float = 0.0
    symbolSize: int = 20
    itemStyle: dict | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str
    weight: float = 0.5
    lineStyle: dict | None = None


class GraphResult(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


class UserGraphResult(GraphResult):
    gap_skills: list[str] = []


class GapSkill(BaseModel):
    skill_name: str
    requirement_level: str
