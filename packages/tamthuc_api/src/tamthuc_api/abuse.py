"""Abuse detection — FR-API-003."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class AbuseSignal(str, Enum):
    velocity_spike = "velocity_spike"
    credential_stuffing = "credential_stuffing"
    probing = "probing"


@dataclass
class AbuseVerdict:
    signal: AbuseSignal | None
    action: Literal["allow", "throttle", "lockout", "flag"]
    window_s: int | None = None


@dataclass
class RequestEvent:
    path: str
    status: int | None = None
    failed_login: bool = False
    malformed: bool = False


@dataclass
class AbuseDetector:
    """In-memory graduated abuse detector (per process)."""

    failed_logins_by_ip: dict[str, int] = field(default_factory=dict)
    requests_by_principal: dict[str, int] = field(default_factory=dict)
    malformed_by_ip: dict[str, int] = field(default_factory=dict)
    velocity_threshold: int = 30
    stuffing_threshold: int = 10
    probing_threshold: int = 15

    def evaluate(
        self,
        principal_id: str | None,
        source_ip: str,
        event: RequestEvent,
    ) -> AbuseVerdict:
        if principal_id:
            self.requests_by_principal[principal_id] = (
                self.requests_by_principal.get(principal_id, 0) + 1
            )
            if self.requests_by_principal[principal_id] > self.velocity_threshold:
                return AbuseVerdict(AbuseSignal.velocity_spike, "throttle", 60)

        if event.failed_login:
            self.failed_logins_by_ip[source_ip] = (
                self.failed_logins_by_ip.get(source_ip, 0) + 1
            )
            n = self.failed_logins_by_ip[source_ip]
            if n >= self.stuffing_threshold:
                return AbuseVerdict(AbuseSignal.credential_stuffing, "lockout", 300)
            if n >= self.stuffing_threshold // 2:
                return AbuseVerdict(AbuseSignal.credential_stuffing, "throttle", 60)

        if event.malformed or (event.status is not None and event.status >= 400):
            self.malformed_by_ip[source_ip] = self.malformed_by_ip.get(source_ip, 0) + 1
            if self.malformed_by_ip[source_ip] >= self.probing_threshold:
                return AbuseVerdict(AbuseSignal.probing, "flag", None)

        return AbuseVerdict(None, "allow", None)
