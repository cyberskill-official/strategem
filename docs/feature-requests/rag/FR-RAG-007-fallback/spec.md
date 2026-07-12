---
id: FR-RAG-007
title: "LLM fallback - timeout + circuit breaker around the RAG-003 LLM caller; on failure degrade to a rule-based interpretation assembled from the detected cach cuc + cited pattern meanings (no free-form generation); always labeled degraded; reads the la so read-only, keeps citations + AIDisclosure"
module: RAG
priority: MUST
status: done
phase: P1
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.3, strategy 4.4, strategy 8]
related_frs: [FR-RAG-003, FR-PLAT-008, FR-RULE-003, FR-KB-002, FR-RAG-004]
depends_on: [FR-RAG-003]
blocks: []
new_paths:
  - packages/tamthuc_rag/tamthuc_rag/fallback.py
  - packages/tamthuc_rag/tamthuc_rag/resilience.py
  - packages/tamthuc_rag/tamthuc_rag/templates/degraded_beginner.md
  - packages/tamthuc_rag/tamthuc_rag/templates/degraded_expert.md
  - packages/tamthuc_rag/tests/test_fallback.py
  - packages/tamthuc_rag/tests/fixtures/fallback_cases.json
---

## §1 - Description (BCP-14 normative)

This FR keeps interpretation available when the LLM is not: it wraps FR-RAG-003's LLM caller with a timeout and a circuit breaker, and on failure it degrades to a rule-based interpretation assembled from the chart's detected cách cục and their cited pattern meanings - no free-form generation - always labeled degraded. It is the graceful-degradation half of the resilience story for the interpretation branch (strategy 4.4; FR-RAG-003 §3 names this FR as the wrapper), the RAG-specific application of the platform resilience patterns (FR-PLAT-008).

The LLM call SHALL carry a per-call timeout. A circuit breaker SHALL open after a configured number of consecutive failures or timeouts, fail fast to the fallback for a cooldown, and half-open a probe before closing; bounded retries with backoff MAY precede a counted failure. On any unrecoverable LLM outcome - timeout, open circuit, or invalid output after FR-RAG-003's single repair retry - the interpreter SHALL NOT error to the user; it SHALL produce a rule-based interpretation. The rule-based interpretation SHALL be assembled from `la_so.cach_cuc` (the deterministic engine's detected patterns, read from the envelope) plus each pattern's `meaning_modern` / `meaning_classical` and citations (FR-KB-002 via FR-RULE-003), stitched through fixed templates; it SHALL contain no model-generated free text and SHALL make no claim that is not carried by a cited pattern meaning.

Every degraded output SHALL be labeled degraded: this FR SHALL add a `degraded: bool` field (default `false`) to the `AIDisclosure` contract - an additive, backward-compatible extension coordinated with FR-RAG-003's schema - and SHALL set it `true`, set `AIDisclosure.model = "rule-based-fallback"`, lower `confidence`, and force `requires_human_review = true` for the degraded reading. The degraded interpretation SHALL still validate against FR-RAG-003's `Interpretation` schema and SHALL carry citation cards for the pattern meanings it used. The fallback SHALL read the la so envelope read-only and SHALL NEVER write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` (strategy 4.3); it assembles cited pattern meanings only, and it preserves the citation and AIDisclosure discipline with the degraded marker set.

## §2 - Why this design (rationale for humans)

An LLM is a network dependency that will be slow or down some of the time, and a divination-adjacent product that simply errors when the model is unavailable teaches users it cannot be relied on. But the naive fix - let the model answer from memory when retrieval or the service is flaky - is exactly the hallucination failure the whole branch is built to prevent (Claude-06 s4.3). The way out is that the chart is already deterministic: the engine has detected the cách cục, and each pattern already carries a cited, curator-reviewed meaning (FR-KB-002). So when the LLM is unavailable, the product can still say something true and sourced - here are the patterns in your chart and what the classics, cited, say they mean - by stitching those cited meanings through fixed templates rather than generating prose. That is a real, honest, degraded reading, not a fabricated one, and it is only possible because the deterministic and cited layers exist beneath the LLM.

Labeling it degraded and forcing human review is the honesty that makes the fallback safe to ship. A rule-based reading is thinner than a grounded LLM interpretation - it does not synthesize across patterns or tailor tone - so the user must be told this is a reduced reading, and the conservative posture (low confidence, review required) reflects that the richer path was unavailable. The circuit breaker is what keeps a struggling LLM from degrading the whole product: without it, every request waits out the timeout and the system stays slow under load; with it, after a few failures the interpreter fails fast to the cheap, available rule-based path and probes for recovery, so a model outage is a quality reduction, not an outage. Keeping the fallback strictly to cited pattern meanings, and strictly off the la so envelope, means the degraded path honors the same two invariants as the primary path - no claim without a citation, and the interpretation never writes the chart - so resilience is bought without any loss of the discipline the product's trust rests on.

## §3 - Contract (resilience wrapper, rule-based fallback, disclosure)

### Resilience wrapper (`tamthuc_rag/resilience.py`)

```python
class CircuitState(str, Enum): closed = "closed"; open = "open"; half_open = "half_open"

class CircuitBreaker:
    def __init__(self, fail_threshold: int = 5, cooldown_s: float = 30.0): ...
    state: CircuitState
    def call(self, fn: Callable[[], T]) -> T: ...   # raises CircuitOpen when open

class ResilientLLM:                                  # implements FR-RAG-003's LLM protocol
    def __init__(self, inner: LLM, breaker: CircuitBreaker,
                 timeout_s: float = 20.0, retries: int = 1, backoff_s: float = 0.5): ...
    def complete(self, messages, schema):
        # bounded retry+backoff -> timeout-guarded inner.complete, via the breaker;
        # on timeout / CircuitOpen / invalid-after-repair, raise LLMUnavailable
```

`ResilientLLM` is a drop-in for the `LLM` FR-RAG-003 already accepts; it reuses FR-PLAT-008's breaker/retry primitives where present, else a local implementation.

### Rule-based fallback (`tamthuc_rag/fallback.py`, `templates/`)

```python
def rule_based_interpretation(la_so: LaSo, persona: str,
                              patterns: PatternIndex, retrieved: RetrievalResult | None) -> Interpretation:
    detected = la_so.cach_cuc                        # read-only from the envelope
    lines, cites = [], []
    for cc in detected:                              # ordered by score/polarity
        p = patterns.get(cc.id)                      # FR-RULE-003 / FR-KB-002: meaning + citations
        lines.append(render(cc, p, persona))         # fixed template; NO model text
        cites += p.citations
    cards = citation_cards(cites, retrieved)          # FR-KB-003-resolved cards for the used patterns
    return Interpretation(
        persona_level=persona,
        beginner_interpretation=assemble("degraded_beginner.md", lines),
        expert_interpretation=assemble("degraded_expert.md", lines),
        recommendations=recommendations_from_polarity(detected, patterns),
        citations=cards,
        confidence=degraded_confidence(detected),     # low
        requires_human_review=True,                   # conservative in degraded mode
        disclosure=AIDisclosure(is_ai_generated=False, model="rule-based-fallback",
            prompt_version="fallback-1.0.0", degraded=True,
            retrieved_citation_ids=[c.citation_id for c in cards], generated_at=now(),
            review_status="pending"))

def interpret_resilient(la_so, request, persona, retriever, llm, patterns,
                        breaker: CircuitBreaker) -> Interpretation:
    try:
        return interpret(la_so, request, persona, retriever, ResilientLLM(llm, breaker))  # FR-RAG-003
    except LLMUnavailable:
        retrieved = safe_retrieve(retriever, request)   # best-effort; None on failure
        return rule_based_interpretation(la_so, persona, patterns, retrieved)
```

`interpret_resilient` wraps FR-RAG-003's `interpret` unchanged: it injects the `ResilientLLM` and catches `LLMUnavailable` to produce the degraded reading. The degraded templates stitch only the cited pattern meanings; they contain no free-form slots the model would fill.

### Disclosure extension (coordinated with FR-RAG-003)

This FR adds one field to the shared contract: `AIDisclosure.degraded: bool = False`. It is additive and defaulted, so every existing FR-RAG-003 output is unaffected; the JSON Schema (`docs/contracts/interpretation.schema.json`) bumps a minor version. The degraded marker is the truthful signal FR-WEB-003 renders as a reduced-reading banner.

## §4 - Acceptance criteria

1. A healthy LLM path returns FR-RAG-003's normal interpretation unchanged, with `disclosure.degraded = false`.
2. On a timeout, the interpreter does not error to the user; it returns a rule-based interpretation assembled from `la_so.cach_cuc` and the cited pattern meanings, valid against the `Interpretation` schema.
3. The circuit breaker opens after the configured consecutive failures and fails fast to the fallback during cooldown, then half-opens a probe; a recovered LLM closes the circuit and the normal path resumes.
4. The degraded output is labeled: `disclosure.degraded = true`, `model = "rule-based-fallback"`, lowered `confidence`, `requires_human_review = true`; it carries citation cards for the pattern meanings used and contains no model-generated free text.
5. Every claim in the degraded reading maps to a cited pattern meaning; a detected cách cục with no cited meaning is omitted rather than asserted uncited (the anti-hallucination invariant holds in degraded mode).
6. The la so envelope is byte-identical before and after `interpret_resilient` (read-only invariant); no code path writes `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`.

## §5 - Verification

- `tests/test_fallback.py`: the healthy path (non-degraded, delegates to FR-RAG-003); the timeout path producing a schema-valid degraded reading; circuit-breaker open/half-open/close transitions with a flaky stub LLM; the degraded-label assertions (`degraded`, `model`, low confidence, `requires_human_review`); the no-free-text assertion (degraded text is exactly the template-stitched cited meanings); the uncited-cach-cuc omission; the read-only-envelope byte-equality check.
- Resilience: assert bounded retries + backoff before a counted failure, fail-fast while open (no timeout wait), and recovery on a healthy probe; deterministic given the stub failure pattern.
- Contract: the additive `AIDisclosure.degraded` field validates against the bumped `interpretation.schema.json` and defaults `false` for existing outputs (backward-compatible); Pydantic/JSON-Schema parity in CI.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_rag`, `pytest packages/tamthuc_rag`.

## §6 - Implementation skeleton

1. `resilience.py`: `CircuitBreaker` (fail threshold, cooldown, half-open probe) and `ResilientLLM` (timeout + bounded retry/backoff + breaker), reusing FR-PLAT-008 primitives where present; `LLMUnavailable`.
2. `fallback.py`: `rule_based_interpretation` (assemble from `la_so.cach_cuc` + cited pattern meanings, read-only) and `interpret_resilient` (wrap FR-RAG-003's `interpret`, catch `LLMUnavailable`).
3. `templates/degraded_beginner.md`, `degraded_expert.md`: fixed templates that stitch cited pattern meanings with no free-form slots; version them (`fallback-1.0.0`).
4. Add `AIDisclosure.degraded: bool = False` to the shared FR-RAG-003 contract; bump `docs/contracts/interpretation.schema.json` a minor version.
5. Wire `patterns` to FR-RULE-003 (the pattern loader serving active FR-KB-002 patterns with meanings + citations) and `citation_cards` to FR-KB-003 resolution.
6. Commit `fixtures/fallback_cases.json` (a chart with detected cách cục, one with a cited meaning and one without) as the test exemplar.

## §7 - Dependencies

Depends on FR-RAG-003 (it wraps that FR's LLM caller and `interpret`, and extends its `AIDisclosure` with the additive `degraded` field). Uses FR-PLAT-008 resilience primitives (circuit breaker, retry/backoff, graceful degradation) where available - this FR is their interpretation-branch application. Reads the detected cách cục from the la so and their cited meanings via FR-RULE-003 (serving active FR-KB-002 patterns) and FR-KB-003 (resolving the citation cards). Composes with FR-RAG-004: a degraded reading is conservative and `requires_human_review = true`, so it also passes the HumanReviewGate; wiring the degraded reading in as the reject-time fallback is a natural follow-up. Blocks nothing in the catalog, but it is the resilience wrapper every production interpretation call SHOULD go through. The RAG-branch invariant is central here and enforced: the fallback reads the la so read-only, asserts only cited pattern meanings, and keeps the citation + AIDisclosure discipline with the degraded marker set.

## §8 - Example payloads

```json
// a degraded Interpretation (abbreviated) after an LLM timeout
{ "persona_level": "beginner",
  "beginner_interpretation": "Reduced reading (AI unavailable). Your chart shows Thanh Long Hoi Dau, a favorable-timing pattern for initiating [yba_dieu_012].",
  "expert_interpretation": "Detected cach cuc: qimen_thanh_long_hoi_dau (cat). Classical basis: 丙加值符 [yba_dieu_012].",
  "recommendations": [ { "text": "Treat the window as supportive for beginning.",
      "rationale": "Cat cach cuc on the acting palace.", "citations": ["yba_dieu_012"] } ],
  "citations": [ { "citation_id": "yba_dieu_012", "source": "yen_ba_dieu_tau_ca", "unit_type": "dieu",
      "han": "丙加值符...", "bach_thoai": "...", "dich": "Binh gia truc phu...", "locator": "dieu 12" } ],
  "confidence": 0.35, "requires_human_review": true,
  "disclosure": { "is_ai_generated": false, "model": "rule-based-fallback", "prompt_version": "fallback-1.0.0",
    "degraded": true, "retrieved_citation_ids": ["yba_dieu_012"], "review_status": "pending" } }
```

## §9 - Open questions

- Whether `is_ai_generated` should be `false` (the text is template-assembled, not model-generated) or `true` with `degraded=true`. Default: `is_ai_generated=false` plus `degraded=true` and `model="rule-based-fallback"`, since no model wrote the text; the UI still shows a machine-assisted, reduced-reading banner. Confirm the exact labeling with FR-LEGAL-003.
- Circuit-breaker tuning (threshold, cooldown, timeout). Default: 5 consecutive failures, 30s cooldown, 20s per-call timeout, 1 retry; tune from FR-PLAT-005 latency/error telemetry.
- Whether the degraded reading synthesizes across multiple cách cục or lists them. Default: list each detected pattern with its cited meaning (no cross-pattern synthesis, which is the LLM's job); keep it strictly template-stitched so it can never drift into generation.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Errors to the user | LLM timeout/outage with no fallback | degrade to the rule-based reading; never surface a raw error as the interpretation |
| Free-memory degradation | fallback lets the model answer from memory | forbidden; degraded text is template-stitched cited pattern meanings only, no model free text |
| Unlabeled degraded output | a reduced reading shown as a full one | `degraded=true` + `model="rule-based-fallback"` + low confidence + review required; UI banner |
| Uncited claim in fallback | a cách cục with no cited meaning asserted | omitted, not asserted; every degraded claim maps to a cited pattern meaning |
| Slow-under-load LLM | every request waits out the timeout | circuit breaker opens, fails fast to fallback, half-open probe recovers |
| Envelope write | fallback mutates the chart | impossible: la so read-only; byte-equality test; assembles from `cach_cuc`, never writes it |
| Schema break from the new field | `degraded` field breaks existing outputs | additive + defaulted `false`; minor schema bump; existing FR-RAG-003 outputs unaffected |

## §11 - Notes

This FR is what lets the interpretation branch stay both available and honest under an LLM outage: the deterministic, cited layers beneath the model make a true degraded reading possible, so resilience never becomes an excuse to hallucinate. Two invariants carry over from FR-RAG-003 unchanged - the fallback reads the la so and never writes it, and it makes no claim without a citation - and one label is added: degraded output is always marked degraded, low-confidence, and review-required, because a reduced reading must announce itself. Keep the degraded templates free of any model-fillable slot so the path can never drift into generation, and coordinate the single additive `AIDisclosure.degraded` field with FR-RAG-003 as a reviewed schema bump. The package `tamthuc_rag` is shared with FR-RAG-001/002/003/004/005/006; this FR adds `fallback.py`, `resilience.py`, and the degraded templates, so the RAG branch stays one installable, mypy-clean unit.
