---
id: FR-AUTH-002
title: "RBAC tiers - Free / Premium / Enterprise / Admin roles + per-tier capability and rate-limit quota config (Free 100/day, Premium 5000/day, Enterprise custom), the single source FR-API-003 enforces, Enterprise API-key auth"
module: AUTH
priority: MUST
status: ready_to_implement
phase: P0
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-36, Grok-12, strategy 4.4]
related_frs: [FR-AUTH-001, FR-API-001, FR-API-003, FR-PLAT-007]
depends_on: [FR-AUTH-001]
blocks: [FR-API-003, FR-PLAT-007]
new_paths:
  - packages/tamthuc_auth/tamthuc_auth/rbac.py
  - packages/tamthuc_auth/tamthuc_auth/tiers.py
  - packages/tamthuc_auth/tamthuc_auth/scopes.py
  - packages/tamthuc_auth/tamthuc_auth/apikey.py
  - packages/tamthuc_auth/tests/test_rbac.py
  - docs/contracts/rbac-tiers.json
---

## §1 - Description (BCP-14 normative)

This FR defines authorization: the four roles a user can hold, the capabilities each role grants, and the per-tier rate-limit quotas that FR-API-003 enforces. It extends the `tamthuc_auth` package. It owns the tier and quota configuration as a single source of truth; it does NOT implement the counting or the 429 responses (that is FR-API-003) nor issue tokens (FR-AUTH-001).

The role set SHALL be the closed enum Free, Premium, Enterprise, Admin. Each role SHALL map to a capability set (which endpoints and features it may reach) and, for the request-serving tiers, to a rate-limit quota. The quotas SHALL be: Free 100 requests/day, Premium 5000 requests/day, Enterprise custom (a per-account override), with Admin unmetered for operational use. Tier and quota configuration SHALL live in one machine-readable artifact (`docs/contracts/rbac-tiers.json`) that both this package and FR-API-003 read, so the limit a request is judged against and the limit the product advertises are the same number in one place.

Authorization SHALL be expressed as FastAPI dependencies (`require_tier`, `require_role`, `require_capability`) that read the `tier` claim from the FR-AUTH-001 access token and reject an under-privileged request with a 403 in the FR-API-001 error envelope. Enterprise clients SHALL additionally be able to authenticate machine-to-machine with an API key (distinct from a user JWT); an Enterprise API key SHALL resolve to an Enterprise-tier principal with its account's custom quota. A tier change SHALL take effect on the next token issuance or refresh, and SHALL be an auditable action (FR-API-004).

## §2 - Why this design (rationale for humans)

Tiering is both the product's commercial model and a safety control. The commercial side is obvious - Free, Premium, and Enterprise are the plan ladder (Grok-36). The safety side is why it lives in AUTH and not only in billing: the rate-limit quota is the primary abuse and cost control on an endpoint that calls an LLM, and the tier a user holds is exactly the input the limiter needs (Grok-12). Keeping the quota numbers in one config that both AUTH and API-003 read prevents the classic drift where the enforced limit and the documented limit diverge and a user is throttled at a number no page mentions.

Separating capability (what you may do) from quota (how much) keeps the two axes independent: Admin is unmetered but that is a role capability, not a huge quota; Enterprise has a custom quota but standard capabilities plus API-key auth. Expressing authorization as dependencies rather than scattered inline checks means every protected route declares its requirement in its signature, which is auditable and hard to forget. Enterprise API-key auth is a deliberate second principal type because machine clients should not carry a user's refresh token; a scoped, revocable key that resolves to the account's tier is the right grant for server-to-server use.

## §3 - Contract (schema / types / config)

### Roles and capabilities (`tamthuc_auth/rbac.py`)

```python
class Role(str, Enum): free = "Free"; premium = "Premium"; enterprise = "Enterprise"; admin = "Admin"

class Capability(str, Enum):
    calculate_single = "calculate_single"     # /calculate/{qimen,liuren,taiyi}
    calculate_all = "calculate_all"           # /calculate/all (cross-system)
    timing_optimize = "timing_optimize"       # /timing/optimize (STRAT)
    scenario_compare = "scenario_compare"     # /scenario/compare (STRAT)
    report_generate = "report_generate"
    api_key_auth = "api_key_auth"             # machine-to-machine
    admin_console = "admin_console"

ROLE_CAPABILITIES: dict[Role, set[Capability]]   # e.g. Free lacks calculate_all + api_key_auth
```

### Tier quota config (`docs/contracts/rbac-tiers.json`, read by this package and FR-API-003)

```json
{
  "Free":       { "requests_per_day": 100,  "capabilities": ["calculate_single", "report_generate"] },
  "Premium":    { "requests_per_day": 5000, "capabilities": ["calculate_single", "calculate_all",
                                                              "timing_optimize", "scenario_compare", "report_generate"] },
  "Enterprise": { "requests_per_day": "custom", "capabilities": ["calculate_single", "calculate_all",
                                                              "timing_optimize", "scenario_compare",
                                                              "report_generate", "api_key_auth"] },
  "Admin":      { "requests_per_day": "unmetered", "capabilities": ["admin_console"] }
}
```

`tiers.py` loads this file into typed `TierConfig` objects; `enterprise` accounts carry a per-account numeric override resolved at auth time. This JSON is the one place the quota numbers live.

### Authorization dependencies (`tamthuc_auth/scopes.py`)

```python
def require_role(*roles: Role) -> Callable: ...              # 403 if current tier not in roles
def require_tier(min_tier: Role) -> Callable: ...            # ordered Free < Premium < Enterprise < Admin
def require_capability(cap: Capability) -> Callable: ...     # 403 if cap not in the tier's capability set
def quota_for(principal) -> int | Literal["unmetered"]: ...  # the number FR-API-003 enforces
```

### Enterprise API key (`tamthuc_auth/apikey.py`)

```python
def issue_api_key(account_id: str) -> str: ...              # hashed at rest, shown once
def resolve_api_key(key: str) -> Principal | None: ...      # -> Enterprise principal + custom quota, or None
def revoke_api_key(key_id: str) -> None: ...
```

## §4 - Acceptance criteria

1. `Role` is exactly {Free, Premium, Enterprise, Admin}; `ROLE_CAPABILITIES` maps each to its capability set, and `docs/contracts/rbac-tiers.json` agrees with it (a parity test rejects drift).
2. `require_capability(calculate_all)` rejects a Free principal with a 403 in the error envelope and allows a Premium principal.
3. `quota_for` returns 100 for Free, 5000 for Premium, the account override for Enterprise, and `"unmetered"` for Admin; FR-API-003 consumes exactly this.
4. An Enterprise API key resolves via `resolve_api_key` to an Enterprise principal with the account's custom quota; a revoked key resolves to `None`; the key is stored hashed, never in plaintext.
5. `require_tier(Premium)` uses the documented ordering Free < Premium < Enterprise < Admin, so an Enterprise principal passes a Premium gate.
6. A tier change is reflected on the next token issuance/refresh and produces an auditable action record consumed by FR-API-004.

## §5 - Verification

- `tests/test_rbac.py`: role/capability map completeness; the config-vs-code parity test; per-capability allow/deny cases across all four roles; the tier ordering; `quota_for` for each tier including the Enterprise override; API-key issue/resolve/revoke with hashed-at-rest assertion.
- Config parity: a test loads `docs/contracts/rbac-tiers.json` and asserts every role and capability matches the enums, so the advertised and enforced limits cannot diverge.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_auth`, `pytest packages/tamthuc_auth`.

## §6 - Implementation skeleton

1. `rbac.py`: `Role`, `Capability`, `ROLE_CAPABILITIES`.
2. `tiers.py`: load `docs/contracts/rbac-tiers.json` into `TierConfig`; resolve the Enterprise per-account override.
3. `scopes.py`: `require_role` / `require_tier` / `require_capability` FastAPI dependencies and `quota_for`.
4. `apikey.py`: Enterprise API-key issue (hash at rest), resolve, revoke.
5. Author `docs/contracts/rbac-tiers.json` as the single source; wire the parity test.

## §7 - Dependencies

Depends on FR-AUTH-001 (the user, the `tier` claim in the access token, and the token-issuance path a tier change flows through). Blocks FR-API-003 (rate limiting reads `quota_for` and `rbac-tiers.json` to enforce the per-tier limit) and FR-PLAT-007 (security hardening's authorization controls build on these roles). The authorization dependencies are consumed by FR-API-001's protected routes; tier-change audit rows are written by FR-API-004.

## §8 - Example payloads

```json
// a Free user calling /calculate/all
// require_capability(calculate_all) -> 403 in the FR-API-001 envelope:
{ "error": { "code": "FORBIDDEN_TIER", "message": "This endpoint requires the Premium tier or higher.",
             "details": { "required": "Premium", "current": "Free" } } }
```

```json
// quota_for a principal, consumed by FR-API-003
{ "principal": "user:...", "tier": "Premium", "requests_per_day": 5000 }
{ "principal": "apikey:...", "tier": "Enterprise", "requests_per_day": 50000 }   // account override
```

## §9 - Open questions

- Whether quotas are per-day only or also per-minute burst. Default: this FR fixes the per-day quota (the documented plan number); FR-API-003 may add a burst window on top, reading the same config. Keep the burst config in `rbac-tiers.json` if added, so it stays single-source.
- Enterprise custom quota storage: a column on the account vs an entry in the config. Default: a per-account override resolved at auth time (config holds the sentinel `"custom"`, the account holds the number), so the shared config file stays free of per-customer data.
- Capability granularity. Default: coarse capabilities at MVP (single vs all vs strategic tools vs report vs admin); finer per-feature flags are deferred until a plan needs them. Revisit with billing.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Advertised vs enforced drift | quota number changed in code but not config (or vice versa) | one source (`rbac-tiers.json`); the parity test fails CI on divergence |
| Privilege escalation | a Free token reaches a Premium endpoint | `require_capability` / `require_tier` reject with 403; every protected route declares its requirement |
| API key in plaintext | key stored bare or logged | keys hashed at rest, shown once at issue; a test asserts no plaintext storage |
| Stale tier | tier changed but old token still honored at old tier | tier resolved from the token claim; change takes effect on next issue/refresh; short access TTL bounds staleness |
| Admin over-metered / under-guarded | Admin treated as a huge quota instead of a capability | Admin is `unmetered` capability-gated to `admin_console`, not a numeric quota |
| Enterprise key over-privileged | key grants user-level actions | an API key resolves to a machine principal scoped to the account tier, not a user's full session |

## §11 - Notes

This FR is small but load-bearing twice over: it is the commercial plan ladder and the primary cost/abuse control on an LLM-backed endpoint. The one discipline that matters most is single-source config - the quota a request is judged against and the quota a pricing page shows must be the same JSON. Keep the split clean: AUTH-002 decides what a principal may do and how much; FR-API-003 does the counting and returns the 429. The package `tamthuc_auth` is shared with FR-AUTH-001/003/004; this FR extends it with the authorization layer the FastAPI gateway leans on.
