from __future__ import annotations

import copy

from tamthuc_rag.fuse import RankedHit
from tamthuc_rag.interpret import interpret
from tamthuc_rag.llm import StubLlm


def test_interpret_happy_path_and_readonly() -> None:
    laso = {"he": "ky_mon", "ban": {"x": 1}, "cach_cuc": []}
    original = copy.deepcopy(laso)
    chunks = [
        RankedHit(
            score=1.0,
            unit_id="u1",
            citation_id="yba_1",
            system="qimen",
            arms=("vector",),
            layers={"han": "青龙", "dich": "azure dragon"},
            unit_type="dieu",
        )
    ]
    out = interpret(laso, chunks, llm=StubLlm())
    assert out.ai_disclosure.is_ai_generated
    assert out.ai_disclosure.model
    assert "yba_1" in out.ai_disclosure.retrieved_citation_ids
    assert out.citations
    assert laso == original  # read-only


def test_empty_retrieval() -> None:
    out = interpret({"he": "ky_mon"}, [])
    assert out.confidence == 0.0
    assert out.requires_human_review
    assert "Insufficient" in out.beginner or "insufficient" in out.beginner.lower()


def test_fabricated_citation_stripped() -> None:
    class BadLlm:
        model = "bad"

        def complete(self, prompt: str) -> dict[str, object]:
            return {
                "beginner": "ok reading",
                "expert": "ok expert",
                "recommendations": [
                    {"text": "claim", "citations": ["fake_id"]},
                    {"text": "good", "citations": ["yba_1"]},
                ],
            }

    chunks = [
        RankedHit(
            score=1.0,
            unit_id="u1",
            citation_id="yba_1",
            system="qimen",
            arms=("vector",),
            layers={"dich": "x"},
        )
    ]
    out = interpret({"he": "ky_mon"}, chunks, llm=BadLlm())
    assert all(all(c in {"yba_1"} for c in r["citations"]) for r in out.recommendations)
    assert not any("fake_id" in str(r) for r in out.recommendations)
