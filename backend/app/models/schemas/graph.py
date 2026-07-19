"""Graph module Pydantic request/response models.
"""
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    name: str
    category: str | None = None
    level: float = 0.0
    level_label: str = "none"          # "none" | "beginner" | "intermediate" | "advanced"
    symbolSize: int = 20
    itemStyle: dict | None = None
    importance: float = 3.0            # Job skill importance (1-5)
    required_level: str = "NICE"       # Job skill requirement level (MUST/NICE/BONUS)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str
    weight: float = 0.5
    lineStyle: dict = {}               # Always populated by backend


class CategoryItem(BaseModel):
    name: str
    color: str


class GraphResult(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    state: str = "ready"               # "empty" | "ready"
    categories: list[CategoryItem] = [] # name -> color for frontend
    sunburst_data: dict | None = None   # Hierarchical tree for ECharts sunburst 旭日图 series


class UserGraphResult(GraphResult):
    gap_skills: list = []


class GapSkill(BaseModel):
    skill_name: str
    requirement_level: str
