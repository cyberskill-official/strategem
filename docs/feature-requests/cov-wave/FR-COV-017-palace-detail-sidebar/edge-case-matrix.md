# edge-case-matrix@1 — COV-017

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | UI | palace select | sidebar with fields | palace-detail-sidebar + results-panel |
| E2 | NULL | no selection | empty hint | data-testid palace-detail-empty |
| E3 | PATTERNS | cung match | related list | palace-related-patterns |
| E4 | A11Y | ARIA labels | aria-label on aside | palace-detail-sidebar.tsx |
| E5 | WEB | smoke | source asserts | palace-lunar-patterns-cov017-019.test.mjs |
