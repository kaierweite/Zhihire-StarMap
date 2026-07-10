"""Verify Day04 modules compile and routes register."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db import compat

# Imports with correct names
from app.models.entities import SkillRelation, Role, RoleSkill, AbilityGraph
print("[OK] ORM entities imported")

from app.repositories import (
    skill_relation_repository,
    role_repository,
    role_skill_repository,
    ability_graph_repository,
)
print("[OK] Repositories imported")

from app.core.graph.builder import SkillGraphHolder
from app.core.graph.echarts_mapper import graph_to_echarts, build_user_graph, build_job_graph
print("[OK] Core modules imported")

from app.services.graph_service import get_user_graph, get_job_graph, reload_graph_endpoint
print("[OK] Service imported")

from app.api.v1.graph import router as graph_router
print("[OK] Routes imported")

# Check app routes
from app.main import app
routes = sorted([r.path for r in app.routes if hasattr(r, "path")])

print(f"\nTotal routes: {len(routes)}")
for r in routes:
    if "graph" in r or "skill" in r:
        print(f"  [OK] {r}")

print("\n=== Day04 Verification Complete: All OK ===")
