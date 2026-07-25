"""Local classical corpus retrieval for default RAG path."""

from __future__ import annotations

from tamthuc_rag.llm import StubLlm
from tamthuc_rag.local_corpus import load_corpus_units, load_pattern_glosses, retrieve_classical


def test_corpus_and_patterns_load() -> None:
    units = load_corpus_units()
    glosses = load_pattern_glosses()
    assert units or glosses  # repo ships at least one of these
    assert glosses  # seeded patterns always present in workspace


def test_retrieve_by_pattern_name() -> None:
    hits = retrieve_classical(
        "Thanh Long 青龍",
        system="qimen",
        k=5,
        pattern_ids=["qimen_thanh_long_hoi_dau"],
        citation_ids=["yba_khac_ung_1"],
    )
    assert hits
    assert any(h.layers for h in hits)
    # Prefer substantive gloss / classical text over bare pattern-name stubs
    blob = " ".join(" ".join(h.layers.values()) for h in hits).lower()
    assert "classical" in blob or "educational" in blob or "青" in blob or "thanh" in blob


def test_stub_llm_grounded_not_generic() -> None:
    prompt = (
        "## La so (read-only)\n{'he': 'ky_mon'}\n\n"
        "## Retrieved sources\n"
        "- yba_1: han=青龍返首 | dich=Azure dragon returns\n"
        "- kmdg_1: bach_thoai=Educational decision-support reading\n"
    )
    out = StubLlm().complete(prompt)
    assert "cautious educational reading of the chart patterns" not in out["beginner"].lower()
    assert "yba_1" in out["beginner"] or "青龍" in out["beginner"] or "Azure" in out["beginner"]
    assert out["recommendations"]
    assert out["recommendations"][0]["citations"]
