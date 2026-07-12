---
id: FR-RAG-006
title: "Interpretation eval loop - score interpretations on faithfulness (grounded in retrieved text), relevance, and citation accuracy against the KB-002 150-200 validation set; committed baseline per prompt_version; a CI gate fails on regression beyond a threshold; the RISK-9 way interpretation regressions are caught"
module: RAG
priority: MUST
status: done
phase: P2
slice: 1
lang: python
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.3, strategy RISK-9, strategy 8]
related_frs: [FR-RAG-003, FR-KB-002, FR-RAG-001, FR-RAG-002, FR-RAG-005, FR-PLAT-004]
depends_on: [FR-RAG-003, FR-KB-002]
blocks: []
new_paths:
  - packages/tamthuc_rag/tamthuc_rag/eval/__init__.py
  - packages/tamthuc_rag/tamthuc_rag/eval/cases.py
  - packages/tamthuc_rag/tamthuc_rag/eval/metrics.py
  - packages/tamthuc_rag/tamthuc_rag/eval/judge.py
  - packages/tamthuc_rag/tamthuc_rag/eval/run.py
  - packages/tamthuc_rag/tamthuc_rag/eval/baseline.json
  - packages/tamthuc_rag/tests/test_eval.py
  - packages/tamthuc_rag/tests/fixtures/eval_cases_sample.json
  - docs/contracts/eval-report.schema.json
---

## §1 - Description (BCP-14 normative)

This FR is the measurable-quality gate for interpretation: it scores FR-RAG-003's output on faithfulness, relevance, and citation accuracy against the FR-KB-002 validation set of 150-200 cited cases, compares to a committed baseline, and fails CI on a regression beyond a threshold. It is the RISK-9 mitigation made executable - the mechanism by which interpretation regressions are caught before they ship (strategy RISK-9; Claude-06 s4.3). It scores the interpreter; it does not change it, and it produces no user-facing interpretation.

The eval set SHALL be the FR-KB-002 `validation_cases()` projection: each seeded pattern becomes a case carrying `id`, `version`, `system`, `conditions`, `expected_polarity`, `meaning_classical`, and `expected_citations`. For each case the loop SHALL run FR-RAG-003's `interpret` over a retrieval context built from the case, and SHALL score three metrics: (1) faithfulness - every asserted claim is grounded in the retrieved passages it cites, with a deterministic lower bound (every claim carries a citation present in the retrieved set) and an optional stronger judge; (2) relevance - the reading addresses the case's question and conveys its `expected_polarity`; (3) citation accuracy - precision and recall of the emitted `citation_id`s against the case's `expected_citations`. Each case SHALL yield a `CaseScore`; the run SHALL aggregate an `EvalReport` stamped with the `prompt_version` under test.

The gate SHALL fail when any aggregate metric falls below its absolute threshold, OR when any metric regresses beyond a delta versus the committed baseline for the same `prompt_version` lineage. The baseline SHALL be a committed artifact (`eval/baseline.json`) updated only as a reviewed diff, so a prompt or retrieval change that lowers quality is a failing check, not a silent ship. The default CI eval SHALL be deterministic - FR-RAG-003 run with a stub or pinned LLM over the committed fixture cases - so the gate is reproducible; the full-set eval against a real pinned model SHALL run behind a marker. The loop SHALL stamp the exact `(case_id, case_version)` and `prompt_version` it scored, so a regression is always traceable to the versioned cases and prompt that produced it.

## §2 - Why this design (rationale for humans)

Interpretation quality is the one thing this product cannot afford to leave unmeasured, because the failure is invisible: a prompt tweak or a retrieval change can make readings subtly less grounded or less on-point, and nothing breaks, no test goes red, and the regression ships (strategy RISK-9). The only defense is a fixed corpus of known-answer cases scored every build, which is exactly why FR-KB-002 was authored to double as the validation set: each pattern already pairs a machine-checkable condition with a cited classical meaning, so the same 150-200 rows that the engine detects are the answer key the interpreter is graded against. This FR turns that answer key into a gate. Faithfulness, relevance, and citation accuracy are the three things that can silently rot, so they are the three things measured; a committed baseline turns "is it still as good as last release" from a memory into a diff.

The determinism discipline is what makes the gate trustworthy rather than flaky. A gate that depends on a live model's stochastic output would fail randomly and get muted, defeating its purpose, so the CI gate runs on a stub or pinned interpreter over committed cases and scores primarily on reproducible signals - citation-in-retrieved, expected-citation overlap, polarity conveyed. The stronger semantic judge (does this claim actually follow from this passage) is real and worth having, but it is advisory and marker-gated, reported as a tracked band rather than a hard pass, because it cannot be both non-deterministic and a blocking gate. Stamping the case and prompt versions is the last piece: because FR-KB-004 versions the cases and FR-RAG-003 versions the prompt, a regression report points at the exact versioned inputs, so the fix is targeted rather than a hunt. This FR is where the two invariants FR-RAG-003 rests on - never assert beyond the sources, never cite what was not retrieved - stop being rules and become a number that must not drop.

## §3 - Contract (cases, metrics, judge, run, gate)

### Eval case (`tamthuc_rag/eval/cases.py`)

```python
class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str; version: int                 # stamped from FR-KB-002 (case_id, case_version)
    system: System
    query: str                            # a probe question that should trigger this pattern
    conditions: dict                      # the pattern conditions (to build the retrieval context)
    expected_polarity: str                # cat | hung | trung
    meaning_classical: str
    expected_citations: list[str]

def load_cases(system: System | None = None) -> list[EvalCase]:
    # adapt FR-KB-002 validation_cases() -> EvalCase; build a synthetic ChartContext/RetrievalRequest
    # per case so FR-RAG-003.interpret can run without a live engine cast.
```

### Metrics (`tamthuc_rag/eval/metrics.py`)

```python
class CaseScore(BaseModel):
    case_id: str; case_version: int
    faithfulness: float          # 0..1 (deterministic lower bound; judge refines behind a marker)
    relevance: float             # 0..1 (polarity conveyed + question addressed)
    citation_precision: float    # emitted ids that are expected / emitted
    citation_recall: float       # expected ids that are emitted / expected
    passed: bool

def faithfulness(interp, retrieved) -> float:  # every claim carries a citation in the retrieved set
def relevance(interp, case) -> float:           # expected_polarity conveyed; recommendation on-topic
def citation_scores(interp, expected) -> tuple[float, float]:  # precision, recall vs expected_citations
```

### Optional judge (`tamthuc_rag/eval/judge.py`)

```python
class Judge(Protocol):
    version: str                 # pinned rubric + judge-prompt version, like FR-RAG-003's prompt_version
    def entails(self, claim: str, passage: str) -> float: ...   # NLI / LLM-judge, temperature 0

# advisory, marker-gated: refines faithfulness/relevance; reported as a band, never the hard gate.
```

### Run and report (`tamthuc_rag/eval/run.py`, `eval/baseline.json`)

```python
class EvalReport(BaseModel):
    prompt_version: str
    judge_version: str | None
    n_cases: int
    faithfulness: float; relevance: float
    citation_precision: float; citation_recall: float; citation_f1: float
    per_case: list[CaseScore]
    regressions: list[str]       # case_ids that dropped vs baseline
    baseline_ref: str | None

class Thresholds(BaseModel):
    faithfulness: float = 0.90; relevance: float = 0.80; citation_f1: float = 0.85
    max_regression_delta: float = 0.03

def evaluate(cases, interpret_fn, thresholds, baseline, judge=None) -> EvalReport: ...
def gate(report: EvalReport, thresholds: Thresholds, baseline: EvalReport) -> GateResult:
    # fail if any aggregate < its absolute threshold, OR any metric regresses > max_regression_delta
    # vs the committed baseline for this prompt_version lineage; name the failing metric + regressed cases.
```

The baseline is committed per `prompt_version`; a prompt change (new `prompt_version` from FR-RAG-003) requires a re-run and a reviewed baseline update. The gate runs in CI (FR-PLAT-004).

## §4 - Acceptance criteria

1. `load_cases` returns one `EvalCase` per FR-KB-002 seeded pattern with its `(id, version)` stamp and `expected_citations`; the count lands in the 150-200 band for the full set.
2. `faithfulness` scores 1.0 for an interpretation whose every claim cites a retrieved id and below 1.0 when a claim is uncited or cites outside the retrieved set (the deterministic lower bound tracks FR-RAG-003's guard).
3. `citation_precision`/`recall` are correct against a case's `expected_citations` (a hand-built case with known emitted vs expected ids scores as computed); `relevance` reflects whether the `expected_polarity` is conveyed.
4. `evaluate` aggregates an `EvalReport` stamped with `prompt_version`; `gate` fails when an aggregate is below threshold and when a metric regresses beyond `max_regression_delta` versus the committed baseline, naming the failing metric and regressed `case_id`s.
5. The default CI eval is deterministic: run with a stub/pinned interpreter over `fixtures/eval_cases_sample.json`, repeated runs produce an identical `EvalReport`; the real-model full-set eval is marker-gated.
6. A prompt change that lowers faithfulness on the fixture makes the gate fail until the baseline is updated as a reviewed diff (the RISK-9 regression catch).

## §5 - Verification

- `tests/test_eval.py`: metric correctness on hand-built cases (faithful vs uncited-claim vs fabricated-citation interpretations); citation precision/recall math; relevance/polarity scoring; `gate` pass and both fail paths (below-threshold and regression-vs-baseline) with the failing metric and regressed cases named; determinism of the stub eval (repeat runs equal).
- Baseline discipline: a test asserts a bumped `prompt_version` requires a matching baseline entry and that an unreviewed baseline drop fails the gate; `eval/baseline.json` validates against the committed report shape.
- Judge isolation: the marker-gated judge path is exercised with a stub `Judge` (fixed scores) so CI needs no live model; the judge contributes an advisory band, not the hard gate.
- Contract: `EvalReport` / `CaseScore` validate against `docs/contracts/eval-report.schema.json`; Pydantic/JSON-Schema parity in CI.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_rag`, `pytest packages/tamthuc_rag`; the interpretation-quality gate itself runs in CI on the fixture and behind a marker on the full set.

## §6 - Implementation skeleton

1. `eval/cases.py`: adapt FR-KB-002 `validation_cases()` to `EvalCase`, build the per-case synthetic `RetrievalRequest`/context so FR-RAG-003 runs without a live engine cast.
2. `eval/metrics.py`: `faithfulness` (deterministic lower bound), `relevance` (polarity + on-topic), `citation_scores` (precision/recall), `CaseScore`.
3. `eval/judge.py`: the `Judge` protocol and a stub; the marker-gated LLM/NLI judge with a pinned rubric version.
4. `eval/run.py`: `evaluate`, `EvalReport`, `Thresholds`, `gate` (absolute + regression-vs-baseline); commit an initial `eval/baseline.json`.
5. Author `docs/contracts/eval-report.schema.json`; wire the CI gate (fixture deterministic; full set marker-gated) into FR-PLAT-004.
6. Commit `fixtures/eval_cases_sample.json` (a handful of KB-002-shaped cases across systems, including a deliberately uncited-claim case) as the deterministic test exemplar.

## §7 - Dependencies

Depends on FR-RAG-003 (the interpreter it scores; it consumes the `prompt_version` and `retrieved_citation_ids` hooks FR-RAG-003 exposes for exactly this purpose) and FR-KB-002 (the 150-200 cited `validation_cases()` that are the answer key - authored to double as this RISK-9 dataset). Reads retrieval quality via FR-RAG-001/002 indirectly and provides the number that decides FR-RAG-005's expansion trade-off (recall lift vs faithfulness/precision). Runs its gate in CI through FR-PLAT-004; stamps the FR-KB-004-versioned case versions so regressions trace to exact inputs. Blocks nothing in the catalog, but it is the gate every interpretation-affecting change must pass. The RAG-branch invariant holds: this FR scores interpretations and never produces a user-facing one; it never writes `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`, and it measures - it does not weaken - the citation and AIDisclosure discipline.

## §8 - Example payloads

```json
// an EvalCase projected from a FR-KB-002 pattern
{ "id": "qimen_thanh_long_hoi_dau", "version": 2, "system": "qimen",
  "query": "co nen khoi su kinh doanh trong cua so nay khong",
  "conditions": { "type": "and", "rules": [ { "field": "cach_cuc", "operator": "contains",
    "value": "qimen_thanh_long_hoi_dau" } ] },
  "expected_polarity": "cat", "meaning_classical": "丙加值符, cát khí tụ tập, lợi cho khởi sự.",
  "expected_citations": ["yba_dieu_012"] }
```

```json
// an EvalReport (abbreviated) that fails the gate on a citation-accuracy regression
{ "prompt_version": "sys-1.1.0", "judge_version": null, "n_cases": 172,
  "faithfulness": 0.94, "relevance": 0.86, "citation_precision": 0.79,
  "citation_recall": 0.83, "citation_f1": 0.81,
  "regressions": ["qimen_phi_dieu_diet_huyet", "liuren_nguyen_thai"],
  "baseline_ref": "sys-1.0.0" }
```

## §9 - Open questions

- How much of faithfulness/relevance the deterministic checks can carry versus the judge. Default: the hard gate uses reproducible signals (citation-in-retrieved, expected-citation overlap, polarity conveyed); the semantic judge is advisory/marker-gated. Promote a judge signal to the hard gate only if it proves stable at temperature 0 with a tolerance.
- Absolute thresholds and the regression delta. Default: faithfulness 0.90, relevance 0.80, citation_f1 0.85, max regression 0.03; set the first real numbers from the initial full-set run and ratchet upward, never down without review.
- Whether per-case queries are authored or generated from the pattern. Default: author a probe query per flagship pattern; template the rest from `conditions` + `meaning_classical`; keep the probe queries versioned with the cases (FR-KB-004).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Silent quality regression | a prompt/retrieval change lowers grounding | gate fails on below-threshold or regression-vs-baseline; naming the metric + cases (RISK-9) |
| Flaky gate | eval depends on live-model stochasticity | default gate is deterministic (stub/pinned interpreter, reproducible signals); judge is advisory/marker-gated |
| Baseline gamed | baseline lowered to pass a bad change | baseline is a committed reviewed diff; an unreviewed drop fails; ratchet up, not down |
| Ruleset/test-set drift | cases diverge from the loaded patterns | cases derive from FR-KB-002 `validation_cases()`, so they are the loaded rows by construction |
| Untraceable regression | a drop with no versioned inputs | every score stamps `(case_id, case_version)` + `prompt_version`; regressions point at exact inputs |
| Judge masquerades as gate | non-deterministic judge blocks CI | judge reports a band, never the hard pass; only reproducible metrics gate |

## §11 - Notes

This FR is where FR-RAG-003's two invariants become a measured number: no claim beyond the sources, no citation the retriever did not supply, scored every build against the same 150-200 cited cases the engine detects. Its credibility rests on determinism - keep the hard gate reproducible and the semantic judge advisory - and on the committed baseline, which turns "still as good as last release" into a diff a human signs. Wire it into CI as soon as FR-RAG-003 and FR-KB-002 exist; it is the difference between interpretation quality being managed and being hoped for (RISK-9). The package `tamthuc_rag` is shared with FR-RAG-001/002/003/004/005/007; this FR adds the `eval/` module, so the RAG branch stays one installable, mypy-clean unit.
