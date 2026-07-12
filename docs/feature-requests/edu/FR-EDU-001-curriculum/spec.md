---
id: FR-EDU-001
title: "Four-level curriculum + progression criteria - typed L1..L4 structure (can chi/ngu hanh -> LiuRen -> QiMen+TaiYi -> integration), measurable level-up criteria from Tam-Thuc-07 s3.2, engine-as-grader hooks; renders in the WEB-001 shell"
module: EDU
priority: SHOULD
status: done
phase: P3
slice: 1
lang: typescript
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 5, strategy 7, Claude-07 s3, Claude-07 s3.2]
related_frs: [FR-EDU-002, FR-EDU-003, FR-EDU-004, FR-WEB-001, FR-WEB-006, FR-KB-003]
depends_on: [FR-WEB-001]
blocks: [FR-EDU-002]
new_paths:
  - apps/web/src/content/edu/curriculum.ts
  - apps/web/src/content/edu/criteria.ts
  - apps/web/src/features/edu/progression.ts
  - apps/web/src/features/edu/progression.test.ts
  - apps/web/src/features/edu/types.ts
---

## §1 - Description (BCP-14 normative)

This FR defines the training platform's spine: the four-level Tam Thuc curriculum and its measurable progression criteria (Tam-Thuc-07 s3.1-3.2). It is the P3 learning flow's structural foundation; FR-EDU-002 wires the auto-grader onto it and FR-EDU-003 supplies the bilingual library it links to.

The module SHALL define four levels in the fixed knowledge-dependency order: L1 can chi / ngu hanh foundation, L2 LiuRen (the base system), L3 QiMen then TaiYi, L4 integration across the three. Each level SHALL declare its prerequisites, so the levels form a linear chain L1 -> L2 -> L3 -> L4 with no cycles. Each transition SHALL carry a measurable level-up criterion drawn verbatim from the s3.2 table; criteria SHALL be tied to practical ability (build a correct chart) rather than theory recall.

A learner's current level SHALL be a pure function of which criteria they have met: a level cannot be entered while a prerequisite's criterion is unmet. Criteria that Tam-Thuc-07 s3.3 grades with the deterministic engine SHALL be marked so (measure `auto_graded`, `gradedBy: "engine"`), so FR-EDU-002 knows exactly which criteria it grades by diffing the learner's chart against the engine's. The curriculum content SHALL render inside the FR-WEB-001 app shell using the existing Design System v1.3.0 components, introducing no new tokens, and SHALL be bilingual-ready (an optional `han` field on domain modules; stable ids on criteria so FR-WEB-006 can translate by id).

## §2 - Why this design (rationale for humans)

Tam Thuc is hard to learn: it needs a solid ganzhi foundation, many memorized tables, and repeated chart-casting practice (Tam-Thuc-07 s3). A flat pile of lessons would let a learner attempt QiMen dinh cuc before they can build four pillars, and they would fail without knowing why. Encoding the dependency order as prerequisites, and gating each level on a measurable criterion, makes the path honest: you advance when you can actually cast the charts of the level below, not when you have clicked through the pages.

The criteria are the pedagogical version of the project's core discipline. The engine has to be exactly right for casting; that same determinism makes it an ideal marker (Tam-Thuc-07 s3.3) - one input yields one chart, so a learner's chart can be diffed against the engine's and the exact missed step pointed out. Marking which criteria are engine-graded (chart-casting ones) versus interpretive (the L4 "choose the right system and explain" criterion, which is subjective and stays quiz/manual) keeps the auto-grader inside the boundary it can be trusted in: it grades casting, not meaning (strategy 7).

Keeping the criteria as machine-checkable records with stable ids, rather than prose in a lesson, is what lets FR-EDU-002 grade them, FR-WEB-006 translate them, and this FR test them against the source table. The curriculum is data, not copy.

## §3 - Contract (types and data)

### Types (`apps/web/src/features/edu/types.ts`)

```ts
export type Level = 1 | 2 | 3 | 4;

export interface Module {
  id: string;
  title: string;
  han?: string;            // original Han for domain modules (bilingual-ready)
  summary: string;
}

export type Measure = "auto_graded" | "quiz" | "manual";

export interface Criterion {
  id: string;              // stable; WEB-006 translates by id
  transition: "1->2" | "2->3" | "3->4" | "4";
  description: string;     // verbatim from Tam-Thuc-07 s3.2
  measure: Measure;
  gradedBy?: "engine";     // set when EDU-002 grades this by chart diff
  systems?: ("luc_nham" | "ky_mon" | "thai_at")[];  // which engine(s) grade it
}

export interface CurriculumLevel {
  level: Level;
  title: string;
  prerequisites: Level[];
  modules: Module[];
  levelUpCriteria: Criterion[];
}
```

### The four levels (Tam-Thuc-07 s3.1)

- L1 - nen can chi + ngu hanh: thien can dia chi, ngu hanh sinh khac, chi hop/xung/hinh/hai, tu tru, tiet khi, chan thai duong thoi. The shared foundation of all three engines (the FR-CORE content).
- L2 - one system in depth, LiuRen: thien dia ban, tu khoa, tam truyen, thien tuong, khoa the. Started first because it is the base system with the most shared concepts.
- L3 - second and third systems: QiMen (dinh cuc, bat mon / cuu tinh / bat than, truc phu / truc su) then TaiYi (tich nien, muoi sau than, tam tuong, cac toan va cach).
- L4 - integration: choose the system by question type, cross-check results across the three, apply the chu-khach / dung than frame across systems.

### Progression criteria (Tam-Thuc-07 s3.2, reproduced verbatim)

| Cap | Tieu chi len cap |
|---|---|
| 1 -> 2 | Dựng đúng bốn trụ và xác định tiết khí cho một tập ngày giờ cho trước; thuộc ngũ hành sinh khắc và quan hệ chi |
| 2 -> 3 | Lập đúng lá số Lục Nhâm gồm tứ khoá tam truyền và an thiên tướng cho một tập ca kiểm, khớp đáp án |
| 3 -> 4 | Lập đúng lá số Kỳ Môn và Thái Ất cho tập ca kiểm; nhận diện được các cách cục cơ bản của từng hệ |
| 4 | Chọn đúng hệ cho một loại câu hỏi và giải thích được cách đọc; đối chiếu kết quả nhiều hệ cho cùng tình huống |

The 1->2 (pillars + tiet khi) and 2->3 (LiuRen chart) criteria are `auto_graded` / `gradedBy: "engine"`: FR-EDU-002 casts the learner's answer and diffs it against the engine. The 3->4 criterion is `auto_graded` for the chart-casting half and `manual`/`quiz` for the "nhan dien cach cuc co ban" half. The L4 criterion ("chon dung he ... giai thich duoc cach doc") is `quiz` / `manual` - it is interpretive, so the engine does not grade it.

### Progression rule (`apps/web/src/features/edu/progression.ts`)

```ts
// Given the set of met criterion ids, return the highest unlocked level.
// A level unlocks only when every criterion of every prerequisite transition is met.
export function unlockedLevel(metCriterionIds: ReadonlySet<string>): Level;
export function isLevelUnlocked(level: Level, met: ReadonlySet<string>): boolean;
```

## §4 - Acceptance criteria

1. Four `CurriculumLevel` records exist with prerequisites forming the linear chain L1 -> L2 -> L3 -> L4; a test asserts the prerequisite graph is acyclic and linear.
2. The s3.2 table is represented as four `Criterion` records (transitions 1->2, 2->3, 3->4, and the L4 mastery criterion); each `description` matches the source table text verbatim.
3. `unlockedLevel` is a pure function of the met-criteria set: a level is not unlocked while any prerequisite transition's criterion is unmet.
4. The 1->2 and 2->3 criteria are marked `measure: "auto_graded"`, `gradedBy: "engine"`, with `systems` set (`["luc_nham"]` for 2->3); the L4 criterion is `quiz`/`manual` with no `gradedBy`.
5. Domain modules carry an optional `han` field and every `Criterion` has a stable `id`; the curriculum renders in the FR-WEB-001 shell with no new design tokens.

## §5 - Verification

- Vitest: DAG test (prerequisite chain is linear + acyclic); criteria-completeness test (one criterion per transition + the L4 criterion); source-parity test asserting each `description` equals the s3.2 text.
- Progression test: for representative met-criteria sets, `unlockedLevel` returns the correct level, and an unmet prerequisite blocks the next level.
- Grader-hook test: every `gradedBy: "engine"` criterion has a non-empty `systems` list (so FR-EDU-002 knows what to cast); the L4 criterion has none.
- Component/snapshot test: the curriculum renders in the app shell using DS v1.3.0 components only.
- Gates: `pnpm test`, `tsc --noEmit`, `eslint` (the WEB toolchain).

## §6 - Implementation skeleton

1. `content/edu/curriculum.ts`: the four `CurriculumLevel` records with their modules.
2. `content/edu/criteria.ts`: the four `Criterion` records with the s3.2 text verbatim and the `measure` / `gradedBy` / `systems` flags.
3. `features/edu/types.ts`: the types above.
4. `features/edu/progression.ts`: `unlockedLevel`, `isLevelUnlocked`.
5. `features/edu/progression.test.ts`: DAG, completeness, source-parity, progression, and grader-hook tests.
6. Render the levels + criteria + lock state in the FR-WEB-001 learning flow (list view, no new tokens).

## §7 - Dependencies

Depends on FR-WEB-001 (the app shell and Design System v1.3.0 components; the curriculum renders in the learning flow, Tam-Thuc-07 s6). Blocks FR-EDU-002 (auto-graded practice consumes the criteria marked `gradedBy: "engine"` and needs FR-QMDG-006 + FR-LN-006 to cast the reference charts) and informs FR-EDU-004 (onboarding). Related to FR-KB-003 / FR-EDU-003 (the bilingual classical library the curriculum links out to) and FR-WEB-006 (i18n translates the criteria by id).

## §8 - Example payloads

The L2 -> L3 level record and its criterion (abridged):

```ts
export const level2: CurriculumLevel = {
  level: 2,
  title: "Luc Nham chuyen sau",
  prerequisites: [1],
  modules: [
    { id: "ln-thien-dia-ban", title: "Thien dia ban", han: "天地盤", summary: "..." },
    { id: "ln-tu-khoa", title: "Tu khoa", han: "四課", summary: "..." },
    { id: "ln-tam-truyen", title: "Tam truyen", han: "三傳", summary: "..." },
  ],
  levelUpCriteria: [
    {
      id: "edu.crit.2to3",
      transition: "2->3",
      description:
        "Lập đúng lá số Lục Nhâm gồm tứ khoá tam truyền và an thiên tướng cho một tập ca kiểm, khớp đáp án",
      measure: "auto_graded",
      gradedBy: "engine",
      systems: ["luc_nham"],
    },
  ],
};
```

## §9 - Open questions

- QiMen vs TaiYi ordering inside L3: default LiuRen (L2) then QiMen then TaiYi within L3, matching the build order (strategy 3.4) and s3.1.
- Are L3/L4 criteria auto_graded? Default: the chart-casting half is engine-graded (diff); "nhan dien cach cuc co ban" and the L4 "choose the system + explain" are quiz/manual because they are interpretive - the engine grades casting, not meaning (strategy 7).
- Localization: the s3.2 table is Vietnamese; the EN mirror is deferred to FR-WEB-006. This FR keeps the VN source text and a stable id per criterion so WEB-006 can translate by id without re-authoring.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Level enterable with unmet prerequisite | progression not gated on criteria | DAG + progression tests fail |
| Criterion not measurable | vague "read the chapter" text | schema requires a `measure`; a test asserts every criterion has one |
| s3.2 text drift | a criterion edited away from the source | source-parity test against the s3.2 table fails |
| auto_graded criterion with no engine hook | mislabeled `measure` / missing `systems` | grader-hook test: every `gradedBy: "engine"` criterion has a non-empty `systems` list |
| Curriculum cycle | a prerequisite loop introduced | DAG acyclicity test fails |

## §11 - Notes

This is the P3 training platform's spine - the four-level curriculum (can chi / ngu hanh -> LiuRen -> QiMen + TaiYi -> integration) with measurable, mostly engine-graded level-up criteria (Tam-Thuc-07 s3.1-3.2). The deterministic engine doubles as the auto-grader (s3.3): because one input yields exactly one chart, the app diffs the learner's chart against the engine's and points to the exact step they missed. This FR owns the levels, the criteria, and the gating; FR-EDU-002 wires the grader; FR-EDU-003 the bilingual library. Language is TypeScript (DEC-2) - typed curriculum data plus a pure progression function - and the content renders in the WEB-001 shell with no new design tokens. refs Claude-07 s3.
