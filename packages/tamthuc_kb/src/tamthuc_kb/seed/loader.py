"""Load and validate pattern seed files — FR-KB-002."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tamthuc_kb.seed.validation import SeedValidationError, validate_pattern_row


def _repo_patterns_dir() -> Path:
    # packages/tamthuc_kb/src/tamthuc_kb/seed/loader.py -> repo root (5 levels up)
    return Path(__file__).resolve().parents[5] / "data" / "patterns"


def load_system_patterns(system: str, *, root: Path | None = None) -> list[dict[str, Any]]:
    path = (root or _repo_patterns_dir()) / f"{system}.json"
    rows: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    for row in rows:
        validate_pattern_row(row)
        if row["system"] != system:
            raise SeedValidationError(f"{row['id']}: system mismatch file={system}")
    return rows


def load_all_patterns(*, root: Path | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for system in ("qimen", "liuren", "taiyi"):
        out.extend(load_system_patterns(system, root=root))
    ids = [r["id"] for r in out]
    if len(ids) != len(set(ids)):
        raise SeedValidationError("duplicate pattern ids in seed set")
    return out
