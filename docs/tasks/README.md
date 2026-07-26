# Tam Thuc Strategem - task catalog

Master index of every task for the Tam Thuc Strategem product. Source of rationale: `../strategy/tam-thuc-unified-plan-2026-07-08.md` (read section refs in each task). Implementation order, status, and the agent trigger live alongside this catalog: `IMPLEMENTATION_ORDER.md`, `backlog.yaml`, `PROMPT.md`, `LEDGER.md` (see the section at the end).

87 tasks across 16 modules, roughly 900 engineering-hours, sequenced into four phases (P0 and P1 = MVP). IDs never renumber.

## Conventions

- Path: `tasks/<module-lowercase>/FR-<CODE>-<NNN>-<slug>.md`.
- Priority is MoSCoW: MUST, SHOULD, COULD.
- Phase is P0..P3 (see strategy section 6). Effort is engineering-hours (rough).
- `depends_on` lists task IDs that must be `done` (or `in_review` with reviewer waiver) before this task is eligible.
- Language per module follows DEC-2 (hybrid): engines and rule detection in Rust, AI/RAG/orchestration/report in Python, frontend in Next.js/TypeScript.
- Every engine task emits the la so JSON envelope (strategy 4.3) and stamps its full school-flag set. Every AI task is retrieval-grounded, cited, and carries AIDisclosure.

## task document template

Every task file uses this shape (heavyweight - the contract must be complete enough for an agent to implement without re-deriving from the strategy report):

```
---
id: FR-<CODE>-<NNN>
title: "<one-line, includes the key acceptance signals>"
module: <CODE>
priority: MUST | SHOULD | COULD
status: draft | ready_to_implement | implementing | in_review | done | superseded
phase: P0 | P1 | P2 | P3
slice: <int>
lang: rust | python | typescript | iac | doc
effort_h: <int>
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.3, Claude-05 s2, Grok-28]     # strategy sections + source docs
related_frs: [...]
depends_on: [...]
blocks: [...]
new_paths: [...]                                  # files/dirs this task creates
---

## §1 - Description (BCP-14 normative)     # MUST/SHALL/SHOULD language
## §2 - Why this design (rationale)
## §3 - Contract (schema / API / types / algorithm)
## §4 - Acceptance criteria
## §5 - Verification (tests, oracle checks, gates)
## §6 - Implementation skeleton
## §7 - Dependencies
## §8 - Example payloads
## §9 - Open questions
## §10 - Failure modes inventory
## §11 - Notes
```

## Module map

| Code | Module | Lang | tasks | Phase focus |
|---|---|---:|---|---|
| [PLAT](plat/README.md) | Platform, infra, ops | Rust/IaC | 10 | P0 floor, P1-P2 hardening |
| [CORE](core/README.md) | Calendar and ganzhi core | Rust | 7 | P0 |
| [QMDG](qmdg/README.md) | Ky Mon Don Giap engine | Rust | 7 | P0 |
| [RULE](rule/README.md) | Rule engine / pattern matching | Rust | 4 | P0 |
| [KB](kb/README.md) | Knowledge base and graph | Python | 5 | P0-P2 |
| [RAG](rag/README.md) | AI interpretation | Python | 7 | P0-P2 |
| [AUTH](auth/README.md) | Auth and user management | Python | 4 | P0-P2 |
| [API](api/README.md) | API gateway and orchestration | Python | 4 | P0-P1 |
| [CHART](chart/README.md) | Interactive chart components | TS/Next | 4 | P0-P2 |
| [WEB](web/README.md) | Frontend app shell and pages | TS/Next | 8 | P0-P3 |
| [LEGAL](legal/README.md) | Legal, ethics, compliance | doc/Python | 4 | P0-P1 |
| [LN](ln/README.md) | Dai Luc Nham engine | Rust | 6 | P1 |
| [REPORT](report/README.md) | Report generation | Python | 3 | P1-P2 |
| [STRAT](strat/README.md) | Strategic tools | Python/TS | 4 | P1-P2 |
| [TAT](tat/README.md) | Thai At Than So engine | Rust | 6 | P2 |
| [EDU](edu/README.md) | Training and learning | TS/Python | 4 | P3 |

## Master task list

Status column is a snapshot; the live status source of truth is `backlog.yaml` in this folder.

### PLAT - platform, infra, ops

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| PLAT-001 | MUST | P0 | 12 | - | Monorepo + hybrid workspace (cargo + uv + Next.js) + CI skeleton |
| PLAT-002 | MUST | P0 | 10 | PLAT-001 | La so JSON envelope contract (Rust+Python shared types, versioned, contract test) |
| PLAT-003 | MUST | P0 | 12 | PLAT-001 | DB schema + migrations + RLS + indexes (users/queries/charts/patterns/reports/audit) |
| PLAT-004 | MUST | P0 | 10 | PLAT-001 | CI/CD pipeline (lint/type/test, docker, security scan, staging->prod gate) |
| PLAT-005 | MUST | P1 | 10 | PLAT-004 | Observability (Prometheus/Grafana, Sentry, structured logs, alerting) |
| PLAT-006 | SHOULD | P1 | 8 | PLAT-003 | Redis caching (chart cache 24h TTL, invalidation, warming) |
| PLAT-007 | MUST | P1 | 12 | PLAT-004, AUTH-002 | Security hardening (STRIDE controls, TLS 1.3, secrets, dep scan) |
| PLAT-008 | MUST | P1 | 8 | PLAT-005 | Resilience (circuit breaker, retry/backoff, graceful degradation) |
| PLAT-009 | SHOULD | P2 | 8 | PLAT-003 | Backup + DR (daily backup, PITR, RPO 1h / RTO 4h, restore drill) |
| PLAT-010 | SHOULD | P2 | 10 | PLAT-004 | Infra as code (Terraform + K8s manifests, autoscaling) |

### CORE - calendar and ganzhi core

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| CORE-001 | MUST | P0 | 20 | PLAT-001 | Solar longitude + 24 tiet khi (Meeus, inverse solve, delta-T) |
| CORE-002 | MUST | P0 | 12 | CORE-001 | True solar time (equation of time + longitude correction + flags) |
| CORE-003 | MUST | P0 | 16 | CORE-001, CORE-002 | Four pillars (Ngu Ho / Ngu Thu don, Julian-day, zi-hour flags) |
| CORE-004 | MUST | P0 | 10 | CORE-003 | Derived states (tuan khong, vuong-suy, truong sinh, school flag) |
| CORE-005 | MUST | P0 | 10 | CORE-002, CORE-003, CORE-004 | Calendar module API + JSON output + flag set + stamp |
| CORE-006 | MUST | P0 | 14 | CORE-005 | Oracle cross-check harness (sxwnl + tyme4py, decades, boundary, CI gate) |
| CORE-007 | MUST | P0 | 8 | PLAT-001 | Ganzhi primitives + relations (ngu hanh sinh/khac, chi hinh/xung/pha/hai/hop) |

### QMDG - Ky Mon Don Giap engine

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| QMDG-001 | MUST | P0 | 18 | CORE-005 | Dinh cuc (24-jieqi x 3-nguyen table, duong/am don, sieu than tiep khi, 3-method flag) |
| QMDG-002 | MUST | P0 | 8 | QMDG-001 | Bo dia ban (luc nghi tam ky placement, directional fill) |
| QMDG-003 | MUST | P0 | 14 | QMDG-002 | Truc phu / truc su + thien ban rotation (chuyen/phi ban flag, ky cung) |
| QMDG-004 | MUST | P0 | 12 | QMDG-003 | Cuu tinh / bat mon / bat than placement (am/duong ban than swap) |
| QMDG-005 | MUST | P0 | 16 | QMDG-004, RULE-003 | Cach cuc detection (thap can khac ung, cat/hung, nhap mo / khong vong / phan-phuc ngam) |
| QMDG-006 | MUST | P0 | 12 | QMDG-005, CORE-006 | Engine assembly + JSON envelope + full flag set + kinqimen oracle gate |
| QMDG-007 | SHOULD | P1 | 6 | QMDG-006 | Dung than by question type (mapping table) |

### RULE - rule engine / pattern matching

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| RULE-001 | MUST | P0 | 8 | PLAT-003 | Pattern-as-data schema + knowledge_patterns table + versioning |
| RULE-002 | MUST | P0 | 12 | RULE-001 | Condition DSL (AND/OR/NOT, field operators) + evaluator + scoring |
| RULE-003 | MUST | P0 | 6 | RULE-002 | Pattern loader + per-system filter + match API |
| RULE-004 | COULD | P2 | 8 | RULE-002 | Cross-system pattern support (nested, multi-system) |

### KB - knowledge base and graph

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| KB-001 | SHOULD | P0 | 12 | PLAT-001 | Knowledge-graph schema (node + edge taxonomy) + storage |
| KB-002 | MUST | P0 | 16 | RULE-001, KB-001 | Pattern seeding (150-200 patterns, 3 systems, JSON conditions + citations) |
| KB-003 | MUST | P1 | 12 | PLAT-001 | Classical-text three-layer store (Han/bach thoai/dich) + chunking |
| KB-004 | SHOULD | P2 | 10 | KB-002 | KB curation workflow + expert review + versioning |
| KB-005 | SHOULD | P2 | 12 | KB-001, KB-003 | Knowledge-graph hybrid-retrieval query API |

### RAG - AI interpretation

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| RAG-001 | MUST | P0 | 14 | KB-003, PLAT-001 | Classical-text ingest + multilingual embedding + vector store |
| RAG-002 | MUST | P0 | 12 | RAG-001 | Hybrid retriever - vector arm (P0); graph arm activates when KB-005 lands (soft, P2) |
| RAG-003 | MUST | P0 | 16 | RAG-002 | Prompt library + LLM caller + structured output + anti-hallucination + AIDisclosure |
| RAG-004 | MUST | P1 | 12 | RAG-003 | HumanReviewGate pipeline (queue, approve/reject, audit) |
| RAG-005 | SHOULD | P2 | 10 | RAG-002 | Term-sense expansion (ban nghia / dan than / gia ta / dien tich) |
| RAG-006 | MUST | P2 | 12 | RAG-003, KB-002 | Interpretation eval loop (faithfulness/relevance/citation) + CI gate |
| RAG-007 | MUST | P1 | 8 | RAG-003 | LLM fallback + circuit breaker + rule-based degradation |

### AUTH - auth and user management

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| AUTH-001 | MUST | P0 | 14 | PLAT-001 | Auth (JWT + refresh, email + Google/Apple) + birth-data AES-256 + profile |
| AUTH-002 | MUST | P0 | 8 | AUTH-001 | RBAC tiers (Free/Premium/Enterprise/Admin) + rate-limit tiers |
| AUTH-003 | SHOULD | P1 | 6 | AUTH-001 | Email verification + password reset |
| AUTH-004 | SHOULD | P2 | 8 | AUTH-001, LEGAL-002 | DSAR self-service (export + erasure) |

### API - gateway and orchestration

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| API-001 | MUST | P0 | 14 | AUTH-001, CORE-005 | Query orchestration + endpoint contracts (calculate/*, error envelope) |
| API-002 | SHOULD | P1 | 6 | API-001 | API versioning + deprecation policy (URL v1, header) |
| API-003 | MUST | P0 | 8 | API-001, AUTH-002 | Rate limiting + abuse detection (per tier) |
| API-004 | MUST | P0 | 8 | API-001, PLAT-003 | Query/chart/report persistence + audit rows |
| API-005 | SHOULD | P1 | 4 | API-001 | Patterns `?system=` filter contract lock (live-audit truth-up) |

### CHART - interactive chart components

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| CHART-001 | MUST | P0 | 16 | WEB-001, QMDG-006 | Interactive 9-palace QiMen chart (4 layers, hover/click, cat/hung color, export) |
| CHART-002 | MUST | P1 | 12 | CHART-001, LN-006 | LiuRen chart view (thien dia ban, tu khoa, tam truyen, thien tuong) |
| CHART-003 | SHOULD | P2 | 12 | CHART-001, TAT-006 | TaiYi chart view (cuu cung, 16 than, tuong) |
| CHART-004 | SHOULD | P1 | 8 | CHART-001 | Chart export (PNG/SVG/print) + accessibility (dau chong test, screen reader) |

### WEB - frontend app shell and pages

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| WEB-001 | MUST | P0 | 18 | PLAT-001 | App shell + Design System v1.3.0 tokens + component library (incl. AIDisclosureBadge, HumanReviewGate) |
| WEB-002 | MUST | P0 | 12 | WEB-001, API-001 | Query input screen (datetime, place, question type, system tabs) |
| WEB-003 | MUST | P0 | 14 | WEB-002, CHART-001, RAG-003 | Results screen (chart + patterns + cited interpretation + AIDisclosure) |
| WEB-004 | SHOULD | P1 | 8 | WEB-001 | Dashboard |
| WEB-005 | SHOULD | P1 | 8 | WEB-003, REPORT-001 | Report view screen |
| WEB-006 | MUST | P1 | 10 | WEB-001 | i18n (VN + EN, next-intl, content/label split) |
| WEB-007 | SHOULD | P2 | 12 | WEB-003 | Management flow (history, school-flag config, share/export) |
| WEB-008 | COULD | P3 | 10 | WEB-006 | Chinese i18n + RTL-ready |

### LEGAL - legal, ethics, compliance

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| LEGAL-001 | MUST | P0 | 6 | WEB-001 | Disclaimer + AI-disclosure + positioning copy (in-product) |
| LEGAL-002 | MUST | P1 | 12 | AUTH-001 | PDPD/GDPR compliance pack (consent, retention, erasure/export contracts) |
| LEGAL-003 | MUST | P1 | 8 | RAG-003 | Ethical-AI + cultural-sensitivity guardrails (language rules, school fairness, attribution) |
| LEGAL-004 | MUST | P1 | 4 | LEGAL-001 | VN legal review checklist + counsel sign-off gate (pre-launch) |

### LN - Dai Luc Nham engine

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| LN-001 | MUST | P1 | 12 | CORE-005 | Thien dia ban + nguyet tuong (gia nguyet tuong, thien can ky cung) |
| LN-002 | MUST | P1 | 10 | LN-001 | Tu khoa (four lessons, thuong/ha khac) |
| LN-003 | MUST | P1 | 16 | LN-002 | Chin tong mon + tam truyen (nine-method decision tree, phuc/phan ngam) |
| LN-004 | MUST | P1 | 10 | LN-002 | Muoi hai thien tuong (khoi quy nhan, thuan/nghich bo, cat/hung) |
| LN-005 | SHOULD | P1 | 10 | LN-003, LN-004 | Khoa the + luc than + dung than |
| LN-006 | MUST | P1 | 12 | LN-003, LN-004, CORE-006 | Engine assembly + JSON + flags + kinliuren oracle gate |

### REPORT - report generation

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| REPORT-001 | MUST | P1 | 10 | RAG-003 | Structured report assembly (chart + patterns + interpretation + citations) |
| REPORT-002 | SHOULD | P1 | 10 | REPORT-001 | PDF export (templated, branded, bilingual) |
| REPORT-003 | COULD | P2 | 6 | REPORT-001 | Sample report templates per question type |

### STRAT - strategic tools

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| STRAT-001 | MUST | P1 | 16 | QMDG-006, RULE-003 | Timing Optimizer (date-range scan, scored windows) |
| STRAT-002 | SHOULD | P1 | 10 | STRAT-001 | Scenario Comparison (compare timing results across options) |
| STRAT-003 | SHOULD | P1 | 8 | RAG-003 | Chu-khach decision framework (4-step, dung than framing) |
| STRAT-004 | SHOULD | P2 | 10 | QMDG-006, LN-006 | Cross-system validate (/calculate/all + agreement view) |

### TAT - Thai At Than So engine

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| TAT-001 | MUST | P2 | 12 | CORE-005 | Tich nien + ky nguyen (3 reduction methods, flag) |
| TAT-002 | MUST | P2 | 12 | TAT-001 | An Thai At qua cuu cung + 16 than (chinh cung / gian than) |
| TAT-003 | MUST | P2 | 14 | TAT-002 | Bat tuong + cac toan (Van Xuong, Thuy Kich, ke than, chu/khach toan) |
| TAT-004 | SHOULD | P2 | 8 | TAT-002 | Bon phep (nien/nguyet/nhat/thoi ke) |
| TAT-005 | SHOULD | P2 | 10 | TAT-003 | Cach cuc + chu-khach thang bai (tam tai, truong/doan toan) |
| TAT-006 | MUST | P2 | 12 | TAT-003, CORE-006 | Engine assembly + JSON + flags + kintaiyi oracle gate |

### EDU - training and learning

| task | Pri | Phase | h | depends_on | Title |
|---|---|---|--:|---|---|
| EDU-001 | SHOULD | P3 | 12 | WEB-001 | Four-level curriculum structure + progression criteria |
| EDU-002 | SHOULD | P3 | 16 | QMDG-006, LN-006 | Auto-graded chart practice (engine as grader, step diff) |
| EDU-003 | SHOULD | P3 | 10 | KB-003 | Bilingual classical library (search, cite) |
| EDU-004 | COULD | P3 | 8 | WEB-001 | Onboarding + help center |

## Cross-module dependency spine (P0 critical path)

```
PLAT-001 -> PLAT-002 (envelope) -> every engine + RAG
PLAT-001 -> PLAT-003 (db) -> RULE-001 -> RULE-002 -> QMDG-005
PLAT-001 -> CORE-001 -> CORE-002/003 -> CORE-004 -> CORE-005 -> CORE-006 -> QMDG-006
CORE-005 -> QMDG-001 -> 002 -> 003 -> 004 -> 005 -> 006
KB-003 -> RAG-001 -> RAG-002 -> RAG-003
AUTH-001 -> API-001 -> {API-003, API-004}
WEB-001 -> WEB-002 -> WEB-003 ; CHART-001 needs QMDG-006 + WEB-001
end-to-end P0 demo = CORE-006 + QMDG-006 + RULE-003 + RAG-003 + CHART-001 + WEB-003 + API-001 + AUTH-001
```

## Implementation order and triggering

At greenfield stage the tasks are the plan, so the build order and the agent trigger live here alongside the catalog rather than in a separate `improvement/` folder. `docs/improvement/` is reserved for the post-launch audit and evolution stage (the cyberos convention), and is not created yet.

Files in this folder:

| File | Purpose |
|---|---|
| `IMPLEMENTATION_ORDER.md` | Master status index of every FR-as-task, grouped by phase, plus the per-phase wave/track sequencing and exit gates. The human-readable single source of order. |
| `backlog.yaml` | Machine-readable mirror of the status index (agents update it; humans audit it). |
| `PROMPT.md` | Pointer to the two trigger skills `strategem-implement` and `strategem-review` (under `.claude/skills/`). |
| `LEDGER.md` | Append-only execution ledger; every task run adds an entry (populated once implementation starts). |

### One ID space

Task id = task id (task `QMDG-001` implements `TASK-QMDG-001`). No second numbering scheme. The task is the task spec; it carries its own acceptance criteria (section 4) and verification (section 5), so there are no separate task cards.

### Lifecycle

`draft` (task body not yet authored - none at this snapshot; all 87 are authored) -> `ready_to_implement` -> `blocked` (unmet deps) -> `implementing` -> `in_review` -> `done` (human only) -> `superseded`. A `draft` task's first unit of work is to author the task body from its module README plus the cited primary source plus the two exemplars (`TASK-PLAT-002`, `TASK-CORE-001`). Eligibility: task is `ready_to_implement`, status not `done`, every `depends_on` is `done`. Pick order: phase, dependency spine, id.

### Conventions and gates

- One task = one branch `auto/tt-<id-lowercase>` = one review packet.
- Acceptance criteria in the task are binding; a task is not `in_review` until every criterion has evidence (test output, oracle-diff number, screenshot path, commit hash), recorded in `LEDGER.md`.
- Gates by language (DEC-2):
- Rust: `cargo fmt --check`, `cargo clippy -p <crate> -- -D warnings`, `cargo test -p <crate>`.
- Python: `ruff check`, `mypy`, `python -m pytest packages/<pkg>`.
- Web: `pnpm -C apps/web lint`, `pnpm -C apps/web typecheck`, `pnpm -C apps/web test`, `pnpm -C apps/web build`.
- Engines additionally run the oracle cross-check (kinqimen / kinliuren / kintaiyi / sxwnl / tyme4py) per the task.

### Safety invariants (non-negotiable)

- Never push to main, deploy, rotate a secret, or run a destructive migration on shared data without the operator.
- Engines keep the la so JSON envelope (strategy 4.3) exact and stamp every school flag; interpretation code never writes `ban` / `cach_cuc` / `lich_phap` / `co_truong_phai` and keeps citation + AIDisclosure + HumanReviewGate.
- CORE carries the highest test density; a solar-term instant off by more than 60 seconds is a stop-ship (strategy RISK-1).
- Sensitive personal data (birth data, question text): AES-256 at rest, TLS in transit, audit, PDPD/GDPR erasure and export. Never log it.
- Legal positioning (heritage education, not fortune-telling) is enforced in copy and behavior; LEGAL-004 counsel sign-off gates launch.

### How to trigger

Invoke the `strategem-implement` skill in a fresh agent session (for sign-off, invoke `strategem-review`), or say:

> Implement TT task PLAT-001 (runs the strategem-implement skill)

With no id, the agent takes the next eligible task in `IMPLEMENTATION_ORDER.md` order. At this snapshot only PLAT-001 is eligible (the single root); everything else cascades from it.
