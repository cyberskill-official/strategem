"""Validate pattern seed rows — TASK-KB-002."""

from __future__ import annotations

from typing import Any


class SeedValidationError(ValueError):
    pass


REQUIRED = (
    "id",
    "system",
    "name",
    "conditions",
    "polarity",
    "meaning_classical",
    "meaning_modern",
    "citations",
    "version",
    "status",
)


def validate_pattern_row(row: dict[str, Any]) -> None:
    rid = row.get("id", "<missing-id>")
    for k in REQUIRED:
        if k not in row:
            raise SeedValidationError(f"{rid}: missing field {k}")
    if row["status"] == "active" and not row.get("citations"):
        raise SeedValidationError(f"{rid}: active pattern requires citations")
    if row["system"] not in ("qimen", "liuren", "taiyi"):
        raise SeedValidationError(f"{rid}: bad system {row['system']}")
    if row["polarity"] not in ("cat", "hung", "trung"):
        raise SeedValidationError(f"{rid}: bad polarity")
    if not isinstance(row["conditions"], dict):
        raise SeedValidationError(f"{rid}: conditions must be object")
    modern = str(row["meaning_modern"]).lower()
    banned = ("guaranteed", "will definitely", "diagnose", "prescribe")
    if any(b in modern for b in banned):
        raise SeedValidationError(f"{rid}: meaning_modern uses banned verdict language")
