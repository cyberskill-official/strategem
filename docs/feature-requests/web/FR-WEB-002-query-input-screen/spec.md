---
id: FR-WEB-002
title: "Query input screen - the left input panel of the chart-casting layout: datetime, place/longitude, question type, system tabs, and the Ochre 44px cast button that calls /calculate/{system}"
module: WEB
priority: MUST
status: done
phase: P0
slice: 1
lang: typescript
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s5.2, Grok-51, strategy 4.2]
related_frs: [FR-WEB-001, FR-WEB-003, FR-API-001, FR-AUTH-002, FR-WEB-006, FR-LEGAL-001]
depends_on: [FR-WEB-001, FR-API-001]
blocks: [FR-WEB-003]
new_paths:
  - apps/web/src/app/cast/page.tsx
  - apps/web/src/components/query/query-form.tsx
  - apps/web/src/components/query/datetime-field.tsx
  - apps/web/src/components/query/place-field.tsx
  - apps/web/src/components/query/question-type-select.tsx
  - apps/web/src/components/query/system-tabs.tsx
  - apps/web/src/lib/api/client.ts
  - apps/web/src/lib/api/schemas.ts
  - apps/web/tests/query-form.test.tsx
---

## §1 - Description (BCP-14 normative)

This FR builds the query input screen - the left panel of the two-column chart-casting layout (FR-WEB-001) - through which a user specifies the moment and the question and casts a chart. It is the lookup flow's entry point (strategy 1, the "ask" step of ask -> cast -> read). It owns the form and the typed API client call; it does NOT render the chart or the interpretation (FR-WEB-003) and does NOT compute anything - it collects input and calls the gateway.

The form SHALL collect: a datetime (local date and time of the question or event) with an explicit timezone (default `+07:00`); a place, resolvable to a longitude (`kinh_do`), with a manual longitude override; a question type (`loai_cau_hoi`, e.g. trach_thoi, hon_nhan, ...); the system selection via the top system tabs (LiuRen / QiMen / TaiYi, with QiMen the P0 default); an optional persona level (beginner default); and optional school-flag overrides (`co_truong_phai`), defaulting to the engine defaults when omitted. The primary action SHALL be a single Ochre cast button at control height md `44px` (FR-WEB-001), and it SHALL be the only primary action on the view.

On submit, the screen SHALL POST to `POST /api/v1/calculate/{system}` (FR-API-001) with a body matching the `QueryRequest` contract, SHALL show a loading state while the nine-step flow runs, and SHALL route to the results screen (FR-WEB-003) with the returned `query_id` / response on success. It SHALL render the FR-API-001 structured error envelope faithfully: a validation error (400) inline on the offending field, an auth error (401) to sign-in, a tier error (403 `FORBIDDEN_TIER`, e.g. a Free principal requesting `all`) as a clear capability message (FR-AUTH-002), and a rate-limit error (429) with the reset hint. The screen SHALL surface the in-product disclaimer (FR-LEGAL-001) so the framing is present at the point of asking, not buried.

## §2 - Why this design (rationale for humans)

The input screen is where the product's determinism begins: every field here is an input that changes the chart, so the screen's job is to collect a complete, well-formed casting request and hand it to the gateway unaltered. Making datetime, timezone, and longitude explicit (rather than inferring silently from the browser) matters because a chart is reproducible only from its stated inputs plus flags (strategy 4.3) - a hidden timezone or an assumed longitude would make two "identical" casts diverge. The place-to-longitude resolution with a manual override respects that the longitude, not the place name, is the astronomical input.

The screen is a thin client on purpose. It validates shape for a fast local error, but the authoritative validation, calendar resolution, casting, and interpretation all happen server-side through the one orchestrator (strategy 4.2, FR-API-001); the screen never re-implements any of it. Rendering the server's structured error envelope faithfully - field-level for validation, capability for tier, reset-hint for rate limit - is what lets one error contract serve the whole UI (FR-API-001 §2). Placing the disclaimer at the point of asking, not only in a footer, is the legal-and-ethical framing shown where the user forms the expectation (FR-LEGAL-001, strategy 7).

## §3 - Contract (screen / form / API call)

### Layout (Claude-07 s5.2, Grok-51 wireframe)

Left panel of the FR-WEB-001 two-column shell. Top: the system tabs (in the top bar) select the engine. Body: the form fields top to bottom. Bottom: the Ochre `44px` cast button, full-width of the panel, the single primary action. The right panel shows an empty/prompt state until a cast returns (FR-WEB-003 fills it).

### Form fields

| Field | Maps to `QueryRequest` | Notes |
|---|---|---|
| date + time | `datetime` (ISO local) | explicit, no silent browser inference |
| timezone | `tz` | default `+07:00` |
| place | `place` (+ resolves `kinh_do`) | autocomplete; longitude override visible |
| longitude override | `kinh_do` | manual `double`; the astronomical input |
| question type | `question_type` | select of `loai_cau_hoi` values |
| system | `systems` | from the top tabs (["qimen"] default) |
| persona level | `persona_level` | beginner default |
| school flags (advanced) | `co_truong_phai` | optional; omitted -> engine defaults |

### API client (`lib/api/client.ts`, `lib/api/schemas.ts`)

```ts
// mirrors the FR-API-001 QueryRequest / QueryResponse (validated with zod)
type QueryRequest = {
  datetime: string; tz: string;
  place?: string; kinh_do?: number;
  question_type: string;
  systems: string[];            // ["qimen"] | ["qimen","liuren"] | ["all"]
  persona_level?: "beginner" | "expert";
  co_truong_phai?: Record<string, string>;
};

async function cast(system: string, body: QueryRequest): Promise<QueryResponse>;
// POST /api/v1/calculate/{system}; sends the JWT Bearer; on non-2xx, parses the
// FR-API-001 error envelope { error: { code, message, details, request_id } } and throws a typed error.
```

The client attaches the auth token (FR-AUTH-001), validates the request shape with zod before sending, and parses the structured error envelope on failure into a typed error the form maps to UI.

### Error handling (renders the FR-API-001 envelope)

| HTTP / code | UI |
|---|---|
| 400 `VALIDATION_ERROR` | inline message on the offending field |
| 401 `UNAUTHENTICATED` | route to sign-in, preserve the draft |
| 403 `FORBIDDEN_TIER` | capability message (e.g. "all-systems needs Premium"), FR-AUTH-002 |
| 429 `RATE_LIMITED` | disable cast + show `reset_at` from `details` |
| 502/503 `UPSTREAM_*` | non-blocking "engine/LLM unavailable, retry" (FR-PLAT-008) |

## §4 - Acceptance criteria

1. The form collects datetime, timezone, place/longitude, question type, system (from the tabs), persona level, and optional school flags, and builds a `QueryRequest` matching the FR-API-001 contract.
2. The cast button is a single Ochre primary at md `44px`; there is no second primary action on the view (FR-WEB-001).
3. Submitting POSTs to `/api/v1/calculate/{system}` with the correct body and auth token; a valid response routes to the results screen (FR-WEB-003) carrying the response/`query_id`.
4. Timezone and longitude are explicit inputs (defaulted, editable), never silently inferred; a place resolves to a longitude and the override is honored.
5. A 400 renders inline on the offending field; a 403 `FORBIDDEN_TIER` renders a capability message; a 429 disables cast and shows the reset hint; each is driven by the parsed error envelope, not ad hoc.
6. The in-product disclaimer (FR-LEGAL-001) is visible on the screen at the point of asking.
7. A loading state is shown while the nine-step flow runs and the cast button is disabled to prevent double submits.

## §5 - Verification

- `tests/query-form.test.tsx`: builds a `QueryRequest` from filled fields and asserts the body shape; asserts the tabs drive `systems`; asserts the place/longitude override; asserts a stubbed `cast()` success routes to results and a stubbed error envelope (400/403/429) renders the correct UI branch; asserts the single-Ochre-primary rule and the disclaimer presence.
- Contract: the zod `QueryRequest` schema is checked against the FR-API-001 `QueryRequest` (a shared fixture) so the client and the gateway agree; a drift fails the test.
- Accessibility: labeled fields, keyboard submit, focus-visible Ochre ring, and the stacked-diacritics clip test (FR-WEB-001) over Vietnamese field labels and question-type options.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/api/schemas.ts` + `lib/api/client.ts`: the zod `QueryRequest`/`QueryResponse`, the `cast()` call with auth + error-envelope parsing.
2. `components/query/*`: `datetime-field` (date+time+tz), `place-field` (autocomplete + longitude override), `question-type-select`, `system-tabs` (bound to the top bar), and `query-form` composing them with the cast button.
3. `app/cast/page.tsx`: the left panel wired into the FR-WEB-001 shell; the empty right-panel prompt state; the disclaimer slot (FR-LEGAL-001).
4. Loading + error states from the parsed envelope; route to FR-WEB-003 on success.
5. `tests/query-form.test.tsx` + the shared `QueryRequest` contract fixture.

## §7 - Dependencies

Depends on FR-WEB-001 (the shell, tokens, and the Button/tabs library) and FR-API-001 (the `/calculate/{system}` endpoint and the `QueryRequest`/error-envelope contracts it calls). Blocks FR-WEB-003 (the results screen it routes to on a successful cast). Uses FR-AUTH-002 capabilities for the tier error, FR-WEB-006 for label i18n, and FR-LEGAL-001 for the disclaimer copy. It never casts a chart itself - the gateway does (strategy 4.2).

## §8 - Example payloads

```ts
// built by query-form, sent by cast("qimen", body)
const body: QueryRequest = {
  datetime: "2004-01-01T10:30:00", tz: "+07:00",
  place: "Ha Noi", kinh_do: 105.85,
  question_type: "trach_thoi", systems: ["qimen"], persona_level: "beginner"
};
// POST /api/v1/calculate/qimen  (Authorization: Bearer <jwt>)
```

```json
// 403 error envelope the screen renders as a capability message
{ "error": { "code": "FORBIDDEN_TIER",
    "message": "All-systems casting is a Premium capability.",
    "details": { "required_tier": "premium" }, "request_id": "req_..." } }
```

## §9 - Open questions

- Place-to-longitude resolution source: a bundled VN gazetteer vs a geocoding API. Default: a small bundled set of common VN localities (offline, privacy-friendly) plus the manual longitude override for anything else; a geocoding integration is a later enhancement. The longitude is the real input, so the override is always available.
- School-flag overrides in the P0 UI: expose the full `co_truong_phai` set now vs defaults-only. Default: defaults-only in the primary form with an "advanced" disclosure for flags, since the flag set is engine-specific (FR-QMDG-006) and most users cast under the defaults; the full config surface is the management flow (FR-WEB-007).
- Client-side validation depth: how much to validate before the server. Default: shape and obvious-range checks (a parseable datetime, a longitude in range) for a fast local error; the gateway remains the authority (strategy 4.2), so the client never rejects what only the server can judge.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Silent timezone/longitude | inferred from the browser without showing it | forbidden; tz and longitude are explicit, defaulted, editable inputs (reproducibility, strategy 4.3) |
| Client re-computes a chart | UI tries to cast locally | forbidden; the screen only POSTs to the gateway; no engine logic in the client |
| Ad hoc error text | error shown without parsing the envelope | the parsed FR-API-001 envelope drives the UI branch (field/tier/rate-limit); no bespoke strings |
| Double submit | user double-clicks cast | cast is disabled during the loading state; one in-flight request |
| Missing disclaimer | framing only in a footer | the FR-LEGAL-001 disclaimer is present on the screen at the point of asking |
| Tier bypass illusion | Free user shown `all` as castable | the tab/capability state reflects FR-AUTH-002; `all` for Free surfaces the 403 capability message |

## §11 - Notes

This screen is the front door of the lookup flow and a thin client by design: it collects a complete, reproducible casting request (explicit datetime, timezone, longitude, question type, system, flags) and hands it to the one orchestrator that actually casts (strategy 4.2, FR-API-001). Keep the cast button the single Ochre primary, keep the error rendering driven by the parsed structured envelope, and keep the disclaimer at the point of asking. The moment the client tries to infer a hidden input or compute anything locally, reproducibility and the deterministic boundary are compromised.
