from __future__ import annotations

from typing import Any


def degrade_calculate_all(
    engines: dict[str, CallableResult],
) -> dict[str, Any]:
    """Return successful engines; mark failed `he` as degraded without failing all."""
    charts: dict[str, Any] = {}
    degraded: list[str] = []
    for he, result in engines.items():
        if result.ok:
            charts[he] = result.value
        else:
            degraded.append(he)
    return {"charts": charts, "degraded": degraded, "partial": bool(degraded)}


class CallableResult:
    def __init__(self, ok: bool, value: Any = None, error: str | None = None) -> None:
        self.ok = ok
        self.value = value
        self.error = error


def fallback_interpretation(
    patterns: list[dict[str, Any]],
    *,
    model: str = "rules-fallback",
) -> dict[str, Any]:
    """Rule-based interpretation when LLM circuit is open."""
    citations: list[str] = []
    for p in patterns:
        citations.extend(p.get("citations") or [])
    return {
        "summary": "Rule-based interpretation (LLM unavailable).",
        "patterns": patterns,
        "citations": citations,
        "ai_disclosure": {
            "model": model,
            "fallback": True,
            "limits": "Deterministic pattern citations only; not a full LLM reading.",
        },
    }
