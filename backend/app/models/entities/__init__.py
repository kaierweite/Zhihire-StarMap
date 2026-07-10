"""ORM entities package.
Central export of all ORM entities and Base for Alembic autogenerate.
"""
from app.models.entities.base import Base
from app.models.entities.career_plan import CareerPlan
from app.models.entities.company import Company
from app.models.entities.skill import Skill
from app.models.entities.skill_synonym import SkillSynonym
from app.models.entities.skill_relation import SkillRelation
from app.models.entities.role import Role
from app.models.entities.role_skill import RoleSkill
from app.models.entities.ability_graph import AbilityGraph
from app.models.entities.user import User
from app.models.entities.user_certificate import UserCertificate
from app.models.entities.user_language import UserLanguage
from app.models.entities.user_profile import UserProfile
from app.models.entities.user_project_experience import UserProjectExperience
from app.models.entities.user_skill import UserSkill
from app.models.entities.user_work_experience import UserWorkExperience
from app.models.entities.upload_file import UploadFile
from app.models.entities.resume import Resume
from app.models.entities.parse_task import ParseTask
from app.models.entities.job import Job
from app.models.entities.job_skill import JobSkill
from app.models.entities.occupation_role import OccupationRole
from app.models.entities.match_result import MatchResult
from app.models.entities.recommend_record import RecommendRecord
from app.models.entities.job_application import JobApplication
# === Day08: Interview module entities ===
from app.models.entities.interview_session import InterviewSession
from app.models.entities.interview_question import InterviewQuestion
from app.models.entities.interview_answer import InterviewAnswer
from app.models.entities.interview_report import InterviewReport
from app.models.entities.resume_optimization import ResumeOptimization
# === Day09: Notification module entity ===
from app.models.entities.notification import Notification
from app.models.entities.operation_log import OperationLog
from app.models.entities.ai_provider import AiProvider

__all__ = [
    "Base",
    "CareerPlan",
    "User",
    "Company",
    "UserProfile",
    "UserSkill",
    "Skill",
    "SkillSynonym",
    "SkillRelation",
    "Role",
    "RoleSkill",
    "AbilityGraph",
    "UserWorkExperience",
    "UserProjectExperience",
    "UserLanguage",
    "UserCertificate",
    "UploadFile",
    "Resume",
    "ParseTask",
    "Job",
    "JobSkill",
    "JobApplication",
    "OccupationRole",
    "MatchResult",
    "RecommendRecord",
    # Day08 interview
    "InterviewSession",
    "InterviewQuestion",
    "InterviewAnswer",
    "InterviewReport",
    "ResumeOptimization",
    # Day09 notification
    "Notification",
    # Day11 admin
    "OperationLog",
    # Day11 admin
    "AiProvider",
]
