from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError
from tamthuc_kb.corpus.load import load_source_file
from tamthuc_kb.corpus.models import ClassicalUnit, LayerText, UnitType
from tamthuc_kb.corpus.segment import segment_source
from tamthuc_kb.corpus.store import InMemoryCorpusStore

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "data/corpus/qimen/yen_ba_dieu_tau_ca.json"


def test_load_yen_ba_segments() -> None:
    store = InMemoryCorpusStore()
    n = load_source_file(CORPUS, store)
    assert n == 2
    units = store.units_of_source("yen_ba_dieu_tau_ca")
    assert [u.ordinal for u in units] == [0, 1]
    assert all(u.citation_id.startswith("yba_") for u in units)
    assert store.resolve_citation("yba_thien_can_khac_ung_12") is not None
    assert store.get_unit("yen_ba_dieu_tau_ca:0") is not None


def test_idempotent_reload() -> None:
    store = InMemoryCorpusStore()
    load_source_file(CORPUS, store)
    load_source_file(CORPUS, store)
    assert store.unit_count() == 2
    assert store.source_count() == 1


def test_empty_layers_rejected() -> None:
    with pytest.raises(ValidationError):
        ClassicalUnit(
            unit_id="x",
            source_id="s",
            citation_id="yba_x",
            unit_type=UnitType.cau,
            ordinal=0,
            system="qimen",
            layers=LayerText(),
        )


def test_non_monotonic_ordinal_fails() -> None:
    from tamthuc_kb.corpus.models import ClassicalSource

    src = ClassicalSource(source_id="s", title="t", system="qimen", citation_prefix="yba_")
    with pytest.raises(ValueError, match="ordinal"):
        segment_source(
            src,
            [
                {
                    "ordinal": 1,
                    "unit_type": "cau",
                    "citation_id": "yba_a",
                    "dich": "a",
                },
                {
                    "ordinal": 1,
                    "unit_type": "cau",
                    "citation_id": "yba_b",
                    "dich": "b",
                },
            ],
        )


def test_dangling_citations() -> None:
    store = InMemoryCorpusStore()
    load_source_file(CORPUS, store)
    assert store.dangling_citations(["yba_thien_can_khac_ung_12", "missing"]) == ["missing"]


def test_iter_units_schema_shape() -> None:
    store = InMemoryCorpusStore()
    load_source_file(CORPUS, store)
    for u in store.iter_units():
        d = u.model_dump()
        assert "citation_id" in d and "layers" in d
