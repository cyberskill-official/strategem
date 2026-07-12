---
id: FR-PLAT-008
title: "Resilience - circuit breaker for the LLM and external services, retry with exponential backoff for transient errors, graceful degradation (one engine fails -> return the others; LLM fails -> rule-based interpretation), and the structured error envelope (code, message, details) with standard HTTP codes"
module: PLAT
priority: MUST
status: done
phase: P1
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-47, strategy 4.1, strategy 4.2, strategy RISK-3]
related_frs: [FR-PLAT-005, FR-API-001, FR-API-003, FR-RAG-003, FR-RAG-007]
depends_on: [FR-PLAT-005]
blocks: []
new_paths:
  - packages/tamthuc_api/tamthuc_api/resilience/__init__.py
  - packages/tamthuc_api/tamthuc_api/resilience/circuit_breaker.py
  - packages/tamthuc_api/tamthuc_api/resilience/retry.py
  - packages/tamthuc_api/tamthuc_api/resilience/degradation.py
  - packages/tamthuc_api/tamthuc_api/resilience/errors.py
  - packages/tamthuc_api/tests/test_circuit_breaker.py
  - packages/tamthuc_api/tests/test_retry.py
  - packages/tamthuc_api/tests/test_degradation.py
  - docs/contracts/resilience-policy.md
---

## §1 - Description (BCP-14 normative)

This FR is the resilience layer: the reusable patterns that keep the platform serving when an external dependency fails. It provides a circuit breaker for external services (chiefly the LLM), retry with exponential backoff for transient errors, graceful degradation policies, and the mapping from a failure to the structured error envelope with the correct standard HTTP code. It owns the resilience primitives and the degradation policy; it does NOT own the error-envelope shape (FR-API-001 defines it) nor the LLM-specific fallback wiring (FR-RAG-007 applies these primitives to the RAG caller) - it is the shared library both consume.

External-service calls SHALL be wrapped in a circuit breaker: after a threshold of failures the breaker SHALL open and fail fast (returning a degraded result or a typed upstream error) rather than piling requests onto a dead dependency, SHALL move to half-open after a cooldown to probe recovery, and SHALL close on success. Transient errors (timeouts, 502/503, connection resets) SHALL be retried with exponential backoff and jitter, bounded by a maximum attempt count and a total deadline; non-transient errors (4xx, validation) SHALL NOT be retried. Retries and breaker state transitions SHALL emit metrics and signals to FR-PLAT-005 so an operator sees a dependency degrade.

Degradation SHALL be graceful and explicit: if one engine fails in a multi-system `/calculate/all`, the gateway SHALL still return the results of the engines that succeeded, marking the failed one, rather than failing the whole request; if the LLM fails, the platform SHALL fall back to a rule-based interpretation (the detected patterns plus their cited classical text, without the LLM's synthesis) rather than returning nothing. Every failure that does surface SHALL be rendered as the FR-API-001 structured error envelope `{ code, message, details }` with the correct HTTP status (502/503 `UPSTREAM_*` for dependency failures, not an opaque 500). Degradation SHALL NOT silently drop the AIDisclosure or the citation obligations - a rule-based fallback is still labeled and still cited.

## §2 - Why this design (rationale for humans)

The platform's hot path crosses two external dependencies that will fail sometimes: the LLM and (transitively) whatever the LLM provider depends on. Without resilience, a slow or dead LLM turns every query into a hung request and a cascade - the classic failure where retries against a dead dependency amplify the outage. A circuit breaker converts that into fail-fast plus a degraded-but-useful answer; exponential backoff with jitter handles the far more common transient blip without a retry storm. These are boring, well-understood patterns, and that is exactly why they belong in one shared library rather than reinvented per call site (Grok-47).

Graceful degradation is where resilience meets the product's values. A multi-system reading where one engine hiccups should still show the other engines - a partial chart is far more useful than an error page. And when the LLM is down, the platform still has something true to say: the deterministic engine already cast the chart and the rule engine already detected the patterns with their citations, so a rule-based interpretation (patterns + cited text, minus the LLM's prose) is a real, grounded answer, not a stub. Crucially, this is also the safe degradation: falling back to cited patterns can never hallucinate, because there is no generative step to hallucinate (RISK-3). The one thing degradation must not do is quietly drop the disclosure or citation obligations - a fallback answer is still AI-adjacent output on a legally sensitive surface, so it stays labeled and cited. Mapping every failure to the structured envelope with the right code keeps the frontend and SDK reacting correctly instead of guessing at a bare 500.

## §3 - Contract (primitives / policy / errors)

### Circuit breaker (`resilience/circuit_breaker.py`)

```python
class BreakerState(str, Enum): closed = "closed"; open = "open"; half_open = "half_open"

class CircuitBreaker:
    # opens after `failure_threshold` failures in a window; half-open after `cooldown_s`; closes on success
    def __init__(self, failure_threshold: int, cooldown_s: float, name: str): ...
    async def call(self, fn: Callable[[], Awaitable[T]]) -> T: ...   # raises BreakerOpen when open
```

### Retry with backoff (`resilience/retry.py`)

```python
async def with_retry(fn: Callable[[], Awaitable[T]], *, max_attempts: int, base_s: float,
                     max_s: float, deadline_s: float, retry_on: tuple[type[Exception], ...]) -> T:
    # exponential backoff base_s * 2**n + jitter, capped at max_s, bounded by deadline_s;
    # retries only `retry_on` (transient) exceptions; never retries 4xx/validation
    ...
```

### Degradation policy (`resilience/degradation.py`, `docs/contracts/resilience-policy.md`)

| Failure | Degraded behavior | Surfaced as |
|---|---|---|
| one engine fails in `/calculate/all` | return the succeeding engines' charts; mark the failed `he` | 200 with a `degraded` note per system |
| LLM fails / breaker open | rule-based interpretation (patterns + cited text, no LLM synthesis); AIDisclosure marks the fallback | 200 degraded, or 503 `UPSTREAM_LLM` if even patterns are unavailable |
| engine service down (single-system) | no chart to interpret | 502 `UPSTREAM_ENGINE` in the error envelope |
| DB write fails (persist) | request fails transactionally (no silent 200) | 500 `INTERNAL` / 503 per FR-API-004 |

### Error mapping (`resilience/errors.py`)

Maps `BreakerOpen`, timeout, and upstream errors to the FR-API-001 envelope codes (`UPSTREAM_LLM`, `UPSTREAM_ENGINE`) with the correct HTTP status; never surfaces a raw exception as an opaque 500.

## §4 - Acceptance criteria

1. A circuit breaker around a failing dependency opens after the threshold, fails fast while open, moves to half-open after the cooldown, and closes on a successful probe; a test drives all four transitions.
2. A transient error is retried with exponential backoff + jitter up to the attempt/deadline bound and then surfaces the mapped upstream error; a non-transient 4xx is not retried.
3. In `/calculate/all`, an injected failure of one engine still returns the other engines' charts, with the failed `he` marked degraded, and does not fail the whole request.
4. With the LLM down (or the breaker open), the response is a rule-based interpretation built from the detected patterns and their citations, carrying the AIDisclosure marked as a fallback and keeping citations - never an empty or unlabeled answer.
5. Every surfaced failure is the FR-API-001 error envelope with the correct status: a dependency failure is 502/503 `UPSTREAM_*`, not an opaque 500; a test asserts the code/status mapping.
6. Breaker transitions and retries emit metrics/signals to FR-PLAT-005 (an operator can see a dependency degrade and recover).

## §5 - Verification

- `tests/test_circuit_breaker.py`: closed->open->half_open->closed transitions; fail-fast while open; the cooldown probe.
- `tests/test_retry.py`: backoff timing (mocked clock), jitter bounds, the attempt/deadline cap, retry-only-on-transient.
- `tests/test_degradation.py`: the one-engine-fails-in-all case returns partial results; the LLM-down case returns a cited rule-based interpretation with the fallback AIDisclosure; the error-envelope code/status mapping for each failure.
- Integration: the FR-API-001 orchestrator uses these primitives on the engine and LLM calls; a fault-injection run confirms degrade-not-fail behavior end to end and the emitted PLAT-005 signals.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`.

## §6 - Implementation skeleton

1. `resilience/circuit_breaker.py`: the `CircuitBreaker` with state machine, thresholds, cooldown, and metric hooks.
2. `resilience/retry.py`: `with_retry` (exponential backoff + jitter, deadline bound, transient-only) as a reusable helper/decorator.
3. `resilience/degradation.py`: the degradation policy - partial multi-engine results and the LLM-down rule-based fallback (patterns + citations + fallback AIDisclosure).
4. `resilience/errors.py`: map breaker/timeout/upstream failures to the FR-API-001 envelope codes and HTTP statuses.
5. Wire the primitives into the FR-API-001 orchestrator's engine and LLM calls; emit transitions to FR-PLAT-005; expose the LLM-specific application to FR-RAG-007.

## §7 - Dependencies

Depends on FR-PLAT-005 (observability: breaker/retry/degradation transitions must be observable, and they feed the LLM-downtime and error-rate alerts). Consumes the FR-API-001 error-envelope contract (this FR maps failures onto it, it does not redefine it) and plugs into the FR-API-001 orchestrator's engine and LLM calls. Provides the shared resilience primitives FR-RAG-007 applies to the LLM caller (RAG-007 is the LLM-specific instance of this library). Coordinates with FR-API-003 (the limiter's fail-safe posture is the same principle applied to the rate-limit datastore) and FR-RAG-003 (the rule-based fallback reuses the detected patterns and their citations).

## §8 - Example payloads

```json
// /calculate/all with one engine degraded - partial success, not a failure
{ "query_id": "q_...", "charts": [ { "he": "ky_mon", "...": "..." } ],
  "degraded": [ { "he": "luc_nham", "reason": "UPSTREAM_ENGINE", "message": "LiuRen engine unavailable" } ],
  "interpretation": { "...": "..." }, "ai_disclosure": { "ai_generated": true } }
```

```json
// LLM down - rule-based fallback, still labeled and cited
{ "interpretation": { "mode": "rule_based_fallback",
    "patterns": [ { "id": "qimen_thanh_long_hoi_dau", "polarity": "cat", "citations": ["Yen Ba Dieu Tau Ca"] } ] },
  "ai_disclosure": { "ai_generated": false, "fallback": "llm_unavailable", "note": "rule-based, citation-grounded" } }
```

## §9 - Open questions

- Breaker granularity: one breaker per external dependency vs per provider+model. Default: per dependency at MVP (one LLM breaker, one engine-service breaker); split per provider when FR-RAG-007 adds multi-provider fallback so a single provider's outage does not open the whole LLM path.
- Whether the rule-based fallback is a distinct response mode or a reduced interpretation. Default: a distinct `mode: rule_based_fallback` so the frontend can render it honestly (patterns + citations, no synthesized prose) and the AIDisclosure can mark it; keep the response shape otherwise identical.
- Retry budget interaction with the FR-API-003 rate limit. Default: retries are internal and do not consume the user's quota (the quota counts user requests, not internal attempts); a retried upstream call is one metered request.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Cascade on dead dependency | unbounded requests to a failing LLM | circuit breaker opens and fails fast; no pile-on; half-open probe for recovery |
| Retry storm | retrying non-transient or without a cap | retry only transient errors, exponential backoff + jitter, bounded by attempts + deadline |
| All-or-nothing multi-engine | one engine failure fails `/calculate/all` | return the succeeding engines; mark the failed `he` degraded |
| Empty answer on LLM outage | LLM down returns nothing | rule-based fallback from detected patterns + citations; never empty |
| Unlabeled/uncited fallback | degradation drops AIDisclosure or citations | forbidden; the fallback stays labeled and cited (RISK-3) |
| Opaque 500 on upstream failure | dependency error surfaced as generic 500 | mapped to 502/503 `UPSTREAM_*` in the FR-API-001 envelope |

## §11 - Notes

This FR keeps the platform useful when its external dependencies are not. The reusable primitives - circuit breaker, retry-with-backoff, degradation policy, error mapping - live here as one shared library so FR-API-001 and FR-RAG-007 apply them instead of reinventing them. Two disciplines matter most: degrade, do not fail (partial multi-engine results; a cited rule-based interpretation when the LLM is down), and the degraded answer stays labeled and cited (the fallback is safe precisely because it has no generative step to hallucinate, but it still carries AIDisclosure and citations on this legally sensitive surface). It depends on FR-PLAT-005 because a breaker that trips invisibly is worse than none - every transition is observable and alertable.
