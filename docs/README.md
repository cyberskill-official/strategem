# Tam Thuc Strategem - docs

This folder holds the sources and the engineering plan for the Tam Thuc Strategem product (a platform that digitizes the three classical arts Ky Mon Don Giap, Dai Luc Nham, Thai At Than So).

## Where to start

- New to the project: read `strategy/tam-thuc-unified-plan-2026-07-08.md`. It analyzes the two source doc sets, reconciles them, and fixes the architecture, module taxonomy, phases, and risks. Everything else refs it.
- Building a feature: open `feature-requests/README.md` (the catalog), then the module folder for the FR you want.
- Running the program with agents: open `feature-requests/PROMPT.md` to trigger, and `feature-requests/IMPLEMENTATION_ORDER.md` for build order and status.

## Layout

| Path | What it is |
|---|---|
| `Claude/` | Source doc set A - 8 dense Markdown/PDF volumes (engines, calendar core, architecture, product/UI). Authoritative on algorithms and design. |
| `Grok/` | Source doc set B - 51 outline PDFs + UI mockups (PRD, backend, DB, API, ops, security, testing, i18n, legal). Authoritative on product breadth. |
| `strategy/` | The unified plan and source reconciliation - the anchor report. |
| `feature-requests/` | 87 FRs across 16 modules. Each module has a README index; each FR is a heavyweight contract (section 1-11), all 87 authored. |
| `feature-requests/` (also) | The build-order and trigger layer, folded in alongside the FRs: `IMPLEMENTATION_ORDER.md` (status + phase waves), `backlog.yaml`, `PROMPT.md`, `LEDGER.md`. `docs/improvement/` is intentionally not created; it is reserved for the post-launch audit and evolution stage. |

## The one principle

Everything is built around a hard split: a deterministic engine casts the chart (and must match reference oracles to the digit); an AI layer only interprets it (retrieval-grounded, cited, human-reviewed). The boundary is the la so JSON envelope. Engine does not guess meaning; AI does not invent numbers. See strategy section 4.

## Status (2026-07-08)

Plan complete and validated. All 87 FR bodies are authored as heavyweight contracts across the 16 modules. The backlog is acyclic, single-rooted at PLAT-001, and agent-runnable via `feature-requests/PROMPT.md`.

Hien Thuc Hoa Y Chi.
