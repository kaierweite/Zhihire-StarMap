"""知识图谱构建器。
基于 networkx 构建常驻内存的技能关系图。
"""
import logging
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import skill_repository, skill_relation_repository

logger = logging.getLogger(__name__)

CATEGORY_COLORS: dict[str, str] = {
    "\u540e\u7aef": "#5470C6",
    "\u524d\u7aef": "#91CC75",
    "\u6d4b\u8bd5": "#FAC858",
    "\u8fd0\u7ef4": "#EE6666",
    "\u6570\u636e": "#73C0DE",
    "\u7b97\u6cd5": "#3BA272",
    "\u79fb\u52a8\u7aef": "#FC8452",
    "\u901a\u7528": "#9A60B4",
}


class SkillGraphHolder:
    """持有常驻内存 networkx 图对象的单例容器。"""

    def __init__(self) -> None:
        self._graph: nx.Graph | None = None

    def get(self) -> nx.Graph:
        if self._graph is None:
            return nx.Graph()
        return self._graph

    def set(self, graph: nx.Graph) -> None:
        self._graph = graph

    def clear(self) -> None:
        self._graph = None


skill_graph = SkillGraphHolder()


async def build_graph(db: AsyncSession) -> nx.Graph:
    """从数据库加载技能与关系数据，构建 networkx 图。"""
    G = nx.Graph()
    all_skills = await skill_repository.list_active(db)
    for sk in all_skills:
        color = CATEGORY_COLORS.get(sk.category or "", "#999999")
        G.add_node(str(sk.id), name=sk.name, category=sk.category or "\u901a\u7528", color=color)
    logger.info("Loaded %d skills into graph", len(all_skills))

    all_relations = await skill_relation_repository.list_active(db)
    for rel in all_relations:
        a_id = str(rel.skill_id_a)
        b_id = str(rel.skill_id_b)
        if G.has_node(a_id) and G.has_node(b_id):
            G.add_edge(a_id, b_id, relation_type=rel.relation_type, weight=rel.weight)
    logger.info("Loaded %d relations into graph", len(all_relations))

    # Auto-generate edges for skills in the same category (INCLUDES)
    # This ensures the graph has connections even without manual skill_relation entries
    from collections import defaultdict
    cat_groups: dict[str, list[str]] = defaultdict(list)
    for sk in all_skills:
        cat = sk.category or "通用"
        cat_groups[cat].append(str(sk.id))

    auto_edges = 0
    for cat, skill_ids in cat_groups.items():
        if len(skill_ids) <= 1:
            continue
        # Connect skills within the same category with INCLUDES edges
        # Use a hub approach: connect first skill to all others in same category
        hub = skill_ids[0]
        for sid in skill_ids[1:]:
            if not G.has_edge(hub, sid):
                G.add_edge(hub, sid, relation_type="INCLUDES", weight=0.6)
                auto_edges += 1

    logger.info("Auto-generated %d INCLUDES edges (same-category)", auto_edges)

    skill_graph.set(G)
    return G


async def reload_graph(db: AsyncSession) -> nx.Graph:
    """重建图谱并覆盖单例。"""
    return await build_graph(db)
