"""Deterministic scoring over cach_cuc — FR-STRAT-001."""

from __future__ import annotations

from typing import Any


def score_envelope(
    envelope: dict[str, Any],
) -> tuple[float, list[dict[str, Any]], list[dict[str, Any]]]:
    """Score = sum(cat scores) - sum(hung scores). Explainable by listed patterns."""
    cat: list[dict[str, Any]] = []
    hung: list[dict[str, Any]] = []
    total = 0.0
    for cc in envelope.get("cach_cuc") or []:
        if not isinstance(cc, dict):
            continue
        pol = str(cc.get("polarity", "trung")).lower()
        s = float(cc.get("score") or 0.5)
        item = {
            "id": cc.get("id"),
            "name": cc.get("name"),
            "score": s,
            "citations": cc.get("citations") or [],
            "cung": cc.get("cung"),
        }
        if pol == "cat":
            cat.append(item)
            total += s
        elif pol == "hung":
            hung.append(item)
            total -= s
    return total, cat, hung
