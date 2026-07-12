from __future__ import annotations

from pathlib import Path

import pytest
from tamthuc_rag.embed import HashEmbedder
from tamthuc_rag.ingest import ingest_corpus
from tamthuc_rag.vectorstore import new_index

FIX = Path(__file__).parent / "fixtures" / "sample_corpus.jsonl"


def test_ingest_one_chunk_per_layer() -> None:
    idx = ingest_corpus(FIX)
    # u1 has 3 layers, u2 has 2
    assert len(idx.rows) == 5
    layers_u1 = {c.layer for c, _ in idx.rows.values() if c.unit_id == "u1"}
    assert layers_u1 == {"han", "bach_thoai", "dich"}


def test_filters_and_crosslingual_stub() -> None:
    emb = HashEmbedder()
    idx = ingest_corpus(FIX, embedder=emb)
    # query Vietnamese-ish for dragon unit
    hits = idx.query(emb.embed("thanh long dragon"), k=5)
    assert hits
    assert any(h.unit_id == "u1" for h in hits)
    qimen_only = idx.query(emb.embed("thanh long"), filters={"system": "qimen"})
    assert all(h.system == "qimen" for h in qimen_only)
    han_only = idx.query(emb.embed("青龙"), filters={"layer": "han"})
    assert all(h.layer == "han" for h in han_only)
    assert not any(h.system == "liuren" for h in qimen_only)


def test_idempotent_reingest() -> None:
    emb = HashEmbedder()
    idx = ingest_corpus(FIX, embedder=emb)
    n = len(idx.rows)
    ids = set(idx.rows)
    ingest_corpus(FIX, embedder=emb, index=idx)
    assert len(idx.rows) == n
    assert set(idx.rows) == ids


def test_backend_env_parity() -> None:
    emb = HashEmbedder()
    a = ingest_corpus(FIX, embedder=emb, backend="pgvector")
    b = ingest_corpus(FIX, embedder=emb, backend="chroma")
    qa = [c.chunk_id for c in a.query(emb.embed("thanh long"), k=3)]
    qb = [c.chunk_id for c in b.query(emb.embed("thanh long"), k=3)]
    assert qa == qb


def test_dim_mismatch_raises() -> None:
    emb = HashEmbedder(dim=32)
    idx = new_index(emb)
    ingest_corpus(FIX, embedder=emb, index=idx)
    other = HashEmbedder(name="other", dim=16)
    with pytest.raises(ValueError, match="reindex-required"):
        idx.query(other.embed("x"))
