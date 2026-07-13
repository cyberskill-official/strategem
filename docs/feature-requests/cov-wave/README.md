# Coverage-to-100% FR pack

Wave created 2026-07-13 from dual benchmarks:
- Claude: `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md` (~65–72%)
- Grok: `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md` (~55–60%)

These FRs close **residual product + oracle acceptance** gaps. Many original module FRs are already `done` at package level; COV-* is the integration/certification layer required for **100% coverage claims**.

## Status

All COV-* start as `ready_to_implement`. Only a human sets `done`.

## Suggested order (critical path)

1. COV-001 oracle suite
2. **COV-027 local Docker full-stack** + **COV-028 LMStudio OpenAI-compatible AI** (enterprise local path)
3. COV-002 flag stamp + COV-003 flag UI
4. COV-004/005/006 engine depth
5. COV-010 postgres + COV-020 deploy wiring
6. COV-007/008 timing + scenario product
7. COV-009 auth product
8. COV-011 RAG default path (uses COV-028 client)
9. COV-013–016 education surfaces
10. COV-012, 017–019 polish
11. COV-021–026 ops/monetize/coverage floors

## Index

| ID | Pri | Phase | Module | Title | h |
|----|-----|-------|--------|-------|--:|
| COV-001 | MUST | P0 | CORE | Oracle certification suite — kinqimen/kinliuren/kintaiyi + j… | 40 |
| COV-002 | MUST | P0 | PLAT | Every cast stamps full co_truong_phai + co_lich_phap on enve… | 12 |
| COV-003 | MUST | P0 | WEB | Complete school-flag matrix UI (maoshan, zhong_gong_ky, dem_… | 10 |
| COV-004 | MUST | P0 | QMDG | QiMen full cat/hung cach_cuc tables as pattern-as-data + det… | 24 |
| COV-005 | MUST | P1 | LN | LiuRen nine-school tam truyen branch suite + khoa_the UX… | 20 |
| COV-006 | MUST | P1 | TAT | TaiYi cach_cuc + chu-khach victory surfaced in API and story… | 16 |
| COV-007 | MUST | P1 | STRAT | Timing Optimizer product path — un-stub API + web page… | 24 |
| COV-008 | MUST | P1 | STRAT | Scenario comparison product path — un-stub API + web page… | 16 |
| COV-009 | MUST | P1 | AUTH | Auth product surface — login/signup + session + optional cas… | 28 |
| COV-010 | MUST | P1 | PLAT | Postgres default persistence for queries/charts/reports in n… | 16 |
| COV-011 | MUST | P1 | RAG | Production RAG default interpretation path (or honest templa… | 24 |
| COV-012 | SHOULD | P1 | STRAT | Cross-system validation UI (calculate/all + consensus view)… | 14 |
| COV-013 | MUST | P2 | EDU | Four-level curriculum UI wired to EDU-001 data… | 16 |
| COV-014 | MUST | P2 | EDU | Auto-graded chart practice UI (engine as marker)… | 20 |
| COV-015 | MUST | P2 | EDU | Bilingual classical library reader UI… | 14 |
| COV-016 | SHOULD | P2 | EDU | First-run onboarding + help center product… | 12 |
| COV-017 | SHOULD | P1 | CHART | Palace/detail sidebar for interactive charts… | 12 |
| COV-018 | SHOULD | P2 | WEB | Lunar calendar and Bát tự input modes… | 14 |
| COV-019 | SHOULD | P1 | WEB | Searchable pattern library (top seeds across 3 systems)… | 10 |
| COV-020 | MUST | P1 | PLAT | Staging deploy wiring — Vercel + VPS API + Supabase linked r… | 20 |
| COV-021 | SHOULD | P2 | PLAT | Monitoring & alerting productization (metrics, cast latency,… | 16 |
| COV-022 | COULD | P2 | KB | Knowledge-graph browse API + lightweight explorer UI… | 16 |
| COV-023 | SHOULD | P1 | REPORT | Report PDF polish + full legal disclaimer block… | 10 |
| COV-024 | MUST | P1 | WEB | Playwright full product journeys (home→cast→results→timing→a… | 16 |
| COV-025 | SHOULD | P1 | PLAT | Raise coverage floors to 90% engines+API and wire gates.env… | 12 |
| COV-026 | SHOULD | P2 | WEB | Single payment rail for premium tier (one provider only)… | 20 |
| COV-027 | MUST | P0 | PLAT | Local full-stack Docker compose — build api+web+cast-cli from source… | 20 |
| COV-028 | MUST | P0 | RAG | LMStudio local AI — OpenAI-compatible LLM client + honest degraded path… | 16 |

**Total effort (sum): 488 h** (rough). Includes enterprise local Docker + LMStudio (COV-027/028).

## Definition of 100%

When all COV-* MUST items are human-accepted `done` (including **COV-027** local Docker and **COV-028** LMStudio), and SHOULD/COULD either done or explicitly waived in benchmark addenda:
- Claude weighted score ≥ 100% on capability dimensions in the benchmark tables.
- Grok weighted score ≥ 100% on MVP + ops dimensions (or waived with operator signature).
- Both benchmark docs updated with evidence links.
