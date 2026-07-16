"""Roles, capabilities, and the ROLE_CAPABILITIES map (TASK-AUTH-002)."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    free = "Free"
    premium = "Premium"
    enterprise = "Enterprise"
    admin = "Admin"


class Capability(StrEnum):
    calculate_single = "calculate_single"
    calculate_all = "calculate_all"
    timing_optimize = "timing_optimize"
    scenario_compare = "scenario_compare"
    report_generate = "report_generate"
    api_key_auth = "api_key_auth"
    admin_console = "admin_console"


ROLE_CAPABILITIES: dict[Role, frozenset[Capability]] = {
    Role.free: frozenset({Capability.calculate_single, Capability.report_generate}),
    Role.premium: frozenset(
        {
            Capability.calculate_single,
            Capability.calculate_all,
            Capability.timing_optimize,
            Capability.scenario_compare,
            Capability.report_generate,
        }
    ),
    Role.enterprise: frozenset(
        {
            Capability.calculate_single,
            Capability.calculate_all,
            Capability.timing_optimize,
            Capability.scenario_compare,
            Capability.report_generate,
            Capability.api_key_auth,
        }
    ),
    Role.admin: frozenset(set(Capability)),
}

TIER_ORDER: tuple[Role, ...] = (
    Role.free,
    Role.premium,
    Role.enterprise,
    Role.admin,
)


def parse_role(value: str) -> Role:
    """Accept enum value (Free) or lowercase claim (free)."""
    v = value.strip()
    for r in Role:
        if r.value == v or r.name == v.lower():
            return r
    raise ValueError(f"unknown role: {value}")


def role_rank(role: Role) -> int:
    return TIER_ORDER.index(role)
