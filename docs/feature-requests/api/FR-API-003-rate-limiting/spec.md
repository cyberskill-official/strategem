---
id: FR-API-003
title: "Rate limiting and abuse detection - per-tier quota enforcement (Free 100/day, Premium 5000/day, Enterprise custom) reading the AUTH-002 config, Redis-backed counters, 429 in the error envelope with Retry-After, plus velocity/anomaly abuse controls"
module: API
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-12, Grok-21, strategy RISK-5]
related_frs: [FR-API-001, FR-AUTH-002, FR-PLAT-006, FR-PLAT-007, FR-PLAT-008]
depends_on: [FR-API-001, FR-AUTH-002]
blocks: []
new_paths:
  - packages/tamthuc_api/tamthuc_api/ratelimit.py
  - packages/tamthuc_api/tamthuc_api/abuse.py
  - packages/tamthuc_api/tamthuc_api/middleware/__init__.py
  - packages/tamthuc_api/tamthuc_api/middleware/ratelimit.py
  - packages/tamthuc_api/tests/test_ratelimit.py
  - packages/tamthuc_api/tests/test_abuse.py
---

## §1 - Description (BCP-14 normative)

This FR adds rate limiting and abuse detection to the gateway: it enforces the per-tier request quotas that FR-AUTH-002 configures, and it detects and blunts abusive traffic patterns. It extends the `tamthuc_api` package. It owns the counting and the enforcement; it does NOT own the quota numbers (those are FR-AUTH-002's single-source config) nor the tier resolution (FR-AUTH-001/002).

The limiter SHALL enforce the quotas from `docs/contracts/rbac-tiers.json` via FR-AUTH-002's `quota_for(principal)`: Free 100 requests/day, Premium 5000 requests/day, Enterprise the account's custom number, Admin unmetered. Counting SHALL be per principal (user id or Enterprise API-key account) over a rolling or calendar-day window, backed by Redis (FR-PLAT-006) so the count is shared across gateway instances. When a principal exceeds its quota the gateway SHALL return HTTP 429 with the FR-API-001 error envelope (`code = RATE_LIMITED`), a `Retry-After` header, and `details` carrying the limit and the reset time. Limiting SHALL be applied as middleware on the metered routes so no metered endpoint can be reached without passing the check, and Admin/unmetered principals SHALL bypass counting.

Abuse detection SHALL run alongside quota enforcement and cover at least: request-velocity spikes (a burst well above a principal's normal rate), credential-stuffing signatures on the auth routes (many failed logins across accounts from one source), and repeated malformed or probing requests. On a detected abuse signal the gateway SHALL apply a graduated response - short-window throttle, temporary lockout, and an audited flag - rather than a silent drop, and SHALL record the event for FR-API-004 audit and FR-PLAT-005 alerting. Rate-limit and abuse state SHALL fail safe: if Redis is unavailable the limiter SHALL degrade to a conservative local limit rather than failing open to unlimited traffic.

## §2 - Why this design (rationale for humans)

The calculate endpoints call an LLM, so an unmetered request is a direct cost and a direct abuse surface (Grok-12). Rate limiting is therefore not just a plan-enforcement nicety; it is the first line of cost control and the first line of denial-of-service defence (Grok-21). Reading the quota from FR-AUTH-002's single config rather than hardcoding numbers here is what keeps the enforced limit equal to the advertised one - the same discipline stated from the enforcement side.

Backing the counters with Redis matters because the gateway scales horizontally; a per-instance in-memory counter would let a principal multiply its quota by the number of instances. Failing safe rather than open is the non-obvious but critical choice: a limiter that disables itself when its datastore blinks turns a cache outage into an unlimited-spend incident, so the degraded mode is a conservative local cap, never "allow everything". Abuse detection is separate from quota because the shapes differ - a paying Premium user can hit their quota legitimately, while a burst of failed logins across many accounts from one IP is abuse regardless of any single account's quota. Graduated, audited responses (throttle, then lock, then flag) give operators signal and a paper trail instead of a silent black hole (RISK-5 touches this: the auth surface is where credential attacks against sensitive accounts land).

## §3 - Contract (types / middleware / policy)

### Limiter (`tamthuc_api/ratelimit.py`)

```python
class RateDecision(BaseModel):
    allowed: bool
    limit: int | Literal["unmetered"]
    remaining: int
    reset_at: int           # epoch seconds
    retry_after: int | None # seconds, when not allowed

class RateLimiter(Protocol):
    async def check_and_count(self, principal: Principal) -> RateDecision: ...

class RedisRateLimiter:     # default (FR-PLAT-006 Redis); shared counter across instances
    # key: rl:{principal}:{yyyymmdd}; INCR + EXPIRE; quota from AUTH-002 quota_for(principal)
    ...
class LocalFallbackLimiter: # conservative per-instance cap when Redis is unreachable (fail safe)
    ...
```

### Abuse detection (`tamthuc_api/abuse.py`)

```python
class AbuseSignal(str, Enum):
    velocity_spike = "velocity_spike"
    credential_stuffing = "credential_stuffing"
    probing = "probing"                    # repeated malformed / 4xx-heavy traffic

class AbuseVerdict(BaseModel):
    signal: AbuseSignal | None
    action: Literal["allow", "throttle", "lockout", "flag"]
    window_s: int | None

async def evaluate(principal: Principal | None, source_ip: str, event: RequestEvent) -> AbuseVerdict: ...
```

### Middleware (`tamthuc_api/middleware/ratelimit.py`)

```python
# ASGI middleware on the metered routes:
#  1. resolve principal (FR-AUTH-001/002); Admin/unmetered -> pass through, no count
#  2. limiter.check_and_count(principal); if not allowed -> 429 envelope + Retry-After
#  3. abuse.evaluate(...); on throttle/lockout -> 429/423 envelope; on flag -> allow + audit event
#  4. set X-RateLimit-Limit / X-RateLimit-Remaining / X-RateLimit-Reset response headers
```

### 429 envelope (via FR-API-001 error contract)

```json
{ "error": { "code": "RATE_LIMITED",
             "message": "Daily request quota exceeded for the Free tier.",
             "details": { "limit": 100, "remaining": 0, "reset_at": 1700000000 },
             "request_id": "req_..." } }
```

with header `Retry-After: <seconds>`.

## §4 - Acceptance criteria

1. A Free principal is allowed for 100 requests in the window and receives 429 `RATE_LIMITED` with `Retry-After` on the 101st; a Premium principal's cutover is at 5000; the numbers come from `quota_for`, not from constants in this module.
2. Counting is shared across two limiter instances against one Redis (a second instance sees the first's count); an Admin/unmetered principal is never counted and never limited.
3. Response headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` are set on metered responses and reflect the true remaining count.
4. When Redis is unreachable the limiter degrades to the conservative `LocalFallbackLimiter` cap and never fails open to unlimited traffic; a test simulates the outage.
5. A burst well above a principal's baseline raises `velocity_spike` and a graduated `throttle`; many failed logins across accounts from one source raise `credential_stuffing` and a `lockout`; each produces an audited event for FR-API-004 and an alert signal for FR-PLAT-005.
6. The Enterprise custom quota from the account override is honored, and an Enterprise API-key principal is metered against the account, not per key.

## §5 - Verification

- `tests/test_ratelimit.py`: per-tier cutovers using a fake/embedded Redis; cross-instance shared count; unmetered bypass; header correctness; the fail-safe degraded mode on Redis outage; Enterprise override.
- `tests/test_abuse.py`: velocity-spike, credential-stuffing, and probing detection with synthetic event streams; the graduated allow/throttle/lockout/flag actions; the audit-event emission and the alert signal.
- Integration: the middleware rejects an over-quota request before it reaches the orchestrator (a metered route cannot be served without the check).
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`.

## §6 - Implementation skeleton

1. `ratelimit.py`: `RateLimiter` protocol, `RedisRateLimiter` (INCR/EXPIRE keyed by principal + day, quota from `quota_for`), `LocalFallbackLimiter`.
2. `abuse.py`: the signal enum, `evaluate` with velocity, credential-stuffing, and probing heuristics; the graduated action policy.
3. `middleware/ratelimit.py`: the ASGI middleware wiring principal resolution, limiter, abuse, headers, and the 429/423 envelope.
4. Wire the middleware onto the metered routes in `app.py`; emit audit events to the FR-API-004 seam and alert signals to FR-PLAT-005.

## §7 - Dependencies

Depends on FR-API-001 (the gateway, the metered routes, and the error envelope this returns) and FR-AUTH-002 (the tier resolution and `quota_for` single-source config). Uses FR-PLAT-006 Redis for the shared counters; audited events flow to FR-API-004 and alerts to FR-PLAT-005; the fail-safe posture aligns with FR-PLAT-008 resilience. This FR blocks nothing directly but is a gating control on the FR-API-001 endpoints.

## §8 - Example payloads

```json
// audited abuse event (to FR-API-004)
{ "action": "credential_stuffing_lockout", "source_ip": "...", "principal": null,
  "details": { "failed_logins": 42, "window_s": 300, "accounts_touched": 17 } }
```

```json
// response headers on an allowed metered request
{ "X-RateLimit-Limit": "5000", "X-RateLimit-Remaining": "4987", "X-RateLimit-Reset": "1700000000" }
```

## §9 - Open questions

- Window model: calendar-day vs rolling 24h. Default: calendar-day counters (simplest to reason about and to communicate as a plan limit), with a short burst window optionally layered on from the same AUTH-002 config. Revisit if users report day-boundary gaming.
- Where abuse heuristics live long-term. Default: in-process heuristics at MVP reading Redis-held velocity keys; a dedicated WAF or an external anomaly service is a later PLAT-007 concern that this module can defer to without changing the middleware seam.
- Whether Enterprise API keys get per-key sub-limits under the account quota. Default: metered at the account level now; per-key sub-limits are an Enterprise-management feature deferred until requested.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Fail open on datastore outage | Redis down, limiter disabled | forbidden; degrade to the conservative `LocalFallbackLimiter`, never unlimited |
| Per-instance count multiplies quota | in-memory counter under horizontal scaling | shared Redis counter keyed by principal; cross-instance test asserts one count |
| Advertised vs enforced drift | quota hardcoded here | numbers come only from `quota_for` / `rbac-tiers.json`; no constants in this module |
| Silent abuse drop | abusive traffic dropped with no record | graduated throttle/lockout/flag, each audited (FR-API-004) and alerted (FR-PLAT-005) |
| Metered route bypass | a calculate route served without the check | middleware applied to all metered routes; integration test asserts pre-orchestrator rejection |
| Unmetered principal throttled | Admin counted and limited | Admin/unmetered bypasses counting entirely |

## §11 - Notes

This FR is the cost and abuse control on an LLM-backed API, so its two rules are: read the quota from one source (never hardcode), and fail safe (never fail open). Keep the split with FR-AUTH-002 clean - AUTH decides the number, API-003 does the counting and returns the 429. It extends the same `tamthuc_api` app as FR-API-001/002/004; the limiter and abuse controls are middleware on the existing routes, so the gateway stays one installable, mypy-clean unit.
