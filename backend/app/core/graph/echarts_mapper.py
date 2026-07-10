"""networkx \u2192 ECharts \u5173\u7cfb\u56fe JSON \u6620\u5c04\u5668。
"""
import networkx as nx
from app.models.schemas.graph import GraphEdge, GraphNode, GraphResult, UserGraphResult


def _relation_line_style(rel_type: str) -> dict:
    styles = {
        "PREREQUISITE": {"color": "#5470C6", "width": 2, "type": "solid", "curveness": 0.1},
        "INCLUDES": {"color": "#91CC75", "width": 2, "type": "dashed", "curveness": 0.2},
        "SIMILAR": {"color": "#FAC858", "width": 1.5, "type": "dotted", "curveness": 0.15},
        "COMPLEMENTARY": {"color": "#9A60B4", "width": 2, "type": "solid", "curveness": 0.3},
    }
    return styles.get(rel_type, {"color": "#ccc", "width": 1, "type": "solid"})


def build_user_graph(G: nx.Graph, user_skill_ids: set[str], user_proficiencies: dict[str, float]) -> UserGraphResult:
    """为用户构建含熟练度和缺口标记的子图。"""
    nodes: list[dict] = []
    edges: list[dict] = []
    subgraph = G.subgraph(user_skill_ids)

    for node_id, data in subgraph.nodes(data=True):
        name = data.get("name", node_id)
        category = data.get("category", "\u901a\u7528")
        level = user_proficiencies.get(node_id, 0.0)
        color = data.get("color", "#999999")
        symbol_size = max(15, int(level * 8 + 15))
        nodes.append({
            "id": node_id, "name": name, "category": category,
            "level": level, "symbolSize": symbol_size,
            "itemStyle": {"color": color},
            "label": {"show": True, "formatter": name},
        })

    for u, v, data in subgraph.edges(data=True):
        rel_type = data.get("relation_type", "SIMILAR")
        weight = data.get("weight", 0.5)
        edges.append({
            "source": u, "target": v, "relation_type": rel_type,
            "weight": weight, "lineStyle": _relation_line_style(rel_type),
        })

    return UserGraphResult(
        nodes=[GraphNode(**n) for n in nodes],
        edges=[GraphEdge(**e) for e in edges],
    )


def build_job_graph(G: nx.Graph, job_skill_ids: set[str]) -> GraphResult:
    """为岗位构建技能图谱。"""
    nodes: list[dict] = []
    edges: list[dict] = []
    subgraph = G.subgraph(job_skill_ids)

    for node_id, data in subgraph.nodes(data=True):
        name = data.get("name", node_id)
        category = data.get("category", "\u901a\u7528")
        color = data.get("color", "#999999")
        nodes.append({
            "id": node_id, "name": name, "category": category,
            "symbolSize": 30, "itemStyle": {"color": color},
            "label": {"show": True, "formatter": name},
        })

    for u, v, data in subgraph.edges(data=True):
        rel_type = data.get("relation_type", "SIMILAR")
        weight = data.get("weight", 0.5)
        edges.append({
            "source": u, "target": v, "relation_type": rel_type,
            "weight": weight, "lineStyle": _relation_line_style(rel_type),
        })

    return GraphResult(
        nodes=[GraphNode(**n) for n in nodes],
        edges=[GraphEdge(**e) for e in edges],
    )
