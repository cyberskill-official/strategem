---
id: TASK-WEB-003
title: "Results screen - the right panel: the 9-palace chart (via CHART-001), the detected cach cuc, the cited AI interpretation with citation cards, a mandatory AIDisclosureBadge, and a HumanReviewGate where the interpretation is flagged"
module: WEB
priority: MUST
status: done
phase: P0
slice: 1
lang: typescript
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s6, strategy 4.4, strategy 4.2]
related_frs: [TASK-WEB-002, TASK-CHART-001, TASK-RAG-003, TASK-RAG-004, TASK-WEB-001, TASK-WEB-005, TASK-LEGAL-001, TASK-API-001]
depends_on: [TASK-WEB-002, TASK-CHART-001, TASK-RAG-003]
blocks: [TASK-WEB-005, TASK-WEB-007]
new_paths:
  - apps/web/src/app/results/[queryId]/page.tsx
  - apps/web/src/components/results/results-panel.tsx
  - apps/web/src/components/results/pattern-list.tsx
  - apps/web/src/components/results/interpretation-view.tsx
  - apps/web/src/components/results/citation-card.tsx
  - apps/web/src/components/results/persona-toggle.tsx
  - apps/web/tests/results-panel.test.tsx
---

## §1 - Description (BCP-14 normative)

This task builds the results screen - the right panel of the chart-casting layout (TASK-WEB-001) - which presents the outcome of a cast: the chart, the deterministic patterns the engine and rule layer found, and the AI's cited interpretation, each clearly attributed to its source (strategy 4.4). It is the "read" step of the lookup flow. It owns the results presentation; it does NOT render the chart internals (TASK-CHART-001) nor produce interpretation (TASK-RAG-003) - it composes their outputs and is where the deterministic/AI boundary is made legible to the user.

The screen SHALL render, from the TASK-API-001 `QueryResponse`: (a) the chart via TASK-CHART-001, reading `charts[i]` (the la so envelope, `he = "ky_mon"` at P0); (b) the detected patterns from `charts[i].cach_cuc` / `patterns[]` as a list with each pattern's name, Han name, palace (`cung`), and cat/hung polarity shown with icon and text, never color alone (TASK-WEB-001); and (c) the interpretation from `interpretation` (TASK-RAG-003) with both persona readings (beginner/expert, toggleable), the recommendations, and the citation cards (Han + bach thoai + dich + locator).

The screen SHALL display an `AIDisclosureBadge` (TASK-WEB-001) on the interpretation, always, fed by the `ai_disclosure` block - it is mandatory on any AI output (strategy 4.4). Where `interpretation.requires_human_review` is true (or `review_status` is pending), the screen SHALL render a `HumanReviewGate` (TASK-WEB-001, TASK-RAG-004) and SHALL clearly distinguish a not-yet-reviewed interpretation from an approved one. The screen SHALL visually separate the deterministic region (chart + patterns, sourced from the engine) from the interpreted region (AI reading, sourced from RAG and labeled), so a user can always tell computed fact from AI interpretation. It SHALL treat the la so envelope as read-only and SHALL NOT mutate `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` (strategy 4.3).

## §2 - Why this design (rationale for humans)

The results screen is where the platform's central promise becomes visible: the engine computed these facts, the AI interpreted them, and you can see which is which and whether a human vetted it (strategy 4.4). That is why the layout physically separates the deterministic region (the chart and the detected cach cuc, which came from the engine and match an oracle) from the interpreted region (the AI reading, which is grounded, cited, and labeled). Collapsing them into one undifferentiated block would erase the boundary the whole architecture exists to protect and would let a user read an AI sentence as if it carried the engine's determinism.

The AIDisclosureBadge is mandatory and the citation cards are first-class because interpretation without visible sourcing is exactly the failure mode that turns heritage education into unaccountable fortune-telling (strategy 7, RISK-3/RISK-4). Showing each claim's citations (the three text layers plus a locator) lets a user trace a reading back to a classical passage; showing the badge lets them see the model and its limits. The HumanReviewGate, shown when the interpretation is flagged, keeps a person in the loop for consequential readings and makes the review state honest - a pending reading must not look approved. Presenting cat/hung with icon and text (never color alone) is the same accessibility floor as the rest of the system, and it matters most here where a polarity could be misread as a verdict.

## §3 - Contract (screen / regions / data)

### Layout (Claude-07 s6, the right panel of TASK-WEB-001)

```
+-------------------- results panel (right) --------------------+
| [ chart region - deterministic ]                             |
|   <NinePalaceChart envelope={charts[0]} />   (TASK-CHART-001)  |
| [ patterns region - deterministic ]                          |
|   cach cuc list: name / Han / cung / cat|hung (icon + text)  |
| --------------- boundary (visually separated) -------------- |
| [ interpretation region - AI, labeled ]                      |
|   AIDisclosureBadge  +  persona toggle (beginner | expert)   |
|   reading text ... [citation refs]                           |
|   recommendations ...                                        |
|   citation cards (Han / bach thoai / dich / locator)         |
|   HumanReviewGate  (only when requires_human_review)         |
+--------------------------------------------------------------+
```

### Data source (the TASK-API-001 `QueryResponse`)

```ts
type QueryResponse = {
  query_id: string;
  charts: LaSo[];                 // TASK-PLAT-002 envelope(s); read-only here
  patterns: CachCuc[];            // detected cach cuc
  interpretation: Interpretation; // TASK-RAG-003: beginner/expert, recommendations, citations, confidence, requires_human_review, disclosure
  ai_disclosure: AIDisclosure;    // mandatory
};
```

- Chart region: passes `charts[0]` to TASK-CHART-001 (`he = "ky_mon"` at P0); the component reads `ban` and marks `cach_cuc` palaces. Read-only.
- Patterns region: `pattern-list` renders each `cach_cuc` with `name`, `name`/Han, `cung`, and `polarity` (cat/hung) as an icon+text badge using the semantic tokens (never color alone).
- Interpretation region: `interpretation-view` renders the persona-selected reading, the recommendations (each with its citations), and the `citation-card`s; `AIDisclosureBadge` is always present; `HumanReviewGate` renders when `interpretation.requires_human_review` is true.

### Persona toggle and citation card

`persona-toggle` switches between `beginner_interpretation` and `expert_interpretation` (both present in one response, TASK-RAG-003). `citation-card` shows the three text layers (`han`, `bach_thoai`, `dich`) and the `locator`; in-text citation refs link to their card.

## §4 - Acceptance criteria

1. The screen renders the chart (TASK-CHART-001) from `charts[0]`, the detected cach cuc list, and the interpretation from a `QueryResponse`, in the three regions above.
2. The deterministic region (chart + patterns) is visually separated from the interpreted region (AI reading), so computed fact and AI interpretation are distinguishable.
3. `AIDisclosureBadge` is present on the interpretation on every result carrying AI output; a result without it fails a test (mandatory, strategy 4.4).
4. cat/hung polarity on each pattern is shown with icon and text, never color alone (TASK-WEB-001).
5. When `interpretation.requires_human_review` is true (or `review_status` is pending), a `HumanReviewGate` is shown and the reading is marked not-yet-approved, distinct from an approved reading.
6. Citation cards render the three text layers (Han / bach thoai / dich) and a locator; in-text citation refs resolve to their card; the persona toggle switches beginner/expert without a re-fetch.
7. The la so envelope is unchanged by the screen (read-only): no code path writes `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`.

## §5 - Verification

- `tests/results-panel.test.tsx`: renders a `QueryResponse` fixture (with and without `requires_human_review`); asserts the three regions, the deterministic/AI separation, the always-present `AIDisclosureBadge`, the cat/hung icon+text badges, the citation-card three layers + locator, the persona toggle, and the `HumanReviewGate` presence only when flagged; asserts the envelope is byte-identical before/after render (read-only).
- Accessibility: `jest-axe` clean; the `HumanReviewGate` state announced to screen readers (TASK-WEB-001); the stacked-diacritics clip test over the interpretation text and pattern names on light+dark.
- Contract: the `Interpretation` / `AIDisclosure` types are checked against the TASK-RAG-003 shapes (shared fixture) so the screen and the interpreter agree; a drift fails the test.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `app/results/[queryId]/page.tsx`: fetch/receive the `QueryResponse` (routed from TASK-WEB-002 or fetched by `query_id`), mount the right panel in the TASK-WEB-001 shell.
2. `results-panel.tsx`: the three regions and the visual boundary; pass `charts[0]` to TASK-CHART-001.
3. `pattern-list.tsx`: the cach cuc list with cat/hung icon+text badges (semantic tokens).
4. `interpretation-view.tsx` + `persona-toggle.tsx` + `citation-card.tsx`: the AI region with the mandatory `AIDisclosureBadge`, the persona toggle, the recommendations, and the citation cards.
5. Conditional `HumanReviewGate` on `requires_human_review`; mark pending vs approved.
6. `tests/results-panel.test.tsx` + the shared TASK-RAG-003 contract fixture.

## §7 - Dependencies

Depends on TASK-WEB-002 (routes here on a successful cast, carrying the response/`query_id`), TASK-CHART-001 (the 9-palace chart it embeds), and TASK-RAG-003 (the `Interpretation` and `AIDisclosure` it renders). Uses TASK-WEB-001 (`AIDisclosureBadge`, `HumanReviewGate`, tokens, the cat/hung icon+text convention) and pairs with TASK-RAG-004 behind the gate. Reads the TASK-API-001 `QueryResponse`. Blocks TASK-WEB-005 (the report view builds on this presentation) and TASK-WEB-007 (the management flow lists past results). Reads the TASK-PLAT-002 envelope read-only (strategy 4.3).

## §8 - Example payloads

```json
// QueryResponse (abridged) this screen renders
{ "query_id": "q_...",
  "charts": [ { "he": "ky_mon", "ban": { "...": "KyMonBan" },
    "cach_cuc": [ { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "cung": 1, "polarity": "cat" } ] } ],
  "patterns": [ { "id": "qimen_thanh_long_hoi_dau", "polarity": "cat" } ],
  "interpretation": { "persona_level": "beginner",
    "beginner_interpretation": "A favorable window to begin... [yba_dieu_012].",
    "expert_interpretation": "Thanh Long Hoi Dau on cung 1... [yba_dieu_012].",
    "recommendations": [ { "text": "Treat the near-term as supportive.", "citations": ["yba_dieu_012"] } ],
    "citations": [ { "citation_id": "yba_dieu_012", "han": "丙加值符...", "bach_thoai": "...",
      "dich": "Binh gia truc phu...", "locator": "dieu 12" } ],
    "confidence": 0.72, "requires_human_review": false,
    "disclosure": { "is_ai_generated": true, "model": "gpt-4o-mini", "review_status": "not_required" } } }
```

## §9 - Open questions

- Multi-chart layout for `/calculate/all` (P1+): tabs, stacked, or side-by-side per system. Default: render `charts[0]` at P0 (QiMen only); the panel already takes a list, so a per-system tab set is additive when LiuRen/TaiYi land (TASK-CHART-002/003, TASK-STRAT-004).
- Where the persona default comes from: the request's `persona_level` vs a user preference. Default: honor the request's persona as the initial toggle state; both readings are present in one response, so switching is local and free (TASK-RAG-003 §9).
- How prominent the confidence value is. Default: show `confidence` alongside the AIDisclosureBadge as supporting context, not as a headline number, so it informs without implying false precision; the badge carries the limits copy (TASK-LEGAL-001).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Boundary erased | chart/patterns and AI reading in one undifferentiated block | forbidden; deterministic and interpreted regions are visually separated (strategy 4.4) |
| Missing disclosure | interpretation shown without the badge | forbidden; `AIDisclosureBadge` is mandatory on AI output; a test rejects its absence |
| Color-only polarity | cat/hung shown by color alone | forbidden; polarity is icon + text + color (TASK-WEB-001) |
| Pending looks approved | flagged interpretation shown as final | the `HumanReviewGate` renders and the reading is marked not-yet-approved, distinct from approved |
| Envelope mutated | screen writes an engine field | forbidden; read-only; a byte-equality test asserts the envelope is unchanged |
| Uncited claim rendered as sourced | interpretation text without a resolvable citation | citations come from TASK-RAG-003 (guarded there); the card/ref link must resolve, or the claim is not shown as sourced |

## §11 - Notes

This screen is where the deterministic/AI boundary becomes something a user can see, so its non-negotiables are visible attribution and separation: the chart and the detected cach cuc are the engine's deterministic output (matched to an oracle), the reading is the AI's grounded, cited, labeled interpretation, and the two are never blurred (strategy 4.4). The `AIDisclosureBadge` is mandatory, the citation cards are first-class, the `HumanReviewGate` keeps pending readings honest, and cat/hung is never color alone. The screen reads the la so envelope and never writes it - the same read-only invariant the interpretation branch honors (strategy 4.3), enforced here by a byte-equality test.
