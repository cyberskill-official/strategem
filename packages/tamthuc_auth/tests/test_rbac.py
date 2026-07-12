"""FR-AUTH-002 RBAC / tiers / API keys."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tamthuc_auth.apikey import ApiKeyStore, issue_api_key, resolve_api_key, revoke_api_key
from tamthuc_auth.rbac import ROLE_CAPABILITIES, Capability, Role, parse_role, role_rank
from tamthuc_auth.scopes import (
    check_capability,
    has_capability,
    quota_for,
)
from tamthuc_auth.tiers import Principal, assert_config_parity, load_tier_configs


def test_roles_closed_set() -> None:
    assert {r.value for r in Role} == {"Free", "Premium", "Enterprise", "Admin"}


def test_config_parity_with_json() -> None:
    assert_config_parity()
    path = Path("docs/contracts/rbac-tiers.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    for name, body in raw.items():
        role = Role(name)
        assert ROLE_CAPABILITIES[role] == frozenset(Capability(c) for c in body["capabilities"])


def test_require_capability_free_vs_premium() -> None:
    free = Principal(subject="u1", role=Role.free)
    prem = Principal(subject="u2", role=Role.premium)
    with pytest.raises(PermissionError):
        check_capability(free, Capability.calculate_all)
    check_capability(prem, Capability.calculate_all)
    assert has_capability(Role.free, Capability.calculate_single)
    assert not has_capability(Role.free, Capability.api_key_auth)


def test_quota_for_each_tier() -> None:
    assert quota_for(Principal(subject="a", role=Role.free)) == 100
    assert quota_for(Principal(subject="b", role=Role.premium)) == 5000
    assert (
        quota_for(Principal(subject="c", role=Role.enterprise, enterprise_quota_override=12_000))
        == 12_000
    )
    assert quota_for(Principal(subject="d", role=Role.admin)) == "unmetered"


def test_tier_ordering() -> None:
    assert role_rank(Role.free) < role_rank(Role.premium)
    assert role_rank(Role.premium) < role_rank(Role.enterprise)
    assert role_rank(Role.enterprise) < role_rank(Role.admin)
    # Enterprise passes Premium gate
    assert role_rank(Role.enterprise) >= role_rank(Role.premium)


def test_api_key_issue_resolve_revoke_hashed() -> None:
    store = ApiKeyStore()
    key_id, raw = issue_api_key("acct-1", custom_quota=999, store=store)
    assert raw.startswith("tt_")
    assert not store.stored_plaintext_present()
    # only hash stored
    rec = store._by_id[key_id]
    assert rec.key_hash != raw
    assert len(rec.key_hash) == 64

    p = resolve_api_key(raw, store=store)
    assert p is not None
    assert p.role == Role.enterprise
    assert p.enterprise_quota_override == 999
    assert p.kind == "api_key"

    revoke_api_key(key_id, store=store)
    assert resolve_api_key(raw, store=store) is None


def test_parse_role_accepts_claim_case() -> None:
    assert parse_role("free") == Role.free
    assert parse_role("Free") == Role.free
    assert parse_role("Premium") == Role.premium


def test_load_tier_configs_quotas() -> None:
    cfgs = load_tier_configs()
    assert cfgs[Role.free].requests_per_day == 100
    assert cfgs[Role.premium].requests_per_day == 5000
    assert cfgs[Role.enterprise].requests_per_day == "custom"
    assert cfgs[Role.admin].requests_per_day == "unmetered"
