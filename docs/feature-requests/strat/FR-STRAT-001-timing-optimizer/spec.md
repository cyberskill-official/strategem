---
id: FR-STRAT-001
title: "Timing Optimizer - given a date-range + question type, scan candidate times, cast QiMen for each via the engine, score windows by cat/hung cach cuc, return the top recommended windows with explainable scores and citations"
module: STRAT
priority: MUST
status: ready_to_implement
phase: P1
slice: 1
lang: python
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 5, strategy 7, Claude-07 s1.1, Grok-02]
related_frs: [FR-STRAT-002, FR-STRAT-003, FR-STRAT-004, FR-QMDG-006, FR-QMDG-007, FR-RULE-003, FR-PLAT-002, FR-PLAT-006]
depends_on: [FR-QMDG-006, FR-RULE-003]
blocks: [FR-STRAT-002]
new_paths:
  - packages/tamthuc_strat/__init__.py
  - packages/tamthuc_strat/models.py
  - packages/tamthuc_strat/timing_optimizer.py
  - packages/tamthuc_strat/scoring.py
  - packages/tamthuc_strat/tests/test_timing_optimizer.py
  - packages/tamthuc_strat/tests/fixtures/timing_windows.json
---

## §1 - Description (BCP-14 normative)

This FR builds the product's headline strategic tool: the Timing Optimizer. Given a date range and a question type, it scans candidate times, casts QiMen for each via the engine, scores each window by its cat / hung cach cuc, and returns the top recommended windows with their scores. It is the technical form of trach thoi / trach nhat (choosing a good time for an action, Claude-07 s1.1).

The module SHALL accept a `TimingRequest` (start, end, granularity, question type, timezone, longitude, school flags, top_n) and enumerate candidate instants across the range at the chosen granularity. For each candidate it SHALL cast a QiMen chart by calling the FR-QMDG-006 engine and SHALL NOT re-implement any casting logic - the chart, its plates, and its detected `cach_cuc` come only from the engine (strategy 4.3). It SHALL score each window as a documented, deterministic function over the envelope's `cach_cuc` (polarity and score), using FR-RULE-003 to select and weight the patterns that matter for the question type; when a phuong vi (direction) component is present the score MAY include a directional-favorability term. It SHALL rank the windows and return the top_n with, for each, the score, the contributing cat and hung cach cuc (with citations), and a reference to the cast.

The module SHALL be deterministic: identical request plus identical flags yields identical ranked windows. The result is a decision-support signal, never a verdict: every window SHALL carry its contributing patterns and citations so the score is explainable, and any interpretation prose attached downstream SHALL carry an AIDisclosure (strategy 7). Interpretation itself is the RAG branch's job; STRAT-001 returns the scored structure.

## §2 - Why this design (rationale for humans)

The product is named and positioned around strategic timing (strategy 3.4). The lookup flow answers "what does this chart say"; the Timing Optimizer answers the question a decision-maker actually asks: "of all the times I could do this, which are best, and why". That turn - from one chart to a ranked, explained set of windows over a real range - is the "Strategem" in the product name (Claude-07 s1.1, Grok-02).

The optimizer must call the engine and never cast its own chart, for the same reason the whole platform splits deterministic casting from everything else: if STRAT re-implements dinh cuc or plate placement, it will drift from the oracle-gated engine and quietly recommend the wrong hour. Scanning through FR-QMDG-006 (with the FR-PLAT-006 chart cache making repeat casts cheap) keeps every recommendation traceable to an oracle-exact chart.

The score is a pure, documented function of the chart's `cach_cuc` so it is explainable. A timing tool that returned a bare number would be a black box and, worse, would read as a fortune-telling verdict. Returning the contributing cat / hung patterns with citations makes the recommendation a transparent, auditable decision aid - the responsible-positioning rule (strategy 7) expressed as a feature.

## §3 - Contract (models and process)

### Models (`packages/tamthuc_strat/models.py`)

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta

class TimingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: datetime
    end: datetime
    granularity: str                  # "gio" (2h) | "ngay" | ISO 8601 duration
    loai_cau_hoi: str                 # question type -> dung than palace filter
    tz: str
    kinh_do: float
    co_truong_phai: dict              # QiMen school flags, passed through to the engine
    top_n: int = 5

class ScoredWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: datetime
    end: datetime
    score: float
    cat: list[dict]                   # contributing cat cach cuc (id, name, score, citations)
    hung: list[dict]                  # contributing hung cach cuc
    cast_ref: str                     # cache key / id of the QMDG-006 envelope

class TimingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    windows: list[ScoredWindow]       # ranked, length <= top_n
    request_echo: TimingRequest
```

### Process

1. Enumerate candidate instants across `[start, end]` at `granularity` (QiMen changes per gio / per cuc; the default scan granularity is gio).
2. For each candidate, cast via the FR-QMDG-006 engine client (cache-keyed by FR-PLAT-002 rules) -> la so envelope. Never compute plates in STRAT.
3. Select the relevant `cach_cuc` for `loai_cau_hoi` via FR-RULE-003 (per-system filter + match); default all-palace until FR-QMDG-007 (dung than by question type) narrows to the dung than palace.
4. Score = a documented aggregation over the selected `cach_cuc` (sum of cat scores minus sum of hung scores, each pattern's own `score` and `polarity` from the envelope), plus an optional phuong vi term.
5. Rank by score; break ties by earliest instant first; return the top_n with contributing patterns + citations + `cast_ref`.

Determinism: the scan reuses the chart cache and the score is pure, so the same request returns the same ranked windows. An inverted range (`end < start`) returns a typed error; `start == end` returns exactly one window.

## §4 - Acceptance criteria

1. For a fixed range + granularity + flags, the scan produces exactly one candidate per granularity step and one `ScoredWindow` each, in deterministic order.
2. Each candidate is cast via the FR-QMDG-006 engine (a repeat scan hits the cache); a test asserts STRAT calls the engine and does not compute plates itself.
3. `score` is a pure function of the selected `cach_cuc` (polarity + score) for the question type; the same envelope yields the same score.
4. The returned windows are the `top_n` highest scores, ties broken by earliest instant first.
5. Each window lists its contributing cat and hung cach cuc with citations, and its `score` equals the documented aggregation of exactly those listed patterns (explainability).
6. `start == end` returns one window; `end < start` raises a typed error, not an empty result.

## §5 - Verification

- pytest with a stub engine returning known envelopes over a small range: assert candidate count, per-window scoring, ranking, tie-break, and top_n selection.
- Determinism test: the same request twice yields identical results; the second scan hits the cache (spy on the engine client).
- Explainability test: each window's `score` equals the documented aggregation of its listed cat/hung patterns.
- Property: adding a hung cach cuc to a candidate's envelope never raises its window score; adding a cat never lowers it (monotonicity).
- Boundary: `start == end` (one window); `end < start` (typed error); a long range at fine granularity trips the candidate cap with a typed error.
- Gates: `python -m pytest packages/tamthuc_strat`, `ruff check`, `mypy packages/tamthuc_strat`.

## §6 - Implementation skeleton

1. Create the `tamthuc_strat` package (`models.py`, `timing_optimizer.py`, `scoring.py`, `tests/`).
2. `models.py`: `TimingRequest`, `ScoredWindow`, `TimingResult`.
3. `timing_optimizer.py`: enumerate candidates by granularity; call the FR-QMDG-006 engine client per candidate (cache-keyed); collect envelopes.
4. `scoring.py`: the documented weighting over `cach_cuc` polarity/score; FR-RULE-003 selection for the question type; the optional phuong vi term.
5. Rank + top_n + tie-break; attach contributing patterns + citations + `cast_ref`.
6. Expose the STRAT API endpoint; tests with a stub engine and golden windows.

## §7 - Dependencies

Depends on FR-QMDG-006 (casts each candidate chart and emits the `cach_cuc`) and FR-RULE-003 (selects and weights the patterns that matter for the question type). Reads the FR-PLAT-002 envelope and benefits from FR-PLAT-006 (chart cache makes the scan cheap). Blocks FR-STRAT-002 (Scenario Comparison compares `TimingResult`s across options). When FR-QMDG-007 (dung than by question type) lands, the palace filter tightens from all-palace to the dung than palace.

## §8 - Example payloads

Request over one day at gio granularity, and the ranked result (abridged):

```json
// request
{ "start": "2004-01-01T00:00:00", "end": "2004-01-01T23:59:59", "granularity": "gio",
  "loai_cau_hoi": "trach_thoi", "tz": "+07:00", "kinh_do": 106.7,
  "co_truong_phai": { "dingju_method": "chaibu", "pan_method": "zhuan", "yin_yang_pan": "duong" },
  "top_n": 2 }

// result
{ "windows": [
    { "start": "2004-01-01T10:00:00", "end": "2004-01-01T12:00:00", "score": 1.7,
      "cat": [ { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "score": 0.9,
                 "citations": ["Yen Ba Dieu Tau Ca"] } ],
      "hung": [], "cast_ref": "qmdg:2004-01-01T11:00+07:..." },
    { "start": "2004-01-01T06:00:00", "end": "2004-01-01T08:00:00", "score": 0.4,
      "cat": [ { "id": "...", "name": "...", "score": 0.4, "citations": ["..."] } ],
      "hung": [ { "id": "...", "name": "...", "score": -0.0, "citations": ["..."] } ],
      "cast_ref": "qmdg:2004-01-01T07:00+07:..." }
  ],
  "request_echo": { "...": "the request above" } }
```

## §9 - Open questions

- Default granularity: QiMen changes per gio (2h) and per cuc; default gio-level scan, with an optional coarser day-level pre-filter for long ranges (perf). Confirm against p95 once FR-QMDG-006 timing is known; FR-PLAT-006 cache makes the scan cheap.
- Cross-engine timing: should the optimizer also consult LiuRen for a concrete yes/no on the chosen time? Deferred to FR-STRAT-004 (cross-system validate); STRAT-001 is QiMen-only, which is its trach thoi strength (Claude-07 s1.1).
- Score weights: fixed or per-question configurable? Default fixed and documented; expose as config only if evals show a need. The weighting is versioned so a change is auditable.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| STRAT recomputes a chart | optimizer implements casting itself | forbidden; must call FR-QMDG-006; a test asserts the engine is invoked |
| Non-deterministic ranking | unstable sort / tie not broken | deterministic tie-break (earliest instant first); repeat-run equality test |
| Unbounded scan | a huge range at fine granularity | cap candidate count / require coarser granularity for long ranges; typed error past the cap |
| Score not explainable | window score != sum of its listed patterns | explainability test ties the score to the contributing cach_cuc |
| Inverted range | `end < start` | typed error, not an empty result |

## §11 - Notes

Package `tamthuc_strat` (Python, DEC-2). The Timing Optimizer is the product's headline strategic tool: it turns the QiMen engine's per-instant cat / hung cach cuc into a ranked set of recommended windows for a real decision (trach thoi, Claude-07 s1.1). STRAT is where the "Strategem" positioning lives - a scored, explainable, cited timing recommendation framed as decision support, never a verdict (strategy 7). It scans via the engine and never casts a chart itself; the score is a pure, documented function of the envelope's `cach_cuc`, so every recommendation is auditable. FR-STRAT-002 builds Scenario Comparison on top of this. refs Claude-07 s1.1, Grok-02.
