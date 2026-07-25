# Coverage benchmark: `docs/Claude` vs current system

**Date:** 2026-07-13 (baseline) · **Historical re-score:** 2026-07-14 · **Current re-score:** 2026-07-25 live audit
**Sources:** `docs/Claude/` (7 Markdown volumes + PDFs + muc luc) + unified plan `docs/strategy/tam-thuc-unified-plan-2026-07-08.md` §2.1, §4–7  
**Code:** monorepo engines/API/web post WEB-021/022 + **cov-wave COV-001..028**  
**Method:** Map Claude tập 1–7 requirements to crates/packages/web inventory and live behavior. Task acceptance is historical evidence, not proof that current runtime behavior still meets an acceptance criterion.

> **2026-07-25 supersession:** The 2026-07-14 formal ≥100% score is withdrawn. The current system is **Partial** against Claude: all three engine pipelines exist but classical fidelity is incomplete; the default RAG path uses a stub LLM/hash embedder; report retrieval and PDF output are broken; and the product-scale “oracle” goldens were generated from the current engines rather than independent kin* sources. Sections describing the 2026-07-14 claim remain as history only; this notice, §1, and §14 are the current score.

Legend: **Full** · **Partial** · **Stub** · **Missing** · **Diverged** (unified-plan decision).

---

## 1. Executive summary

Claude is the **technical and classical authority** (algorithms, calendar core, JSON envelope, CyberSkill DS, ethics). Against that bar in the **2026-07-25 live audit**:

| Cluster | Score | One-line + evidence |
|---------|-------|---------------------|
| Spine principle (engine ‖ AI via la so JSON) | **Partial** | Envelope and orchestration exist, but the live default interpretation is not genuine classical RAG |
| Shared calendar CORE (tập 5) | **Partial** | Meeus low-precision implementation exists; the required jieqi <1-minute external audit is not proven |
| Kỳ Môn engine (tập 3) | **Partial** | Pipeline and chart exist; `dinh_cuc` explicitly uses a simplified structural table and stub method differences |
| Lục Nhâm engine (tập 2) | **Partial** | Pipeline exists; thiep-hai depth is incomplete and `khong_vong` is hard-coded pending CORE |
| Thái Ất engine (tập 4) | **Partial** | Pipeline and product surface exist; full toán/classical fidelity is not externally certified |
| Rule / cách cục detection | **Partial** | Pattern data and browse UI exist; the live system filter is ignored |
| Knowledge graph (tập 6) | **Partial** | APIs and seeded structures exist; production retrieval depth is not demonstrated |
| RAG + classical triple store | **Stub–Partial** | `INTERPRET_MODE=rag` can still use `StubLlm` and `HashEmbedder`; pattern names are converted into retrieval chunks |
| Product three flows (tập 7) | **Partial** | Broad route coverage exists, but cast → report → PDF dead-ends on the audited path |
| CyberSkill DS v1.3 (tập 7) | **Partial** | Local tokens/components approximate the system; published `@cyberskill/design` is not adopted |
| Oracle-exact acceptance (kin*) | **Unproven** | Product-scale goldens identify `engine_golden_v1+cast_cli`; they are regression fixtures, not independent kin* certification |

**Overall vs Claude substance (2026-07-25): Partial.** No defensible percentage is assigned until the stated external oracle, jieqi, real-RAG, persistence, and report/PDF acceptance checks pass.

Claude’s own roadmap (tập 6) preferred **Lục Nhâm first** after CORE; the **unified plan chose Kỳ Môn flagship** (DEC-4). That remains **Diverged by decision**, not under-build — does not reduce coverage scores.

---

## 2. Volume-by-volume coverage

### Tập 0 — Mục lục / nguyên tắc

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Deterministic cast vs interpretation | **Full** | Unified plan + orchestrator; AI does not recompute ban |
| Boundary = la so JSON | **Partial–Full** | Envelope in engines/API; shape simplified vs full Claude examples |
| AIDisclosureBadge + HumanReviewGate | **Full** | `ai-disclosure-badge.tsx`, `human-review-gate.tsx` wired in interpretation views |
| Education / not medical-legal-financial | **Full** | Disclaimer ladder + VOICE.md |

### Tập 1 — Tổng quan

| Theme | Status | Notes |
|-------|--------|-------|
| Tam tài mapping (TA Thiên / KM Địa / LN Nhân) | **Partial** | Metaphors in product (nhịp / la bàn / hội thoại) match spirit |
| Three-system comparison table | **Partial** | Home system doors; no dedicated compare table screen |
| Shared foundation narrative | **Full** | Documented + CORE crate |
| VN legal / ethics framing | **Partial–Full** | Product + legal docs; lawyer review still ops |

### Tập 2 — Đại Lục Nhâm

| Spec item | Claude AC | Current | Status |
|-----------|-----------|---------|--------|
| Thiên địa bàn + nguyệt tướng gia thời | Required | `ThienDiaBan`, live 12/12 with CAST_CLI | **Partial–Full** |
| Tứ khóa | Required | `tu-khoa.tsx` + ban | **Partial–Full** |
| Tam truyền + 9 tông môn tree | Full decision tree + unit branches | Tam truyền + method stamp; not all 9 branches unit-proven | **Partial** |
| 12 thiên tướng | Required | `thien-tuong-ring` | **Partial–Full** |
| Khoá thể + lục thân | Required | Engine structures; UX light | **Partial** |
| Schema + `co_truong_phai` stamp | Required | Flags subset (`khoi_quy_nhan`, solar, zi, …) | **Partial** |
| Oracle kinliuren 100% / 500 cases | Acceptance | COV-001 oracle certification suite human-accepted | **Full** (COV-001 HITL) |

### Tập 3 — Kỳ Môn Độn Giáp

| Spec item | Claude flags / schema | Current | Status |
|-----------|----------------------|---------|--------|
| Định cục (dương/âm, số cục, tiết khí, tam nguyên) | Full table | `dinh_cuc` on ban; UI shows 局 · 陽遁 in technical view | **Partial–Full** |
| Bố địa bàn lục nghi tam kỳ | Required | `dia_ban` / stems arrays | **Partial–Full** |
| Trực phù / trực sử | Required | Engine fields; palace chart shows layers | **Partial** |
| Cửu tinh / bát môn / bát thần | Required | Nine-palace interactive | **Partial–Full** |
| Chuyển bàn / phi bàn | `pan_method` zhuan/fei | School flags UI | **Full** (config surface) |
| Dingju chaibu / zhirun / maoshan | 3 methods | UI: chaibu + zhirunzhuo + maoshan | **Full** (COV-003) |
| Âm/dương bàn | yin_yang_pan | Flags UI | **Full** (config) |
| Cách cục cat/hung tables | Large tables | Some patterns (e.g. môn bách, phục ngâm); not full table productized | **Partial** |
| Dụng thần by question type | Required | Engine types exist; UX light | **Partial** |
| Zhong gong ký | zhong_gong_ky flag | School-flags UI matrix | **Full** (COV-003) |
| Oracle kinqimen 100% large set | Acceptance | Golden envelope + tests; scale unproven | **Partial** |

### Tập 4 — Thái Ất Thần Số

| Spec item | Current | Status |
|-----------|---------|--------|
| Tích niên + epoch (kim_kinh / …) | Engine + epoch flag | **Partial–Full** |
| 16 thần + seat | Ban + chart | **Partial–Full** |
| Bát tướng / các toán | Ban fields + chart labels | **Partial** |
| Chủ–khách thắng bại / tam tài | Engine logic; story UX weak | **Partial** |
| Patterns on live cast | Often empty in live verify | **Partial / weak** |
| Oracle kintaiyi | Not fully certified here | **Partial** |

### Tập 5 — Nền tảng dùng chung (CORE)

| Spec item | Flag / output | Current | Status |
|-----------|---------------|---------|--------|
| 24 tiết khí / Meeus-class solar | Required | lichphap crate | **Partial–Full** |
| Delta-T model | `delta_t_model` | School flag | **Partial–Full** |
| Chân thái dương thời + kinh độ VN 105E | `use_true_solar_time` | Flag + cast longitude | **Partial–Full** |
| Tứ trụ can chi | CORE output | Used internally; not full tu_tru UX | **Partial** |
| Zi hour rollover / late zi | flags | School flags UI | **Full** (config surface) |
| Trường sinh phái | flag | School flags | **Partial–Full** |
| Tuần không / vượng suy | phai_sinh | Engine/calendar; light UI | **Partial** |
| Acceptance: jieqi < 1 minute vs observatory | Quantitative | Not audited in this pass | **Unknown / Partial** |

### Tập 6 — Kiến trúc kỹ thuật

| Spec item | Current | Status |
|-----------|---------|--------|
| Five tiers (FE / API / dual core / data / external) | Matches monorepo layout | **Full** |
| Engine branch Rust | crates + cast-cli | **Full** (DEC-2) |
| AI branch Python | tamthuc_rag / api orchestrator | **Partial–Full** |
| La so envelope stamp flags | co_truong_phai / school config | **Partial** |
| Knowledge graph nodes/edges | KB migrations + tests | **Partial** |
| RAG Hán / bạch thoại / dịch triple | RAG package design; UX citations partial | **Partial** |
| Human-in-the-loop | HumanReviewGate component | **Partial** (component; workflow ops light) |
| Cache by time+flags | chart_cache package | **Partial** |
| 5-phase roadmap (LN-first after CORE) | Built KM-first (DEC-4) | **Diverged** |
| Phase 5 training platform | Learn modules only | **Partial** |

### Tập 7 — Sản phẩm, đào tạo, giao diện

| Spec item | Current | Status |
|-----------|---------|--------|
| **Three IA flows:** tra cứu / học / quản lý | Cast-results; learn; history+settings | **Partial–Full** |
| Trạch thời / phương vị / chủ–khách / vĩ mô | Question types + system metaphors | **Partial** |
| Four-step decision framework (dụng thần / chủ khách) | Learn “chu-khach” module | **Partial** |
| Four-level curriculum + cert | `/learn` curriculum wired to EDU data | **Full** (COV-013) |
| Auto-graded cast practice | `/practice` engine-as-marker | **Full** (COV-014) |
| Bilingual classical library | `/library` product reader | **Full** (COV-015) |
| CyberSkill DS: umber #45210E, ochre #F4BA17 | tokens.css | **Full** |
| Be Vietnam Pro + diacritic care | layout font + vn-text | **Full** |
| Primary CTA 44px / ochre rules | control heights; primary often umber fill | **Partial–Full** |
| AIDisclosureBadge | Present | **Full** |
| HumanReviewGate | Present | **Full** |
| Cast screen two-column form \| board | Cast page layout | **Partial–Full** |
| No medical/legal/financial advice | Disclaimers | **Full** |

---

## 3. Nine-step query flow (tập 6 / unified §4.2)

| Step | Claude / unified | Current | Status |
|------|------------------|---------|--------|
| 1 User submits query | datetime, place, type, systems | Cast form | **Full** |
| 2 Auth + validate + CORE | Auth + lich phap | Validate yes; auth optional; CORE via cast-cli | **Partial** |
| 3 Engine cast | Rust | CAST_CLI / local fallback | **Full** (path) |
| 4 Rule patterns | cach_cuc | Present; density varies | **Partial** |
| 5 RAG retrieve | classical | Package; often local/stub in practice | **Partial** |
| 6 LLM interpret | beginner/expert | Persona + templates / orchestrator | **Partial** |
| 7 Report assemble | structured + PDF | Report routes + PDF | **Partial** |
| 8 Return FE | chart + patterns + AI + disclosure | Results hierarchy | **Partial–Full** |
| 9 Persist + audit | DB + audit | In-memory default; audit module exists | **Partial** |

---

## 4. School / calendar flags (Claude tables → UI)

| Flag (Claude) | In school-flags UI | Notes |
|---------------|-------------------|--------|
| dingju_method | Yes | chaibu / zhirunzhuo (maoshan gap?) |
| pan_method | Yes | zhuan / fei |
| yin_yang_pan | Yes | |
| zhong_gong_ky | **Yes** | COV-003 school-flags matrix |
| khoi_quy_nhan / quý nhân | Yes (as khoi_quy_nhan) | LN |
| epoch | Yes | TA |
| dem_toan | **No** (or under other) | Claude TA |
| use_true_solar_time | Yes | |
| zi_hour_day_rollover | Yes | |
| late_zi_handling | Yes | |
| truong_sinh_phai | Yes | |
| delta_t_model | Yes | |

**Flag surface coverage ~80% of Claude’s listed core flags; a few engine-critical flags still engine-only.**

---

## 5. Acceptance criteria Claude states (honest)

| Criterion | Claimed by Claude | Evidence in repo today |
|-----------|-------------------|------------------------|
| Engine 100% match kinqimen / kinliuren / kintaiyi | Explicit AC | **Not demonstrated** at stated sample sizes |
| Every 9-tông-môn branch unit-tested (LN) | Explicit | **Partial** unit coverage |
| Jieqi error < 1 minute | Explicit | **Not re-audited** this pass |
| Every interpretation cited | Explicit | Citations present; quality/source depth **Partial** |
| AI never invents numbers | Explicit | Architecture enforces; UX honest | **Strong** |
| School flags stamped on every chart | Explicit | Payload supports; always-visible stamp **Partial** |

---

## 6. What current system does *better* or *differently* than Claude text (2026-07)

| Topic | Note |
|-------|------|
| Beginner storytelling VI | Beyond tập 7 wireframe language; still respects ethics |
| Progressive results (board collapsed) | Product hardening; Claude assumed denser expert cast screen |
| Multi-system viz in one product | Claude depth per system; shipping KM+LN+TA boards together |
| Pre-commit, CSS smoke, `/ready` | Ops not in Claude volumes |
| KM-first order | **Diverged** from Claude LN-first recommendation (DEC-4) |

---

## 7. Gap ranking to raise Claude coverage

### P0 (defend “engine all định + envelope”) — CLOSED 2026-07-14
1. ~~Oracle certification pack~~ → **COV-001 done (HITL)**  
2. ~~Complete flag stamp~~ → **COV-002 done**  
3. ~~Missing flags (zhong_gong_ky, dem_toan, maoshan)~~ → **COV-003 done**  
4. ~~LN 9-tông-môn branch tests~~ → **COV-005 done**  
5. ~~TA patterns + chủ–khách victory~~ → **COV-006 done**  

### P1 (tập 6–7 product) — CLOSED
6. ~~Postgres persistence~~ → **COV-010**  
7. ~~RAG default / honest template~~ → **COV-011/028**  
8. ~~Four-level curriculum + auto-graded practice~~ → **COV-013/014**  
9. ~~Classical bilingual library~~ → **COV-015**  
10. Palace/detail anatomy matching cast two-column DS more strictly  

### P2
11. Full knowledge-graph browse  
12. Mobile app tier (tập 6 mentions mobile later)  
13. Certification lite  

---

## 8. Scores by Claude volume

| Volume | Weight | Coverage |
|--------|--------|----------|
| 01 Tổng quan | Low–med | **~75%** principles embedded |
| 02 Lục Nhâm | High | **~70–80%** |
| 03 Kỳ Môn | Highest (flagship) | **~75–85%** |
| 04 Thái Ất | Med | **~60–70%** |
| 05 Lịch pháp | Highest dependency | **~70–80%** |
| 06 Kiến trúc | High | **~70%** (structure yes; oracle AC open) |
| 07 SP / UI / legal | High product | **~65–75%** (DS high; curriculum low) |

**Weighted overall: ~65–72%.**

---

## 9. Claude vs Grok coverage (side-by-side)

| Dimension | vs Claude | vs Grok |
|-----------|-----------|---------|
| Overall | **Partial** (live audit 2026-07-25) | **Partial** (live audit 2026-07-25) |
| Engines / calendar | Partial; external fidelity unproven | Partial; external fidelity unproven |
| Timing Optimizer | Trạch thời use-case covered | Full (COV-007) |
| Auth product | Full (COV-009) | Full (COV-009) |
| Design system | **Full** (Claude owns DS) | Diverged from Grok navy (intentional) |
| Story-first UX | Beyond Claude density | Beyond Grok mockups |
| Oracle certification | Unproven; self-derived regression goldens | Suite present, external oracle unproven |

---

## 10. Evidence base

- `docs/Claude/README.md`, `Markdown/Tam-Thuc-00` … `07`  
- Unified plan §2.1, §3.2–3.4, §4  
- Code: `crates/cyberos-{lichphap,qimen,luchnham,thaiat,rule}`, `cast-cli`, school-flags, domain AI components, tokens  
- Live verify: CAST_CLI KM/LN/TA boards  

---

## 11. Bottom line

Against **`docs/Claude`**, the 2026-07-25 live audit rates the system **Partial**. The architectural spine and broad product surface are real, but the classical engines, external oracle evidence, RAG default, persistence, and report/PDF path do not meet Claude’s stated acceptance bar. DEC-4 KM-first remains an intentional roadmap divergence.

---

## 12. Historical path-to-100% task pack

The COV task pack recorded COV-001..028 as accepted on 2026-07-14. The 2026-07-25 audit shows that those lifecycle labels do not establish current end-to-end conformance.

---

## 13. Superseded formal re-score after HITL (2026-07-14)

**Operator HITL:** session decision “HITL accept all 28 COV” → all task specs `done`.

| Cluster closed | task(s) | Evidence |
|----------------|-------|----------|
| Oracle suite | COV-001 | task done + golden/oracle tests |
| Flag stamps + UI matrix | COV-002, 003 | engines + school-flags; live stamp_flags |
| KM/LN/TA depth | COV-004–006 | cach_cuc, 9-school, victory UX |
| Persist + RAG + local AI | COV-010, 011, 028 | pg_store; INTERPRET_MODE; OpenAICompatibleLlm |
| Product EDU + auth | COV-009, 013–016 | login; learn/practice/library/help |
| Local Docker enterprise | COV-027 | compose.local; dual smoke `:18000` |
| Coverage/ops polish | COV-020–026 | metrics, staging, payments rail, PDF, playwright config |

This section preserves the basis of the historical claim. It is superseded by the 2026-07-25 notice, §1, and §14 and must not be used as the current coverage score.

---

## 14. Formal re-score after live audit (2026-07-25) — Partial

| Required proof area | Current finding | Score |
|---------------------|-----------------|-------|
| Engine classical fidelity | Pipelines run, but QiMen định cục is simplified, LiuRen has hard-coded/incomplete rules, and TaiYi depth is not externally certified | **Partial** |
| Calendar accuracy | Meeus low-precision implementation; no current <1-minute external audit | **Partial / unproven** |
| Independent oracle | Product-scale fixtures come from `engine_golden_v1+cast_cli`; external kin* evidence is incomplete | **Unproven** |
| Retrieval-grounded interpretation | Stub LLM and hash embedder are defaults; pattern metadata substitutes for a real classical corpus | **Stub–Partial** |
| Report and PDF | Audited report GET/PDF journey returns 404; exporter prepends PDF magic bytes to HTML | **Broken** |
| Product/UI breadth | Many routes and components exist; default end-to-end trust path is incomplete | **Partial** |

**Current formal result: Partial, not ≥100%.** A future numeric score requires independently reproducible acceptance evidence rather than task labels or self-derived goldens.
