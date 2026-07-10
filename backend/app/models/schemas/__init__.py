"""Pydantic request/response models package."""
from app.models.schemas.result import PageResult, Result
from app.models.schemas.admin import (
    AdminServiceStatus,
    AdminStatResponse,
    AuditRequest,
    CompanyAuditItem,
    JobAdminItem,
    JobStatusRequest,
    LogItem,
    SkillAuditItem,
    SkillAuditRequest,
    UserAdminItem,
    UserStatusRequest,
)
from app.models.schemas.career import (
    CareerPlanGenerateRequest,
    CareerPlanRecord,
    CareerPlanResponse,
    GapSkillItem,
    LearningPathItem,
)
from app.models.schemas.company import (
    CompanyDashboardResponse,
    CompanyInfoResponse,
    CompanyUpdateRequest,
    DashboardApplicationItem,
    DashboardJobItem,
    DashboardStats,
)
from app.models.schemas.interview import (
    InterviewMessageRequest,
    InterviewMessageResponse,
    InterviewQuestionItem,
    InterviewReportResponse,
    InterviewStartRequest,
    InterviewStartResponse,
    QuestionBankItem,
    QuestionBankQuery,
)

__all__ = [
    # Day11 admin
    "AdminServiceStatus",
    "AdminStatResponse",
    "AuditRequest",
    "CompanyAuditItem",
    "JobAdminItem",
    "JobStatusRequest",
    "LogItem",
    "SkillAuditItem",
    "SkillAuditRequest",
    "UserAdminItem",
    "UserStatusRequest",
    "Result",
    "PageResult",
    # Day10 company
    "CompanyInfoResponse",
    "CompanyUpdateRequest",
    "CompanyDashboardResponse",
    "DashboardStats",
    "DashboardJobItem",
    "DashboardApplicationItem",
    # Day07 career
    "CareerPlanGenerateRequest",
    "CareerPlanRecord",
    "CareerPlanResponse",
    "GapSkillItem",
    "LearningPathItem",
    # Day08 interview
    "InterviewStartRequest",
    "InterviewStartResponse",
    "InterviewMessageRequest",
    "InterviewMessageResponse",
    "InterviewReportResponse",
    "InterviewQuestionItem",
    "QuestionBankItem",
    "QuestionBankQuery",
]
