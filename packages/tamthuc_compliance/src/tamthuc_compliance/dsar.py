"""DSAR contracts AUTH-004 must implement (TASK-LEGAL-002)."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class ExportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: str
    exported_at: str
    packages: list[str] = Field(description="data class names included")
    payload: dict[str, Any]


class ErasureResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: str
    erased_at: str
    crypto_shredded: list[str]
    soft_deleted: list[str]
    retained_audit: bool = True
    idempotent_replay: bool = False


@runtime_checkable
class ExportContract(Protocol):
    def export(self, subject_id: str) -> ExportResult: ...


@runtime_checkable
class ErasureContract(Protocol):
    def erase(self, subject_id: str) -> ErasureResult: ...


class InMemoryDsarStub:
    """Reference stub proving contracts + crypto-shred semantics."""

    def __init__(self) -> None:
        self._erased: set[str] = set()
        self._keys: dict[str, bytes] = {}

    def export(self, subject_id: str) -> ExportResult:
        return ExportResult(
            subject_id=subject_id,
            exported_at="1970-01-01T00:00:00Z",
            packages=["birth_data", "question_text", "charts", "reports"],
            payload={"note": "stub"},
        )

    def erase(self, subject_id: str) -> ErasureResult:
        replay = subject_id in self._erased
        self._erased.add(subject_id)
        # crypto-shred: drop DEK material
        self._keys.pop(subject_id, None)
        return ErasureResult(
            subject_id=subject_id,
            erased_at="1970-01-01T00:00:00Z",
            crypto_shredded=["birth_data", "question_text"],
            soft_deleted=["charts", "reports"],
            retained_audit=True,
            idempotent_replay=replay,
        )
