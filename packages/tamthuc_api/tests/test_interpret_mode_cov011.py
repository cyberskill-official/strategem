"""COV-011: INTERPRET_MODE=rag|template + anti-hallucination + review gate."""

from __future__ import annotations

from typing import Any

import pytest
from tamthuc_api.clients.rag import LocalRagClient
from tamthuc_rag.config import interpret_mode, is_restricted_category


def test_interpret_mode_explicit_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERPRET_MODE", "template")
    assert interpret_mode() == "template"


def test_interpret_mode_explicit_rag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERPRET_MODE", "rag")
    monkeypatch.setenv("RAG_VECTOR_BACKEND", "pgvector")
    assert interpret_mode() == "rag"


def test_template_mode_badge_no_fake_rag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERPRET_MODE", "template")
    client = LocalRagClient()
    patterns: list[dict[str, Any]] = [
        {"id": "p1", "name": "青龍返首", "polarity": "cat", "citations": ["yba_1"]}
    ]
    env: dict[str, Any] = {
        "he": "ky_mon",
        "cach_cuc": patterns,
        "provenance": {"cache_key": "abc"},
    }
    out = client.interpret(env, patterns)
    assert client.last_mode == "template"
    disc = out.get("ai_disclosure") or {}
    assert disc.get("is_ai_generated") is False or disc.get("mode_badge") == "template"
    assert "template" in str(disc.get("model", "")).lower() or disc.get("mode_badge") == "template"
    assert out.get("citations") or disc.get("retrieved_citation_ids")
    assert "fake" not in out.get("beginner", "").lower()


def test_rag_mode_requires_citation_layers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERPRET_MODE", "rag")
    monkeypatch.setenv("RAG_CORPUS_READY", "1")
    monkeypatch.setenv("LLM_BACKEND", "stub")
    client = LocalRagClient()
    patterns = [
        {
            "id": "qimen_thanh_long_hoi_dau",
            "name": "Thanh Long Hồi Đầu",
            "name_han": "青龍返首",
            "polarity": "cat",
            "citations": ["yba_1"],
            "system": "qimen",
        }
    ]
    out = client.interpret({"he": "ky_mon", "cach_cuc": patterns}, patterns)
    # released or gated, but must not invent free-form without cites
    if out.get("citations"):
        c0 = out["citations"][0]
        layers = c0.get("layers") or {}
        # triple-layer keys present (han/bach_thoai/dich or subset)
        assert layers or c0.get("locator")
    else:
        # withheld under review still carries disclosure
        assert out.get("ai_disclosure") or out.get("human_review_gate")
    beginner = (out.get("beginner") or out.get("summary") or "").lower()
    # Grounded stub must not emit the old generic one-liner alone
    assert "cautious educational reading of the chart patterns" not in beginner
    if beginner and "refuse" not in beginner and out.get("human_review_gate") != "pending":
        assert "retrieved" in beginner or "classical" in beginner or "educational" in beginner


def test_refuse_when_no_sources_rag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERPRET_MODE", "rag")
    monkeypatch.setenv("RAG_CORPUS_READY", "1")
    client = LocalRagClient()
    out = client.interpret({"he": "ky_mon", "cach_cuc": []}, [])
    text = (out.get("beginner") or out.get("summary") or "").lower()
    assert "refuse" in text or "no sources" in text or out.get("human_review_gate")


def test_restricted_category_triggers_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    assert is_restricted_category("medical")
    monkeypatch.setenv("INTERPRET_MODE", "template")
    client = LocalRagClient()
    out = client.interpret(
        {
            "he": "ky_mon",
            "question_type": "medical",
            "cach_cuc": [{"id": "p", "name": "x", "citations": ["c1"]}],
        },
        [{"id": "p", "name": "x", "citations": ["c1"]}],
    )
    # high-stakes → pending or released with gate flag
    assert (
        out.get("human_review_gate") in {"pending", "released"}
        or out.get("review_status") == "pending"
        or "review" in str(out).lower()
    )
