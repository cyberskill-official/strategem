from __future__ import annotations

import pytest
from tamthuc_kb.seed.build_patterns import main
from tamthuc_kb.seed.loader import load_all_patterns
from tamthuc_kb.seed.validation import SeedValidationError, validate_pattern_row


def test_seed_coverage_and_citations() -> None:
    rows = load_all_patterns()
    assert 150 <= len(rows) <= 200
    by = {"qimen": 0, "liuren": 0, "taiyi": 0}
    for r in rows:
        by[r["system"]] += 1
        assert r["status"] != "active" or r["citations"]
    assert by["qimen"] >= 90
    assert by["liuren"] >= 30
    assert by["taiyi"] >= 20


def test_build_main() -> None:
    assert main() == 0


def test_active_without_citation_fails() -> None:
    with pytest.raises(SeedValidationError):
        validate_pattern_row(
            {
                "id": "x",
                "system": "qimen",
                "name": "x",
                "conditions": {},
                "polarity": "cat",
                "meaning_classical": "c",
                "meaning_modern": "m",
                "citations": [],
                "version": 1,
                "status": "active",
            }
        )
