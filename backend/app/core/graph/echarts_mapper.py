"""networkx -> ECharts guanxi tu JSON. All computed fields filled by backend.
"""
import networkx as nx
from app.core.graph.builder import CATEGORY_COLORS
from app.models.schemas.graph import CategoryItem, GraphEdge, GraphNode, GraphResult, UserGraphResult


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(v, hi))


def _compute_level_label(level: float) -> str:
    """Map 0-5 proficiency to human label. Clamped by backend so frontend doesn't need thresholds."""
    if level <= 0.0:
        return "none"
    if level < 2.0:
        return "beginner"
    if level < 4.0:
        return "intermediate"
    return "advanced"


def _relation_line_style(rel_type: str) -> dict:
    styles = {
        "PREREQUISITE": {"color": "#5470C6", "width": 2, "type": "solid", "curveness": 0.1},
        "INCLUDES": {"color": "#91CC75", "width": 2, "type": "dashed", "curveness": 0.2},
        "SIMILAR": {"color": "#FAC858", "width": 1.5, "type": "dotted", "curveness": 0.15},
        "COMPLEMENTARY": {"color": "#9A60B4", "width": 2, "type": "solid", "curveness": 0.3},
    }
    return styles.get(rel_type, {"color": "#ccc", "width": 1, "type": "solid"})


def _build_categories() -> list[CategoryItem]:
    """Build category list from builder constants so frontend doesn't need a copy."""
    return [CategoryItem(name=k, color=v) for k, v in CATEGORY_COLORS.items()]


def _build_nodes(G: nx.Graph, user_proficiencies: dict[str, float] | None = None) -> list[dict]:
    nodes = []
    for node_id, data in G.nodes(data=True):
        name = data.get("name", node_id)
        category = data.get("category", "tongyong")
        color = data.get("color", "#999999")
        level = user_proficiencies.get(node_id, 0.0) if user_proficiencies else 0.0
        symbol_size = int(_clamp(level * 8 + 15, 15, 60)) if user_proficiencies else 30
        nodes.append({
            "id": node_id,
            "name": name,
            "category": category,
            "level": level,
            "level_label": _compute_level_label(level),
            "symbolSize": symbol_size,
            "itemStyle": {"color": color},
            "label": {"show": True, "formatter": name},
        })
    return nodes


def _build_edges(G: nx.Graph) -> list[dict]:
    edges = []
    for u, v, data in G.edges(data=True):
        rel_type = data.get("relation_type", "SIMILAR")
        weight = data.get("weight", 0.5)
        edges.append({
            "source": u,
            "target": v,
            "relation_type": rel_type,
            "weight": weight,
            "lineStyle": _relation_line_style(rel_type),
        })
    return edges


def graph_to_echarts(G: nx.Graph) -> dict:
    return {
        "nodes": _build_nodes(G),
        "edges": _build_edges(G),
        "state": "empty" if G.number_of_nodes() == 0 else "ready",
        "categories": [c.model_dump() for c in _build_categories()],
    }


def build_user_graph(G: nx.Graph, user_skill_ids: set[str], user_proficiencies: dict[str, float]) -> UserGraphResult:
    subgraph = G.subgraph(user_skill_ids) if user_skill_ids else nx.Graph()
    nodes = _build_nodes(subgraph, user_proficiencies)
    edges = _build_edges(subgraph)
    result = UserGraphResult(
        nodes=[GraphNode(**n) for n in nodes],
        edges=[GraphEdge(**e) for e in edges],
        state="empty" if len(nodes) == 0 else "ready",
        categories=_build_categories(),
    )
    return result


def build_job_graph(G: nx.Graph, job_skill_ids: set[str], importance: dict[str, float] | None = None, required_level: dict[str, str] | None = None) -> GraphResult:
    subgraph = G.subgraph(job_skill_ids) if job_skill_ids else nx.Graph()
    nodes = []
    for node_id, data in subgraph.nodes(data=True):
        name = data.get("name", node_id)
        category = data.get("category", "tongyong")
        color = data.get("color", "#999999")
        imp = importance.get(node_id, 3.0) if importance else 3.0
        req_level = required_level.get(node_id, "NICE") if required_level else "NICE"
        nodes.append({
            "id": node_id,
            "name": name,
            "category": category,
            "level": 0.0,
            "level_label": "none",
            "symbolSize": int(_clamp(imp * 8 + 15, 15, 60)),
            "itemStyle": {"color": color},
            "label": {"show": True, "formatter": name},
            "importance": imp,
            "required_level": req_level,
        })
    edges = _build_edges(subgraph)
    return GraphResult(
        nodes=[GraphNode(**n) for n in nodes],
        edges=[GraphEdge(**e) for e in edges],
        state="empty" if len(nodes) == 0 else "ready",
        categories=_build_categories(),
    )
