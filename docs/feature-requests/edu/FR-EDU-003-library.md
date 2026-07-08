---
id: FR-EDU-003
title: "Bilingual classical library - search and cite over the FR-KB-003 three-layer store; the learner reads original Han beside bach thoai and translation, with citations, to reach primary sources; a citation id resolves to the exact passage"
module: EDU
priority: SHOULD
status: ready_to_implement
phase: P3
slice: 1
lang: typescript
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 5, strategy 7, strategy 4.4, Claude-07 s3.3, Claude-07 s4.3]
related_frs: [FR-KB-003, FR-EDU-001, FR-EDU-002, FR-RULE-001, FR-RAG-003, FR-WEB-001, FR-WEB-006]
depends_on: [FR-KB-003]
blocks: []
new_paths:
  - apps/web/src/features/edu/library/types.ts
  - apps/web/src/features/edu/library/api.ts
  - apps/web/src/features/edu/library/search.ts
  - apps/web/src/features/edu/library/LibraryReader.tsx
  - apps/web/src/features/edu/library/library.test.ts
---

## §1 - Description (BCP-14 normative)

This FR builds the bilingual classical library: the learning flow's search-and-read surface over the FR-KB-003 three-layer classical-text store, so a learner reads the original Han (chu Han) beside the bach thoai gloss and the translation, always with a citation, and reaches the primary source rather than a second-hand summary (Claude-07 s3.3, s4.3).

The module SHALL present each retrieved unit as a `Passage` carrying all three layers - `han`, `bach_thoai`, `dich` - never dropping the original Han (strategy 7, the cultural-respect rule). It SHALL expose search over the store (`searchLibrary`) and single-passage retrieval by id (`getPassage`), both backed by a library endpoint over the FR-KB-003 store; this FR owns the client, the view, and the request / result contract, not the store or the retrieval engine (those are FR-KB-003 and the RAG retriever). It SHALL resolve a citation id (`resolveCitation`): given the citation string a pattern (FR-RULE-001) or an AI interpretation (FR-RAG-003) carries, it SHALL deep-link to the exact passage, so a citation shown anywhere in the product is a live link into the source text.

Every rendered passage SHALL show its citation (work, and locator where present) and SHALL keep the Han visible at all breakpoints (the dau chong / diacritic-clipping rule from the design system applies to the mixed Han + Vietnamese text). The surface SHALL render inside the FR-WEB-001 shell using Design System v1.3.0 components with no new tokens, and SHALL be i18n-ready (FR-WEB-006) for its own chrome while the three text layers are content, not translatable labels.

## §2 - Why this design (rationale for humans)

The library is where the product keeps faith with its sources (Claude-07 s4.3, strategy 7). Tam Thuc is the intellectual heritage of East Asian culture; a responsible product cites the classical text, keeps the original Han beside transliteration and translation, and anchors to real scholarship rather than paraphrasing it away. Presenting three layers at once - Han, bach thoai, translation - lets a beginner read in their own language while a serious learner checks the gloss against the original character, which is exactly the "reach the source" value the training framework calls out (Claude-07 s3.3: kho nguyen van, bach thoai, va dich, co trich dan, de nguoi hoc tra tan goc).

Making a citation id resolve to a passage is what closes the chain the rest of the platform builds. A pattern row carries citation ids into the corpus (FR-RULE-001); an AI interpretation cites the passages it stands on (FR-RAG-003, strategy 4.4). Until those citations are clickable, they are just strings; this FR is where `yba_thien_can_khac_ung_12` becomes a readable Han-plus-translation passage the learner can open. That turns citation-required interpretation from a claim into something a learner can verify, which is both the anti-hallucination rule (strategy 4.4) and the cultural-respect rule (strategy 7) seen from the reading surface - the same principle from two sides.

Keeping this FR to the client, the view, and the contract - and letting FR-KB-003 own the store and chunking - is the same layering as the rest of EDU: the heavy retrieval lives in the Python / KB layer, the TypeScript surface reads it through a stable endpoint. The three text layers are content, so they are never run through the label-translation path; only the library's own chrome is i18n.

## §3 - Contract (types and API)

### Types (`apps/web/src/features/edu/library/types.ts`)

```ts
export type Layer = "han" | "bach_thoai" | "dich";

export interface Citation {
  id: string;              // e.g. "yba_thien_can_khac_ung_12"; resolves into the FR-KB-003 corpus
  work: string;            // e.g. "Yen Ba Dieu Tau Ca"
  work_han?: string;       // 煙波釣叟歌 (original title preserved)
  locator?: string;        // chapter / verse / line range, when the store has one
}

// One retrieved unit of classical text, three layers side by side. Han is never dropped.
export interface Passage {
  id: string;              // chunk id in the FR-KB-003 store
  work: string;
  work_han?: string;
  han: string;             // original Han (always present)
  bach_thoai: string;      // vernacular gloss
  dich: string;            // translation (VN; EN mirror via FR-WEB-006 later)
  citation: Citation;
  system?: "luc_nham" | "ky_mon" | "thai_at" | "chung";  // which system the passage belongs to
}

export interface LibrarySearchRequest {
  q: string;               // query text
  work?: string;           // filter to a work
  layer?: Layer;           // which layer to search (default: all)
  system?: Passage["system"];
  limit?: number;          // default 20
}

export interface LibrarySearchResult {
  passages: Passage[];
  total: number;
  query: string;
}
```

### Library client (`apps/web/src/features/edu/library/api.ts`)

```ts
// Search the three-layer store (backed by FR-KB-003 through a library endpoint).
export function searchLibrary(req: LibrarySearchRequest): Promise<LibrarySearchResult>;

// Fetch one passage by its chunk id - the deep-link target for a citation.
export function getPassage(id: string): Promise<Passage>;

// Resolve a citation id (from a pattern or an AI interpretation) to its passage.
export function resolveCitation(c: Citation): Promise<Passage>;   // getPassage(c.id) with work fallback
```

The three functions call the library endpoint; this FR does not implement retrieval (FR-KB-003 owns the store; the endpoint may reuse the FR-RAG-002 retriever's index). `resolveCitation` is `getPassage(c.id)` with a graceful fallback to a `work` + `locator` lookup when an id is not directly addressable, so a citation never dead-ends.

### Reader view (`apps/web/src/features/edu/library/LibraryReader.tsx`)

A three-column (or stacked, on narrow screens) passage reader: Han, bach thoai, dich, with the citation footer always shown. The Han column keeps its own line-height so mixed Han + Vietnamese diacritics are not clipped (the design-system dau chong rule). A passage opened via `resolveCitation` scrolls to and highlights the cited chunk.

## §4 - Acceptance criteria

1. A `Passage` always carries non-empty `han`, `bach_thoai`, and `dich`, and its `citation`; a render test asserts the Han layer is present and visible (never dropped) at the app's breakpoints.
2. `searchLibrary` returns a `LibrarySearchResult` whose passages match the query and honor the `work` / `layer` / `system` filters; a test asserts filtering narrows results and that `total` reflects the unfiltered match count.
3. `getPassage(id)` returns the passage for a known chunk id and a typed not-found for an unknown one (never a partial or empty passage).
4. `resolveCitation` turns a pattern / interpretation citation id (for example `yba_thien_can_khac_ung_12`) into the correct passage, and falls back to a `work` + `locator` lookup when the id is not directly addressable.
5. The reader renders the three layers side by side with the citation footer, keeps the Han un-clipped (dau chong test), and uses DS v1.3.0 components with no new tokens.
6. The library chrome is i18n-ready (FR-WEB-006) while the three text layers are treated as content, not passed through label translation.

## §5 - Verification

- Vitest (`library.test.ts`): a fixture corpus of a few passages (Han + bach thoai + dich + citation) mirroring the FR-KB-003 shape. Search-and-filter cases; `getPassage` hit and typed miss; `resolveCitation` for a real pattern citation id (shared with the FR-RULE-001 seed) and the `work` + `locator` fallback.
- Contract test: the `Passage` shape matches the FR-KB-003 store's export (field parity), so a store change surfaces here.
- Render test: `LibraryReader` shows all three layers and the citation; a dau chong test asserts the Han and Vietnamese diacritics are not clipped at 100 / 200 / 400 percent, light and dark.
- Deep-link test: a passage opened from a citation scrolls to and highlights the cited chunk.
- Gates: `pnpm test`, `tsc --noEmit`, `eslint` (the WEB toolchain).

## §6 - Implementation skeleton

1. `types.ts`: `Layer`, `Citation`, `Passage`, `LibrarySearchRequest`, `LibrarySearchResult`.
2. `api.ts`: `searchLibrary`, `getPassage`, `resolveCitation` over the library endpoint (FR-KB-003-backed).
3. `search.ts`: query-state helpers (filters, pagination) for the reader.
4. `LibraryReader.tsx`: the three-layer reader in the WEB-001 shell, citation footer, deep-link highlight, dau chong-safe Han column.
5. `library.test.ts`: the fixture corpus and the acceptance cases above.

## §7 - Dependencies

Depends on FR-KB-003 (the three-layer classical-text store - Han / bach thoai / dich - and its chunking); this FR is the search-and-cite surface over it, not the store. Consumes citation ids emitted by FR-RULE-001 patterns and FR-RAG-003 interpretations (it is where those citations resolve to readable passages). Renders in the FR-WEB-001 shell and is i18n-ready via FR-WEB-006. Related to FR-EDU-001 (the curriculum links out to library passages) and FR-EDU-002 (a wrong practice step can link to the relevant source passage).

## §8 - Example payloads

A search result and a resolved citation:

```ts
await searchLibrary({ q: "青龍返首", system: "ky_mon", limit: 5 })
// ->
{
  query: "青龍返首",
  total: 2,
  passages: [
    {
      id: "yba_thien_can_khac_ung_12",
      work: "Yen Ba Dieu Tau Ca", work_han: "煙波釣叟歌",
      han: "戊加丙兮青龍返首 ...",
      bach_thoai: "戊 gia Binh, goi la Thanh Long hoi dau ...",
      dich: "When 戊 is over 丙, the Green Dragon turns its head - a great-fortune configuration for major undertakings.",
      citation: { id: "yba_thien_can_khac_ung_12", work: "Yen Ba Dieu Tau Ca", work_han: "煙波釣叟歌", locator: "thien can khac ung, cau 12" },
      system: "ky_mon",
    },
  ],
}
```

```ts
// a pattern's citation id (FR-RULE-001) becomes a readable passage
await resolveCitation({ id: "yba_thien_can_khac_ung_12", work: "Yen Ba Dieu Tau Ca" });
// -> the Passage above
```

## §9 - Open questions

- Search backend: does the library reuse the FR-RAG-002 vector index or a lighter lexical index over the FR-KB-003 store? Default: reuse the FR-RAG-002 retriever's index through the library endpoint so Han, bach thoai, and translation are all searchable; a dedicated index is a later optimization if learner search differs from interpretation retrieval.
- Layer for EN users: the `dich` layer is Vietnamese at MVP; the EN translation is deferred to FR-WEB-006. Default: keep `dich` as authored and add an `en` layer through the i18n content pipeline, never machine-translating the classical text inline.
- Locator granularity: some works have verse / line locators, others only a work-level citation. Default: show whatever locator the store provides and fall back to work-level; do not fabricate a locator.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Han dropped | a passage rendered without the original characters | render test fails; the `han` layer is mandatory and always shown (strategy 7) |
| Dead citation | a citation id resolves to nothing | `resolveCitation` falls back to work + locator; a truly missing source is a typed not-found, surfaced, not silent |
| Diacritic clipping | mixed Han + Vietnamese clips at zoom | dau chong test fails at 100 / 200 / 400 percent |
| Store drift | FR-KB-003 changes the passage shape | `Passage` field-parity contract test fails |
| Machine-translated source | classical text run through label i18n | text layers are content, not labels; a test asserts the three layers bypass the translation path |
| New design token | reader adds a token | snapshot/lint asserts DS v1.3.0 tokens only |

## §11 - Notes

This is the surface that lets a learner reach the source (Claude-07 s3.3): original Han beside bach thoai and translation, always cited. It is the cultural-respect rule (strategy 7) and the anti-hallucination rule (strategy 4.4) meeting on the reading surface - keep the Han, keep the citation, and make every citation a live link into the passage it names. This FR owns the client, the reader, and the contract; FR-KB-003 owns the store and the chunking. Language is TypeScript (DEC-2) rendering in the WEB-001 shell; the heavy retrieval stays in the KB / RAG layer behind the library endpoint. refs Claude-07 s3.3, s4.3.
