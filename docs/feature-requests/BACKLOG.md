# strategem FR backlog

Source of truth for FR state = each FR's frontmatter `status`. This file indexes them.
The `ship-feature-requests` workflow reads this file, picks the first eligible FR
(`ready_to_implement` with all `depends_on` done), and drives it through the lifecycle.
HITL is required: the agent halts at review acceptance and final acceptance for a
recorded human verdict, and never sets `done` itself.

Lifecycle: draft -> ready_to_implement -> implementing -> ready_to_review -> reviewing ->
ready_to_test -> testing -> done. Off-ramps: on_hold, closed. See
`.cyberos/cuo/STATUS-REFERENCE.md`.

## ready_to_implement

- (none yet - add FRs here as `- [ready_to_implement] FR-001-slug - title`)

## in flight

- [reviewing] FR-LASO-001-supported-versions-sot - single source of truth for supported envelope versions (awaiting human review acceptance)

## done

- (shipped FRs, for the audit trail)

## on_hold / closed

- (deferred or killed FRs)
