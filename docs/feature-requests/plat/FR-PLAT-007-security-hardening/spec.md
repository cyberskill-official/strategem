---
id: FR-PLAT-007
title: "Security hardening - STRIDE control set (JWT + rate limit, input validation + signed calcs, audit logging, AES-256 + least privilege, rate limit + autoscale + WAF, RBAC), TLS 1.3 in transit, secret-manager custody, dependency scanning (Snyk/Dependabot/Trivy), OWASP Top 10 checklist, annual + post-change pentest, and an incident-response playbook with GDPR 72h / VN PDPD breach notification"
module: PLAT
priority: MUST
status: ready_to_implement
phase: P1
slice: 1
lang: iac/python
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-21, strategy 4.4, strategy 7, strategy RISK-5, strategy RISK-6]
related_frs: [FR-PLAT-004, FR-AUTH-001, FR-AUTH-002, FR-API-003, FR-API-004, FR-LEGAL-002]
depends_on: [FR-PLAT-004, FR-AUTH-002]
blocks: []
new_paths:
  - docs/security/stride-threat-model.md
  - docs/security/owasp-top10-checklist.md
  - docs/security/incident-response-playbook.md
  - docs/security/pentest-schedule.md
  - deploy/security/tls-config.md
  - deploy/security/waf-rules.md
  - deploy/security/secrets.md
  - packages/tamthuc_api/tamthuc_api/security/__init__.py
  - packages/tamthuc_api/tamthuc_api/security/headers.py
  - packages/tamthuc_api/tamthuc_api/security/validation.py
  - packages/tamthuc_api/tamthuc_api/security/signing.py
  - packages/tamthuc_api/tests/test_security.py
  - .github/workflows/dependency-scan.yml
---

## §1 - Description (BCP-14 normative)

This FR is the security-hardening pass: a STRIDE-driven control set, transport and secret hygiene, dependency scanning, an OWASP Top 10 review, a penetration-test cadence, and an incident-response playbook with regulatory breach notification. It hardens the system the FR-PLAT-004 pipeline ships and the FR-AUTH-002 tiers govern. It owns the threat model, the control mapping, and the operational security artifacts; it does NOT re-implement auth (FR-AUTH-001), tiers (FR-AUTH-002), rate limiting (FR-API-003), or audit (FR-API-004) - it composes them into a defensible whole and adds the missing controls.

The control set SHALL be derived from a STRIDE threat model and SHALL map each threat class to a control: Spoofing to JWT authentication plus rate limiting; Tampering to input validation plus signed calculations; Repudiation to audit logging; Information disclosure to AES-256 encryption at rest plus least-privilege access; Denial of service to rate limiting plus autoscaling plus a WAF; Elevation of privilege to RBAC. All personal data SHALL be protected in transit with TLS 1.3. Secrets SHALL come from a secret manager or the environment, never from the repository or a config committed to source. Dependencies SHALL be scanned continuously (Snyk, Dependabot, Trivy) and a high or critical finding SHALL fail the FR-PLAT-004 build, overridable only by a reviewable allowlist entry.

The codebase SHALL be reviewed against the OWASP Top 10 with a checked-in checklist, and a penetration test SHALL be run at least annually and after any significant change. An incident-response playbook SHALL define detection, containment, eradication, recovery, and notification, and SHALL encode the regulatory clocks: GDPR 72-hour breach notification and the VN PDPD notification obligation (FR-LEGAL-002). Oracle libraries SHALL remain CI-only references, never embedded runtime dependencies, so their licenses and code never enter the shipped artifact (RISK-6).

## §2 - Why this design (rationale for humans)

Security here is not a generic checklist bolted on late; it is the technical guarantee behind the product's legal footing (strategy 7). The data at stake is birth data and question text - sensitive personal data under VN PDPD and GDPR (RISK-5) - so a breach is simultaneously a privacy harm and a legal event with a statutory clock. Driving the control set from STRIDE rather than from a vibe means every threat class has a named, testable control and nothing important is left implicit: the mapping is the contract. Most of the controls already exist in other FRs (JWT in AUTH-001, RBAC in AUTH-002, rate limiting in API-003, audit in API-004, at-rest crypto in AUTH-001); this FR's job is to prove they compose into full STRIDE coverage and to add the pieces no single feature FR owns - TLS 1.3, secret custody, dependency scanning, WAF, the OWASP review, the pentest cadence, and the incident playbook.

The incident-response playbook with the 72-hour clock is the control that turns a bad day into a survivable one. A breach with no rehearsed playbook is a breach plus a missed regulatory deadline plus a scramble; a breach with a playbook is a defined sequence with the notification obligations already written down. Keeping secrets out of the repo and failing the build on a high/critical dependency finding closes the two most common real-world holes (leaked credentials and known-vulnerable dependencies) at the pipeline, where FR-PLAT-004 already has the teeth. Keeping the oracle libraries as CI-only references (RISK-6) means their licenses never contaminate the commercial artifact - a legal control expressed as a build rule.

## §3 - Contract (STRIDE map / controls / policies)

### STRIDE control mapping (`docs/security/stride-threat-model.md`)

| Threat | Control | Owner / where enforced |
|---|---|---|
| Spoofing | JWT authentication + rate limiting | FR-AUTH-001 tokens; FR-API-003 limiter |
| Tampering | input validation + signed calculations | `security/validation.py`, `security/signing.py` |
| Repudiation | audit logging (append-only) | FR-API-004 `audit_logs` |
| Information disclosure | AES-256 at rest + least-privilege access | FR-AUTH-001 crypto; FR-PLAT-003 RLS + DB grants |
| Denial of service | rate limiting + autoscaling + WAF | FR-API-003; FR-PLAT-010 HPA; `deploy/security/waf-rules.md` |
| Elevation of privilege | RBAC | FR-AUTH-002 roles/capabilities |

Each row SHALL have evidence: a test, a policy file, or a pipeline gate. A threat class with no evidenced control is a hardening gap.

### Transport, secrets, headers

- TLS 1.3 in transit for all personal data, terminated at the edge (`deploy/security/tls-config.md`); HTTP redirects to HTTPS; HSTS set.
- Secrets from a secret manager / environment only (`deploy/security/secrets.md`); a committed-secret scan runs in the pipeline; no secret in the repo or an image layer.
- Security response headers (`security/headers.py`): HSTS, `X-Content-Type-Options`, `X-Frame-Options`/CSP, `Referrer-Policy`.

### Signed calculations (`security/signing.py`)

An engine cast result carries an integrity signature so a tampered chart in transit or at rest is detectable; the la so envelope's `provenance` is covered by a signature the API verifies before trusting a stored/forwarded chart (anti-tampering for the deterministic branch).

### Dependency scanning (`.github/workflows/dependency-scan.yml`)

Snyk + Dependabot + Trivy across the Rust/Python/Node manifests and the built images; a HIGH/CRITICAL finding fails the FR-PLAT-004 build; suppression only via a checked-in allowlist with owner + reason.

### OWASP + pentest + incident response

`docs/security/owasp-top10-checklist.md` (reviewed each release), `docs/security/pentest-schedule.md` (annual + post-significant-change), `docs/security/incident-response-playbook.md` (detect/contain/eradicate/recover/notify, with GDPR 72h and VN PDPD notification steps).

## §4 - Acceptance criteria

1. The STRIDE threat model maps every threat class to a named control, and each control has evidence (a test, a policy file, or a pipeline gate); a threat class with no evidenced control fails the review.
2. All personal-data traffic is TLS 1.3; a probe of a plaintext or downgraded connection is refused, and HSTS + the security headers are present on responses.
3. No secret is readable from the repository or an image layer; the committed-secret scan passes and a planted test secret is caught.
4. A dependency with a known HIGH/CRITICAL CVE fails the dependency-scan workflow and the FR-PLAT-004 build; adding an allowlist entry with owner + reason passes it (proof the gate bites and the override is explicit).
5. Input validation rejects malformed/oversized/injection-shaped input with the FR-API-001 error envelope; a signed calculation detects a tampered chart (the signature check fails on a mutated envelope).
6. The OWASP Top 10 checklist is complete for the release; the pentest schedule is defined (annual + post-change); the incident-response playbook encodes the GDPR 72h and VN PDPD notification clocks (FR-LEGAL-002).

## §5 - Verification

- `tests/test_security.py`: security headers present and correct; input-validation rejection cases; the signed-calculation tamper-detection test; a least-privilege check that a non-admin principal cannot reach an admin control.
- A pipeline check: the dependency-scan workflow fails on a planted known-vulnerable dependency and passes with an allowlist entry; the committed-secret scan catches a planted secret.
- A TLS probe (in staging) confirms TLS 1.3 and refuses a downgraded/plaintext connection; HSTS asserted.
- A tabletop review of the incident-response playbook confirms the detect->notify sequence and the 72h / PDPD clocks; the STRIDE evidence table is checked row-by-row.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api`; the security workflows run in the FR-PLAT-004 pipeline.

## §6 - Implementation skeleton

1. Author `docs/security/stride-threat-model.md` mapping each STRIDE class to its control and evidence; identify the gaps this FR must fill.
2. `security/headers.py`, `security/validation.py`, `security/signing.py`: the response-header middleware, the input-validation layer, and the signed-calculation integrity check.
3. `deploy/security/*`: TLS 1.3 config, WAF rules, secret-manager custody notes; wire the committed-secret scan.
4. `.github/workflows/dependency-scan.yml`: Snyk + Dependabot + Trivy; fail on HIGH/CRITICAL; the allowlist convention (extends the FR-PLAT-004 security scan).
5. `docs/security/owasp-top10-checklist.md`, `pentest-schedule.md`, `incident-response-playbook.md` with the GDPR 72h / VN PDPD notification steps.
6. Confirm oracle libraries are CI-only (not runtime deps) and record the license review (RISK-6).

## §7 - Dependencies

Depends on FR-PLAT-004 (the pipeline that runs the dependency and secret scans and where the build fails on a finding) and FR-AUTH-002 (the RBAC/tier model that is the Elevation-of-privilege and the authorization control this hardens). Composes FR-AUTH-001 (JWT + AES-256 at rest), FR-API-003 (rate limiting as the DoS/Spoofing control), FR-API-004 (audit as the Repudiation control), and FR-PLAT-003 (RLS + least-privilege DB grants). Coordinates with FR-PLAT-010 (autoscaling as a DoS control) and FR-LEGAL-002 (the breach-notification obligations and the consent/retention contracts the playbook references).

## §8 - Example payloads

```yaml
# .github/workflows/dependency-scan.yml (abridged) - fail on high/critical
- uses: aquasecurity/trivy-action@...
  with: { scan-type: fs, severity: 'HIGH,CRITICAL', exit-code: '1', trivyignores: .trivyignore }
- uses: snyk/actions/python@...      # + Dependabot alerts enabled on the repo
```

```json
// incident-response notification obligations (from the playbook)
{ "regime": "GDPR", "clock_hours": 72, "trigger": "personal data breach likely to risk rights" }
{ "regime": "VN_PDPD", "action": "notify authority + affected data subjects per Nghi dinh 13/2023" }
```

## §9 - Open questions

- WAF choice: a managed WAF (cloud provider) vs an app-layer WAF (e.g. Coraza/ModSecurity rules). Default: the managed edge WAF at MVP for DoS + common-attack coverage, with app-layer input validation as defense in depth; revisit under FR-PLAT-010.
- Secret manager: cloud KMS/Secrets Manager vs a self-hosted vault. Default: align with the FR-AUTH-001 master-key custody decision (envelope encryption works with either); the birth_data master key and the app secrets share the chosen manager.
- Pentest sourcing: external firm vs internal + external hybrid. Default: an external pentest annually and after any significant change (the schedule is fixed here; the vendor is an ops decision), with continuous automated scanning between engagements.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| STRIDE gap | a threat class with no evidenced control | forbidden; every class maps to a control with a test/policy/gate; the review fails on a gap |
| Secret in repo/image | credential committed or baked into a layer | committed-secret scan fails the build; secrets come from the manager/env only |
| Vulnerable dependency ships | HIGH/CRITICAL finding ignored | dependency-scan fails the FR-PLAT-004 build; only a reviewable allowlist entry passes it |
| Plaintext/downgraded transit | TLS not enforced | forbidden; TLS 1.3 required, HSTS set, downgraded/plaintext refused |
| Tampered chart trusted | a mutated envelope accepted | the signed-calculation check rejects it; provenance integrity verified before trust |
| Unrehearsed breach | no playbook, missed clock | the incident-response playbook encodes GDPR 72h + VN PDPD notification and is tabletop-tested |
| Oracle license contamination | an oracle lib vendored as a runtime dep | forbidden; oracles are CI-only references; the license review confirms it (RISK-6) |

## §11 - Notes

This FR is where the platform's legal footing becomes a set of enforced controls rather than intentions. Hold three things: the STRIDE map is the contract (every threat class -> a control with evidence), secrets and vulnerable dependencies die at the FR-PLAT-004 pipeline (never in the repo, never HIGH/CRITICAL past the gate), and the incident-response playbook carries the real regulatory clocks (GDPR 72h, VN PDPD). Most controls are composed from AUTH/API/PLAT FRs; this FR proves the composition and adds TLS 1.3, secret custody, dependency scanning, the OWASP review, the pentest cadence, and the playbook. The Python controls live in `tamthuc_api/security`, the operational artifacts under `docs/security/` and `deploy/security/`, reflecting the iac/python split. Oracle libraries stay CI-only so their licenses never enter the shipped artifact (RISK-6).
