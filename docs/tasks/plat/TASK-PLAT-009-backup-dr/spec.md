---
id: TASK-PLAT-009
title: "Backup and disaster recovery - daily automated backups + point-in-time recovery (RPO 1h, RTO 4h), multi-AZ deployment with cross-region failover, and a scheduled restore drill against the PLAT-003 schema"
module: PLAT
priority: SHOULD
status: done
phase: P2
slice: 1
lang: iac
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-50, Grok-22, strategy 4.1, strategy RISK-5]
related_frs: [TASK-PLAT-003, TASK-PLAT-004, TASK-PLAT-010, TASK-LEGAL-002]
depends_on: [TASK-PLAT-003]
blocks: []
new_paths:
  - deploy/backup/backup-policy.md
  - deploy/backup/pitr-config.md
  - deploy/backup/cron/pg-backup.sh
  - deploy/dr/dr-plan.md
  - deploy/dr/failover-runbook.md
  - deploy/dr/restore-drill.md
  - .github/workflows/restore-drill.yml
  - docs/contracts/rpo-rto.md
---

## §1 - Description (BCP-14 normative)

This task is backup and disaster recovery for the data tier: automated backups, point-in-time recovery, a multi-AZ deployment with cross-region failover, and a recurring restore drill that proves the backups are actually restorable. It protects the TASK-PLAT-003 schema (users, queries, charts, knowledge_patterns, reports, audit_logs). It owns the backup policy, the recovery targets, and the DR runbooks; it does NOT own the schema (TASK-PLAT-003) nor the infrastructure provisioning (TASK-PLAT-010), though it constrains both (backups run against the PLAT-003 tables; the multi-AZ/cross-region topology is realized in the PLAT-010 IaC).

Backups SHALL be automated and daily, retained on a documented schedule, and SHALL be complemented by point-in-time recovery (PITR) via continuous WAL archiving so the database can be restored to any instant within the retention window, not only to the last daily snapshot. The recovery targets SHALL be a Recovery Point Objective (RPO) of 1 hour and a Recovery Time Objective (RTO) of 4 hours: at most one hour of data may be lost in a disaster, and service SHALL be restored within four hours. The deployment SHALL be multi-AZ so a single availability-zone failure does not take the data tier down, with cross-region failover for a regional outage. Backups SHALL be encrypted at rest and stored in a region/account separate from the primary so a compromise of the primary does not destroy the backups.

The restore SHALL be drilled, not assumed: a scheduled restore drill SHALL restore a backup into an isolated environment, apply PITR to a target instant, and verify the TASK-PLAT-003 schema, the row-level security, and a data-integrity sample - and SHALL fail loudly if the restore does not reproduce a working database within the RTO. The drill SHALL run on a recurring schedule in CI/ops, and its result SHALL be recorded. Because the data is sensitive personal data (RISK-5), backups SHALL honor the same protection posture as the live data (encryption at rest, access control) and SHALL be within the erasure scope of TASK-LEGAL-002 so a right-to-erasure is not silently defeated by an immortal backup copy.

## §2 - Why this design (rationale for humans)

A backup you have never restored is a hypothesis, not a safeguard. The single most common disaster-recovery failure is discovering during an actual incident that the backups were incomplete, corrupt, or un-restorable within any useful time. So the center of this task is not the backup - it is the drill that proves the backup restores into a working, RLS-enforced, schema-correct database within the RTO. Daily backups plus PITR give the RPO teeth: the daily snapshot bounds the worst case and continuous WAL archiving shrinks the actual data-loss window to the RPO of one hour, so a disaster costs at most an hour of queries and charts, not a day. The RTO of 4 hours is the promise that the restore is a rehearsed procedure with a known duration, not an open-ended scramble.

Multi-AZ with cross-region failover matches the two failure scales that actually happen: an AZ failure (common, survived by multi-AZ with no data loss) and a regional outage (rare, survived by cross-region failover). Storing backups in a separate region/account is the control against the correlated failure where whatever destroyed the primary also destroys the backups sitting next to it - including ransomware and operator error, not just hardware. And because this is sensitive personal data, the backups are not a loophole in the privacy posture: they carry the same encryption and access control as the live data (RISK-5), and they are inside the TASK-LEGAL-002 erasure scope, so a user's right-to-erasure is honored across backups on the documented cadence rather than quietly defeated by a copy that lives forever.

## §3 - Contract (backup policy / recovery targets / drill)

### Recovery targets (`docs/contracts/rpo-rto.md`)

| Target | Value | Meaning |
|---|---|---|
| RPO | 1 hour | maximum acceptable data loss in a disaster |
| RTO | 4 hours | maximum acceptable time to restore service |
| Backup frequency | daily (automated) + continuous WAL (PITR) | snapshot floor + point-in-time granularity |
| Backup locality | separate region/account, encrypted at rest | survives a primary-region/account compromise |
| Topology | multi-AZ primary + cross-region failover | survives an AZ failure (no loss) and a regional outage |

### Backup policy (`deploy/backup/backup-policy.md`, `pitr-config.md`, `cron/pg-backup.sh`)

Daily automated logical + physical backups of the TASK-PLAT-003 database; continuous WAL archiving for PITR; a documented retention window; encryption at rest; access restricted to the DR role. `cron/pg-backup.sh` is the scriptable path when not using a managed backup service; a managed Postgres (per the strategy 4.1 note that any managed Postgres works) satisfies this via its native automated backups + PITR.

### DR plan and failover (`deploy/dr/dr-plan.md`, `failover-runbook.md`)

The DR plan names the failure scenarios (AZ failure, regional outage, data corruption, accidental deletion), the response per scenario, and the failover steps to promote the cross-region replica; the runbook is a step-by-step an operator follows under pressure, with the RTO clock.

### Restore drill (`deploy/dr/restore-drill.md`, `.github/workflows/restore-drill.yml`)

A recurring drill restores a backup into an isolated environment, applies PITR to a target instant, and asserts: the TASK-PLAT-003 tables/indexes exist, RLS is enabled and fail-closed (the no-GUC probe sees zero rows), and a data-integrity sample matches; it fails if the restore exceeds the RTO or the assertions fail.

## §4 - Acceptance criteria

1. Daily automated backups run and are retained per the policy; continuous WAL archiving enables PITR to an arbitrary instant within the retention window (not only the last daily snapshot).
2. A restore drill restores a backup + PITR into an isolated environment and verifies the TASK-PLAT-003 schema, fail-closed RLS (the no-GUC probe sees zero rows), and a data-integrity sample; the drill fails loudly if any check fails.
3. The measured restore time in the drill is within the RTO of 4 hours, and the PITR granularity satisfies the RPO of 1 hour; both are recorded.
4. The deployment is multi-AZ (an AZ failure does not take the data tier down) and a cross-region failover procedure is documented and exercised at least once in the drill/runbook.
5. Backups are encrypted at rest and stored in a separate region/account from the primary; access is restricted to the DR role; a test confirms backups are not readable by an ordinary app principal.
6. Backups are within the TASK-LEGAL-002 erasure scope: a right-to-erasure is applied across backups on the documented cadence, so an erased subject does not persist indefinitely in backup copies.

## §5 - Verification

- The restore-drill workflow runs on a schedule, restores a backup + PITR into an ephemeral environment, and asserts schema presence, fail-closed RLS, and the integrity sample; the run records the restore duration against the RTO.
- A PITR test restores to a chosen past instant and confirms the data state at that instant (RPO granularity).
- A backup-locality/encryption check confirms backups live in the separate region/account, are encrypted, and are not readable by an app principal.
- A failover tabletop (and at least one exercised failover in staging) confirms the cross-region promotion steps and the RTO clock.
- Gates: the restore-drill workflow is required in ops CI; the DR runbooks are reviewed; `actionlint`/`hadolint` where applicable via the TASK-PLAT-004 pipeline.

## §6 - Implementation skeleton

1. `docs/contracts/rpo-rto.md`: fix RPO 1h / RTO 4h and the topology + locality targets.
2. `deploy/backup/*`: the daily-backup + WAL/PITR policy and config; `cron/pg-backup.sh` for the self-managed path (or the managed-Postgres native equivalent).
3. `deploy/dr/dr-plan.md` + `failover-runbook.md`: the per-scenario DR plan and the cross-region failover steps with the RTO clock.
4. `deploy/dr/restore-drill.md` + `.github/workflows/restore-drill.yml`: the scheduled restore + PITR drill with the schema/RLS/integrity assertions and the RTO check.
5. Wire the erasure-across-backups cadence to TASK-LEGAL-002; confirm backup encryption + separate-region storage in the TASK-PLAT-010 topology.

## §7 - Dependencies

Depends on TASK-PLAT-003 (the schema and the fail-closed RLS the backups protect and the drill verifies; the restore drill asserts the same no-GUC probe PLAT-003 defines). Realized on the topology TASK-PLAT-010 provisions (multi-AZ + cross-region), so the two coordinate: PLAT-010 builds the infrastructure, PLAT-009 sets the backup/recovery policy on it. Coordinates with TASK-PLAT-004 (the drill runs as a scheduled ops workflow alongside the pipeline) and TASK-LEGAL-002 (erasure must reach into backups on a documented cadence so RISK-5 data does not outlive a right-to-erasure).

## §8 - Example payloads

```yaml
# docs/contracts/rpo-rto.md (abridged)
rpo_hours: 1
rto_hours: 4
backup: { frequency: daily, pitr: continuous_wal, retention_days: 30, encrypted: true, locality: separate-region }
topology: { primary: multi-az, failover: cross-region }
```

```
# restore-drill assertions (must all pass, within RTO)
[ok] tables: users, queries, charts, knowledge_patterns, reports, audit_logs
[ok] rls: no-GUC probe returns 0 rows on charts/queries/reports   (fail-closed)
[ok] pitr: restored to 2026-07-08T11:00:00Z (target instant)
[ok] restore_duration: 00:52:00  (< RTO 04:00:00)
```

## §9 - Open questions

- Managed vs self-managed backups. Default: rely on the managed Postgres's native automated backups + PITR (strategy 4.1 notes any managed Postgres works), keeping `cron/pg-backup.sh` as the portable fallback; the RPO/RTO targets are the same regardless of provider.
- Retention window length. Default: 30 days PITR + a longer cold-snapshot tail for the legally required minimum; the exact numbers are set with TASK-LEGAL-002's retention policy, not hardcoded here.
- Erasure-across-backups mechanism: crypto-shred (drop the per-record wrapped key so ciphertext in backups is unreadable) vs scheduled backup rewrite. Default: crypto-shred for birth_data (the wrapped DEK is dropped, so all backup copies become unreadable at once), aligned with the TASK-AUTH-001 envelope-encryption design and TASK-AUTH-004's erasure.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Untested backup | backups exist but are never restored | forbidden; a scheduled restore drill proves restorability within the RTO and fails loudly otherwise |
| RPO/RTO unmet | data loss > 1h or restore > 4h | the drill records both; missing either target is a failure to remediate |
| Correlated backup loss | backups stored with the primary | backups live in a separate region/account, encrypted; a primary compromise does not destroy them |
| Single-AZ data tier | no multi-AZ | multi-AZ primary + cross-region failover; an AZ failure is survived without data loss |
| Backup privacy hole | backups readable or outside erasure scope | backups carry the live protection posture and are in the TASK-LEGAL-002 erasure scope (RISK-5) |
| Silent restore drift | restored DB missing RLS or schema | the drill asserts schema + fail-closed RLS + an integrity sample; a drift fails the drill |

## §11 - Notes

The point of this task is the drill, not the backup: a backup nobody has restored into a working, RLS-enforced, schema-correct database within the RTO is an assumption, so the restore drill is scheduled, asserted, and allowed to fail loudly. Hold the two numbers (RPO 1h, RTO 4h) as real commitments the drill measures, keep backups in a separate region/account with the same protection as live data, and keep them inside the TASK-LEGAL-002 erasure scope so RISK-5 data does not outlive a right-to-erasure. This task is IaC/ops: it sets policy and runbooks on the topology TASK-PLAT-010 provisions and the schema TASK-PLAT-003 owns.
