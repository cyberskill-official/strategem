---
id: TASK-STRAT-003
title: "Chu-khach decision framework - reframe a RAG-003 interpretation into the four-step decision analysis from Claude-07 s2.2 (define question + dung than for each party; read the structured signals; set them beside real-world context; the user decides), with the chu-khach host/guest lens mapped to competitor / risk / partner analysis; reads RAG-003 + the la so, never re-computes a chart"
module: STRAT
priority: SHOULD
status: done
phase: P1
slice: 1
lang: python/ts
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s2.2, Claude-07 s1.3, strategy 7, strategy 4.3]
related_frs: [TASK-RAG-003, TASK-PLAT-002, TASK-STRAT-001, TASK-STRAT-004, TASK-WEB-003, TASK-LEGAL-003]
depends_on: [TASK-RAG-003]
blocks: []
new_paths:
  - packages/tamthuc_strat/chu_khach.py
  - packages/tamthuc_strat/tests/test_chu_khach.py
  - apps/web/src/lib/strat/chuKhachFramework.ts
  - apps/web/src/lib/strat/chuKhachFramework.test.ts
---

## §1 - Description (BCP-14 normative)

This task turns a TASK-RAG-003 interpretation into the four-step chu khach 主客 decision framework from Claude-07 s2.2, so a reading is presented as decision analysis rather than a verdict. Given a la so envelope (TASK-PLAT-002) and a RAG-003 `Interpretation`, the module SHALL assemble a `DecisionFrame` with four steps: (1) framing - define the question and choose the dung than 用神 for the matter and for each party (chu 主 = self / initiator, khach 客 = other / counterparty); (2) signals - the structured signals read from the chart (dung than relations, chu-khach posture, cach cuc), copied from the envelope and the interpretation, each cited; (3) context - the place where the user sets those signals beside real-world facts (the tool supplies prompts, never invents facts); (4) decision - explicitly the user's, carrying the AIDisclosure and a "you decide" framing.

The module SHALL read the envelope and the interpretation read-only and SHALL NEVER cast or re-compute a chart (strategy 4.3). The chu-khach host / guest lens SHALL map to competitor / risk / partner analysis (Claude-07 s1.3): self vs competitor, action-as-chu vs external-event-as-khach, self vs partner or hire. A TypeScript presenter SHALL render the four steps in the results UI (TASK-WEB-003) as decision analysis. No step SHALL contain a certain-future or medical / legal / financial verdict (TASK-LEGAL-003).

## §2 - Why this design (rationale for humans)

This is the product's positioning made into a feature (Claude-07 s2.1-2.2, strategy 7). The same la so can read as a fortune ("you will win") or as a decision frame ("here is how the two sides sit; you decide"). STRAT-003 forces the second: it never adds a signal the engine or the cited interpretation did not provide, and it ends, structurally, at the user's own decision - step four is not a recommendation, it is a handoff.

The chu-khach lens is the reason Tam Thuc maps so cleanly onto modern decision analysis (Claude-07 s1.3): host / guest is already a two-sided, structured comparison, so competitor analysis, risk analysis, and partner or personnel decisions all fit the same frame with different party labels. Keeping the tool read-only over the chart (strategy 4.3) and cited at every signal (Claude-06) is what keeps this a decision aid rather than a dressed-up prediction. The Python side owns the frame; the TypeScript presenter owns the affordance - the same split the AIDisclosureBadge follows, legal / logic owning the substance and the component owning the surface.

## §3 - Contract (models and mapping)

### Models (`packages/tamthuc_strat/chu_khach.py`)

Imports `AIDisclosure` from the TASK-RAG-003 schema so the shapes never drift.

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict
from tamthuc_rag.schema import AIDisclosure

class DungThanAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    party: Literal["chu", "khach"]    # chu 主 = self / initiator; khach 客 = other
    role_label: str                   # "us" | "the competitor" | "the risk event" | "the partner"
    dung_than: str                    # the chosen dung than for this party
    cung: int | None = None           # palace, if applicable

class Signal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str                         # dung_than_relation | chu_khach_posture | cach_cuc
    reading: str                      # from the interpretation, decision-framed
    citations: list[str]              # citation_ids from RAG-003; each must exist in the interpretation

class DecisionHandoff(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str                       # "Weigh the signals against your context and decide."
    disclosure: AIDisclosure          # carried from RAG-003; never a verdict

class DecisionFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str
    lens: Literal["competitor", "risk", "partner"]
    step1_framing: list[DungThanAssignment]
    step2_signals: list[Signal]
    step3_context_prompts: list[str]
    step4_decision: DecisionHandoff
```

### The chu-khach lens mapping (Claude-07 s1.3)

| Lens | chu 主 (self) | khach 客 (other) |
|---|---|---|
| competitor | us | the competitor |
| risk | the action we take | the external event |
| partner | us | the partner / hire |

`build_frame(la_so, interp, lens)` reads both read-only, assigns the dung than per party, copies the cited signals from the interpretation, sets the step-three context prompts, and ends at the step-four handoff. It is pure, does no I/O, and makes no engine call. `chuKhachFramework.ts` mirrors the `DecisionFrame` type and renders the four steps.

## §4 - Acceptance criteria

1. `build_frame` returns a `DecisionFrame` with all four steps: framing (dung than per party), signals (cited), context prompts, and a decision handoff carrying the AIDisclosure.
2. Every `Signal` carries at least one `citation_id` that exists in the RAG-003 interpretation's citations (no uncited signal; no fabricated id).
3. Step four is a handoff, not a recommendation: it contains no imperative verdict and no certain-future / medical / legal / financial claim (aligned with TASK-LEGAL-003).
4. The lens maps chu / khach to the right party labels for competitor / risk / partner (the s1.3 table).
5. `build_frame` performs no engine call and never mutates the envelope or the interpretation (a read-only test diffs both before and after).
6. The TS `DecisionFrame` type matches the Python schema (parity check) and the presenter renders four steps.

## §5 - Verification

- `test_chu_khach.py`: a golden la so + a golden RAG-003 `Interpretation` -> a golden `DecisionFrame` per lens; assert the step structure, the party mapping, and that every signal's citations are a subset of the interpretation's citation ids.
- Read-only: deep-copy the envelope and the interpretation, run `build_frame`, assert both are byte-identical after and that no engine / retriever client was invoked (a spy).
- Framing guard: an adversarial interpretation with a verdict phrase does not leak into step four; findings align with the TASK-LEGAL-003 checks.
- TS: `chuKhachFramework.test.ts` snapshot-renders the four steps for a fixture `DecisionFrame`; a type-parity check ties the TS type to the Python schema.
- Gates: `python -m pytest packages/tamthuc_strat`, `ruff check`, `mypy packages/tamthuc_strat`; `pnpm -C apps/web typecheck`, `pnpm -C apps/web test`.

## §6 - Implementation skeleton

1. `chu_khach.py`: `DungThanAssignment`, `Signal`, `DecisionHandoff`, `DecisionFrame`; import `AIDisclosure` from the RAG-003 schema.
2. `build_frame(la_so, interp, lens)`: assign the dung than per party; copy the cited signals; set the context prompts; build the handoff; pure and read-only.
3. The lens mapping table (competitor / risk / partner).
4. `chuKhachFramework.ts`: the mirrored type and a four-step presenter for TASK-WEB-003.
5. tests: golden frames per lens, the read-only invariant, the citation-subset check, TS parity + snapshot.

## §7 - Dependencies

Depends on TASK-RAG-003 (the `Interpretation` it reframes and whose citations and AIDisclosure it carries; reuses the AIDisclosure shape). Reads the TASK-PLAT-002 la so envelope read-only for the dung than and chu-khach positions. Renders in TASK-WEB-003 (results screen). Aligned with TASK-LEGAL-003 (no verdict in step four). Sibling to TASK-STRAT-001 and TASK-STRAT-004. Nothing depends on it (blocks empty).

## §8 - Example payloads

```json
// DecisionFrame (competitor lens, abridged)
{ "question": "Should we enter the northern market this quarter?",
  "lens": "competitor",
  "step1_framing": [
    { "party": "chu", "role_label": "us", "dung_than": "nhat can", "cung": 1 },
    { "party": "khach", "role_label": "the competitor", "dung_than": "ung than", "cung": 7 } ],
  "step2_signals": [
    { "kind": "chu_khach_posture", "reading": "the acting side holds the initiative this window",
      "citations": ["yba_dieu_012"] },
    { "kind": "cach_cuc", "reading": "a cat cach cuc sits on the acting palace",
      "citations": ["yba_dieu_012"] } ],
  "step3_context_prompts": [
    "What is the competitor's actual position and timing?",
    "What resources can you commit this quarter?" ],
  "step4_decision": { "prompt": "Weigh the signals against your context and decide.",
    "disclosure": { "model": "gpt-4o-mini", "limits": "decision support, not a verdict; no medical/legal/financial advice",
      "review_status": "not_required" } } }
```

## §9 - Open questions

- Does STRAT-003 choose the lens or the user? Default: the user picks the lens (competitor / risk / partner) at request time; the mapping is fixed per lens.
- Dung than selection: from the question type (the TASK-QMDG-007 mapping) or user-specified parties? Default: seed from the question type + interpretation, let the user relabel parties (`role_label` is free text).
- Multi-party (more than two)? Default: the frame is two-sided (chu / khach) at MVP, matching the classical lens; multi-party is a later extension.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Verdict in step four | the handoff carries a recommendation / certain-future | forbidden; step four is a handoff; framing guard + TASK-LEGAL-003 |
| Uncited / fabricated signal | a signal with no citation or an id not in the interpretation | rejected; every signal cites an existing RAG-003 id |
| Chart re-computed | the frame casts or edits the chart | forbidden; read-only over envelope + interpretation; byte-equality test |
| Wrong party mapping | chu / khach swapped for the lens | the s1.3 mapping table is fixed and tested |
| TS / Python drift | the presenter type diverges from `DecisionFrame` | parity check fails |

## §11 - Notes

Package `tamthuc_strat` (Python) + a TS presenter in `apps/web` (DEC-2). The chu-khach framework is the positioning of the whole product turned into a tool (Claude-07 s2.1-2.2): a reading presented as a four-step decision analysis that ends at the user's own decision, never a verdict (strategy 7). The host / guest lens is why Tam Thuc maps so naturally onto competitor, risk, and partner analysis (Claude-07 s1.3) - two structured sides, different labels. It reads RAG-003 and the la so read-only and adds no signal the engine or the cited interpretation did not provide (strategy 4.3), so the frame is a decision aid, not a prediction. Python owns the frame; the TS presenter owns the affordance.
