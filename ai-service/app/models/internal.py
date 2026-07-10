"""
内部数据模型 — 服务内部传递的结构体
"""

from pydantic import BaseModel, Field


class SkillNode(BaseModel):
    """图谱中的技能节点"""
    id: int = Field(..., description="技能 ID")
    name: str = Field(..., description="技能名称")
    category: str = Field(default="", description="技能分类")
    level: int = Field(default=1, description="技能等级 1-5")


class SkillRelation(BaseModel):
    """技能关系"""
    source_id: int = Field(..., description="源技能 ID")
    target_id: int = Field(..., description="目标技能 ID")
    relation_type: str = Field(default="related", description="关系类型")
    weight: float = Field(default=1.0, description="关系权重")


class ParsedDocument(BaseModel):
    """文档解析中间结果"""
    raw_text: str = Field(default="", description="原始文本")
    file_type: str = Field(default="unknown", description="文件类型 pdf/docx")
    metadata: dict = Field(default_factory=dict, description="文件元信息")
