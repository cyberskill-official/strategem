# Tam Thuc Strategem - agent trigger (now two skills)

The implementation trigger and the human review protocol that used to live here are now two skills under `.claude/skills/`, so an agent invokes a skill instead of pasting a prompt:

- `strategem-implement` - build the next eligible task (or a named task) to a reviewable state: load context, run the language gates and the engine oracle checks, record evidence in the ledger, hand off. See `.claude/skills/strategem-implement/SKILL.md`.
- `strategem-review` - verify an `in_review` task against its acceptance criteria and the ledger, re-run the accuracy and security gates, then set `done` or reject. Includes the per-phase P0-P3 sign-off gates. See `.claude/skills/strategem-review/SKILL.md`.

To trigger a build, invoke the `strategem-implement` skill (or say "implement TT task <ID>"); for sign-off, invoke `strategem-review`. Build order and status live in `IMPLEMENTATION_ORDER.md`, the machine-readable status is `backlog.yaml`, and evidence goes to `LEDGER.md`.
