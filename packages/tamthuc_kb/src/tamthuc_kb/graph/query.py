"""Graph traversal query API — TASK-KB-005."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_kb.graph.citations import (
    ClassicalStore,
    NullClassicalStore,
    collect_path_citations,
    resolvable,
)
from tamthuc_kb.graph.resolve import resolve_seeds
from tamthuc_kb.graph.store import GraphStore, InMemoryGraphStore
from tamthuc_kb.graph.taxonomy import EdgeRel, NodeKind

System = Literal["qimen", "liuren", "taiyi", "all"]


class GraphQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: System
    seeds: list[str]
    max_hops: int = 2
    rels: list[EdgeRel] | None = None
    k: int = 12


class GraphRelation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    src: str
    rel: EdgeRel
    dst: str
    src_label: str = ""
    dst_label: str = ""
    attrs: dict[str, Any] = Field(default_factory=dict)
    citations: list[str] = Field(default_factory=list)


class GraphHit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: str
    label: str
    label_han: str | None = None
    kind: NodeKind
    system: System
    path: list[GraphRelation] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    score: float
    dangling_citations: list[str] = Field(default_factory=list)


class GraphQueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hits: list[GraphHit]
    seeds_resolved: list[str]
    seeds_unresolved: list[str]
    filter: dict[str, Any] = Field(default_factory=dict)


class GraphQueryService:
    def __init__(
        self,
        graph: GraphStore | None = None,
        corpus: ClassicalStore | None = None,
    ) -> None:
        self.graph = graph or InMemoryGraphStore()
        self.corpus = corpus or NullClassicalStore()

    def query(self, q: GraphQuery) -> GraphQueryResult:
        resolved, unresolved = resolve_seeds(q.seeds, q.system, self.graph)
        # BFS: state = (node_id, hops, path_edges as list of (edge, from_id))
        from collections import deque

        hit_map: dict[str, tuple[float, list[Any], list[Any], int]] = {}
        # node_id -> (score, path_nodes, path_edges, hops)

        for seed in resolved:
            seed_node = self.graph.get_node(seed)
            if seed_node is None:
                continue
            q_queue: deque[tuple[str, int, list[Any], list[Any]]] = deque()
            q_queue.append((seed, 0, [seed_node], []))
            visited: set[tuple[str, int]] = {(seed, 0)}
            while q_queue:
                nid, hops, pnodes, pedges = q_queue.popleft()
                if hops > 0:
                    score = 1.0 / hops + 0.1 * sum(1 for s in resolved if s == seed)
                    prev = hit_map.get(nid)
                    if prev is None or score > prev[0]:
                        hit_map[nid] = (score, pnodes, pedges, hops)
                if hops >= q.max_hops:
                    continue
                for edge in self.graph.neighbors(nid, None):
                    if q.rels is not None and edge.rel not in q.rels:
                        continue
                    nxt = edge.dst if edge.src == nid else edge.src
                    nnode = self.graph.get_node(nxt)
                    if nnode is None:
                        continue
                    neighbor_sys = str(nnode.attrs.get("system") or "all")
                    if q.system != "all" and neighbor_sys not in (q.system, "all"):
                        continue
                    key = (nxt, hops + 1)
                    if key in visited:
                        continue
                    visited.add(key)
                    q_queue.append((nxt, hops + 1, pnodes + [nnode], pedges + [edge]))

        hits: list[GraphHit] = []
        for nid, (score, pnodes, pedges, _hops) in hit_map.items():
            node = self.graph.get_node(nid)
            if node is None:
                continue
            path: list[GraphRelation] = []
            for e in pedges:
                src_n = self.graph.get_node(e.src)
                dst_n = self.graph.get_node(e.dst)
                ecites = [str(c) for c in (e.attrs or {}).get("citations") or []]
                path.append(
                    GraphRelation(
                        src=e.src,
                        rel=e.rel,
                        dst=e.dst,
                        src_label=src_n.label if src_n else "",
                        dst_label=dst_n.label if dst_n else "",
                        attrs=dict(e.attrs or {}),
                        citations=ecites,
                    )
                )
            cites = collect_path_citations(pnodes, pedges)
            ok, dangling = resolvable(cites, self.corpus)
            nsys_raw = str(node.attrs.get("system") or "all")
            if nsys_raw == "qimen":
                hit_sys: System = "qimen"
            elif nsys_raw == "liuren":
                hit_sys = "liuren"
            elif nsys_raw == "taiyi":
                hit_sys = "taiyi"
            else:
                hit_sys = "all"
            hits.append(
                GraphHit(
                    node_id=node.id,
                    label=node.label,
                    label_han=node.attrs.get("han")
                    if isinstance(node.attrs.get("han"), str)
                    else None,
                    kind=node.kind,
                    system=hit_sys,
                    path=path,
                    citations=ok,
                    score=score,
                    dangling_citations=dangling,
                )
            )
        hits.sort(key=lambda h: (-h.score, h.node_id))
        return GraphQueryResult(
            hits=hits[: q.k],
            seeds_resolved=resolved,
            seeds_unresolved=unresolved,
            filter={"system": q.system, "max_hops": q.max_hops, "k": q.k},
        )


def graph_retriever_hits(
    service: GraphQueryService,
    *,
    system: str,
    entities: list[str],
    cach_cuc_ids: list[str],
    k: int = 12,
) -> list[dict[str, Any]]:
    """TASK-RAG-002 seam: ChartContext → GraphQuery → simplified hits."""
    seeds = list(entities) + list(cach_cuc_ids)
    if system == "qimen":
        sys_lit: System = "qimen"
    elif system == "liuren":
        sys_lit = "liuren"
    elif system == "taiyi":
        sys_lit = "taiyi"
    else:
        sys_lit = "all"
    result = service.query(GraphQuery(system=sys_lit, seeds=seeds, k=k))
    return [
        {
            "node_id": h.node_id,
            "score": h.score,
            "citations": h.citations,
            "label": h.label,
        }
        for h in result.hits
    ]
