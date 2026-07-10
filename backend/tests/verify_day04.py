"""Verify Day04 modules compile and routes register."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Apply KingbaseES compat before any imports that create engine
from app.db import compat

# Test all imports
from app.models.entities import *
from app.models.entities import (
    SkillRelation, Role, RoleSkill, AbilityGraph,
)
print("[OK] ORM entities imported")

from app.repositories import (
    skill_relation_repository,
    role_repository,
    role_skill_repository,
    ability_graph_repository,
)
print("[OK] Repositories imported")

from app.core.graph.builder import GraphBuilder
from app.core.graph.echarts_mapper import EChartsMapper
print("[OK] Core modules imported")

from app.services.graph_service import GraphService
print("[OK] Service imported")

from app.api.v1.graph import router as graph_router
print("[OK] Route imported")

# Check app startup
from app.main import app
routes = sorted([r.path for r in app.routes if hasattr(r, "path")])

print(f"\nTotal routes: {len(routes)}")
graph_routes = [r for r in routes if "graph" in r or "skill" in r]
for r in graph_routes:
    print(f"  [OK] {r}")

print("\n=== Day04 Verification Complete ===")
