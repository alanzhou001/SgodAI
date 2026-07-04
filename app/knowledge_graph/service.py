from __future__ import annotations

from app.models import KnowledgeGraphEdge, KnowledgeGraphNode


class KnowledgeGraphService:
    def __init__(
        self,
        nodes: list[KnowledgeGraphNode] | None = None,
        edges: list[KnowledgeGraphEdge] | None = None,
    ) -> None:
        self.nodes = {node.id: node for node in nodes or []}
        self.edges = edges or []

    def add_node(self, node: KnowledgeGraphNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: KnowledgeGraphEdge) -> None:
        self.edges.append(edge)

    def outgoing(self, node_id: str) -> list[KnowledgeGraphEdge]:
        return [edge for edge in self.edges if edge.source_node_id == node_id]

    def impact_path(self, start_node_id: str, max_depth: int = 4) -> list[list[str]]:
        paths: list[list[str]] = []

        def walk(node_id: str, path: list[str], depth: int) -> None:
            if depth >= max_depth:
                paths.append(path)
                return
            next_edges = self.outgoing(node_id)
            if not next_edges:
                paths.append(path)
                return
            for edge in next_edges:
                walk(edge.target_node_id, [*path, edge.target_node_id], depth + 1)

        walk(start_node_id, [start_node_id], 0)
        return paths

