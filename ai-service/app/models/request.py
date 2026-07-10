"""
请求模型 — 定义各接口的入参结构
"""

from pydantic import BaseModel, Field


class ResumeParseRequest(BaseModel):
    """简历解析请求"""
    file_path: str = Field(..., description="简历文件路径")


class JobParseRequest(BaseModel):
    """岗位 JD 解析请求"""
    file_path: str = Field(..., description="岗位描述文件路径")


class MatchRequest(BaseModel):
    """匹配评分请求"""
    user_skills: list[str] = Field(..., description="用户技能列表")
    candidate_ids: list[int] = Field(..., description="候选岗位 ID 列表")


class GraphBuildRequest(BaseModel):
    """构建图谱请求"""
    skills: list[str] = Field(default_factory=list, description="技能节点列表")
    relations: list[dict] = Field(default_factory=list, description="技能关系列表")


class CareerAnalyzeRequest(BaseModel):
    """职业规划请求"""
    user_skills: list[str] = Field(..., description="用户当前技能")
    target_role: str = Field(..., description="目标岗位名称")
