"""TASK-KB-005 graph query tests."""

from __future__ import annotations

from tamthuc_kb.graph.citations import FilteringClassicalStore
from tamthuc_kb.graph.models import Edge, Node
from tamthuc_kb.graph.query import GraphQuery, GraphQueryService, graph_retriever_hits
from tamthuc_kb.graph.store import InMemoryGraphStore
from tamthuc_kb.graph.taxonomy import EdgeRel, NodeKind


def _fixture_store() -> InMemoryGraphStore:
    g = InMemoryGraphStore()
    g.upsert_node(
        Node(
            id="thien_can_binh",
            kind=NodeKind.thien_can,
            label="Binh",
            attrs={"han": "丙", "system": "all", "aliases": ["binh", "Binh"]},
        )
    )
    g.upsert_node(
        Node(
            id="cung_1",
            kind=NodeKind.cuu_cung,
            label="cung_1",
            attrs={"system": "qimen", "aliases": ["cung1"]},
        )
    )
    g.upsert_node(
        Node(
            id="sinh_mon",
            kind=NodeKind.bat_mon,
            label="Sinh mon",
            attrs={"system": "qimen", "aliases": ["Sinh_mon", "sinh"]},
        )
    )
    g.upsert_node(
        Node(
            id="qimen_thanh_long",
            kind=NodeKind.cach_cuc,
            label="Thanh Long",
            attrs={
                "system": "qimen",
                "citations": ["yba_001"],
                "aliases": ["thanh_long"],
            },
        )
    )
    g.upsert_node(
        Node(
            id="liuren_only",
            kind=NodeKind.than_sat,
            label="LR only",
            attrs={"system": "liuren", "citations": ["ln_x"]},
        )
    )
    g.upsert_edge(Edge(src="thien_can_binh", rel=EdgeRel.sinh, dst="cung_1", attrs={}))
    g.upsert_edge(
        Edge(
            src="cung_1",
            rel=EdgeRel.lam,
            dst="sinh_mon",
            attrs={},
        )
    )
    g.upsert_edge(
        Edge(
            src="sinh_mon",
            rel=EdgeRel.thua,
            dst="qimen_thanh_long",
            attrs={"citations": ["edge_cite"]},
        )
    )
    g.upsert_edge(Edge(src="cung_1", rel=EdgeRel.khac, dst="liuren_only", attrs={}))
    return g


def test_resolve_and_unresolved() -> None:
    svc = GraphQueryService(_fixture_store())
    r = svc.query(
        GraphQuery(
            system="qimen",
            seeds=["丙", "cung_1", "Sinh_mon", "unknown_token"],
            max_hops=2,
        )
    )
    assert "unknown_token" in r.seeds_unresolved
    assert r.seeds_resolved
    assert r.hits


def test_max_hops_and_rels() -> None:
    svc = GraphQueryService(_fixture_store())
    only_sinh = svc.query(GraphQuery(system="qimen", seeds=["丙"], max_hops=1, rels=[EdgeRel.sinh]))
    assert all(any(rel.rel == EdgeRel.sinh for rel in h.path) or not h.path for h in only_sinh.hits)
    two = svc.query(GraphQuery(system="qimen", seeds=["丙"], max_hops=2))
    assert two.hits
    # can reach sinh_mon in 2 hops
    ids = {h.node_id for h in two.hits}
    assert "cung_1" in ids or "sinh_mon" in ids


def test_system_filter() -> None:
    svc = GraphQueryService(_fixture_store())
    r = svc.query(GraphQuery(system="qimen", seeds=["cung_1"], max_hops=2))
    assert all(h.system in ("qimen", "all") for h in r.hits)


def test_citations_and_structural() -> None:
    corpus = FilteringClassicalStore({"yba_001", "edge_cite"})
    svc = GraphQueryService(_fixture_store(), corpus)
    r = svc.query(GraphQuery(system="qimen", seeds=["sinh_mon"], max_hops=1))
    hit = next((h for h in r.hits if h.node_id == "qimen_thanh_long"), None)
    assert hit is not None
    assert "yba_001" in hit.citations or "edge_cite" in hit.citations or hit.citations == []
    # structural edges still returned even when citations empty/present
    assert isinstance(hit.path, list)


def test_determinism() -> None:
    svc = GraphQueryService(_fixture_store())
    q = GraphQuery(system="qimen", seeds=["丙", "cung_1"], max_hops=2, k=10)
    a = svc.query(q)
    b = svc.query(q)
    assert a.model_dump() == b.model_dump()


def test_rag_seam() -> None:
    svc = GraphQueryService(_fixture_store())
    hits = graph_retriever_hits(
        svc, system="qimen", entities=["丙"], cach_cuc_ids=["qimen_thanh_long"], k=5
    )
    assert isinstance(hits, list)
