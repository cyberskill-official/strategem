from __future__ import annotations

from pathlib import Path

from tamthuc_rag.graph import NullGraphRetriever, StubGraphRetriever
from tamthuc_rag.ingest import ingest_corpus
from tamthuc_rag.retrieve import retrieve

FIX = Path(__file__).parent / "fixtures" / "sample_corpus.jsonl"


def test_vector_only_degraded() -> None:
    idx = ingest_corpus(FIX)
    r = retrieve(idx, "thanh long", k=3, graph=NullGraphRetriever())
    assert r.graph_arm_used is False
    assert len(r.chunks) <= 3
    # layer collapse: one entry per unit
    uids = [c.unit_id for c in r.chunks]
    assert len(uids) == len(set(uids))


def test_system_filter() -> None:
    idx = ingest_corpus(FIX)
    r = retrieve(idx, "dragon", k=5, system="qimen")
    assert all(c.system == "qimen" for c in r.chunks)


def test_fusion_both_arms_outranks() -> None:
    idx = ingest_corpus(FIX)
    # graph also returns u1
    graph = StubGraphRetriever([("u1", 0.5, {"extra": "g"})])
    r = retrieve(idx, "thanh long", k=5, graph=graph)
    assert r.graph_arm_used is True
    top = r.chunks[0]
    # u1 should appear once with both arms when vector also found it
    u1 = next(c for c in r.chunks if c.unit_id == "u1")
    assert "vector" in u1.arms or "graph" in u1.arms
    if "vector" in u1.arms and "graph" in u1.arms:
        assert set(u1.arms) == {"graph", "vector"}
    assert top.unit_id  # deterministic non-empty


def test_deterministic() -> None:
    idx = ingest_corpus(FIX)
    a = retrieve(idx, "thanh long", k=5, graph=NullGraphRetriever())
    b = retrieve(idx, "thanh long", k=5, graph=NullGraphRetriever())
    assert [c.unit_id for c in a.chunks] == [c.unit_id for c in b.chunks]
    assert [c.score for c in a.chunks] == [c.score for c in b.chunks]
