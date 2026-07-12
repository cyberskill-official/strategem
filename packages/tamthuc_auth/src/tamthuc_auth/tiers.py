"""Load docs/contracts/rbac-tiers.json as the single quota source of truth."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from tamthuc_auth.rbac import ROLE_CAPABILITIES, Capability, Role


class TierConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Role
    requests_per_day: int | Literal["custom", "unmetered"]
    capabilities: frozenset[Capability]


def _contracts_path() -> Path:
    here = Path(__file__).resolve()
    # packages/tamthuc_auth/src/tamthuc_auth/tiers.py -> repo root
    candidates = [
        here.parents[4] / "docs" / "contracts" / "rbac-tiers.json",
        Path.cwd() / "docs" / "contracts" / "rbac-tiers.json",
    ]
    for c in candidates:
        if c.is_file():
            return c
    raise FileNotFoundError("docs/contracts/rbac-tiers.json not found")


@lru_cache
def load_tier_configs() -> dict[Role, TierConfig]:
    raw: dict[str, Any] = json.loads(_contracts_path().read_text(encoding="utf-8"))
    out: dict[Role, TierConfig] = {}
    for name, body in raw.items():
        role = Role(name)
        caps = frozenset(Capability(c) for c in body["capabilities"])
        rpd = body["requests_per_day"]
        quota: int | Literal["custom", "unmetered"]
        if isinstance(rpd, int):
            quota = rpd
        elif rpd == "custom":
            quota = "custom"
        elif rpd == "unmetered":
            quota = "unmetered"
        else:
            raise ValueError(f"bad requests_per_day for {name}: {rpd}")
        out[role] = TierConfig(role=role, requests_per_day=quota, capabilities=caps)
    return out


def assert_config_parity() -> None:
    """Reject drift between ROLE_CAPABILITIES and rbac-tiers.json."""
    configs = load_tier_configs()
    for role, caps in ROLE_CAPABILITIES.items():
        cfg = configs[role]
        if cfg.capabilities != caps:
            raise AssertionError(
                f"capability drift for {role}: code={sorted(c.value for c in caps)} "
                f"json={sorted(c.value for c in cfg.capabilities)}"
            )


class Principal(BaseModel):
    """Authenticated principal for authorization decisions."""

    model_config = ConfigDict(extra="forbid")
    subject: str
    role: Role
    account_id: str | None = None
    enterprise_quota_override: int | None = Field(
        default=None, description="Enterprise custom requests/day"
    )
    kind: Literal["user", "api_key"] = "user"
