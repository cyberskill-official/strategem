# Coverage benchmark: `docs/Grok` vs current system

**Date:** 2026-07-13  
**Sources:** `docs/Grok/` (51 PDFs + mockups + BACKLOG/AGENTS/README) reconciled with `docs/strategy/tam-thuc-unified-plan-2026-07-08.md`  
**Code HEAD (approx):** post WEB-021/022 (`f75d48d` lineage)  
**Method:** Map Grok BACKLOG epics + PRD MVP scope + UI screen list + API reference to inventory of crates, packages, web routes, live verify evidence.

Legend: **Full** · **Partial** · **Stub** · **Missing** · **Diverged** (built differently by design / Claude source).

---

## 1. Executive summary

| Area | Grok intent | Coverage | Score (rough) |
|------|-------------|----------|---------------|
| Deterministic engines (KM/LN/TA + calendar) | Core P0–P2 | **Partial → strong Partial** | ~70–85% |
| La-so envelope + cast API | Backend P0 | **Partial** (working E2E) | ~75% |
| Rule / pattern layer | P0 hundreds of patterns | **Partial** (rule crate + some detect; not 150–200 seeded DB) | ~40–55% |
| RAG + real LLM interpretation | P0 | **Partial** (packages + tests; not production vector/LLM path wired to UX as primary) | ~35–50% |
| Frontend screens (8 major) | MVP + mockups | **Partial** (6/8 present; Timing Optimizer + Auth UI missing) | ~55–65% |
| Interactive charts | 9-palace + LN/TA | **Partial–Full** for viz; export partial | ~70% |
| Auth / RBAC / social | P0 | **Partial** (package + tests; not product login UX) | ~40% |
| Timing Optimizer / Scenario compare | MVP strategic tools | **Stub** (API 501) | ~5–10% |
| Learning hub | simulator + glossary + quiz | **Partial** (3 short modules; no simulator/quiz) | ~30% |
| Ops deploy / monitoring / support | P1 | **Partial** CI; deploy secrets open | ~40% |
| i18n VI/EN/ZH | required | **Strong Partial** (390 keys, VI-first storytelling) | ~80% |
| Ethics / disclaimer / anti-destiny | mandatory | **Strong Partial** (VOICE + ladder) | ~75% |
| Design system | Navy/Teal Grok mockups | **Diverged** → CyberSkill umber/ochre (Claude DS) | intentional |

**Overall (weighted to Grok MVP PRD):** approximately **~55–60% surface coverage**, with **engines + cast → results path** above that, and **strategic tools / full RAG / auth productization** well below.

The Grok set is **product breadth** (outline PDFs). Claude is **algorithm depth**. Current monorepo follows the **unified plan**: Claude engines + CyberSkill DS + Grok-shaped API/product modules — not a pixel-clone of Grok navy mockups.

---

## 2. Grok epic → system coverage

### Epic 1 — Foundation

| Task (Grok BACKLOG) | Spec PDFs | Current system | Status |
|---------------------|-----------|----------------|--------|
| Monorepo backend+frontend | 27, 45 | `apps/web`, `packages/*`, `crates/*`, pnpm/uv/cargo | **Full** (not Turborepo/Nx naming; functional monorepo) |
| CI/CD basic | 22, 39 | GitHub Actions CI (rust/python/web), CD/images, security scans | **Partial** (no full k8s prod link) |
| PostgreSQL + migrations | 14, 46 | `db_schema` / migrations exist in program; runtime cast path often **in-memory** | **Partial** |
| Auth JWT + social + RBAC | 36, 21 | `tamthuc_auth` (JWT/RBAC/crypto/erasure tests) | **Partial** (lib yes; **no Login/Sign-up UI**) |
| Birth data encryption | 36 | Auth crypto tests present | **Partial** (not productized in cast form) |

### Epic 2 — Calculation engines

| System | Grok AC | Current | Status | Notes |
|--------|---------|---------|--------|-------|
| **Kỳ Môn** | Ju + plates + 15–20 patterns; 30 classical tests | `cyberos-qimen` + `cast-cli` + live ban (9 cung, môn/tinh/thần) | **Partial–Full** | School flags (chaibu/zhirunzhuo, zhuan/fei) in settings; classical golden volume vs 30 examples needs audit |
| **Lục Nhâm** | Tứ khóa, tam truyền, 12 tướng | `cyberos-luchnham` + web Thiên địa / tứ khóa / tam truyền / thiên tướng | **Partial–Full** | Live verify: 12/12 dia/thien when CAST_CLI; pattern depth thinner |
| **Thái Ất** | P2 full | `cyberos-thaiat` + web chart | **Partial** | Live often **0 patterns**; mệnh pháp not first-class UX |
| Calendar / lịch pháp | Shared core | `cyberos-lichphap` | **Partial–Full** | True solar / zi flags via school settings |

### Epic 3 — Rule engine & KB

| Item | Grok | Current | Status |
|------|------|---------|--------|
| Rule engine JSON conditions | 31 | `cyberos-rule` + API patterns | **Partial** |
| Seed 150–200 patterns | 37 | KB package + seed tests; not “hundreds live in product UX” | **Partial** |
| Searchable pattern DB UI | 17, 35 | Missing dedicated library UI | **Missing** |

### Epic 4 — RAG & AI

| Item | Grok | Current | Status |
|------|------|---------|--------|
| Vector DB + embed | 32 | `tamthuc_rag` (vectorstore, embed, retrieve, interpret, ethics) | **Partial** (code/tests; not default cloud RAG UX) |
| Beginner/Expert interpretation | PRD 4.2 | Persona toggle + composed literary readings when stubs | **Partial** |
| Citations + disclaimer | 25, PRD | Citation cards, AI disclosure badge, review gate, VOICE.md | **Partial–Full** for disclosure; RAG citations local/stub often |
| Follow-up chat | UI 07 | Missing | **Missing** |
| Cross-system consensus | PRD | `calculate/all` exists; no full UI compare | **Stub–Partial** |

### Epic 5 — Frontend screens (Grok 35 + 51 + mockups)

| Screen (Grok) | Mockup / wireframe | Current route | Status | Gap |
|---------------|-------------------|---------------|--------|-----|
| Landing / Home | Landing Page.jpg | `/` | **Partial–Diverged** | Story-first VI; not navy “Start Free / Watch Demo” mockup |
| Dashboard | Dashboard.jpg | `/dashboard` | **Partial** | Recent + saved + quick cast; no mini live chart hero |
| Query Input | Query Input.jpg | `/cast` | **Partial–Full** | System doors + chips; no birth data / multi-system wizard |
| Results / Chart | Detailed Chart.jpg | `/results/[id]` | **Partial–Full** | Story hierarchy + KM/LN/TA boards; board behind disclosure |
| Timing Optimizer | Timing Optimizer.jpg | — | **Missing** (API **501**) | Core Grok MVP tool |
| Scenario Comparison | Scenario Comparison.jpg | — | **Missing** (API **501**) | |
| Report Detail | Full Report View.jpg | `/report/[id]` | **Partial** | PDF path exists; polish vs mockup |
| Learning Hub | Learning Hub.jpg | `/learn`, `/learn/[slug]` | **Partial** | 3 short modules; no simulator/quiz/glossary DB |
| Profile & Settings | Profile & Settings.jpg | `/manage/settings` | **Partial** | School flags only; no profile/avatar/account |
| History | (management) | `/manage/history` | **Partial** | Present |
| Pricing / packages | (Grok monetize-ish) | `/pricing` | **Partial** | Waitlist local honesty; no real payments |
| Auth Login/Sign-up | wireframes | — | **Missing** | |

### Epic 6 — Report, test, DevOps, launch

| Item | Current | Status |
|------|---------|--------|
| Report PDF generation | API + web PDF button path | **Partial** |
| Comprehensive classical validation suite | Golden + unit tests; not 30–50 classic cases certified | **Partial** |
| CI (fmt/clippy/ruff/eslint/build) | Yes | **Partial–Full** |
| Deploy staging beta | Ship checklist; secrets not linked | **Partial / open** |
| Monitoring/alerting product | packages observability; not full APM | **Partial** |
| Help center / support | Missing | **Missing** |
| Master partnership framework | Doc only | **Missing** (out of code) |

---

## 3. PRD MVP (Grok 05) checklist

| MVP requirement | Coverage |
|-----------------|----------|
| Chart generation 3 systems | **Yes** (live CAST_CLI verified) |
| Cross validation 3 systems | **API all** partial; **no dedicated UX** |
| Timing Optimizer | **No** (501) |
| Scenario comparison | **No** (501) |
| AI interpretation 2 levels | **Yes-ish** (persona + templates; not full RAG LLM prod) |
| Interactive 9-cung | **Yes** |
| Personal dashboard + PDF report | **Partial** |
| Learning hub Kỳ Môn tutorials | **Partial** (story modules, not simulator) |
| Input Gregorian+tz | **Yes** |
| Lunar / Bát tự input | **No** |
| Performance <3s cast | **Yes** locally (observed) |
| Disclaimer always | **Yes** (ladder + VOICE) |

---

## 4. UI/UX (Grok 07) vs CyberSkill DS

| Grok UI spec | Current | Verdict |
|--------------|---------|---------|
| Colors navy/teal | Umber `#45210E` / ochre `#F4BA17` / paper | **Diverged by design** (Claude CyberSkill DS wins in unified plan) |
| Inter typography | Be Vietnam Pro | **Diverged** (better VI diacritics) |
| shadcn/ui | Custom CS components | **Diverged** |
| Dark mode default | Token dark theme exists; not default product mode | **Partial** |
| WCAG AA / a11y | Partial (ARIA, chips, reduced motion) | **Partial** |
| Progressive loading skeleton | Cast/results skeleton added | **Partial** |
| Hover palace sidebar | Click select palace; no rich sidebar metadata panel | **Partial** |
| Thiên/Địa toggle | LN shows both; not full KM toggle story | **Partial** |
| Export PNG/SVG | Libraries present | **Partial** |
| Ask follow-up chat | No | **Missing** |

**Wording vs Grok product voice:** Grok PRD is more “platform / enterprise / timing optimizer.” Current product is intentionally **beginner-story VI**, anti-destiny (aligned with Grok **25 Ethics** and Claude legal framing more than pitch mockups).

---

## 5. API (Grok 12) coverage

| Endpoint (Grok) | Current | Status |
|-----------------|---------|--------|
| `POST /calculate/qimen` | `/api/v1/calculate/qimen` | **Full** (live) |
| `POST /calculate/*` + all | yes | **Partial–Full** |
| `POST /timing/optimize` | **501** | **Stub** |
| `POST /scenario/compare` | **501** | **Stub** |
| `POST /reports/generate` + PDF | yes | **Partial** |
| Auth JWT | package; not enforced on all public cast | **Partial** |
| Rate limit free/premium | middleware present | **Partial** |
| Versioning `/v1` | yes | **Full** |
| Health | `/healthz` + `/ready` | **Full** (beyond Grok outline) |

---

## 6. Non-goals in Grok that current system already exceeds

| Topic | Note |
|-------|------|
| Beginner storytelling UX | Stronger than 2026-07 Grok mockups (VI-first, progressive results) |
| Multi-system chart viz (LN plates, TA ring) | Grok UI heavily KM-first; we ship LN/TA boards |
| Pre-commit + CSS smoke + voice denylist | Ops/product hardening not in Grok outlines |
| CAST_CLI readiness probe | Production-minded |

---

## 7. Gap ranking (if goal = “cover Grok MVP”)

### P0 gaps (block Grok MVP claim)
1. **Timing Optimizer UI + non-501 API**  
2. **Scenario compare UI + API**  
3. **Auth product surface** (login, session, tier gates on cast)  
4. **Postgres-backed persistence in real deploy** (not only in-memory)  
5. **Pattern seed volume + classical golden set** (30–50 KM examples)  
6. **Production RAG path** (or honestly brand interpretation as rule+template)

### P1 gaps
7. Learning simulator / glossary search / quiz  
8. Cross-system compare UX  
9. Palace detail sidebar (metadata + patterns)  
10. Lunar / Bát tự input  
11. Full report polish vs mockup  
12. Monitoring/alerting productization  

### P2 / later (Grok post-MVP / ops)
13. Help center, partnership, pitch-ready enterprise  
14. Competitive analysis tool  
15. PWA / dark-default  

---

## 8. Coverage scores by Grok document cluster

| Doc cluster (approx PDF #s) | Theme | Coverage |
|----------------------------|--------|----------|
| 01, 28–30, 45 | Algorithms / engines | **70–85%** |
| 05, 02, 03 | PRD / positioning | **50–60%** productized |
| 06, 12, 49 | Backend / API | **65–75%** |
| 07, 15, 34, 35, 51 | UI / pages / charts | **55–65%** (DS diverged) |
| 31, 24, 37 | Rules / KB | **40–55%** |
| 32, 23, 25 | RAG / prompts / ethics | **40–50%** code; ethics UX **75%** |
| 33, 08 | Reports / samples | **45–55%** |
| 36 | Auth | **40%** |
| 17, 42 | Onboarding / support | **25–35%** |
| 09, 38 | Testing strategy | **50–60%** |
| 18, 41 | Analytics / monitoring | **30–40%** |
| 21–22, 39 | Security / DevOps | **45–55%** CI; deploy open |
| 19, 13 | Legal / budget | Docs elsewhere; not full in-app legal suite |
| 11, 16, 43 | Pitch / competitive / partners | Strategy docs only |

**Weighted overall vs Grok breadth: ~55%.**  
**Vs Grok P0 engine+cast+basic FE only: ~70%.**  
**Vs Grok full MVP including Timing Optimizer + Auth product: ~45–50%.**

---

## 9. Design / wording divergence (important)

Grok mockups assume:

- English-heavy platform chrome, navy/teal, Timing Optimizer as hero tool  
- Dashboard-centric IA  

Current product assumes:

- **VI-first storytelling**, CyberSkill umber/ochre  
- Cast as “vẽ bức hình”, results “Tóm lại cho bạn”  
- Monetization waitlist honest local-only  

This is **not under-implementation of Grok UI** alone — it is **reconciled direction** (unified plan § design + recent product decisions). Benchmark scores treat Grok **capability** as requirement, Grok **pixels** as optional unless product re-adopts them.

---

## 10. Recommended next builds to raise Grok coverage fastest

1. **Un-stub Timing Optimizer** (even v0: score 7 days with KM only) — largest PRD hole  
2. **Auth gate optional** on cast + “Của bạn” sync  
3. **Postgres persistence** in local Docker compose (user has Docker)  
4. **KM classical golden pack** (30 cases) to defend “100% engine” claim  
5. **Pattern seed surface** (browse top 50 patterns) for Learning/KB  

---

## 11. Evidence sources for this audit

- `docs/Grok/README.md`, `BACKLOG.md`, `AGENTS.md`  
- PDF extract: 00, 05, 07, 12, 35, 51, 20, 25  
- `docs/strategy/tam-thuc-unified-plan-2026-07-08.md` §2.2 Grok description  
- Code inventory: crates, `tamthuc_*` packages, `apps/web` routes  
- Live verify (prior session): CAST_CLI cast KM/LN/TA, `/ready`, browser results  

---

**Bottom line:** Against **Grok’s product map**, the system is a **working decision-support spine** (engines + cast + multi-system charts + beginner results + i18n + ethics) at roughly **mid-coverage**. Against **Grok’s full MVP checklist**, the largest holes are **Timing Optimizer, Scenario compare, Auth UX, full RAG production path, and deploy-linked persistence** — not the story-first landing.
