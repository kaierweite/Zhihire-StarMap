"""networkx -> ECharts Sunburst (旭日图) JSON mapper.

Converts the graph node data (category -> skills with proficiency)
into a hierarchical tree structure for ECharts sunburst series.
"""
import networkx as nx
from app.core.graph.builder import CATEGORY_COLORS


def _build_sunburst_item(
    node_id: str, name: str, category: str, level: float, color: str
) -> dict:
    """Build a leaf (skill) node for sunburst.

    The sunburst chart treats ``value`` as the arc extent. For user skills,
    value = proficiency level 0-5; for job skills (no prof), value = 1.
    """
    return {
        "name": name,
        "value": level if level > 0 else 1,
        "id": node_id,
        "itemStyle": {"color": color},
    }


def build_user_sunburst(
    G: nx.Graph, user_skill_ids: set[str], proficiencies: dict[str, float]
) -> dict:
    """Build a sunburst tree for the user's personal ability graph.

    Hierarchy:
      root ("能力图谱")
        +-- category (e.g. "后端")  - coloured by category
        |     +-- skill leaf  - value = proficiency level
        +-- ...

    Only skills the user actually has (``user_skill_ids``) are included.
    """
    return _do_build(G, user_skill_ids, proficiencies)


def build_job_sunburst(G: nx.Graph, job_skill_ids: set[str]) -> dict:
    """Build a sunburst tree for a job's required skills.

    Every leaf gets ``value=1`` so each skill in the same category
    contributes equally to the arc size.
    """
    return _do_build(G, job_skill_ids, proficiencies=None)


def _do_build(
    G: nx.Graph,
    skill_ids: set[str] | None,
    proficiencies: dict[str, float] | None,
) -> dict:
    """Internal helper - shared logic for user & job sunburst."""
    import collections

    cat_groups: dict[str, list[dict]] = collections.defaultdict(list)

    for sid in skill_ids or ():
        if sid not in G:
            continue
        data = G.nodes[sid]
        name = data.get("name", sid)
        category = data.get("category", "通用")
        color = data.get("color", CATEGORY_COLORS.get(category, "#999999"))
        level = proficiencies.get(sid, 0.0) if proficiencies else 1.0

        leaf = _build_sunburst_item(sid, name, category, level, color)
        cat_groups[category].append(leaf)

    children: list[dict] = []
    for cat_name, skills in cat_groups.items():
        color = CATEGORY_COLORS.get(cat_name, "#999999")
        children.append(
            {
                "name": cat_name,
                "itemStyle": {"color": color},
                "children": skills,
            }
        )

    return {
        "name": "能力图谱",
        "children": children,
    }
