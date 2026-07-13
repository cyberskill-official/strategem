# Coverage benchmark: `docs/Claude` vs current system

**Date:** 2026-07-13  
**Sources:** `docs/Claude/` (7 Markdown volumes + PDFs + muc luc) + unified plan `docs/strategy/tam-thuc-unified-plan-2026-07-08.md` §2.1, §4–7  
**Code:** monorepo engines/API/web post WEB-021/022  
**Method:** Map Claude tập 1–7 requirements (engine schemas, flags, architecture, product IA, DS) to crates/packages/web inventory + live-verify evidence.

Legend: **Full** · **Partial** · **Stub** · **Missing** · **Diverged** (unified-plan decision).

---

## 1. Executive summary

Claude is the **technical and classical authority** (algorithms, calendar core, JSON envelope, CyberSkill DS, ethics). Against that bar:

| Cluster | Score (approx) | One-line |
|---------|----------------|----------|
| Spine principle (engine ‖ AI via la so JSON) | **~90%** | Honored in architecture and product framing |
| Shared calendar CORE (tập 5) | **~70–80%** | Crate + flags; oracle-minute claims not fully proven here |
| Kỳ Môn engine (tập 3) | **~75–85%** | Flagship path live; school flags subset; classical suite not 100% certified |
| Lục Nhâm engine (tập 2) | **~70–80%** | Plates + tứ khóa + tam truyền live; khoa thể / lục thân / 9-school depth thinner |
| Thái Ất engine (tập 4) | **~60–70%** | Ban shape + chart; patterns/victory UX weak |
| Rule / cách cục detection | **~50–65%** | Rule crate + some hits; not full cat/hung tables as product DB |
| Knowledge graph (tập 6) | **~40–50%** | Schema/migrations/tests; not product traversal UX |
| RAG + classical triple store | **~40–55%** | Packages + ethics tests; not full Hán/bạch/dịch retrieval in default UX |
| Product three flows (tập 7) | **~65–75%** | Lookup strong; learning light; management partial |
| CyberSkill DS v1.3 (tập 7) | **~85–95%** | Umber/ochre, Be Vietnam Pro, disclosure + review components |
| Oracle-exact acceptance (kin* 100%) | **~30–50%** | Golden/envelope tests exist; not 500-case kinliuren / kinqimen certification |

**Overall vs Claude substance: ~65–72%.**  
Higher than vs full Grok product breadth (~55%), because the repo is built on Claude’s spine (Rust engines + DS + envelope) first.

Claude’s own roadmap (tập 6) preferred **Lục Nhâm first** after CORE; the **unified plan chose Kỳ Môn flagship** (DEC-4). That is **Diverged by decision**, not accidental under-build.

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
| Oracle kinliuren 100% / 500 cases | Acceptance | Not demonstrated at that scale | **Missing–Partial** |

### Tập 3 — Kỳ Môn Độn Giáp

| Spec item | Claude flags / schema | Current | Status |
|-----------|----------------------|---------|--------|
| Định cục (dương/âm, số cục, tiết khí, tam nguyên) | Full table | `dinh_cuc` on ban; UI shows 局 · 陽遁 in technical view | **Partial–Full** |
| Bố địa bàn lục nghi tam kỳ | Required | `dia_ban` / stems arrays | **Partial–Full** |
| Trực phù / trực sử | Required | Engine fields; palace chart shows layers | **Partial** |
| Cửu tinh / bát môn / bát thần | Required | Nine-palace interactive | **Partial–Full** |
| Chuyển bàn / phi bàn | `pan_method` zhuan/fei | School flags UI | **Full** (config surface) |
| Dingju chaibu / zhirun / maoshan | 3 methods | UI: chaibu + zhirunzhuo; **maoshan?** | **Partial** |
| Âm/dương bàn | yin_yang_pan | Flags UI | **Full** (config) |
| Cách cục cat/hung tables | Large tables | Some patterns (e.g. môn bách, phục ngâm); not full table productized | **Partial** |
| Dụng thần by question type | Required | Engine types exist; UX light | **Partial** |
| Zhong gong ký | zhong_gong_ky flag | Not in school-flags list | **Missing–Partial** |
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
| Four-level curriculum + cert | 3 short modules, no levels/cert | **Partial / Missing** |
| Auto-graded cast practice | Missing | **Missing** |
| Bilingual classical library | Missing as product | **Missing** |
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
| zhong_gong_ky | **No** | Claude KM table |
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

### P0 (defend “engine all định + envelope”)
1. **Oracle certification pack** — run/publish kinqimen/kinliuren/kintaiyi (or china95 / N.H.L.T) golden suites with sample counts  
2. **Complete flag stamp** on every API ban (`co_truong_phai` + `co_lich_phap` always full)  
3. **Missing flags** (e.g. zhong_gong_ky, dem_toan, maoshan if required)  
4. **LN 9-tông-môn branch tests** + khoa thể naming in UX  
5. **TA patterns + chủ–khách victory** surfaced in story/board  

### P1 (tập 6–7 product)
6. Persist stamps + history on Postgres (not only memory)  
7. RAG triple-layer retrieval wired as default interpretation path (or label templates honestly)  
8. Four-level curriculum + auto-graded practice (tập 7 §3)  
9. Classical bilingual library surface  
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
| Overall | **~65–72%** | **~55–60%** |
| Engines / calendar | Stronger | Stronger |
| Timing Optimizer | N/A as named Grok hero (Claude: trạch thời as use-case) | Grok hole |
| Auth product | Similar hole | Similar hole |
| Design system | **High** (Claude owns DS) | Diverged from Grok navy |
| Story-first UX | Beyond Claude density | Beyond Grok mockups |
| Oracle certification | Critical Claude gap | Less emphasized in Grok outlines |

---

## 10. Evidence base

- `docs/Claude/README.md`, `Markdown/Tam-Thuc-00` … `07`  
- Unified plan §2.1, §3.2–3.4, §4  
- Code: `crates/cyberos-{lichphap,qimen,luchnham,thaiat,rule}`, `cast-cli`, school-flags, domain AI components, tokens  
- Live verify: CAST_CLI KM/LN/TA boards  

---

## 11. Bottom line

Against **`docs/Claude`**, the system is a **credible implementation of the architectural spine** (Rust CORE + three engines, JSON boundary, CyberSkill DS, disclosure/review, three product flows in light form).  

It is **not yet** a full Claude-grade claim of:

- **oracle-exact** engines at stated sample sizes,  
- **complete** school-flag matrices and cách cục tables,  
- **full** RAG-on-classical + four-level training platform.

The highest-leverage Claude-aligned next work is **oracle goldens + flag completeness + pattern/khoa-the depth**, not more marketing pages.
