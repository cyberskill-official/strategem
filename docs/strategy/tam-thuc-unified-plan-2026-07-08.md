# Tam Thuc Strategem - unified plan and source reconciliation

Version 1.0 - 2026-07-08 - CyberSkill - "Turn Your Will Into Real"

This is the anchor report for the Tam Thuc Strategem product. It analyzes the two source doc sets under `docs/Claude/` and `docs/Grok/`, reconciles where they disagree, fixes the architecture and the module taxonomy, and lays out the phased roadmap. Every task under `docs/tasks/` and every task in the build order (`docs/tasks/IMPLEMENTATION_ORDER.md`) cites a section of this report in its `refs`. The task block is the spec; this report is the rationale. Read the referenced section before implementing.

Status values used across this program: tasks use `draft | ready_to_implement | implementing | in_review | done | superseded`. Backlog tasks use `todo | doing | review | done | blocked`. Only a human reviewer sets `done`.

## 1. What the product is

Tam Thuc Strategem is a decision-support platform that digitizes the three classical East Asian divination arts collectively called Tam Thuc (三式): Dai Luc Nham (大六壬, LiuRen), Ky Mon Don Giap (奇門遁甲, QiMen), and Thai At Than So (太乙神數, TaiYi). The product casts a chart (lap ban / la so) for a moment and a question, then presents a cited, structured interpretation framed as a decision-analysis lens rather than a fortune-telling verdict.

The one principle the whole platform is built around, stated identically by both sources: separate the deterministic chart-casting engine from the AI interpretation layer, and bind the two through a JSON chart. The engine runs pure algorithms and must match reference oracles to the digit; the AI layer only interprets the chart the engine produced, grounded in retrieved classical text with citations and human review. Engine does not guess meaning; AI does not invent numbers. The boundary between them is the la so JSON.

Three product surfaces sit on top of that spine: a lookup flow (ask -> cast -> read cited interpretation), a learning flow (leveled curriculum, auto-graded chart practice, bilingual classical library), and a management flow (saved-chart history, school-flag configuration, export and share).

## 2. The two sources

### 2.1 Claude source (`docs/Claude/`)

Eight dense Markdown volumes (about 36,000 words) plus parallel PDFs. This is the technical and classical substance of the project.

- 01 Tong quan: what the three systems are, the tam tai (Thien/Dia/Nhan) division of labor, the shared-foundation and deterministic-vs-interpretation principles, the three-system comparison table, VN legal and ethical framing.
- 02 Dai Luc Nham: full LiuRen algorithm - thien dia ban and nguyet tuong, tu khoa, nine-school tam truyen decision tree with pseudocode, twelve thien tuong, khoa the and luc than, engine JSON schema and flags, worked example. Oracle: kinliuren.
- 03 Ky Mon Don Giap: full QiMen algorithm - dinh cuc with the complete 24-jieqi x 3-nguyen table, duong/am don, phu dau and sieu than tiep khi and tri nhuan, three dinh-cuc methods as a flag, bo dia ban algorithm with code, truc phu / truc su, chuyen ban vs phi ban, am ban vs duong ban, cat/hung cach cuc tables with conditions, dung than by question type, engine JSON schema and full flag set. Oracle: kinqimen.
- 04 Thai At Than So: full TaiYi algorithm - tich nien with three reduction methods, sixteen than, eight tuong and the toan, four calculations (nien/nguyet/nhat/thoi ke), chu-khach victory logic, cach cuc, engine JSON schema and flags. Oracle: kintaiyi.
- 05 Nen tang dung chung: the shared calendar and astronomy core. 24 solar terms from solar longitude (Meeus algorithm given in code), inverse solve for the jieqi instant with delta-T correction (Espenak-Meeus polynomial), true solar time (equation of time plus longitude correction, VN standard meridian 105E), four pillars (year at Lap Xuan 315deg with Giap Ty 1984 anchor, month via Ngu Ho Don table, day via Julian-day mod 60, hour via Ngu Thu Don table with zi-hour flags), derived states (tuan khong, vuong-suy, truong sinh), the module JSON output and the calendar flag set. Reference libs: sxwnl, tyme4py; VSOP87.
- 06 Kien truc ky thuat: the five-tier architecture, the deterministic-engine ‖ AI split, the la so JSON envelope, the knowledge-graph node and edge taxonomy, the RAG-on-classical-text strategy, the tech-stack table, and the five-phase build roadmap.
- 07 San pham dao tao: strategic-consulting application (trach thoi, phuong vi, chu-khach, macro outlook), the dung-than / chu-khach four-step decision framework, the four-level training curriculum, VN legal positioning with named statutes, cultural-sensitivity rules, and the CyberSkill Design System v1.3.0 UI layer including the AIDisclosureBadge and HumanReviewGate components.

Strengths: precise algorithms, real lookup tables, the JSON envelope, the design-system tokens, and a clear architecture philosophy. This source is authoritative on the engines, the calendar core, the AI-boundary design, and the UI.

### 2.2 Grok source (`docs/Grok/`)

Fifty-one PDFs (about 17,000 words - broad but each thin, outline or slide style) plus thirteen UI mockup and wireframe images, and its own README, AGENTS.md, and BACKLOG.md. This is the product-and-implementation breadth layer.

It covers everything a product needs beyond the engines: PRD and positioning, backend spec (FastAPI, full endpoint list, DB schema), API reference and versioning, per-engine implementation outlines, rule engine (pattern-as-data JSON), RAG service pipeline, report generation, the interactive 9-palace chart, frontend pages and component library, auth and user management, i18n, security and STRIDE threat model, DevOps and CI/CD, testing strategy with a validation dataset, monitoring, error handling and resilience, performance and caching, onboarding, help center, partnership and master collaboration, ethics, competitive analysis, pitch, budget, and a post-MVP roadmap. It also carries the actual UI mockup images (the 9-palace chart, dashboard, timing optimizer, report view, learning hub).

Strengths: breadth of concerns, concrete endpoint and schema sketches, the pattern-as-data approach spelled out, the test/ops/security checklists, and the visual UI reference.

### 2.3 The fidelity asymmetry

The Claude set has more depth in fewer words; the Grok set has more breadth in more files. They do not conflict on content - they cover different layers. Rule of precedence for this program: on engine algorithms, the calendar core, the AI-boundary design, and the UI design system, the Claude source wins. On product surface area, endpoints, ops, security, testing, and the concrete data schema, the Grok source wins. Where both speak (architecture, RAG, rule engine), they agree in substance and the union is used.

## 3. Reconciliation decisions

Four decisions were confirmed with the operator (Stephen) on 2026-07-08 and are binding for this program.

### 3.1 DEC-1 Output location: self-contained in strategem

tasks live under `strategem/docs/tasks/<module>/`; the build order and agent trigger live alongside the tasks (`IMPLEMENTATION_ORDER.md`, `backlog.yaml`, `PROMPT.md`, `LEDGER.md`), because at greenfield stage the tasks are the plan; `docs/improvement/` is reserved for the post-launch audit and evolution stage, cyberos-style. Layout mirrors the cyberos convention so a later absorption into cyberos is mechanical, but the strategem repo owns its own ID space and lifecycle.

### 3.2 DEC-2 Tech stack: hybrid (Rust engines, Python AI, Next.js frontend)

- Deterministic engines (CORE, QMDG, LN, TAT, RULE detection) are Rust. Rationale: the engines must match reference oracles to the digit and be cargo-testable like the rest of CyberSkill; determinism, performance, and a hard test spine matter more here than ecosystem convenience. This honors the Claude source's "testable like ordinary software" emphasis and the cyberos house discipline (cargo fmt / clippy / test gates).
- AI, RAG, orchestration, report generation, and knowledge ingestion (RAG, KB ingest, REPORT, API orchestration) are Python / FastAPI. Rationale: this is where the Grok source is most detailed, where the LLM and embedding ecosystem lives, and where iteration speed helps.
- Frontend (CHART, WEB, and the learner surfaces) is Next.js 14+ with Tailwind and shadcn/ui, styled by CyberSkill Design System v1.3.0.
- The engines expose a stable boundary to Python: the la so JSON envelope (section 4.3). The Rust engine crates compile to a service (and optionally a PyO3 / WASM binding) that the Python orchestrator calls; Python never re-computes a chart.
- The Grok source proposed an all-Python stack. That path is recorded and rejected for the engines specifically, because a pure-Python engine is harder to pin to oracle-exact behavior under load and diverges from the CyberSkill Rust discipline. Python keeps everything above the JSON boundary.

### 3.3 DEC-3 Scope: full catalog, phased

The catalog covers the whole product (shared core, all three engines, rule engine, KB, RAG, chart, web, report, strategic tools, auth, API, training, legal, platform). Work is sequenced into four phases (section 6) where P0 and P1 constitute the MVP.

### 3.4 DEC-4 Build order and first engine: CORE first, QiMen flagship

Both sources agree the shared calendar core is built first, because all three engines stand on it and any error there propagates to all three. That is non-negotiable and is phase P0.

The two sources disagree on the first engine. The Claude source argues LiuRen first (it is the base system, broadest everyday demand, self-contained per use). The Grok source makes QiMen the P0 flagship (highest strategic-timing applicability; every UI mockup and wireframe centers on the 9-palace QiMen chart; immediate applicability to the "Strategem" positioning). This program resolves to QiMen first, for three reasons: the product is named and positioned around strategic timing and direction, which is exactly QiMen's tam-tai role (Dia); all existing visual assets are the QiMen 9-palace chart; and QiMen is the most school-variant-heavy engine, so building it first forces the flag-and-stamp discipline into the platform early. LiuRen becomes the second engine (P1), TaiYi the third (P2). The Claude LiuRen-first argument is sound and is preserved here as the considered alternative; if early user research shows demand skewing to concrete yes/no questions over timing, the order can flip without architectural cost, because both engines share CORE and the same JSON envelope.

## 4. Architecture spine

### 4.1 Five tiers

1. Presentation - Next.js web (mobile later). Chart-casting screen, bilingual library, lessons.
2. API and orchestration - FastAPI gateway. Auth, request validation, the nine-step query flow, versioning, rate limits.
3. Core services - two parallel branches joined by the JSON chart:
   - Deterministic branch (Rust): CORE calendar/ganzhi core, the three casting engines, and cach-cuc / pattern detection.
   - Interpretation branch (Python): knowledge-graph traversal, RAG over classical text, LLM interpretation, human-review gate.
4. Data - PostgreSQL (users, queries, charts, patterns, reports, audit), a vector DB (Chroma or pgvector or Pinecone) for embeddings, a knowledge graph (Neo4j or a property-graph or relational edge table), a classical-text store (three parallel layers), and a Redis chart cache.
5. External - LLM providers, auth providers, and the reference oracle libraries used in CI (kinqimen, kinliuren, kintaiyi, sxwnl, tyme4py).

### 4.2 The nine-step query flow

1. User submits a query (datetime, place, question type, systems) from the frontend.
2. API authenticates, validates, resolves the calendar context via CORE.
3. The selected engine(s) cast the chart from the CORE context -> raw chart data.
4. The rule engine scans the chart and detects patterns (cach cuc / khoa the).
5. RAG retrieves relevant knowledge (patterns plus classical excerpts) by query plus patterns.
6. The prompt is built (system + retrieved context + chart summary + patterns + persona level) and sent to the LLM.
7. Report generation assembles chart + patterns + interpretation into a structured report.
8. The result returns to the frontend (chart + patterns + cited interpretation + AIDisclosure).
9. Query + chart + patterns + report + flags are persisted with an audit row.

### 4.3 The la so JSON envelope (the boundary contract)

Every engine emits the same envelope shape. This is the single most important cross-module contract; it is owned by PLAT and consumed by every downstream module.

```json
{
  "he": "luc_nham | ky_mon | thai_at",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7 },
  "lich_phap": { "...": "the full CORE calendar output and flags" },
  "ban": { "...": "engine-specific plates and components" },
  "cach_cuc": [ { "id": "...", "name": "...", "cung": 1, "polarity": "cat|hung" } ],
  "co_truong_phai": { "...": "every school flag actually used" }
}
```

Rules: the engine fills `ban`, `cach_cuc`, and stamps `co_truong_phai` and `lich_phap` with every flag that changed the result; the AI layer reads `he`, `ban`, `cach_cuc`, and `co_truong_phai` and never writes them. A chart is reproducible from `dau_vao` + `co_truong_phai` + `lich_phap` flags alone.

### 4.4 Cross-cutting invariants (every task must honor)

- School differences are config flags, never hardcoded; every chart stamps the full flag set it used.
- Interpretation is retrieval-grounded, cited, and never asserts beyond the sources; the AIDisclosureBadge is mandatory on AI output.
- Important judgments pass a HumanReviewGate before reaching the user.
- Personal data (birth data, question text) is sensitive: encrypt at rest (AES-256), TLS in transit, audit sensitive actions, honor VN PDPD and GDPR erasure and export.
- The product is framed as heritage education and decision support, not fortune-telling; no medical, legal, or financial advice under a divination guise (section 7).
- Determinism: identical input plus identical flags yields an identical chart, byte-comparable to the oracle.

## 5. Unified module taxonomy

Seventeen modules. Codes are the task prefix (`TASK-<CODE>-<NNN>`). "Lang" is the primary implementation language per DEC-2.

| Code | Module | Lang | Responsibility | Primary sources |
|---|---|---|---|---|
| CORE | Calendar and ganzhi core | Rust | 24 jieqi, true solar time, four pillars, derived states, calendar flags, JSON output, oracle harness | Claude 05; Grok 01,45,46 |
| QMDG | Ky Mon Don Giap engine | Rust | dinh cuc, bo dia ban, truc phu/su, four plates, am/duong ban, cach cuc, engine JSON, flags | Claude 03; Grok 28 |
| LN | Dai Luc Nham engine | Rust | thien dia ban, nguyet tuong, tu khoa, tam truyen, thien tuong, khoa the, engine JSON, flags | Claude 02; Grok 29 |
| TAT | Thai At Than So engine | Rust | tich nien, 16 than, 8 tuong, four toan, chu-khach, cach cuc, engine JSON, flags | Claude 04; Grok 30 |
| RULE | Rule engine / pattern matching | Rust | pattern-as-data JSON, AND/OR/NOT condition DSL, evaluator, scoring, versioning | Grok 31; Claude 06 |
| KB | Knowledge base and graph | Python | knowledge-graph schema, classical-text three-layer store, pattern seeding, curation | Claude 06; Grok 24,37 |
| RAG | AI interpretation | Python | embeddings, vector store, hybrid retrieval, prompt library, LLM caller, structured output, evals, anti-hallucination | Claude 06; Grok 23,32 |
| CHART | Interactive chart components | TS/Next | 9-palace QiMen chart, LiuRen and TaiYi chart views, hover/click, cat/hung color, export | Grok 34,51; Claude 07 |
| WEB | Frontend app shell and pages | TS/Next | dashboard, query input, results, report view, app shell, component library, i18n, design tokens | Grok 07,15,35,40,51; Claude 07 |
| REPORT | Report generation | Python | structured JSON report (beginner/expert/recommendations), PDF export, sample templates | Grok 08,33 |
| STRAT | Strategic tools | Python/TS | Timing Optimizer, Scenario Comparison, chu-khach decision framework, cross-system validate | Claude 07; Grok 02 |
| AUTH | Auth and user management | Python | JWT + refresh, social login, tiers, birth-data encryption, profile | Grok 36; Claude 07 |
| API | API gateway and orchestration | Python | endpoint contracts, query orchestration, versioning, rate limits, error envelope | Grok 06,12,49 |
| EDU | Training and learning | TS/Python | four-level curriculum, auto-graded practice, bilingual library, simulator, onboarding | Claude 07; Grok 17,42 |
| LEGAL | Legal, ethics, compliance | doc/Python | disclaimers, VN statutes positioning, ethical AI, cultural sensitivity, PDPD, DSAR, retention | Claude 07; Grok 19,25 |
| PLAT | Platform, infra, ops | Rust/IaC | monorepo, JSON envelope contract, CI/CD, Docker/K8s, observability, security/STRIDE, resilience, caching, backup/DR | Grok 21,22,27,39,41,47,48,50 |

## 6. Phase roadmap

The four phases map onto the Claude five-phase roadmap and the Grok epics. P0 + P1 = MVP.

- Phase P0 - core and flagship (maps to Claude phases 1-2, Grok Epics 1-2.1, 3-4). Stand up the platform skeleton and the la so contract, build CORE to oracle accuracy, build the QiMen engine to 100% oracle match across flags, build the rule engine and the first RAG interpretation path, and ship one end-to-end flow: ask -> cast QiMen -> detect patterns -> cited interpretation -> 9-palace chart. Includes auth, the query API, and the platform/ops floor needed to run safely. Exit: a real user can cast a QiMen chart and read a cited interpretation, and CORE + QMDG pass their oracle gates.
- Phase P1 - second engine and the strategic surface (maps to Claude phase 2->3 for LiuRen, Grok Epic 2.2, 5-6). Add the LiuRen engine, the Timing Optimizer and Scenario Comparison, the report generation and PDF export, the results and report UI, and cross-system validate. Exit: MVP complete - two engines, the headline strategic tools, and reports.
- Phase P2 - third engine and depth (maps to Claude phase 3-4, Grok Epic 2.3, post-MVP). Add the TaiYi engine, deepen RAG (term-sense expansion, eval loop, multilingual), the knowledge-graph hybrid retrieval, and the management flow (history, school config, share). Exit: all three engines, mature interpretation.
- Phase P3 - training platform and hardening (maps to Claude phase 5, Grok post-MVP and ops). The learning platform (curriculum, auto-graded practice, bilingual library, simulator), full i18n (add Chinese), and the ops/security/compliance hardening pass. Exit: heritage-education platform, production-grade.

## 7. Legal, ethical, and cultural guardrails

These are product-defining, not add-ons, and every user-facing task inherits them.

- Positioning: heritage education and structured decision support, never fortune-telling or destiny prediction. Language avoids asserting certain future events, avoids medical/legal/financial advice under a divination guise, and avoids fear or dependency.
- VN legal context (informational, requires counsel review before launch): Nghi dinh 38/2021/ND-CP (administrative penalties in culture/advertising, including superstition), Dieu 320 Bo luat Hinh su (crime of practicing superstition for profit), Quyet dinh 34/2020/QD-TTg (sector list and management context). The product must sit clearly on the heritage-education side of the line.
- Cultural respect: cite classical text, present schools fairly (the flag discipline is the technical expression of this), keep the original Han alongside transliteration and translation, and anchor to real scholarship.
- Human-in-the-loop and AI disclosure are the UI expression of the technical boundary (AIDisclosureBadge, HumanReviewGate) - the same principle as citation-required interpretation, seen from the interface.

## 8. Risk register

| ID | Risk | Severity | Mitigation | Owner task area |
|---|---|---|---|---|
| RISK-1 | Calendar core error propagates to all three engines | critical | Highest test density in the project; cross-check two independent libs (sxwnl, tyme4py) over decades incl. boundary cases | CORE-006 |
| RISK-2 | Engine silently mixes school variants, half of users reject the chart | high | No hardcoded school; every chart stamps its full flag set; oracle gate runs per flag combo | QMDG-005, LN, TAT |
| RISK-3 | AI fabricates interpretation with no textual ground | high | Retrieval-only, citation-required, human-review gate, AIDisclosure; eval loop scores faithfulness | RAG-003 |
| RISK-4 | Legal exposure as superstition-for-profit under VN law | high | Heritage-education positioning; counsel review before launch and app-store submission | LEGAL |
| RISK-5 | Birth data / question text leaked (sensitive personal data) | high | AES-256 at rest, TLS 1.3, RBAC, audit, PDPD/GDPR erasure and export | AUTH-001, PLAT, LEGAL |
| RISK-6 | Oracle libraries have incompatible licenses for commercial embedding | medium | Oracles are CI test references, not embedded deps; license review before any lib is vendored | PLAT, CORE-006 |
| RISK-7 | QiMen school-variant explosion makes the test matrix unmanageable | medium | Flags are a closed enum; property tests over the enum product; default config is the common tho-gia duong-ban chaibu | QMDG |
| RISK-8 | Rust engine / Python orchestrator boundary drifts from the JSON envelope | medium | Envelope is a versioned contract in PLAT with a contract test on both sides | PLAT-002 |
| RISK-9 | Interpretation quality cannot be measured, regressions ship silently | medium | Validation dataset of 150-200 classical cases; expert review each release; eval gate | KB-002, RAG, TEST tasks |

## 9. How the task catalog and the backlog relate

Two coupled artifacts, same as cyberos:

- Feature requests (`docs/tasks/<module>/TASK-<CODE>-<NNN>-<slug>.md`) are the durable contracts: what to build, the API and schema, acceptance criteria, dependencies, failure modes. Each module has a README indexing its tasks with priority, phase, hours, and deps.
- The build order and trigger live alongside the tasks under `docs/tasks/`: `IMPLEMENTATION_ORDER.md` (master status index of every TASK-as-task across phases), `backlog.yaml` (machine-readable), phase task cards, `PROMPT.md` (the agent trigger and the human review protocol), and `LEDGER.md` (append-only evidence). An agent picks the next eligible task, opens the referenced task, implements it, records evidence, and moves to `in_review`; a human sets `done`.

task IDs never renumber. A task that grows scope becomes an task; an task that is dropped is marked `superseded`, never deleted.

## 10. Coverage map (source -> module)

| Source area | Module(s) |
|---|---|
| Claude 05 calendar core; Grok 45,46 data flow and schema | CORE, PLAT |
| Claude 03 QiMen; Grok 28 | QMDG |
| Claude 02 LiuRen; Grok 29 | LN |
| Claude 04 TaiYi; Grok 30 | TAT |
| Grok 31 rule engine; Claude 06 cach cuc | RULE |
| Claude 06 knowledge graph; Grok 24 curation, 37 seeding | KB |
| Claude 06 RAG; Grok 23 prompts, 32 RAG service | RAG |
| Grok 34 chart, 51 wireframes; Claude 07 chart screen | CHART |
| Grok 07,15,35 frontend, 40 i18n; Claude 07 UI | WEB |
| Grok 08 sample reports, 33 report gen | REPORT |
| Claude 07 strategic use; Grok 02 timing/scenario | STRAT |
| Grok 36 auth; Claude 07 tiers | AUTH |
| Grok 06 backend, 12 API, 49 versioning | API |
| Claude 07 curriculum; Grok 17 onboarding, 42 help | EDU |
| Claude 07 legal/ethics; Grok 19 legal, 25 ethics | LEGAL |
| Grok 21 security, 22 devops, 27 structure, 39 deploy, 41 monitoring, 47 resilience, 48 perf, 50 checklist | PLAT |

Every source document is accounted for. Business-context docs (Grok 03,04,05 PRD, 11 pitch, 13 budget, 16 competitive, 20 post-MVP, 43 partnership, 44 handoff) inform the roadmap and positioning but are not themselves engineering tasks; they are cited where relevant in STRAT, LEGAL, and this report.

---

Hien Thuc Hoa Y Chi.
