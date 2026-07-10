"""\u56fe\u8c31\u4e1a\u52a1\u670d\u52a1\u6a21\u5757\u3002
"""
import json
import logging
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.graph import build_graph, build_job_graph, build_user_graph, reload_graph, skill_graph
from app.core.career.career_engine import analyze_skill_gap
from app.models.schemas.graph import GapSkill, GraphResult, UserGraphResult
from app.repositories import ability_graph_repository, role_repository, role_skill_repository, user_skill_repository
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)


async def get_or_build_graph(db: AsyncSession) -> nx.Graph:
    G = skill_graph.get()
    if not G or G.number_of_nodes() == 0:
        G = await build_graph(db)
    return G


async def get_user_graph(db: AsyncSession, user_id: int) -> UserGraphResult:
    G = await get_or_build_graph(db)
    user_skills = await user_skill_repository.list_by_user(db, user_id)
    user_skill_ids: set[str] = set()
    proficiencies: dict[str, float] = {}
    for us, sk in user_skills:
        sid = str(sk.id)
        user_skill_ids.add(sid)
        proficiencies[sid] = us.proficiency_level
    result = build_user_graph(G, user_skill_ids, proficiencies)
    result.gap_skills = []
    await ability_graph_repository.upsert(db, "USER", user_id, json.dumps(result.model_dump(), ensure_ascii=False))
    await db.commit()
    return result


async def get_job_graph(db: AsyncSession, job_id: int) -> GraphResult:
    G = await get_or_build_graph(db)
    result = build_job_graph(G, set())
    await ability_graph_repository.upsert(db, "JOB", job_id, json.dumps(result.model_dump(), ensure_ascii=False))
    await db.commit()
    return result


async def reload_graph_endpoint(db: AsyncSession) -> None:
    await reload_graph(db)
    logger.info("Graph manually reloaded")


async def analyze_gap_with_role(db: AsyncSession, user_id: int, role_id: int) -> list[GapSkill]:
    role = await role_repository.get_by_id(db, role_id)
    if role is None:
        raise BusinessError(404, "\u89d2\u8272\u4e0d\u5b58\u5728")
    user_skills = await user_skill_repository.list_by_user(db, user_id)
    user_skill_ids = {us.skill_id for us, _ in user_skills}
    role_skills = await role_skill_repository.list_by_role(db, role_id)
    role_skill_map: dict[int, str] = {}
    skill_names: dict[int, str] = {}
    for rs, sk in role_skills:
        role_skill_map[sk.id] = rs.requirement_level
        skill_names[sk.id] = sk.name
    return analyze_skill_gap(user_skill_ids, role_skill_map, skill_names)
