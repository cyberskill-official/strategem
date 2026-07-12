from __future__ import annotations

from tamthuc_api.resilience.degradation import (
    CallableResult,
    degrade_calculate_all,
    fallback_interpretation,
)


def test_partial_engines() -> None:
    out = degrade_calculate_all(
        {
            "ky_mon": CallableResult(True, {"ok": 1}),
            "luc_nham": CallableResult(False, error="boom"),
        }
    )
    assert "ky_mon" in out["charts"]
    assert out["degraded"] == ["luc_nham"]
    assert out["partial"] is True


def test_llm_fallback_has_disclosure_and_citations() -> None:
    fb = fallback_interpretation(
        [{"id": "p1", "citations": ["yba_1"], "name": "x"}],
    )
    assert fb["ai_disclosure"]["fallback"] is True
    assert "yba_1" in fb["citations"]
    assert fb["summary"]
