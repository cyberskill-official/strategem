"""API versioning + deprecation — FR-API-002."""

from __future__ import annotations

from tamthuc_api.versioning.deprecation import DeprecatedRoute, deprecation_headers
from tamthuc_api.versioning.router import (
    CURRENT_MAJOR,
    SUPPORTED_MAJORS,
    effective_version,
    mount_versioned,
)

__all__ = [
    "CURRENT_MAJOR",
    "SUPPORTED_MAJORS",
    "effective_version",
    "mount_versioned",
    "deprecation_headers",
    "DeprecatedRoute",
]
