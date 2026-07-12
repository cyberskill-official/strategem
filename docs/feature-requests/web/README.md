# WEB - frontend app shell and pages

The user-facing surface of Tam Thuc Strategem: the Next.js app shell, the CyberSkill Design System v1.3.0 as tokens, the shared component library, and the screens of the three product flows - lookup, learning, and management. 8 FRs, ~90 engineering-hours, P0 core then P1-P3. Source of rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (sections 4.1, 4.2, 4.4, 7) and Grok 07,15,35,40,51; Claude 07 (the Design System v1.3.0 and the screen designs). Language is Next.js 14+ / TypeScript with Tailwind and shadcn/ui (DEC-2). Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

The frontend is a thin client over the one orchestrator (strategy 4.2): screens collect input and render results, and never cast or interpret a chart themselves. Its defining job is to make the deterministic-engine || AI boundary legible - the engine's computed facts and the AI's cited interpretation are always distinguishable, labeled, and (where flagged) human-reviewed (strategy 4.4).

## FRs

| FR | Pri | Phase | h | depends_on | Spec | Title |
|---|---|---|--:|---|---|---|
| WEB-001 | MUST | P0 | 18 | PLAT-001 | [FR-WEB-001](FR-WEB-001-app-shell-design-system/spec.md) | App shell + Design System v1.3.0 tokens + component library (incl. AIDisclosureBadge, HumanReviewGate) |
| WEB-002 | MUST | P0 | 12 | WEB-001, API-001 | [FR-WEB-002](FR-WEB-002-query-input-screen/spec.md) | Query input screen (datetime, place, question type, system tabs) |
| WEB-003 | MUST | P0 | 14 | WEB-002, CHART-001, RAG-003 | [FR-WEB-003](FR-WEB-003-results-screen/spec.md) | Results screen (chart + patterns + cited interpretation + AIDisclosure) |
| WEB-004 | SHOULD | P1 | 8 | WEB-001 | [FR-WEB-004](FR-WEB-004-dashboard/spec.md) | Dashboard |
| WEB-005 | SHOULD | P1 | 8 | WEB-003, REPORT-001 | [FR-WEB-005](FR-WEB-005-report-view/spec.md) | Report view screen |
| WEB-006 | MUST | P1 | 10 | WEB-001 | [FR-WEB-006](FR-WEB-006-i18n/spec.md) | i18n (VN + EN, next-intl, content/label split) |
| WEB-007 | SHOULD | P2 | 12 | WEB-003 | [FR-WEB-007](FR-WEB-007-management-flow/spec.md) | Management flow (history, school-flag config, share/export) |
| WEB-008 | COULD | P3 | 10 | WEB-006 | [FR-WEB-008](FR-WEB-008-zh-i18n/spec.md) | Chinese i18n + RTL-ready |

Three P0 FRs are authored (WEB-001..003, the app-shell -> query -> results spine). Five are authored: WEB-004 (dashboard, P1), WEB-005 (report view, P1), WEB-006 (VN+EN i18n, P1), WEB-007 (the management flow - history, school-flag config, share/export, P2), and WEB-008 (Chinese i18n + RTL-ready, P3).

## Internal spine

```
PLAT-001 -> WEB-001 (app shell + Design System v1.3.0 tokens + component library)
   -> WEB-002 (query input screen; also needs API-001)
        -> WEB-003 (results screen; also needs CHART-001 + RAG-003)
             -> WEB-005 (report view; also needs REPORT-001)
             -> WEB-007 (management flow)
   -> WEB-004 (dashboard)
   -> WEB-006 (i18n) -> WEB-008 (Chinese + RTL)
```

WEB-001 is the foundation every other screen composes from; WEB-002 -> WEB-003 is the lookup flow (ask -> cast -> read) and the P0 end-to-end demo's frontend.

## Cross-module dependencies

- Depends on PLAT: PLAT-001 (the `apps/web` scaffold, Tailwind, shadcn/ui). Depends on API: WEB-002 calls FR-API-001 `/calculate/{system}` and renders its structured error envelope; the frontend never casts a chart itself (strategy 4.2).
- Depends on CHART + RAG: WEB-003 embeds the FR-CHART-001 9-palace chart and renders the FR-RAG-003 `Interpretation` + `AIDisclosure`; it pairs with FR-RAG-004 behind the `HumanReviewGate`.
- Depends on LEGAL: the FR-LEGAL-001 copy deck fills the shell disclaimer slot and the `AIDisclosureBadge` popover (legal owns the words, the component owns the affordance).
- Feeds REPORT + STRAT surfaces: WEB-005 renders FR-REPORT-001 output; the strategic tools (Timing Optimizer, Scenario Comparison) surface through later screens.

## Module notes

- CyberSkill Design System v1.3.0 (WEB-001) is the single source of visual truth, shipped as tokens (CSS custom properties mirrored in typed TS), never copied values: the anchor colors Umber `#45210E` (ground) and Ochre `#F4BA17` (primary action, focus ring, brand accent - never semantic), the semantic trio success `#2E7D52` / danger `#B23B3B` / info `#2C5F8A`, the radius / control-height / space / elevation scales, density (compact/cozy/comfortable), and opt-in glass. Every component reads tokens; a hard-coded value is a defect.
- Vietnamese-first with the diacritics clip test: the app's primary language is Vietnamese, and the stacked tone-plus-vowel marks are the first thing a Latin-tuned line-height clips. WEB-001 makes a stacked-diacritics clip test at 100/200/400% zoom on light and dark a first-class acceptance gate; no signal is ever encoded by color alone (always color + icon + text), which is both the accessibility floor and the cat/hung convention the chart uses.
- AIDisclosureBadge and HumanReviewGate are the UI expression of the engine/AI boundary (strategy 4.4): the badge is a link to the model, the interpretation limits, and the citation sources (not decoration), mandatory on every AI output; the gate captures a human's approve/reject with a risk label, screen-reader-announced. They live in the foundational WEB-001 so every AI-bearing screen uses the same trustworthy affordance, and WEB-003 makes the deterministic region (chart + patterns) visibly separate from the interpreted region (AI reading).
- Three flows (strategy 1): lookup (WEB-002 -> WEB-003: ask -> cast -> read a cited interpretation), learning (the EDU surfaces - curriculum, auto-graded practice, bilingual library), and management (WEB-007: saved-chart history, school-flag configuration, share/export). P0 builds the lookup flow end to end; learning and management follow in P2-P3.
- The frontend is a thin client: it collects a complete, reproducible casting request (explicit datetime, timezone, longitude, flags) and renders what the gateway returns; it reads the la so envelope read-only and never writes an engine field (strategy 4.3), asserted by byte-equality tests on the screens that render it.
