---
id: FR-STRAT-002
title: "Scenario Comparison - run the Timing Optimizer (STRAT-001) across multiple candidate options/dates and compare their ranked windows side by side, each window carrying its cat/hung reasons; calls STRAT-001 per scenario and never casts or scores a chart itself"
module: STRAT
priority: SHOULD
status: done
phase: P1
slice: 1
lang: python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 5, strategy 7, Claude-07 s1.1, Grok-02]
related_frs: [FR-STRAT-001, FR-STRAT-003, FR-STRAT-004, FR-QMDG-006, FR-PLAT-006, FR-WEB-007]
depends_on: [FR-STRAT-001]
blocks: []
new_paths:
  - packages/tamthuc_strat/scenario_compare.py
  - packages/tamthuc_strat/tests/test_scenario_compare.py
  - packages/tamthuc_strat/tests/fixtures/scenarios.json
---

## §1 - Description (BCP-14 normative)

This FR builds Scenario Comparison on top of the Timing Optimizer. Given several named candidate scenarios (each an option or a date range for the same decision), it runs FR-STRAT-001 for each and returns their ranked windows side by side, every window carrying its contributing cat / hung cach cuc and citations (Grok-02, Claude-07 s1.1).

The module SHALL accept a `ScenarioSet` (a list of named `Scenario`, each wrapping a STRAT-001 `TimingRequest`) and SHALL obtain each scenario's ranked windows by calling the FR-STRAT-001 optimizer. It SHALL NOT cast a chart, re-implement casting, or re-score windows itself - STRAT-001 (through the FR-QMDG-006 engine) is the only source of windows and scores (strategy 4.3). It SHALL produce a `ScenarioComparison`: per scenario the ranked windows (top_n) with their reasons, plus a cross-scenario view ranking the scenarios by their best window and surfacing the single best window overall. The module SHALL be deterministic: identical scenario set plus identical flags yields an identical comparison. The result is a decision-support signal, never a verdict: every window keeps its patterns and citations so the comparison is explainable, and any interpretation prose attached downstream carries an AIDisclosure (strategy 7).

## §2 - Why this design (rationale for humans)

The Timing Optimizer answers "which time is best for this one action". The next question a decision-maker asks is comparative: "option A next Tuesday, option B next month, option C at our preferred venue - which scenario is best, and why" (Grok-02). That is Scenario Comparison.

Building it as a thin composition over STRAT-001, rather than a new scorer, is deliberate. STRAT-001 already casts through the engine and produces explainable, cited windows, so comparison is a matter of running it per scenario and laying the results side by side. If STRAT-002 re-scored or re-cast, it could diverge from the engine-gated results the user already trusts from STRAT-001 - so it reuses them exactly. The FR-PLAT-006 chart cache makes N scenarios cheap because overlapping instants are cast once. Keeping each window's cat / hung reasons through the comparison is what makes the answer auditable, a transparent side-by-side rather than a leaderboard of bare numbers (strategy 7).

## §3 - Contract (models and process)

### Models (`packages/tamthuc_strat/scenario_compare.py`)

Reuses `TimingRequest` and `ScoredWindow` from FR-STRAT-001.

```python
from pydantic import BaseModel, ConfigDict
from .models import TimingRequest, ScoredWindow

class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str                        # "Option A - launch 12 Mar", ...
    request: TimingRequest            # a STRAT-001 request

class ScenarioSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenarios: list[Scenario]
    top_n: int = 3                    # windows kept per scenario

class ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    windows: list[ScoredWindow]       # from STRAT-001, ranked
    best_score: float                 # windows[0].score, or -inf if none

class ScenarioComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")
    results: list[ScenarioResult]     # one per scenario
    ranked_labels: list[str]          # scenarios ranked by best_score
    best_overall: ScoredWindow | None
```

### Process

1. For each `Scenario`, call the FR-STRAT-001 optimizer with its `TimingRequest` -> `TimingResult` (which casts via the engine, cache-keyed). Never cast or score here.
2. Build a `ScenarioResult` per scenario from its windows; `best_score` = the top window's score (or -inf if the scenario yielded no windows).
3. Rank scenarios by `best_score` (tie-break: earliest best window, then input order) -> `ranked_labels`; `best_overall` = the single highest window across all scenarios.

Determinism follows from STRAT-001's determinism plus a stable sort. An empty `ScenarioSet` returns an empty comparison; a scenario with no windows has `best_score = -inf` and sorts last, never silently dropped.

## §4 - Acceptance criteria

1. For a set of scenarios, the module returns one `ScenarioResult` per scenario, each with STRAT-001's ranked windows (top_n) and their cat / hung + citations preserved.
2. STRAT-002 obtains windows only via STRAT-001; a test asserts it calls the optimizer and does not cast or score charts itself.
3. `ranked_labels` orders scenarios by `best_score`, ties broken by earliest best window then input order; `best_overall` is the single highest window across scenarios.
4. Each preserved window still lists its contributing patterns and citations (explainability carried through unchanged from STRAT-001).
5. Determinism: the same `ScenarioSet` twice yields an identical comparison; overlapping instants hit the FR-PLAT-006 cache.
6. Empty set returns an empty comparison; a scenario yielding zero windows sorts last with `best_score = -inf`, not dropped.

## §5 - Verification

- pytest with a stub STRAT-001 optimizer returning known `TimingResult`s per scenario: assert per-scenario windows, `best_score`, `ranked_labels`, `best_overall`, and the tie-breaks.
- No-recompute test: a spy on the engine client asserts STRAT-002 never calls it directly; only STRAT-001 does.
- Explainability: a compared window's patterns and citations equal STRAT-001's for that window (carried through).
- Determinism: repeat-run equality; a cache hit on overlapping instants.
- Boundary: empty set; a scenario yielding zero windows sorts last, still present.
- Gates: `python -m pytest packages/tamthuc_strat`, `ruff check`, `mypy packages/tamthuc_strat`.

## §6 - Implementation skeleton

1. `scenario_compare.py`: `Scenario`, `ScenarioSet`, `ScenarioResult`, `ScenarioComparison`.
2. `compare(scenario_set, optimizer) -> ScenarioComparison`: call STRAT-001 per scenario; build results.
3. Stable ranking by `best_score` + `best_overall` + tie-break.
4. Expose the STRAT comparison endpoint; tests with a stub optimizer and golden scenarios (`fixtures/scenarios.json`).

## §7 - Dependencies

Depends on FR-STRAT-001 (the Timing Optimizer whose `TimingResult`s it composes; reuses its `TimingRequest` / `ScoredWindow` models). Benefits from FR-PLAT-006 (the chart cache makes N scenarios cheap). Reads the FR-QMDG-006 engine only transitively through STRAT-001. Feeds FR-WEB-007 (the management / compare flow). Sibling to FR-STRAT-003 and FR-STRAT-004. Nothing depends on it (blocks empty).

## §8 - Example payloads

```json
// ScenarioComparison (abridged) - two candidate launch options
{ "results": [
    { "label": "Option A - 12 Mar",
      "windows": [ { "start": "2026-03-12T10:00:00", "end": "2026-03-12T12:00:00", "score": 1.7,
        "cat": [ { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "score": 0.9,
                   "citations": ["Yen Ba Dieu Tau Ca"] } ], "hung": [], "cast_ref": "qmdg:..." } ],
      "best_score": 1.7 },
    { "label": "Option B - 3 Apr",
      "windows": [ { "start": "2026-04-03T06:00:00", "end": "2026-04-03T08:00:00", "score": 0.4,
        "cat": [ { "id": "...", "name": "...", "score": 0.4, "citations": ["..."] } ],
        "hung": [], "cast_ref": "qmdg:..." } ],
      "best_score": 0.4 } ],
  "ranked_labels": ["Option A - 12 Mar", "Option B - 3 Apr"],
  "best_overall": { "start": "2026-03-12T10:00:00", "end": "2026-03-12T12:00:00", "score": 1.7,
    "cat": [ { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "score": 0.9,
               "citations": ["Yen Ba Dieu Tau Ca"] } ], "hung": [], "cast_ref": "qmdg:..." } }
```

## §9 - Open questions

- Should scenarios allow different question types or systems, or must they share one? Default: the same `loai_cau_hoi` for a meaningful comparison; a mix is allowed but the UI labels the difference.
- Cross-scenario normalization: scores are comparable because they share STRAT-001's documented scale; no re-normalization. If scenarios use different granularities, note it; per-window scores stay comparable.
- How many scenarios is reasonable (perf). Default: a small cap (e.g. 8) with the cache; a typed error past the cap, like STRAT-001's scan cap.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| STRAT re-casts / re-scores | comparison computes windows itself | forbidden; must call STRAT-001; a test asserts no direct casting or scoring |
| Non-deterministic ranking | unstable sort / tie not broken | deterministic tie-break (earliest best window, then input order); repeat-run equality |
| Dropped empty scenario | a zero-window scenario silently omitted | it sorts last with `best_score = -inf`, still present |
| Reasons lost | a compared window drops its patterns / citations | carried through unchanged from STRAT-001; explainability test |
| Unbounded set | too many scenarios | cap + typed error |

## §11 - Notes

Package `tamthuc_strat` (Python, DEC-2). Scenario Comparison is the second strategic tool and a thin, honest composition over the Timing Optimizer: run STRAT-001 per candidate option or date, lay the ranked windows side by side, rank the scenarios by their best window, and keep every window's cat / hung reasons and citations (Grok-02, Claude-07 s1.1). It never casts or scores a chart itself - STRAT-001, through the FR-QMDG-006 engine, is the single source of windows - so a comparison can never disagree with the optimizer the user already trusts. Decision support, not a verdict (strategy 7).
