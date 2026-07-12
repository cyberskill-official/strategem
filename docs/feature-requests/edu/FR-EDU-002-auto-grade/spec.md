---
id: FR-EDU-002
title: "Auto-graded chart practice - the deterministic engine as marker: the learner casts a chart step by step, the app diffs each step against the engine's la so and pinpoints the exact error (mis-placed khoa / mis-derived tam truyen / mis-seated sao)"
module: EDU
priority: SHOULD
status: ready_to_implement
phase: P3
slice: 1
lang: typescript
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 5, strategy 7, strategy 4.3, Claude-07 s3.3, Claude-07 s3]
related_frs: [FR-EDU-001, FR-EDU-003, FR-QMDG-006, FR-LN-006, FR-PLAT-002, FR-API-001, FR-CHART-001, FR-CHART-002, FR-WEB-001]
depends_on: [FR-QMDG-006, FR-LN-006]
blocks: []
new_paths:
  - apps/web/src/features/edu/practice/types.ts
  - apps/web/src/features/edu/practice/steps.ts
  - apps/web/src/features/edu/practice/grader.ts
  - apps/web/src/features/edu/practice/grader.test.ts
  - apps/web/src/features/edu/practice/PracticeFlow.tsx
---

## §1 - Description (BCP-14 normative)

This FR builds the learning flow's auto-graded chart practice: the learner casts a chart step by step, and the app grades each step by diffing it against the deterministic engine's chart, pointing at the exact place the learner diverged (Claude-07 s3.3). It consumes the criteria FR-EDU-001 marks `gradedBy: "engine"` and turns them into a graded exercise.

The module SHALL model the casting procedure of a system as an ordered ladder of `CastStep`s, each addressing a slice of the la so envelope (FR-PLAT-002) by JSON path: for QiMen the ladder mirrors the QMDG pipeline (dinh cuc -> dia ban -> truc phu / truc su -> thien ban -> cuu tinh / bat mon / bat than -> cach cuc), for LiuRen the LN pipeline (thien dia ban -> tu khoa -> tam truyen -> thien tuong). For a practice attempt the module SHALL obtain the canonical chart for the learner's input by casting through the existing path (FR-API-001, which calls the FR-QMDG-006 / FR-LN-006 engines) and SHALL treat that la so as the answer key, because one input yields exactly one chart (strategy 4.3, Claude-07 s3.3).

The grader SHALL be a pure function of `(step, learnerAnswer, referenceLaSo)`: it compares the learner's value for a step against the engine's value at that step's paths and returns a `StepResult` listing every mismatch as a `CellDiff` with a specific, localized message (for example "you seated 天蓬 at cung 3; the engine has 天芮 there"). Grading a whole attempt (`gradeCast`) SHALL walk the ladder in order, identify the earliest incorrect step as the root cause, and mark downstream steps that diverge only because of it as `blocked_by` that root rather than flooding the learner with cascade errors. The grader SHALL grade casting only (a fact against the engine) and SHALL NOT interpret the chart's meaning; interpretation stays in the cited AI layer (strategy 7). The practice surface SHALL render inside the FR-WEB-001 shell using Design System v1.3.0 components with no new tokens, reusing the FR-CHART-001 / FR-CHART-002 chart views for input.

## §2 - Why this design (rationale for humans)

The determinism the engine needs for correct casting is exactly what makes it an ideal marker (Claude-07 s3.3). Because a single input produces a single chart, a learner's step-by-step answer can be diffed against the engine's chart and the exact missed step named - an mis-placed khoa, a mis-derived tam truyen, a mis-seated sao (Claude-07 s3.3 lists these three verbatim). That is the most valuable feedback when practicing a many-step skill like lap ban: immediate and specific, not "wrong, try again." Building the grader on the engine rather than a hand-authored answer key means the answer key is never stale and never wrong - it is whatever the oracle-gated engine casts.

Grading each step against the canonical chart, not against the learner's own earlier answer, is what keeps feedback honest and localized. If the learner picked the wrong so cuc at dinh cuc, every downstream plate will differ; scoring each step against the engine and then flagging the first divergence as the root cause tells the learner "fix dinh cuc first" instead of drowning them in twenty consequential mismatches. This mirrors the pipeline's own structure (each QMDG / LN stage is a stage with its own output), so a step maps cleanly onto a slice of `ban`.

Keeping the grader to casting only is the same fact / verdict boundary the whole platform is built on (strategy 7). The engine diffs structure - did you place the right stem in the right palace - which is checkable and objective. What a palace means for the question is interpretation, and that is the cited AI layer's job, never the grader's. A practice tool that started scoring interpretation would cross exactly the line the product is careful to hold.

## §3 - Contract (types and grader)

### Types (`apps/web/src/features/edu/practice/types.ts`)

```ts
import type { LaSo } from "@/lib/laso";   // FR-PLAT-002 envelope

export type System = "luc_nham" | "ky_mon" | "thai_at";

// One step in the casting procedure the learner performs, tied to a slice of the la so.
export interface CastStep {
  id: string;              // stable, e.g. "qimen.dinh_cuc", "luc_nham.tam_truyen"
  system: System;
  label: string;           // display, e.g. "Dinh cuc", "Tam truyen"
  criterionId?: string;    // the FR-EDU-001 criterion this step contributes to
  refPaths: string[];      // JSON paths into the reference la so (default root `ban`)
  errorKind: ErrorKind;    // the class of mistake this step catches, for the message
}

// The three canonical practice errors (Claude-07 s3.3) plus the earlier plate steps.
export type ErrorKind =
  | "dinh_cuc" | "dia_ban" | "truc_phu_su" | "an_sao"      // seated a star/plate wrong
  | "an_khoa"                                              // placed a lesson wrong
  | "tam_truyen"                                           // mis-derived tam truyen
  | "an_tuong" | "cach_cuc";

export interface LearnerAnswer { stepId: string; value: unknown; }

export type StepStatus = "correct" | "incorrect" | "blocked";

export interface CellDiff {
  path: string;            // where the mismatch is, e.g. "cung.3.thien_ban.can"
  expected: unknown;       // from the engine's la so (the answer key)
  got: unknown;            // from the learner
  message: string;         // specific and localized
}

export interface StepResult {
  stepId: string;
  status: StepStatus;
  diffs: CellDiff[];       // empty when correct
  blockedBy?: string;      // set when this step only diverges because of an earlier error
}

export interface CastReport {
  system: System;
  steps: StepResult[];
  rootErrorStepId?: string;  // the earliest incorrect step, the one to fix first
  allCorrect: boolean;
}
```

### The step ladders (`apps/web/src/features/edu/practice/steps.ts`)

The QiMen ladder mirrors the QMDG pipeline; the LiuRen ladder mirrors the LN pipeline. Each step names the `ban` paths it grades:

```ts
export const qimenLadder: CastStep[] = [
  { id: "qimen.dinh_cuc",     system: "ky_mon", label: "Dinh cuc",             refPaths: ["dinh_cuc"],                          errorKind: "dinh_cuc" },
  { id: "qimen.dia_ban",      system: "ky_mon", label: "Bo dia ban",           refPaths: ["dia_ban"],                           errorKind: "dia_ban" },
  { id: "qimen.truc_phu_su",  system: "ky_mon", label: "Truc phu / truc su",   refPaths: ["truc_phu", "truc_su"],               errorKind: "truc_phu_su" },
  { id: "qimen.thien_ban",    system: "ky_mon", label: "Thien ban",            refPaths: ["thien_ban"],                         errorKind: "an_sao" },
  { id: "qimen.sao_mon_than", system: "ky_mon", label: "Cuu tinh / bat mon / bat than", refPaths: ["cuu_tinh", "bat_mon", "bat_than"], errorKind: "an_sao" },
  { id: "qimen.cach_cuc",     system: "ky_mon", label: "Nhan dien cach cuc",   criterionId: "edu.crit.3to4", refPaths: ["$.cach_cuc"], errorKind: "cach_cuc" },
];

export const lucNhamLadder: CastStep[] = [
  { id: "luc_nham.thien_dia_ban", system: "luc_nham", label: "Thien dia ban", criterionId: "edu.crit.2to3", refPaths: ["thien_dia_ban"], errorKind: "an_sao" },
  { id: "luc_nham.tu_khoa",       system: "luc_nham", label: "Tu khoa",       criterionId: "edu.crit.2to3", refPaths: ["tu_khoa"],       errorKind: "an_khoa" },
  { id: "luc_nham.tam_truyen",    system: "luc_nham", label: "Tam truyen",    criterionId: "edu.crit.2to3", refPaths: ["tam_truyen"],    errorKind: "tam_truyen" },
  { id: "luc_nham.thien_tuong",   system: "luc_nham", label: "An thien tuong", criterionId: "edu.crit.2to3", refPaths: ["thien_tuong"],  errorKind: "an_tuong" },
];
```

A `refPath` beginning `$.` addresses the envelope root (so `cach_cuc` reads the detected-pattern set); a bare path addresses `ban`.

### Grader (`apps/web/src/features/edu/practice/grader.ts`)

```ts
// Diff one step against the engine's la so at its ref paths. Pure.
export function gradeStep(step: CastStep, answer: LearnerAnswer, reference: LaSo): StepResult;

// Grade a whole attempt in order: mark the earliest incorrect step as the root cause;
// downstream steps that diverge are graded but flagged `blockedBy` the root.
export function gradeCast(ladder: CastStep[], answers: LearnerAnswer[], reference: LaSo): CastReport;

// Obtain the answer key by casting the learner's input through the normal path.
// (FR-API-001 -> FR-QMDG-006 / FR-LN-006; the engine chart is the ground truth.)
export async function referenceChart(input: DauVao, system: System): Promise<LaSo>;
```

`gradeStep` walks `refPaths`, reads the engine value and the learner value at each addressed cell, and emits a `CellDiff` per mismatch with an `errorKind`-shaped message. `status` is `correct` when `diffs` is empty. `gradeCast` collects results, sets `rootErrorStepId` to the first `incorrect` step, and for later steps whose diffs are explained by the root (a wrong dinh cuc shifts every downstream plate) sets `status: "blocked"` with `blockedBy`.

## §4 - Acceptance criteria

1. The QiMen and LiuRen ladders exist as ordered `CastStep[]`, each step addressing real `ban` (or root `cach_cuc`) paths of the FR-PLAT-002 envelope; a test asserts every `refPath` resolves on a golden la so.
2. `gradeStep` returns `status: "correct"` with no diffs when the learner's step equals the engine's, and one `CellDiff` per mismatched cell otherwise, each with a specific message naming the path, expected, and got.
3. The three canonical error classes are caught with the right `errorKind` and message: a mis-placed tu khoa (`an_khoa`), a mis-derived tam truyen (`tam_truyen`), and a mis-seated sao (`an_sao`), per Claude-07 s3.3.
4. `gradeCast` sets `rootErrorStepId` to the earliest incorrect step, and marks downstream steps that diverge only because of it as `blocked` with `blockedBy` pointing at the root, rather than reporting them as independent errors.
5. The grader is pure: identical `(step, answer, reference)` yields an identical `StepResult` (no clock, no network); the reference chart is fetched separately via `referenceChart`.
6. The practice surface renders in the FR-WEB-001 shell with DS v1.3.0 components, reuses the FR-CHART-001 / FR-CHART-002 views for input, and introduces no new design tokens; it never displays an interpretive verdict (grades casting only).

## §5 - Verification

- Vitest (`grader.test.ts`): golden-la-so fixtures for one QiMen and one LiuRen chart (emitted by the engines or built to the FR-PLAT-002 schema). Correct-answer case (no diffs); each canonical error case (an_khoa, tam_truyen, an_sao) with the expected message; the cascade case where a wrong dinh cuc yields one root and several `blocked` downstream steps.
- Path-resolution test: every `refPath` in both ladders resolves to a present slice of the golden envelope (so a rename of `ban` shape is caught here).
- Purity test: 1,000 repeat calls of `gradeStep` on the same inputs return deep-equal results.
- Boundary test: `StepResult` and `CastReport` carry no interpretation field; a lint/assert guards that grader output has no `meaning` / verdict key.
- Component/snapshot test: the practice flow renders in the app shell with DS v1.3.0 only.
- Gates: `pnpm test`, `tsc --noEmit`, `eslint` (the WEB toolchain).

## §6 - Implementation skeleton

1. `types.ts`: `CastStep`, `LearnerAnswer`, `CellDiff`, `StepResult`, `CastReport`, `ErrorKind`.
2. `steps.ts`: the `qimenLadder` and `lucNhamLadder`, each step tied to `ban` paths and (where applicable) an FR-EDU-001 `criterionId`.
3. `grader.ts`: `gradeStep` (per-cell diff + message), `gradeCast` (root-cause + `blockedBy`), `referenceChart` (cast via FR-API-001).
4. `grader.test.ts`: golden fixtures, the three error cases, the cascade case, purity.
5. `PracticeFlow.tsx`: the step-by-step UI in the WEB-001 shell, reusing the CHART views for input and showing the per-step diff panel with the root-cause highlighted.

## §7 - Dependencies

Depends on FR-QMDG-006 and FR-LN-006 - the oracle-gated QiMen and LiuRen engines whose charts are the answer key; the practice surface reaches them through the normal casting path (FR-API-001), never re-deriving a chart in TypeScript. Consumes the FR-PLAT-002 envelope (the la so it diffs against) and the FR-EDU-001 criteria (the steps carry `criterionId`s for the engine-graded transitions). Renders in the FR-WEB-001 shell and reuses FR-CHART-001 / FR-CHART-002 for chart input. Related to FR-EDU-003 (a wrong step can link out to the relevant library passage).

## §8 - Example payloads

A mis-seated-star result (the learner put 天蓬 where the engine has 天芮):

```ts
gradeStep(qimenLadder[4], { stepId: "qimen.sao_mon_than", value: learnerPlates }, engineLaSo)
// ->
{
  stepId: "qimen.sao_mon_than",
  status: "incorrect",
  diffs: [
    { path: "cuu_tinh.3", expected: "天芮", got: "天蓬",
      message: "You seated 天蓬 at cung 3; the engine has 天芮 there." }
  ],
}
```

A cascade attempt (wrong dinh cuc) reported with one root and blocked downstream steps:

```ts
gradeCast(qimenLadder, answers, engineLaSo)
// ->
{
  system: "ky_mon",
  rootErrorStepId: "qimen.dinh_cuc",
  allCorrect: false,
  steps: [
    { stepId: "qimen.dinh_cuc",     status: "incorrect", diffs: [ /* so_cuc 1 vs 7 */ ] },
    { stepId: "qimen.dia_ban",      status: "blocked", blockedBy: "qimen.dinh_cuc", diffs: [] },
    { stepId: "qimen.truc_phu_su",  status: "blocked", blockedBy: "qimen.dinh_cuc", diffs: [] },
  ],
}
```

## §9 - Open questions

- Partial credit within a step: is a step all-or-nothing, or scored by fraction of correct cells? Default: report every `CellDiff` (so the learner sees each mistake) and treat the step as `incorrect` if any cell diverges; a numeric score is an FR-EDU-001 progression concern, not the grader's.
- Cascade detection heuristic: how do we know a downstream diff is only a consequence of the root? Default at MVP: any incorrect step after the first is marked `blocked` until the learner fixes the root and re-submits; a precise dependency model (which cells the wrong so cuc actually moved) is a later refinement.
- TaiYi practice: the ladder is defined for QiMen and LiuRen (the P3 engines that are built); the TaiYi ladder is added when FR-TAT-006 lands and is out of scope here.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Stale answer key | a hand-authored key drifts from the engine | there is no hand key; the reference is always the freshly cast engine la so |
| Cascade flood | wrong early step reported as many errors | `gradeCast` names one `rootErrorStepId`; downstream diverging steps are `blocked`, not independent errors |
| Grader interprets | practice starts scoring meaning | boundary test: grader output has no verdict field; casting only (strategy 7) |
| Path drift | `ban` shape changes, `refPath` misses | path-resolution test fails on the golden envelope |
| Impure grader | reads clock/network in `gradeStep` | purity test (1,000x deep-equal) fails; casting is done separately in `referenceChart` |
| New design token | practice UI adds a token | snapshot/lint asserts DS v1.3.0 tokens only |

## §11 - Notes

This is the feature that turns the deterministic engine into a teacher (Claude-07 s3.3): because one input yields exactly one chart, the app diffs the learner's chart against the engine's and points to the exact step they missed - a mis-placed khoa, a mis-derived tam truyen, a mis-seated sao. The engine is never wrong here and never stale, because the answer key is whatever the oracle-gated engine casts, not a maintained key. Keep the grader pure and casting-only: it grades structure against the engine (a fact), and leaves meaning to the cited AI layer (strategy 7). Language is TypeScript (DEC-2) - a typed step ladder plus a pure diff function - rendering in the WEB-001 shell over the CHART views, and reaching the Rust engines only through the normal casting path. refs Claude-07 s3.3.
