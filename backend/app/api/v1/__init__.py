"""v1 API routes package.
Central router registration for all v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.ping import router as ping_router
from app.api.v1.user import router as user_router
from app.api.v1.resume import router as resume_router
from app.api.v1.parse import router as parse_router
from app.api.v1.graph import router as graph_router
from app.api.v1.job import router as job_router
from app.api.v1.skill import router as skill_router
from app.api.v1.company import router as company_router
from app.api.v1.companies import router as companies_router
from app.api.v1.match import router as match_router
from app.api.v1.career import router as career_router
from app.api.v1.interview import router as interview_router
from app.api.v1.notification import router as notification_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(ping_router)
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(user_router)
api_router.include_router(resume_router)
api_router.include_router(parse_router)
api_router.include_router(job_router)
api_router.include_router(graph_router)
api_router.include_router(skill_router)
api_router.include_router(company_router)
api_router.include_router(match_router)
api_router.include_router(career_router)
api_router.include_router(interview_router)
api_router.include_router(notification_router)
api_router.include_router(admin_router)

