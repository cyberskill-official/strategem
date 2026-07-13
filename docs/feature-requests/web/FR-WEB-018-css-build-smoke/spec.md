---
id: WEB-018
title: CSS build smoke — critical story classnames
status: ready_to_test
class: improvement
priority: MUST
depends_on: [WEB-014]
---

# WEB-018

## Goal
Prevent silent loss of story/layout CSS (partial HMR / truncate) by asserting critical selectors exist in source CSS and in `.next` output after build.

## §1
1. Unit test lists required classnames (`cs-story-rail`, `cs-cta-band`, `cs-visual-card`, …) and fails if missing from `wow.css`/`globals.css`.
2. Post-`next build` smoke scans compiled CSS under `.next` for the same set (CI web gate).
