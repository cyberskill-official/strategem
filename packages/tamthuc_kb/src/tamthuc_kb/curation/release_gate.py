"""Release gate: every active changed object must be accepted — TASK-KB-004 / RISK-9."""

from __future__ import annotations

from dataclasses import dataclass

from tamthuc_kb.curation.queue import CurationQueue


@dataclass
class ReleaseGateResult:
    passed: bool
    release: str
    unsigned: list[str]


def release_gate(
    release: str,
    *,
    queue: CurationQueue,
    active_objects: dict[tuple[str, str], int],
    last_release_versions: dict[tuple[str, str], int] | None = None,
) -> ReleaseGateResult:
    """Fail if any active object version changed since last release without accept.

    active_objects: (type, id) -> current version
    last_release_versions: (type, id) -> version at last release (default 0)
    """
    prev = last_release_versions or {}
    accepted = queue.accepted_versions()
    unsigned: list[str] = []
    for key, ver in active_objects.items():
        prev_ver = prev.get(key, 0)
        if ver <= prev_ver:
            continue  # unchanged since last release
        if accepted.get(key, 0) < ver:
            unsigned.append(f"{key[0]}:{key[1]}@v{ver}")
    return ReleaseGateResult(passed=not unsigned, release=release, unsigned=sorted(unsigned))
