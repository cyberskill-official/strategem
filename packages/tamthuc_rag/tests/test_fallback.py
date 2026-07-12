from __future__ import annotations

from tamthuc_rag.fallback import interpret_resilient, rule_based_interpretation
from tamthuc_rag.interpret import interpret
from tamthuc_rag.llm import StubLlm
from tamthuc_rag.resilience import CircuitBreaker, LLMUnavailable, ResilientLLM


class FailLlm:
    model = "fail"

    def complete(self, prompt: str) -> dict:
        raise TimeoutError("timeout")


def test_rule_based_degraded() -> None:
    laso = {
        "he": "ky_mon",
        "cach_cuc": [
            {
                "id": "p1",
                "name": "Pattern One",
                "meaning_modern": "Auspicious timing.",
                "citations": [{"source": "Book", "locator": "1", "citation_id": "c1"}],
            }
        ],
    }
    out = rule_based_interpretation(laso)
    assert out.requires_human_review is True
    assert out.ai_disclosure.degraded is True
    assert out.ai_disclosure.model == "rule-based-fallback"
    assert "Pattern One" in out.beginner
    assert out.confidence < 0.5


def test_circuit_opens() -> None:
    br = CircuitBreaker(fail_threshold=2, cooldown_s=60)
    llm = ResilientLLM(inner=FailLlm(), breaker=br, retries=0)
    for _ in range(2):
        try:
            llm.complete("x")
        except LLMUnavailable:
            pass
    assert br.state.value == "open"
    try:
        llm.complete("y")
        raise AssertionError("should fail open")
    except LLMUnavailable:
        pass


def test_interpret_resilient_falls_back() -> None:
    from tamthuc_rag.fuse import RankedHit

    laso = {"cach_cuc": [{"id": "x", "name": "X", "meaning_modern": "m"}]}
    chunks = [
        RankedHit(
            citation_id="c1",
            unit_id="u1",
            score=1.0,
            system="qimen",
            arms=("vector",),
            layers={"vi": "text"},
        )
    ]
    out = interpret_resilient(laso, interpret, FailLlm(), chunks=chunks)
    assert out.ai_disclosure.degraded is True
