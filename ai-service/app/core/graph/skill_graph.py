"""
能力图谱 — networkx 常驻内存图管理
"""

import networkx as nx


class SkillGraph:
    """技能图谱，基于 networkx 有向图"""

    def __init__(self):
        self._graph: nx.DiGraph = nx.DiGraph()

    @property
    def graph(self) -> nx.DiGraph:
        """获取图对象"""
        return self._graph

    def rebuild(self, skills: list[dict], relations: list[dict]) -> None:
        """
        全量重建图谱

        Args:
            skills: 技能节点列表 [{"id": 1, "name": "Python", "category": "语言"}, ...]
            relations: 关系列表 [{"source_id": 1, "target_id": 2, "relation_type": "related", "weight": 1.0}, ...]
        """
        self._graph.clear()
        for skill in skills:
            self._graph.add_node(
                skill["id"],
                name=skill.get("name", ""),
                category=skill.get("category", ""),
            )
        for rel in relations:
            self._graph.add_edge(
                rel["source_id"],
                rel["target_id"],
                relation_type=rel.get("relation_type", "related"),
                weight=rel.get("weight", 1.0),
            )

    def add_skills(self, skills: list[dict]) -> None:
        """增量添加技能节点"""
        for skill in skills:
            self._graph.add_node(
                skill["id"],
                name=skill.get("name", ""),
                category=skill.get("category", ""),
            )

    def add_relations(self, relations: list[dict]) -> None:
        """增量添加关系"""
        for rel in relations:
            self._graph.add_edge(
                rel["source_id"],
                rel["target_id"],
                relation_type=rel.get("relation_type", "related"),
                weight=rel.get("weight", 1.0),
            )

    def get_node_count(self) -> int:
        """节点数量"""
        return self._graph.number_of_nodes()

    def get_edge_count(self) -> int:
        """边数量"""
        return self._graph.number_of_edges()

    def to_echarts_json(self) -> dict:
        """
        导出为 ECharts 图谱 JSON 格式

        Returns:
            {"nodes": [...], "edges": [...]}
        """
        nodes = []
        for node_id, data in self._graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "name": data.get("name", str(node_id)),
                "category": data.get("category", ""),
            })
        edges = []
        for src, tgt, data in self._graph.edges(data=True):
            edges.append({
                "source": src,
                "target": tgt,
                "relationType": data.get("relation_type", "related"),
                "weight": data.get("weight", 1.0),
            })
        return {"nodes": nodes, "edges": edges}


# 全局单例
skill_graph = SkillGraph()
