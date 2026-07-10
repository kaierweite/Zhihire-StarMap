"""Ability graph API routes.

GET /api/graph/user - User personal ability graph
GET /api/graph/job/{job_id} - Job ability graph
POST /api/graph/reload - Admin graph rebuild
GET /api/graph/roles - List occupation roles for role selector
"""
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.graph import GraphResult, UserGraphResult
from app.models.schemas.result import Result
from app.repositories import role_repository
from app.services.graph_service import (
    analyze_gap_with_role,
    get_job_graph,
    get_user_graph,
    reload_graph_endpoint,
)
from app.services.errors import BusinessError

router = APIRouter(prefix="/graph", tags=["Ability Graph"])


@router.get("/user", summary="User personal ability graph")
async def read_user_graph(
    role_id: int | None = Query(None, description="Target role ID for skill gap analysis"),
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[UserGraphResult]:
    """Get the current user's personal ability graph with optional gap analysis."""
    try:
        result = await get_user_graph(db, current_user.id)
        if role_id is not None:
            gaps = await analyze_gap_with_role(db, current_user.id, role_id)
            result.gap_skills = gaps
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="User graph fetched")


@router.get("/job/{job_id}", summary="Job ability graph")
async def read_job_graph(
    job_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER, RoleEnum.COMPANY)),
    db: AsyncSession = Depends(get_db),
) -> Result[GraphResult]:
    """Get the skill graph for a job position."""
    try:
        result = await get_job_graph(db, job_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="Job graph fetched")


@router.post("/reload", summary="Manual graph rebuild")
async def reload_graph(
    current_user: User = Depends(require_role(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Result[None]:
    """Trigger a full graph rebuild from the database (ADMIN only)."""
    try:
        await reload_graph_endpoint(db)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(message="Graph rebuilt successfully")


@router.get("/roles", summary="List occupation roles")
async def list_roles(
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[list[dict[str, Any]]]:
    """Get all active occupation roles for the frontend role selector."""
    roles = await role_repository.list_active(db)
    result = [
        {"id": r.id, "name": r.name, "category": r.category, "description": r.description}
        for r in roles
    ]
    return Result.success(data=result, message="Roles fetched")
