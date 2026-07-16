"""GraphStore protocol + in-memory default — TASK-KB-001."""

from __future__ import annotations

from typing import Protocol

from tamthuc_kb.graph.models import Edge, Node
from tamthuc_kb.graph.taxonomy import EdgeRel, NodeKind


class GraphStore(Protocol):
    def upsert_node(self, node: Node) -> None: ...
    def upsert_edge(self, edge: Edge) -> None: ...
    def get_node(self, node_id: str) -> Node | None: ...
    def neighbors(self, node_id: str, rel: EdgeRel | None = None) -> list[Edge]: ...
    def nodes_by_kind(self, kind: NodeKind) -> list[Node]: ...


class InMemoryGraphStore:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def upsert_node(self, node: Node) -> None:
        # validation happens in Node model
        self.nodes[node.id] = node

    def upsert_edge(self, edge: Edge) -> None:
        if edge.src not in self.nodes or edge.dst not in self.nodes:
            raise ValueError("edge endpoints must exist")
        # replace identical triple
        self.edges = [
            e
            for e in self.edges
            if not (e.src == edge.src and e.rel == edge.rel and e.dst == edge.dst)
        ]
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    def neighbors(self, node_id: str, rel: EdgeRel | None = None) -> list[Edge]:
        out = [e for e in self.edges if e.src == node_id or e.dst == node_id]
        if rel is not None:
            out = [e for e in out if e.rel == rel]
        return out

    def nodes_by_kind(self, kind: NodeKind) -> list[Node]:
        return [n for n in self.nodes.values() if n.kind == kind]
