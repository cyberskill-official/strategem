"""TASK-RAG-005 term-sense expansion tests."""

from __future__ import annotations

from pathlib import Path

from tamthuc_rag.expand import expand_query
from tamthuc_rag.glossary import SenseLayer, TermGlossary

ROOT = Path(__file__).resolve().parents[3]
GLOSS = [
    ROOT / "data" / "glossary" / "qimen_terms.json",
    ROOT / "data" / "glossary" / "liuren_terms.json",
    ROOT / "data" / "glossary" / "taiyi_terms.json",
]


def test_expand_adds_weighted_senses() -> None:
    g = TermGlossary.load(GLOSS)
    eq = expand_query("how does truc phu sit this period", "qimen", g)
    assert eq.original_weight == 1.0
    assert eq.terms
    # original highest
    assert all(t.weight <= eq.original_weight for t in eq.terms)
    forms = {t.form for t in eq.terms}
    assert "acting side" in forms or "initiator" in forms


def test_gia_ta_off_by_default() -> None:
    g = TermGlossary.load(GLOSS)
    eq = expand_query("truc phu reading", "qimen", g)
    assert all(t.layer != SenseLayer.gia_ta for t in eq.terms)


def test_determinism() -> None:
    g = TermGlossary.load(GLOSS)
    a = expand_query("thanh long pattern", "qimen", g)
    b = expand_query("thanh long pattern", "qimen", g)
    assert a.model_dump() == b.model_dump()


def test_max_added_bound() -> None:
    g = TermGlossary.load(GLOSS)
    eq = expand_query("truc phu thanh long", "qimen", g, max_added=2)
    assert len(eq.terms) <= 2


def test_system_filter() -> None:
    g = TermGlossary.load(GLOSS)
    eq = expand_query("nguyen thai stage", "liuren", g)
    assert any(t.term == "nguyen thai" for t in eq.terms)
    # qimen-only query should not pull liuren-only when system=qimen without match
    eq2 = expand_query("random text without terms", "qimen", g)
    assert eq2.terms == []
