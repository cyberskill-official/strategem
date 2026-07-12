# Tam Thuc Strategem - implementation order and status index

Single source of truth for task status and eligibility. Task id = FR id; the spec is the FR in the module folders in this directory. Rationale is the strategy report `../strategy/tam-thuc-unified-plan-2026-07-08.md`.

Status: `draft` (FR body not yet authored) | `ready_to_implement` | `blocked` (unmet deps) | `implementing` | `in_review` | `done` | `superseded`. Only a human sets `done`. Eligibility: FR is `ready_to_implement`, status not `done`, every `depends_on` is `done`. Pick order: phase, then dependency spine, then id.

At this snapshot (2026-07-08) nothing is `done`, so the only immediately eligible task is the root PLAT-001; everything else is `blocked` until its deps clear. All 87 FR bodies are authored.

Legend: Pri = MoSCoW; h = engineering-hours; body = whether the FR spec is written; all 87 are yes at this snapshot.

## Phase P0 - core and QiMen flagship (MVP critical path, ~320h)

| id | title | pri | h | depends_on | body | status |
|---|---|---|--:|---|---|---|
| PLAT-001 | Monorepo + hybrid workspace + CI skeleton | MUST | 12 | - | yes | done |
| PLAT-002 | La so JSON envelope contract | MUST | 10 | PLAT-001 | yes | done |
| PLAT-003 | DB schema + migrations + RLS + indexes | MUST | 12 | PLAT-001 | yes | done |
| PLAT-004 | CI/CD pipeline (scan, staging->prod gate) | MUST | 10 | PLAT-001 | yes | done |
| CORE-001 | Solar longitude + 24 tiet khi (Meeus, delta-T) | MUST | 20 | PLAT-001 | yes | blocked |
| CORE-002 | True solar time (EoT + longitude) | MUST | 12 | CORE-001 | yes | blocked |
| CORE-003 | Four pillars (Ngu Ho/Ngu Thu don, zi-hour) | MUST | 16 | CORE-001, CORE-002 | yes | blocked |
| CORE-004 | Derived states (tuan khong, vuong-suy, truong sinh) | MUST | 10 | CORE-003 | yes | blocked |
| CORE-005 | Calendar module API + JSON + flags + stamp | MUST | 10 | CORE-002, CORE-003, CORE-004 | yes | blocked |
| CORE-006 | Oracle cross-check harness (sxwnl, tyme4py) | MUST | 14 | CORE-005 | yes | blocked |
| CORE-007 | Ganzhi primitives + relations | MUST | 8 | PLAT-001 | yes | done |
| RULE-001 | Pattern-as-data schema + knowledge_patterns | MUST | 8 | PLAT-003 | yes | done |
| RULE-002 | Condition DSL + evaluator + scoring | MUST | 12 | RULE-001 | yes | blocked |
| RULE-003 | Pattern loader + per-system filter + match API | MUST | 6 | RULE-002 | yes | blocked |
| QMDG-001 | Dinh cuc (jieqi x nguyen table, 3-method flag) | MUST | 18 | CORE-005 | yes | blocked |
| QMDG-002 | Bo dia ban (luc nghi tam ky) | MUST | 8 | QMDG-001 | yes | blocked |
| QMDG-003 | Truc phu/su + thien ban rotation (chuyen/phi) | MUST | 14 | QMDG-002 | yes | blocked |
| QMDG-004 | Cuu tinh/bat mon/bat than (am/duong ban) | MUST | 12 | QMDG-003 | yes | blocked |
| QMDG-005 | Cach cuc detection | MUST | 16 | QMDG-004, RULE-003 | yes | blocked |
| QMDG-006 | Engine assembly + envelope + kinqimen oracle gate | MUST | 12 | QMDG-005, CORE-006 | yes | blocked |
| KB-001 | Knowledge-graph schema + storage | SHOULD | 12 | PLAT-001 | yes | blocked |
| KB-002 | Pattern seeding (150-200, 3 systems, cited) | MUST | 16 | RULE-001, KB-001 | yes | blocked |
| RAG-001 | Classical-text ingest + embedding + vector store | MUST | 14 | KB-003, PLAT-001 | yes | blocked |
| RAG-002 | Hybrid retriever (vector arm P0; graph via KB-005) | MUST | 12 | RAG-001 | yes | blocked |
| RAG-003 | Prompt + LLM + structured output + anti-hallucination | MUST | 16 | RAG-002 | yes | blocked |
| AUTH-001 | Auth (JWT+refresh, social) + birth-data AES-256 | MUST | 14 | PLAT-001 | yes | done |
| AUTH-002 | RBAC tiers + rate-limit tiers | MUST | 8 | AUTH-001 | yes | done |
| API-001 | Query orchestration + endpoint contracts | MUST | 14 | AUTH-001, CORE-005 | yes | blocked |
| API-003 | Rate limiting + abuse detection | MUST | 8 | API-001, AUTH-002 | yes | blocked |
| API-004 | Query/chart/report persistence + audit | MUST | 8 | API-001, PLAT-003 | yes | blocked |
| WEB-001 | App shell + Design System v1.3.0 + components | MUST | 18 | PLAT-001 | yes | blocked |
| WEB-002 | Query input screen | MUST | 12 | WEB-001, API-001 | yes | blocked |
| WEB-003 | Results screen (chart + patterns + cited AI) | MUST | 14 | WEB-002, CHART-001, RAG-003 | yes | blocked |
| CHART-001 | Interactive 9-palace QiMen chart | MUST | 16 | WEB-001, QMDG-006 | yes | blocked |
| LEGAL-001 | Disclaimer + AI-disclosure + positioning copy | MUST | 6 | WEB-001 | yes | blocked |

P0 note: RAG-001 depends on KB-003 (classical-text store, P1). To keep the P0 interpretation path live, either author KB-003 early (recommended - pull it into P0 wave 3) or run RAG-001 against a small seeded corpus from KB-002. Tracked in tasks/phase-0.md.

P0 exit gate (the end-to-end demo): a signed-in user casts a QiMen chart for a datetime and question, sees the interactive 9-palace chart, the detected cach cuc, and a cited AI interpretation with the AIDisclosure badge. Requires done: PLAT-001..004, CORE-001..007, RULE-001..003, QMDG-001..006, KB-001..002, RAG-001..003, AUTH-001..002, API-001/003/004, WEB-001..003, CHART-001, LEGAL-001.

## Phase P1 - second engine and strategic surface (MVP completion, ~230h)

| id | title | pri | h | depends_on | body | status |
|---|---|---|--:|---|---|---|
| LN-001 | Thien dia ban + nguyet tuong | MUST | 12 | CORE-005 | yes | blocked |
| LN-002 | Tu khoa | MUST | 10 | LN-001 | yes | blocked |
| LN-003 | Chin tong mon + tam truyen | MUST | 16 | LN-002 | yes | blocked |
| LN-004 | Muoi hai thien tuong | MUST | 10 | LN-002 | yes | blocked |
| LN-005 | Khoa the + luc than + dung than | SHOULD | 10 | LN-003, LN-004 | yes | blocked |
| LN-006 | Engine assembly + kinliuren oracle gate | MUST | 12 | LN-003, LN-004, CORE-006 | yes | blocked |
| QMDG-007 | Dung than by question type | SHOULD | 6 | QMDG-006 | yes | blocked |
| KB-003 | Classical-text three-layer store + chunking | MUST | 12 | PLAT-001 | yes | blocked |
| RAG-004 | HumanReviewGate pipeline | MUST | 12 | RAG-003 | yes | blocked |
| RAG-007 | LLM fallback + circuit breaker + degradation | MUST | 8 | RAG-003 | yes | blocked |
| REPORT-001 | Structured report assembly | MUST | 10 | RAG-003 | yes | blocked |
| REPORT-002 | PDF export (templated, bilingual) | SHOULD | 10 | REPORT-001 | yes | blocked |
| STRAT-001 | Timing Optimizer | MUST | 16 | QMDG-006, RULE-003 | yes | blocked |
| STRAT-002 | Scenario Comparison | SHOULD | 10 | STRAT-001 | yes | blocked |
| STRAT-003 | Chu-khach decision framework | SHOULD | 8 | RAG-003 | yes | blocked |
| CHART-002 | LiuRen chart view | MUST | 12 | CHART-001, LN-006 | yes | blocked |
| CHART-004 | Chart export + accessibility | SHOULD | 8 | CHART-001 | yes | blocked |
| WEB-004 | Dashboard | SHOULD | 8 | WEB-001 | yes | blocked |
| WEB-005 | Report view screen | SHOULD | 8 | WEB-003, REPORT-001 | yes | blocked |
| WEB-006 | i18n (VN + EN) | MUST | 10 | WEB-001 | yes | blocked |
| AUTH-003 | Email verification + password reset | SHOULD | 6 | AUTH-001 | yes | blocked |
| API-002 | API versioning + deprecation policy | SHOULD | 6 | API-001 | yes | blocked |
| PLAT-005 | Observability (Prometheus/Grafana, Sentry) | MUST | 10 | PLAT-004 | yes | blocked |
| PLAT-006 | Redis caching (chart cache 24h) | SHOULD | 8 | PLAT-003 | yes | blocked |
| PLAT-007 | Security hardening (STRIDE, TLS, secrets) | MUST | 12 | PLAT-004, AUTH-002 | yes | blocked |
| PLAT-008 | Resilience (circuit breaker, backoff, degradation) | MUST | 8 | PLAT-005 | yes | blocked |
| LEGAL-002 | PDPD/GDPR compliance pack | MUST | 12 | AUTH-001 | yes | blocked |
| LEGAL-003 | Ethical-AI + cultural-sensitivity guardrails | MUST | 8 | RAG-003 | yes | blocked |
| LEGAL-004 | VN legal review checklist + counsel gate | MUST | 4 | LEGAL-001 | yes | blocked |

## Phase P2 - third engine and depth (~180h)

| id | title | pri | h | depends_on | body | status |
|---|---|---|--:|---|---|---|
| TAT-001 | Tich nien + ky nguyen | MUST | 12 | CORE-005 | yes | blocked |
| TAT-002 | An Thai At + 16 than | MUST | 12 | TAT-001 | yes | blocked |
| TAT-003 | Bat tuong + cac toan | MUST | 14 | TAT-002 | yes | blocked |
| TAT-004 | Bon phep (nien/nguyet/nhat/thoi ke) | SHOULD | 8 | TAT-002 | yes | blocked |
| TAT-005 | Cach cuc + chu-khach thang bai | SHOULD | 10 | TAT-003 | yes | blocked |
| TAT-006 | Engine assembly + kintaiyi oracle gate | MUST | 12 | TAT-003, CORE-006 | yes | blocked |
| KB-004 | KB curation workflow + expert review | SHOULD | 10 | KB-002 | yes | blocked |
| KB-005 | Knowledge-graph hybrid-retrieval query API | SHOULD | 12 | KB-001, KB-003 | yes | blocked |
| RAG-005 | Term-sense expansion | SHOULD | 10 | RAG-002 | yes | blocked |
| RAG-006 | Interpretation eval loop + CI gate | MUST | 12 | RAG-003, KB-002 | yes | blocked |
| RULE-004 | Cross-system pattern support | COULD | 8 | RULE-002 | yes | blocked |
| CHART-003 | TaiYi chart view | SHOULD | 12 | CHART-001, TAT-006 | yes | blocked |
| WEB-007 | Management flow (history, config, share) | SHOULD | 12 | WEB-003 | yes | blocked |
| STRAT-004 | Cross-system validate | SHOULD | 10 | QMDG-006, LN-006 | yes | blocked |
| REPORT-003 | Sample report templates per question type | COULD | 6 | REPORT-001 | yes | blocked |
| AUTH-004 | DSAR self-service (export + erasure) | SHOULD | 8 | AUTH-001, LEGAL-002 | yes | blocked |
| PLAT-009 | Backup + DR (PITR, RPO 1h/RTO 4h, drill) | SHOULD | 8 | PLAT-003 | yes | blocked |
| PLAT-010 | Infra as code (Terraform + K8s) | SHOULD | 10 | PLAT-004 | yes | blocked |

## Phase P3 - training platform and hardening (~130h)

| id | title | pri | h | depends_on | body | status |
|---|---|---|--:|---|---|---|
| EDU-001 | Four-level curriculum + progression criteria | SHOULD | 12 | WEB-001 | yes | blocked |
| EDU-002 | Auto-graded chart practice (engine as grader) | SHOULD | 16 | QMDG-006, LN-006 | yes | blocked |
| EDU-003 | Bilingual classical library | SHOULD | 10 | KB-003 | yes | blocked |
| EDU-004 | Onboarding + help center | COULD | 8 | WEB-001 | yes | blocked |
| WEB-008 | Chinese i18n + RTL-ready | COULD | 10 | WEB-006 | yes | blocked |

## Rollup

| Phase | tasks | hours | bodies authored |
|---|--:|--:|--:|
| P0 | 35 | ~430 | 35 |
| P1 | 29 | ~280 | 29 |
| P2 | 18 | ~185 | 18 |
| P3 | 5 | ~55 | 5 |
| Total | 87 | ~950 | 87 |

(A few SHOULD items sit at phase edges; the phase docs under `tasks/` carry the wave detail. All 87 FR bodies are authored.)

---

# Phase sequencing detail

The tables above are the status index. The sections below add the wave structure, parallel tracks, and per-phase exit gates. They point at FRs; the FR is the spec.

## Phase P0 - core and QiMen flagship

Goal: the end-to-end demo. A signed-in user casts a QiMen chart for a datetime and question, and sees the interactive 9-palace chart, the detected cach cuc, and a cited AI interpretation with the AIDisclosure badge. 35 tasks, roughly 430 hours. All 35 FR bodies are authored.

Status lives in `backlog.yaml`; this file is sequencing only. The FR is the spec.

## Tracks (run in parallel once PLAT-001 is done)

The only wave-0 task is the root PLAT-001 (monorepo + workspace + CI). After it lands, these tracks run in parallel; each arrow is a hard dependency.

- Track A - calendar core (longest critical path):
  CORE-001 -> CORE-002 -> CORE-003 -> CORE-004 -> CORE-005 -> CORE-006. CORE-007 (ganzhi primitives) runs alongside, depends only on PLAT-001. This track is the highest-risk work (RISK-1); do not rush it and do not let a >60s term error past CORE-006.
- Track B - platform floor: PLAT-002 (envelope), PLAT-003 (db), PLAT-004 (ci/cd) all depend only on PLAT-001 and can run together. PLAT-002 blocks every engine; do it early.
- Track C - rule + knowledge: RULE-001 -> RULE-002 -> RULE-003 (RULE-001 needs PLAT-003). KB-001 (needs PLAT-001) and KB-002 (needs RULE-001 + KB-001) run alongside; KB-002 is the 150-200 pattern seed and doubles as the eval set.
- Track D - QiMen engine (needs CORE-005 and RULE-003): QMDG-001 -> 002 -> 003 -> 004 -> 005 -> 006. QMDG-006 also needs CORE-006 for its oracle gate. This is the flagship; the per-flag kinqimen match is mandatory.
- Track E - interpretation (needs KB-003, see pull-forward note): KB-003 -> RAG-001 -> RAG-002 -> RAG-003.
- Track F - auth + api: AUTH-001 -> AUTH-002; API-001 (needs AUTH-001 + CORE-005) -> API-003, API-004.
- Track G - frontend + legal: WEB-001 (needs PLAT-001) -> WEB-002 -> WEB-003; CHART-001 (needs WEB-001 + QMDG-006); LEGAL-001 (needs WEB-001).

Convergence: WEB-003 (results screen) is the demo surface. It needs WEB-002 + CHART-001 + RAG-003, which pull in QMDG-006 (chart), RAG-003 (interpretation), and API-001 (data). When WEB-003 is green end to end, P0 is a candidate for the exit gate.

## Pull-forward decision (RAG needs classical text)

RAG-001 depends on KB-003 (classical-text three-layer store), which the catalog places in P1. To keep the P0 interpretation path live, do one of:
- Recommended: pull KB-003 into P0 (author its body and schedule it in Track E). It is 12 hours and unblocks the whole interpretation branch.
- Or: run RAG-001 against a minimal seeded corpus from KB-002's pattern citations, and defer the full three-layer store to P1. This ships a thinner interpretation at the demo.

Record the choice in the ledger against RAG-001.

## P0 exit gate (human sign-off)

Do not open P1 until all of these are `done` and the live demo passes:
- CORE-006 oracle gate green in CI (sxwnl <60s, tyme4py pillars pass).
- QMDG-006 matches kinqimen across all flag combinations in CI.
- The live flow: sign in (AUTH), cast a QiMen chart for a real datetime + question (WEB-002 -> API-001 -> engine), see the 9-palace chart (CHART-001), the cach cuc (RULE/QMDG-005), and a cited interpretation with the AIDisclosure badge (RAG-003 -> WEB-003).
- LEGAL-001 disclaimer and positioning copy present in-product.
- The envelope contract test (PLAT-002) and the RLS no-GUC probe (PLAT-003) green.

## Phase P1 - second engine and strategic surface (MVP completion)

Goal: complete the MVP - a second engine (LiuRen), the headline strategic tools, reports, and the operability floor. 29 tasks, roughly 280 hours. All FR bodies are authored; implement each per its FR spec (via the strategem-implement skill).

## Tracks

- LiuRen engine: LN-001 (authored) -> LN-002 -> LN-003, LN-004 -> LN-005, LN-006. LN-006 matches kinliuren. Then CHART-002 renders it. This mirrors the QiMen track shape; reuse CORE and the envelope. Read Claude volume 02 (Dai Luc Nham) for each body.
- Strategic surface (the "Strategem" positioning): STRAT-001 (Timing Optimizer, authored) -> STRAT-002 (Scenario Comparison); STRAT-003 (chu-khach framework). These are the product's headline value.
- Reports: REPORT-001 (authored) -> REPORT-002 (PDF); WEB-005 renders the report view.
- Interpretation hardening: RAG-004 (HumanReviewGate pipeline), RAG-007 (fallback + circuit breaker), KB-003 (if not pulled into P0).
- Frontend: WEB-004 (dashboard), WEB-006 (VN+EN i18n), CHART-004 (export + a11y).
- Operability floor: PLAT-005 (observability), PLAT-006 (caching), PLAT-007 (security hardening), PLAT-008 (resilience); AUTH-003 (email verify), API-002 (versioning).
- Compliance: LEGAL-002 (PDPD/GDPR pack), LEGAL-003 (ethical-AI + cultural guardrails), LEGAL-004 (VN counsel sign-off gate - required before any public launch).

## P1 exit gate

LN-006 matches kinliuren in CI; the Timing Optimizer returns scored windows for a real question; a report exports to PDF; observability and security hardening are live; LEGAL-004 counsel review is scheduled or complete before launch.

## Phase P2 - third engine and depth

Goal: all three engines live, and the interpretation branch deepened to production quality. 18 tasks, roughly 185 hours. All FR bodies are authored.

## Tracks

- TaiYi engine: TAT-001 (authored) -> TAT-002 -> TAT-003 -> TAT-004, TAT-005, TAT-006. TAT-006 matches kintaiyi. Then CHART-003 renders it. Read Claude volume 04 (Thai At Than So) for each body. TaiYi is the macro / long-cycle system - the tich nien epoch is a flag.
- RAG depth: KB-005 (knowledge-graph hybrid-retrieval query API - this is the graph arm RAG-002 was built to accept), RAG-005 (term-sense expansion), RAG-006 (interpretation eval loop + CI gate). Once RAG-006 gates CI, interpretation regressions cannot ship silently (RISK-9).
- Knowledge: KB-004 (curation workflow + expert review).
- Rule: RULE-004 (cross-system, nested patterns) - enables cross-system reading.
- Product: STRAT-004 (cross-system validate / calculate-all agreement view), WEB-007 (management flow: history, school-flag config, share/export), REPORT-003 (templates).
- Compliance + ops: AUTH-004 (DSAR self-service, needs LEGAL-002), PLAT-009 (backup + DR drill), PLAT-010 (infra as code).

## P2 exit gate

TAT-006 matches kintaiyi in CI; RAG-006 eval loop is gating; the management flow lets a user browse history and configure school flags; cross-system validate shows agreement across two or more engines.

## Phase P3 - training platform and hardening

Goal: turn the app into a heritage-education platform and finish the hardening pass. 5 tasks in this phase's core plus the security/compliance items that continue from P1-P2. Roughly 55 hours for the P3-tagged tasks. All FR bodies are authored.

## Tracks

- Training platform: EDU-001 (four-level curriculum + progression criteria, authored) -> EDU-002 (auto-graded chart practice - the deterministic engine becomes the grader, per-step diff against the engine chart) ; EDU-003 (bilingual classical library, needs KB-003) ; EDU-004 (onboarding + help center). This is where the engine's determinism pays a second dividend: it is a perfect auto-grader (Claude volume 07 section 3.3).
- Localization: WEB-008 (Chinese i18n + RTL-ready), extending WEB-006.
- Continuous hardening: the security, resilience, backup, and compliance items (PLAT-007/008/009, LEGAL-002/003/004, AUTH-004) are continuous - anything not closed in P1-P2 finishes here. LEGAL-004 counsel sign-off must be recorded before any public launch or app-store submission (RISK-4).

## P3 exit gate

Auto-graded practice works against the live engine for at least QiMen and LiuRen; the bilingual library is searchable with citations; the security and compliance hardening pass is complete; LEGAL-004 sign-off recorded.

## Beyond P3

Post-MVP directions from the sources (Grok 20 roadmap, Claude volume 07): mobile app, deeper macro analysis via TaiYi, expert marketplace and master-collaboration framework (Grok 43), and the partnership model. File these as new FRs when they become concrete; do not pre-spec them here.
