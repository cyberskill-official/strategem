---
id: TASK-WEB-004
title: "Dashboard - the post-login landing: recent and saved charts, a quick-cast entry, and entry points to the three flows (lookup / learning / management), built on the WEB-001 shell"
module: WEB
priority: SHOULD
status: done
phase: P1
slice: 1
lang: typescript
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s6, strategy 4.2, Grok-35]
related_frs: [TASK-WEB-001, TASK-WEB-002, TASK-WEB-003, TASK-WEB-007, TASK-API-004, TASK-AUTH-001, TASK-LEGAL-001]
depends_on: [TASK-WEB-001]
blocks: []
new_paths:
  - apps/web/src/app/dashboard/page.tsx
  - apps/web/src/components/dashboard/dashboard.tsx
  - apps/web/src/components/dashboard/recent-charts.tsx
  - apps/web/src/components/dashboard/saved-charts.tsx
  - apps/web/src/components/dashboard/quick-cast.tsx
  - apps/web/src/components/dashboard/flow-entry-cards.tsx
  - apps/web/src/lib/api/dashboard.ts
  - apps/web/tests/dashboard.test.tsx
---

## §1 - Description (BCP-14 normative)

This task builds the dashboard - the post-login landing screen and the hub of the three product flows (Claude-07 s6, strategy 1). It is where a signed-in user arrives and chooses what to do: cast a new chart, return to a recent or saved chart, or step into one of the three flows (lookup, learning, management). It owns the landing composition and its read-only data fetch; it does NOT cast a chart (TASK-WEB-002), render results (TASK-WEB-003), or own the management surface (TASK-WEB-007) - it routes into them.

The screen SHALL present, for the authenticated principal (TASK-AUTH-001): (a) a recent-charts strip - the user's most recently cast charts, newest first, each showing its system (`he`), question type, and cast time, each a link to its results (TASK-WEB-003) by `query_id`; (b) a saved-charts section - charts the user pinned; (c) a quick-cast entry - a single prominent Ochre call-to-action (control height md `44px`, TASK-WEB-001) that routes into the query input screen (TASK-WEB-002), optionally pre-seeding the last-used system tab; and (d) entry-point cards to the three flows: lookup (ask -> cast -> read), learning (the EDU curriculum, auto-graded practice, bilingual library), and management (saved-chart history, school-flag config, share/export - TASK-WEB-007). It SHALL be built on the TASK-WEB-001 shell (tokens, top bar, density, locale, disclaimer slot) and SHALL surface the in-product disclaimer (TASK-LEGAL-001).

The dashboard SHALL be a thin client: it reads persisted chart references (TASK-API-004) and routes; it never casts or interprets, and where it renders any chart preview it treats the la so envelope as read-only and SHALL NOT write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` (strategy 4.3). An empty account (no charts yet) SHALL show a first-run state that leads with the quick-cast entry rather than an empty list.

## §2 - Why this design (rationale for humans)

A divination-and-strategy product that spans three flows needs one place that makes all three reachable without the user relearning the interface each time (Claude-07 s6). The dashboard is that place: it is the shared front door built on the same component nervous system as every other screen, so a user learns the shell once and applies it everywhere. Leading with a single quick-cast call-to-action keeps the primary action honest - casting a chart is the product's core act, so it gets the one Ochre primary (TASK-WEB-001), and the flow cards are secondary affordances, not competing primaries.

Recent and saved charts are first-class because the value of a cast is not only the moment it is read - a user returns to a chart to re-read it against how events actually unfolded, which is exactly the reflective, decision-support framing the product stands on (strategy 7, Claude-07 s2). Reading those references read-only, by `query_id`, keeps the dashboard a pure navigator over what the engine already cast and the API already persisted; the moment the landing page re-derived or "refreshed" a chart it would be asserting something the engine did not. The first-run state matters for the same reason the quick-cast entry does: a new user should meet the core act, not an empty table.

## §3 - Contract (screen / data / routing)

### Layout (Claude-07 s6, on the TASK-WEB-001 shell)

```
+----------------------------- dashboard -----------------------------+
| top bar (Umber, Ochre mark, system tabs)            (TASK-WEB-001)    |
| quick-cast: [ Ochre 44px "Cast a chart" -> /cast ]  (single primary)|
| recent charts: [ card ][ card ][ card ] ...  -> /results/{query_id} |
| saved charts:  [ card ][ card ] ...          -> /results/{query_id} |
| three flows: [ Lookup ][ Learning ][ Management ]  (entry cards)    |
| disclaimer (TASK-LEGAL-001)                                           |
+--------------------------------------------------------------------+
```

### Data (`lib/api/dashboard.ts`, reads TASK-API-004 persistence)

```ts
type ChartRef = {
  query_id: string;
  he: "ky_mon" | "luc_nham" | "thai_at";
  question_type: string;          // loai_cau_hoi
  cast_at: string;                // ISO
  saved: boolean;
};
type DashboardData = { recent: ChartRef[]; saved: ChartRef[] };

async function getDashboard(): Promise<DashboardData>;
// GET the persisted references for the authed principal (TASK-API-004); sends the JWT Bearer;
// read-only; never fetches or mutates the ban.
```

### Routing

| Affordance | Routes to | task |
|---|---|---|
| quick-cast (Ochre primary) | `/cast` (optionally `?system=<last>`) | TASK-WEB-002 |
| a recent / saved chart card | `/results/{query_id}` | TASK-WEB-003 |
| flow card: lookup | `/cast` | TASK-WEB-002 |
| flow card: learning | the EDU entry | TASK-EDU-001 (later) |
| flow card: management | `/manage` | TASK-WEB-007 (later) |

Where a flow's screen is not yet built (learning at P1), its card SHALL render disabled with a "coming soon" state rather than a dead link.

## §4 - Acceptance criteria

1. Signed in, the dashboard renders a recent-charts strip (newest first) and a saved-charts section from `getDashboard()`, each card showing `he`, question type, and cast time, each linking to `/results/{query_id}`.
2. There is exactly one Ochre primary on the view - the quick-cast entry at md `44px` (TASK-WEB-001) - routing to `/cast`; the three flow cards are secondary, not primary.
3. The three flow entry cards (lookup / learning / management) are present; a not-yet-built flow renders disabled with a "coming soon" state, never a dead link.
4. An account with no charts shows a first-run state that leads with quick-cast, not an empty table.
5. The in-product disclaimer (TASK-LEGAL-001) is present on the screen.
6. The dashboard performs no cast and no interpretation, and where it previews a chart it does not write `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai` (read-only, asserted).

## §5 - Verification

- `tests/dashboard.test.tsx`: renders a `DashboardData` fixture (populated and empty); asserts the recent/saved cards and their `/results/{query_id}` links, the single-Ochre-primary quick-cast routing to `/cast`, the three flow cards with the disabled "coming soon" state for an unbuilt flow, the first-run empty state, and the disclaimer presence.
- Accessibility: `jest-axe` clean; keyboard-reachable cards and CTA; focus-visible Ochre ring; the stacked-diacritics clip test (TASK-WEB-001) over question-type labels and system names.
- Contract: `ChartRef` is checked against the TASK-API-004 persisted-reference shape (shared fixture); a drift fails the test.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/api/dashboard.ts`: the typed `getDashboard()` read against TASK-API-004 with the auth token; read-only.
2. `components/dashboard/quick-cast.tsx`: the single Ochre primary routing to `/cast` (optionally seeding the last system).
3. `recent-charts.tsx` + `saved-charts.tsx`: the `ChartRef` card lists with `/results/{query_id}` links and the empty/first-run states.
4. `flow-entry-cards.tsx`: the lookup / learning / management cards, with the disabled "coming soon" state for unbuilt flows.
5. `dashboard.tsx` + `app/dashboard/page.tsx`: compose the sections in the TASK-WEB-001 shell; wire the disclaimer slot (TASK-LEGAL-001).
6. `tests/dashboard.test.tsx` + the shared TASK-API-004 reference fixture.

## §7 - Dependencies

Depends on TASK-WEB-001 (the shell, tokens, Button, top-bar tabs, disclaimer slot). Reads TASK-API-004 (the persisted query/chart references) for the recent and saved lists, and is gated by TASK-AUTH-001 (post-login). Routes into TASK-WEB-002 (quick-cast and the lookup card), TASK-WEB-003 (a chart card opens its results), TASK-WEB-007 (the management card), and the TASK-EDU-001 learning surface when it lands. Uses TASK-LEGAL-001 for the disclaimer. It never casts a chart itself (strategy 4.2) and reads any envelope read-only (strategy 4.3).

## §8 - Example payloads

```ts
// getDashboard() result the landing renders
const data: DashboardData = {
  recent: [
    { query_id: "q_9f2", he: "ky_mon", question_type: "trach_thoi", cast_at: "2026-07-08T09:12:00Z", saved: false },
    { query_id: "q_8a1", he: "luc_nham", question_type: "hon_nhan", cast_at: "2026-07-07T15:40:00Z", saved: true }
  ],
  saved: [
    { query_id: "q_8a1", he: "luc_nham", question_type: "hon_nhan", cast_at: "2026-07-07T15:40:00Z", saved: true }
  ]
};
// a recent card -> router.push(`/results/${ref.query_id}`)   (TASK-WEB-003)
// quick-cast    -> router.push(`/cast?system=${lastSystem}`) (TASK-WEB-002)
```

## §9 - Open questions

- What "saved" means at P1: an explicit user pin vs an automatic keep of the last N. Default: an explicit saved flag on the chart (toggled from results / management, TASK-WEB-007), with recent being the automatic last-N; this keeps saved a deliberate act and recent a convenience.
- Whether the dashboard previews a rendered chart thumbnail or only a text reference card. Default: a text reference card at P1 (system + question + time), since a thumbnail would need to read the envelope; a read-only preview is an additive enhancement, not P1.
- Where the learning flow lands before TASK-EDU-001 ships. Default: the learning card renders disabled with a "coming soon" state so the three-flow information architecture is visible without a dead link.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Second primary | a flow card styled as an Ochre primary | forbidden; the single primary is quick-cast; flow cards are secondary (TASK-WEB-001) |
| Dead flow link | an unbuilt flow card links nowhere | render disabled with a "coming soon" state, never a broken route |
| Empty-list dead end | a new account shows an empty table | show the first-run state that leads with quick-cast |
| Dashboard casts | the landing tries to compute a chart | forbidden; it reads references and routes; casting is TASK-WEB-002 / the gateway |
| Envelope mutated on preview | a chart preview writes an engine field | forbidden; read-only; a byte-equality test asserts it |
| Missing disclaimer | framing only in a footer elsewhere | the TASK-LEGAL-001 disclaimer is present on the dashboard |

## §11 - Notes

The dashboard is the hub that makes the three-flow information architecture real (Claude-07 s6): one front door, built on the TASK-WEB-001 shell, that leads to casting, to past charts, and to each flow. Keep it a thin navigator - one Ochre primary (quick-cast), read-only reference cards routing by `query_id`, and secondary flow cards - and let the screens it routes to do the casting, reading, and managing. It is a SHOULD at P1 because the P0 lookup spine (WEB-002 -> WEB-003) can stand without it, but it is the screen that turns a set of pages into a coherent product.
