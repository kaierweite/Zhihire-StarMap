"Interview module Pydantic request/response models."
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class InterviewStartRequest(BaseModel):
    job_id: int | None = Field(None, description="Target job ID")
    occupation_role_id: int = Field(..., description="Occupation role ID")

class InterviewMessageRequest(BaseModel):
    session_id: int = Field(..., description="Interview session ID")
    question_id: int = Field(..., description="Question ID")
    answer: str = Field(..., description="User answer text")

class InterviewQuestionItem(BaseModel):
    question_id: int
    content: str
    question_type: str = "TECHNICAL"
    order_no: int = 1

class InterviewStartResponse(BaseModel):
    session_id: int
    status: str = "IN_PROGRESS"
    first_question: InterviewQuestionItem | None = None

class InterviewMessageResponse(BaseModel):
    next_question: InterviewQuestionItem | None = None
    overall_score: float | None = None
    is_finished: bool = False

class InterviewReportResponse(BaseModel):
    session_id: int
    overall_score: float | None = None
    radar: dict[str, float] | None = None
    feedback: dict[str, Any] | None = None
    created_at: datetime | None = None

class QuestionBankQuery(BaseModel):
    job_id: int | None = None
    role: str | None = None
    question_type: str | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=50)

class QuestionBankItem(BaseModel):
    id: int
    question_type: str
    content: str
    order_no: int
