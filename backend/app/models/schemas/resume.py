"""???? Pydantic ???"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class ResumeUploadResult(BaseModel):
    """???????"""
    model_config = ConfigDict(from_attributes=True)
    resume_id: int
    file_id: int
    task_id: int
    title: str


class ResumeListItem(BaseModel):
    """??????"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str | None = None
    status: str = 'NORMAL'
    created_at: datetime | None = None


class ResumeDetail(BaseModel):
    """??????????"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    file_id: int | None = None
    title: str | None = None
    content_text: str | None = None
    """??????? JSON ???"""
    parsed: dict[str, Any] | None = None
    """??????????? content_text JSON ?????"""
    status: str = 'NORMAL'
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ResumeContent(BaseModel):
    """????????????"""
    title: str | None = None
    content_text: str | None = None


class TaskStatus(BaseModel):
    """?????????"""
    task_id: int
    status: str  # WAITING / PARSING / SUCCESS / FAILED
    result: dict[str, Any] | None = None


class OptimizeRequest(BaseModel):
    """???????"""
    resume_id: int
    job_description: str | None = None


class OptimizeSuggestion(BaseModel):
    """???????"""
    section: str
    current: str
    suggestion: str
    relates_to_skill: str | None = None


class OptimizeResult(BaseModel):
    """?????????"""
    resume_id: int
    suggestions: list[OptimizeSuggestion]
