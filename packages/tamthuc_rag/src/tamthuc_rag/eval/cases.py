"""Eval cases projected from TASK-KB-002 validation rows — TASK-RAG-006."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

System = Literal["qimen", "liuren", "taiyi"]


class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    version: int
    system: System
    query: str
    conditions: dict[str, Any]
    expected_polarity: str
    meaning_classical: str
    expected_citations: list[str] = Field(default_factory=list)


def _patterns_root() -> Path:
    # packages/tamthuc_rag/src/tamthuc_rag/eval/cases.py -> repo root
    return Path(__file__).resolve().parents[5] / "data" / "patterns"


def _row_to_case(row: dict[str, Any]) -> EvalCase:
    system = str(row["system"])
    if system not in ("qimen", "liuren", "taiyi"):
        raise ValueError(f"unsupported system: {system}")
    name = str(row.get("name") or row["id"])
    query = f"How should I weigh the pattern {name} for this decision window?"
    return EvalCase(
        id=str(row["id"]),
        version=int(row.get("version") or 1),
        system=system,  # type: ignore[arg-type]
        query=query,
        conditions=dict(row.get("conditions") or {}),
        expected_polarity=str(row.get("polarity") or "trung"),
        meaning_classical=str(row.get("meaning_classical") or ""),
        expected_citations=[str(c) for c in (row.get("citations") or [])],
    )


def load_cases(system: System | None = None, *, root: Path | None = None) -> list[EvalCase]:
    """Adapt TASK-KB-002 seeded patterns into EvalCase list (validation_cases projection)."""
    base = root or _patterns_root()
    systems: tuple[str, ...] = (system,) if system else ("qimen", "liuren", "taiyi")
    cases: list[EvalCase] = []
    for sys in systems:
        path = base / f"{sys}.json"
        rows: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            if row.get("status") == "tombstoned":
                continue
            cases.append(_row_to_case(row))
    return cases


def load_cases_from_path(path: Path | str) -> list[EvalCase]:
    """Load committed fixture cases (deterministic CI set)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "cases" in data:
        data = data["cases"]
    return [EvalCase.model_validate(item) for item in data]
