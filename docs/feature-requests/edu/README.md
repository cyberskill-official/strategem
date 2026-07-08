# EDU - training and learning

Feature requests for the training and learning platform: the module that turns the product into a teaching tool. 4 FRs, ~46 engineering-hours, all P3. Rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (strategy 5, phase P3). Primary source: `../../Claude/Markdown/Tam-Thuc-07-San-pham-dao-tao.md` (s3), with Grok 17 (onboarding) and Grok 42 (help). Language is TS / Python (DEC-2). Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

Tam Thuc is hard to learn: it needs a solid ganzhi foundation, many memorized tables, and repeated chart-casting practice. EDU makes the app a teacher as well as a lookup tool - a four-level curriculum with measurable level-up criteria, auto-graded practice that uses the deterministic engine as the grader, and a bilingual classical library so learners can go to the source. Because one input yields exactly one chart, the engine that must be right for casting is also the ideal marker for practice.

## Summary

Four FRs, all P3, ~46 engineering-hours. One (EDU-001, the four-level curriculum + progression criteria) is authored; the other three are authored. EDU-001 defines the levels and gates; EDU-002 wires the engine-as-grader; EDU-003 is the bilingual library; EDU-004 is onboarding and help.

## FR list

| FR | Pri | Phase | h | Title |
|---|---|---|--:|---|
| [EDU-001](FR-EDU-001-curriculum.md) | SHOULD | P3 | 12 | Four-level curriculum structure + progression criteria |
| EDU-002 | SHOULD | P3 | 16 | Auto-graded chart practice (engine as grader, step diff) |
| EDU-003 | SHOULD | P3 | 10 | Bilingual classical library (search, cite) |
| EDU-004 | COULD | P3 | 8 | Onboarding + help center |

Total P3: 46h. Only EDU-001 is authored in full; the rest are authored.

## Cross-module dependencies

- EDU-001 depends on FR-WEB-001 (the app shell plus Design System v1.3.0 components; the curriculum renders in the learning flow, Tam-Thuc-07 s6). EDU-004 also depends on WEB-001.
- EDU-002 depends on FR-QMDG-006 and FR-LN-006 - it uses the deterministic engines as the auto-grader, diffing the learner's chart against the engine's step by step. It consumes the criteria EDU-001 marks as engine-gradeable.
- EDU-003 depends on FR-KB-003 (the three-layer classical-text store) - it is the search-and-cite surface over that store, and is the library the curriculum links out to.
- Feeds WEB-006 (i18n): the curriculum criteria carry stable ids so the Vietnamese source text can be translated by id without re-authoring.

Internal picture: `WEB-001 -> EDU-001 -> EDU-002` (grader), `KB-003 -> EDU-003`, `WEB-001 -> EDU-004`.

## Module notes

- Language: TS for the curriculum content, progression state, and web surfaces; Python enters at EDU-002 where the engine-as-grader compares casts. EDU-001 is TS - typed curriculum data plus a progression function.
- The four levels follow the knowledge-dependency order (Tam-Thuc-07 s3.1): L1 can chi / ngu hanh foundation, L2 LiuRen (the base system, most shared concepts), L3 QiMen then TaiYi, L4 integration across the three. Each transition has a measurable level-up criterion (s3.2), tied to practical ability rather than theory recall.
- The deterministic engine doubles as the auto-grader (s3.3): because one input yields exactly one chart, the app can diff a learner's chart against the engine's and point to the exact step they missed - an misplaced khoa, a wrong tam truyen, a mislaid star. EDU-001 declares which criteria are engine-graded; EDU-002 implements the diff.
- The library is bilingual by design (KB-003, EDU-003): original Han beside transliteration and translation, always cited, so learners reach the source rather than a second-hand summary. This is the cultural-respect rule (strategy 7) seen from the learning surface.
