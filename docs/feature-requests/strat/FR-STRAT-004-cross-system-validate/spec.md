---
id: FR-STRAT-004
title: "Cross-system validate - /calculate/all runs two or more engines for one question and returns a per-system read plus an agreement view (agreement vs divergence), noting that the three systems cover different scopes (Claude-07 s1.4); calls the engines, never re-casts, and never merges into a single verdict"
module: STRAT
priority: SHOULD
status: ready_to_implement
phase: P2
slice: 1
lang: python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s1.4, strategy 7, strategy 4.3, Grok-02]
related_frs: [FR-QMDG-006, FR-LN-006, FR-TAT-006, FR-RAG-003, FR-API-001, FR-STRAT-001]
depends_on: [FR-QMDG-006, FR-LN-006]
blocks: []
new_paths:
  - packages/tamthuc_strat/cross_system.py
  - packages/tamthuc_strat/tests/test_cross_system.py
  - packages/tamthuc_strat/tests/fixtures/cross_system_agreement.json
---

## §1 - Description (BCP-14 normative)

This FR implements cross-system validation: for one question, run two or more engines (FR-QMDG-006 and FR-LN-006 now; FR-TAT-006 when it lands) and return a per-system read plus an agreement view that shows where the systems agree and where they diverge (Claude-07 s1.4, Grok-02).

The module SHALL accept a `CrossSystemRequest` (one question: datetime, tz, kinh do, loai_cau_hoi, and per-system school flags) and SHALL obtain each system's la so by calling that engine; it SHALL NOT re-cast, re-implement, or merge charts (strategy 4.3). For each system it SHALL produce a `SystemRead`: the he, a documented cat / hung stance derived from the envelope cach cuc, the system's scope, a reference to the cast, and optionally its FR-RAG-003 interpretation. It SHALL then produce an `AgreementView` that compares the stances and marks agreement vs divergence WITHOUT collapsing them into one verdict, and SHALL annotate each system's scope so a divergence is not misread as a contradiction (Claude-07 s1.4: the three systems cover different scopes). The module SHALL be deterministic, and the result is decision support, never a verdict (strategy 7).

## §2 - Why this design (rationale for humans)

A tempting but wrong feature would be a single merged answer across the three systems. It is wrong because the three systems do not answer the same question at the same scope (Claude-07 s1.4): Luc Nham is tactical and per-hour (a specific act, yes or no), Ky Mon is tactical and layout (timing plus direction for a campaign), Thai At is strategic and long-range (a macro trend, a cycle). Forcing them into one verdict would hide exactly the information a cross-system reading exists to surface.

So the honest artifact is a per-system read plus an agreement view that says, in effect, "these two agree that the near-term is supportive; this one speaks to a longer horizon and is neutral there" - agreement and divergence both shown, each with its scope. Like the other strategic tools, it calls the engines and never re-casts (strategy 4.3), and the stance is a documented function of the envelope cach cuc, so the agreement view is explainable rather than an opaque merge. Annotating scope is what keeps a legitimate difference of horizon from reading as a contradiction.

## §3 - Contract (models and process)

### Models (`packages/tamthuc_strat/cross_system.py`)

```python
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CrossSystemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    datetime: datetime
    tz: str
    kinh_do: float
    loai_cau_hoi: str
    co_truong_phai: dict[str, dict]   # per-system flags: {"ky_mon": {...}, "luc_nham": {...}}

class SystemRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    he: str                           # ky_mon | luc_nham | thai_at
    stance: Literal["favorable", "mixed", "unfavorable"]   # documented fn of cach_cuc
    scope: str                        # "tactical/hourly" | "tactical/layout" | "strategic/long-range"
    cat: list[dict]                   # contributing cat cach cuc (id, name, citations)
    hung: list[dict]
    cast_ref: str                     # QMDG-006 / LN-006 envelope reference
    interp_ref: str | None = None     # optional RAG-003 interpretation reference

class AgreementView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agree: bool                       # do the comparable stances align
    summary: str                      # "both favorable near-term; TaiYi neutral at longer horizon"
    by_scope: list[dict]              # agreement annotated per scope, so divergence != contradiction

class CrossSystemResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reads: list[SystemRead]           # one per engine run
    agreement: AgreementView
    request_echo: CrossSystemRequest
```

### The scope table (Claude-07 s1.4)

| He | Scope | Question it fits |
|---|---|---|
| Luc Nham | tactical / hourly | a specific act, yes or no |
| Ky Mon | tactical / layout | choose the time and direction for a campaign |
| Thai At | strategic / long-range | a macro trend, a cycle, over years |

### Process

1. For each system in the request, call its engine (FR-QMDG-006, FR-LN-006; FR-TAT-006 when present) with the shared question plus that system's flags -> la so envelope. Never re-cast.
2. Derive each `SystemRead`'s stance from the envelope cach cuc by a documented rule (net cat vs hung on the dung than palace / lesson), attach cat / hung + citations, and stamp the system's scope.
3. Build the `AgreementView`: compare stances at comparable scope; mark agree / divergence; annotate `by_scope` so a long-range-vs-hourly difference reads as different-scope, not contradiction. Never merge into one verdict.

Determinism follows from the engines plus a pure stance rule. A requested system with no engine yet returns a typed "system unavailable", not a silent drop.

## §4 - Acceptance criteria

1. For a question with two systems, the result has one `SystemRead` per system, each with a stance, scope, cat / hung + citations, and a `cast_ref`.
2. The module obtains each chart via its engine; a test asserts it calls QMDG-006 and LN-006 and does not cast or merge charts itself.
3. `stance` is a documented, pure function of the envelope cach cuc; the same envelope yields the same stance (explainable).
4. The `AgreementView` marks agreement vs divergence and annotates scope; a divergence at different scopes is labeled as such, not as contradiction (Claude-07 s1.4).
5. The result is never a single merged verdict; both reads remain present and separable.
6. Determinism: the same request twice yields an identical result.

## §5 - Verification

- `test_cross_system.py`: stub QMDG-006 + LN-006 engines returning known envelopes; assert the per-system reads, the stance derivation, the scope stamps, and the agreement view (an agree case and a divergent-scope case) against `fixtures/cross_system_agreement.json`.
- No-merge test: the result exposes both reads; there is no single verdict field.
- No-recompute test: a spy asserts each engine is called once and STRAT does not cast or merge.
- Explainability: `stance` equals the documented aggregation of the read's cat / hung.
- Scope: a favorable-hourly vs neutral-long-range case is labeled different-scope, not a contradiction.
- Gates: `python -m pytest packages/tamthuc_strat`, `ruff check`, `mypy packages/tamthuc_strat`.

## §6 - Implementation skeleton

1. `cross_system.py`: `CrossSystemRequest`, `SystemRead`, `AgreementView`, `CrossSystemResult`.
2. `validate(request, engines) -> CrossSystemResult`: call each engine; derive the stance from cach cuc; stamp the scope; build the agreement view.
3. The documented stance rule + the s1.4 scope table.
4. Wire `/calculate/all` in the API (FR-API-001); tests with stub engines and golden agreement fixtures.

## §7 - Dependencies

Depends on FR-QMDG-006 and FR-LN-006 (the two engines it runs; FR-TAT-006 joins at P2 for the third system, which is why this FR is P2). Reads the FR-PLAT-002 envelopes and, optionally, FR-RAG-003 interpretations per system. Exposed via FR-API-001 (`/calculate/all`). Sibling to FR-STRAT-001/002/003. Nothing depends on it (blocks empty).

## §8 - Example payloads

```json
// CrossSystemResult (abridged) - Ky Mon and Luc Nham agree near-term
{ "reads": [
    { "he": "ky_mon", "stance": "favorable", "scope": "tactical/layout",
      "cat": [ { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "citations": ["Yen Ba Dieu Tau Ca"] } ],
      "hung": [], "cast_ref": "qmdg:...", "interp_ref": null },
    { "he": "luc_nham", "stance": "favorable", "scope": "tactical/hourly",
      "cat": [ { "id": "ln_khoa_...", "name": "...", "citations": ["..."] } ],
      "hung": [], "cast_ref": "ln:...", "interp_ref": null } ],
  "agreement": { "agree": true,
    "summary": "Both systems read the near-term as supportive at tactical scope.",
    "by_scope": [ { "scope": "tactical", "agree": true } ] },
  "request_echo": { "...": "the request above" } }
```

## §9 - Open questions

- Does the agreement view include a RAG-003 interpretation per system or only the deterministic stance? Default: the deterministic stance + cat / hung for the agreement; interpretation is optional (`interp_ref`) and per-system, never merged.
- Stance granularity (3-band favorable / mixed / unfavorable vs a score). Default: 3-band from the documented cach cuc rule; a score is an internal detail, the band is what the agreement compares.
- Two engines vs all three at MVP. Default: two (Ky Mon + Luc Nham); the third (Thai At) activates at FR-TAT-006 (P2), which is why this FR is P2.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Merged verdict | the result collapses systems into one answer | forbidden; per-system reads kept separate; no verdict field (Claude-07 s1.4) |
| Re-cast / merge chart | STRAT casts or fuses charts | forbidden; calls the engines; a test asserts no direct casting |
| Scope ignored | divergent scopes reported as a contradiction | scope stamped per read; the agreement annotates `by_scope` |
| Stance not explainable | `stance` != its cat / hung | documented pure rule; explainability test |
| Missing engine | a requested system has no engine yet (e.g. Thai At pre-TAT-006) | typed "system unavailable", not a silent drop |

## §11 - Notes

Package `tamthuc_strat` (Python, DEC-2). Cross-system validate is the P2 strategic tool that runs two or more engines for one question and shows agreement vs divergence, honestly annotated by scope (Claude-07 s1.4): Luc Nham tactical / hourly, Ky Mon tactical / layout, Thai At strategic / long-range. It calls the engines and never re-casts (strategy 4.3), derives each stance from the envelope cach cuc by a documented rule, and never merges the systems into a single verdict - the divergence is the signal. Decision support, not a prediction (strategy 7). Depends on FR-QMDG-006 + FR-LN-006; the third system joins at FR-TAT-006.
