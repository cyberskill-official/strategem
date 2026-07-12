# strategem FR backlog

Source of truth for FR state = each FR's frontmatter `status`.
HITL required at review acceptance and final acceptance; agent never self-sets `done`.

Sequencing: `docs/feature-requests/IMPLEMENTATION_ORDER.md`.

## ready_to_implement

Eligible (deps done; MUST unless noted):

- [ready_to_implement] FR-PLAT-004-cicd-pipeline
- [ready_to_implement] FR-CORE-001-solar-longitude-tiet-khi
- [ready_to_implement] FR-CORE-007-ganzhi-primitives
- [ready_to_implement] FR-KB-003-classical-text-store
- [ready_to_implement] FR-WEB-001-app-shell-design-system
- [ready_to_implement] FR-RULE-001-pattern-schema
- [ready_to_implement] FR-AUTH-002-rbac-tiers (unblocked by FR-AUTH-001)
- [ready_to_implement] FR-AUTH-003-email-verify (unblocked by FR-AUTH-001)
- [ready_to_implement] FR-LEGAL-002-pdpd-gdpr (unblocked by FR-AUTH-001)
- [ready_to_implement] FR-PLAT-006-caching (SHOULD)
- [ready_to_implement] FR-PLAT-009-backup-dr (SHOULD)
- [ready_to_implement] FR-KB-001-knowledge-graph (SHOULD)

## in flight

- (none)

## done

- [done] FR-PLAT-001-monorepo-workspace
- [done] FR-PLAT-002-la-so-json-envelope
- [done] FR-PLAT-003-db-schema-migrations
- [done] FR-AUTH-001-auth-user - Auth JWT+refresh + birth_data AES-256-GCM
- [done] FR-LASO-001-supported-versions-sot (improvement)

## on_hold / closed

- (none)
