from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Sensitivity(StrEnum):
    sensitive = "sensitive"
    personal = "personal"
    operational = "operational"


class ErasureMechanism(StrEnum):
    crypto_shred = "crypto_shred"
    soft_delete = "soft_delete"
    hard_delete = "hard_delete"
    retain = "retain"  # audit fact of erasure


class RetentionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    data_class: str
    contents: str
    sensitivity: Sensitivity
    lawful_basis: str
    retention: str
    erasure: ErasureMechanism
    log_redaction: Literal["required"] = "required"


DATA_CLASSES: tuple[RetentionPolicy, ...] = (
    RetentionPolicy(
        data_class="birth_data",
        contents="date/time/place of birth (encrypted at rest)",
        sensitivity=Sensitivity.sensitive,
        lawful_basis="consent (Nghi dinh 13/2023 + GDPR Art.6/9)",
        retention="account lifetime + 30d after erasure request",
        erasure=ErasureMechanism.crypto_shred,
    ),
    RetentionPolicy(
        data_class="question_text",
        contents="user question free text",
        sensitivity=Sensitivity.sensitive,
        lawful_basis="consent + contract performance",
        retention="account lifetime + 30d",
        erasure=ErasureMechanism.crypto_shred,
    ),
    RetentionPolicy(
        data_class="charts",
        contents="la so envelope jsonb",
        sensitivity=Sensitivity.personal,
        lawful_basis="contract performance",
        retention="account lifetime",
        erasure=ErasureMechanism.soft_delete,
    ),
    RetentionPolicy(
        data_class="reports",
        contents="AI interpretation + disclosure",
        sensitivity=Sensitivity.personal,
        lawful_basis="contract performance",
        retention="account lifetime",
        erasure=ErasureMechanism.soft_delete,
    ),
    RetentionPolicy(
        data_class="audit",
        contents="access and mutation audit rows",
        sensitivity=Sensitivity.operational,
        lawful_basis="legal obligation / security",
        retention="7 years",
        erasure=ErasureMechanism.retain,
    ),
)


def retention_schedule() -> dict[str, RetentionPolicy]:
    return {p.data_class: p for p in DATA_CLASSES}


def sensitive_classes() -> list[str]:
    return [p.data_class for p in DATA_CLASSES if p.sensitivity == Sensitivity.sensitive]
