---
id: FR-PLAT-004
title: "CI/CD pipeline - GitHub Actions extending the PLAT-001 gate with lint/typecheck, unit+integration tests, docker image build, security scan (Trivy/Snyk), and a staging -> production deploy with a manual approval gate"
module: PLAT
priority: MUST
status: implementing
phase: P0
slice: 1
lang: iac
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-22, Grok-39, strategy 4.1, strategy RISK-5]
related_frs: [FR-PLAT-001, FR-PLAT-003, FR-PLAT-005, FR-PLAT-007, FR-PLAT-008, FR-PLAT-010]
depends_on: [FR-PLAT-001]
blocks: [FR-PLAT-005, FR-PLAT-007, FR-PLAT-008, FR-PLAT-010]
new_paths:
  - .github/workflows/cd.yml
  - .github/workflows/security-scan.yml
  - deploy/docker/engine.Dockerfile
  - deploy/docker/api.Dockerfile
  - deploy/docker/web.Dockerfile
  - deploy/docker/.dockerignore
  - deploy/compose/docker-compose.staging.yml
  - deploy/environments/staging.md
  - deploy/environments/production.md
  - deploy/README.md
---

## §1 - Description (BCP-14 normative)

This FR is the continuous-delivery pipeline. It extends the three-lane CI gate FR-PLAT-001 established (lint/typecheck/test for Rust, Python, and web) with the release half: unit and integration tests against real service containers, docker image builds for the three deployables (the Rust engine service, the Python API, the Next.js web app), a security scan (Trivy for images and dependencies, Snyk for dependency advisories), and a deploy that promotes to staging automatically and to production only behind a manual approval gate (Grok-22, Grok-39). It owns the pipeline and the Dockerfiles; it does NOT own the runtime infrastructure definitions (FR-PLAT-010 Terraform/K8s), the metrics stack (FR-PLAT-005), or the security controls themselves (FR-PLAT-007), though it is where those are exercised in CI.

The pipeline SHALL, on every pull request, run the FR-PLAT-001 gate plus the integration tests (including the FR-PLAT-003 RLS isolation test against an ephemeral Postgres) and the security scan, and SHALL block merge on any failure. On merge to the main branch it SHALL build and tag the three docker images, push them to the registry, and deploy to staging automatically. Promotion from staging to production SHALL require a manual approval (a GitHub Environments protection rule / required reviewer); production SHALL NOT deploy without that approval. The security scan SHALL fail the build on a high or critical severity finding in an image or a dependency, and SHALL be overridable only by an explicit, recorded allowlist entry, never silently.

Deploys SHALL be reproducible and rollback-able: images are content-addressed by tag (git SHA), the deployed tag is recorded, and a rollback re-deploys a prior known-good tag. Secrets SHALL come from the CI secret store and the environment, never from the repository (the control set is FR-PLAT-007; this FR consumes it).

## §2 - Why this design (rationale for humans)

The gate that stops bad code and the pipeline that ships good code are one continuous system, but they have different stakes, so they are split into two workflows: `ci.yml` (FR-PLAT-001, fast, runs on every push, blocks merge) and `cd.yml` (this FR, runs on merge, builds and deploys). Keeping the security scan and the integration tests on the pull-request path means a vulnerable dependency or a broken RLS policy is caught before merge, not after it has shipped - and RLS isolation is exactly the check that must never regress silently (RISK-5), so it runs as an integration test in the pipeline, not only as a local one.

The staging -> production manual approval gate is the single most important line in this FR. This is a product that gives divination interpretations under VN legal constraints; an unreviewed auto-deploy to production is the wrong default for a heritage-and-legal-sensitive surface. Auto-deploy to staging keeps iteration fast; a required human approval before production keeps a person in the loop for the surface real users see, mirroring the same human-in-the-loop principle the interpretation layer uses (strategy 4.4). Content-addressed image tags and a recorded deployed tag make rollback a re-deploy of a known SHA rather than a scramble.

## §3 - Contract (pipeline stages / images / gate)

### Workflows

| Workflow | Trigger | Stages |
|---|---|---|
| `ci.yml` (FR-PLAT-001) | push, pull_request | rust / python / web lanes (lint, typecheck, unit test) |
| `security-scan.yml` (this FR) | pull_request, schedule | Trivy (fs + image), Snyk (deps); fail on high/critical |
| `cd.yml` (this FR) | pull_request (integration), push to main (deploy) | integration tests -> build+push images -> deploy staging -> [approval] -> deploy production |

### Pipeline stages (`cd.yml`)

```
1. integration    services: postgres (FR-PLAT-003), redis (FR-PLAT-006 when present)
                  run: migrations apply + RLS isolation test + API integration tests
2. build          build engine.Dockerfile, api.Dockerfile, web.Dockerfile
                  tag each image with ${{ github.sha }} (+ a moving 'staging'/'prod' tag)
3. scan           Trivy scan the three built images; fail on HIGH|CRITICAL (allowlist file only)
4. push           push images to the registry (GHCR or the chosen registry)
5. deploy-staging (auto, on push to main) roll the staging environment to ${{ github.sha }}
6. approve        GitHub Environment 'production' protection rule: required reviewer
7. deploy-prod    (only after approval) roll production to the same ${{ github.sha }}
```

### The three images

- `engine.Dockerfile` - multi-stage Rust build (`cargo build --release` of the engine service bin crate), a slim runtime image; this is the deterministic branch exposed over the la so envelope.
- `api.Dockerfile` - the `tamthuc_api` (and RAG/KB/auth) Python service, `uv`-synced, running FastAPI under an ASGI server.
- `web.Dockerfile` - the `apps/web` Next.js production build.

### Security scan gate

Trivy scans image filesystems and the built images; Snyk scans the Rust/Python/Node dependency manifests. A HIGH or CRITICAL finding fails the build. Suppression is only via a checked-in allowlist (`.trivyignore` / a Snyk policy file) with a comment and an owner, so every exception is reviewable in a diff (RISK-6 supply-chain hygiene; the deeper control set is FR-PLAT-007).

## §4 - Acceptance criteria

1. On a pull request, the pipeline runs the FR-PLAT-001 gate, the integration tests (migrations + RLS isolation against an ephemeral Postgres), and the security scan; any failure blocks merge.
2. On merge to main, the three docker images build, are tagged with the git SHA, are scanned, pushed, and deployed to staging automatically.
3. Production deploy does not run until a manual approval is granted via the `production` GitHub Environment protection rule; without approval, production stays on its prior tag.
4. A HIGH or CRITICAL Trivy/Snyk finding fails the build; the only way past is a checked-in allowlist entry with an owner and reason (verified by a test PR that introduces a known-vulnerable dependency).
5. The deployed tag is recorded, and a rollback re-deploys a prior git-SHA image and is exercised once in staging.
6. No secret is read from the repository; the pipeline sources secrets from the CI secret store / environment (FR-PLAT-007), verified by a scan for committed secrets in the security workflow.

## §5 - Verification

- A test pull request that adds a dependency with a known CVE is shown to fail the `scan` stage; adding the allowlist entry (with owner+reason) is shown to pass - proof the gate bites and the override is explicit.
- The integration stage is shown to run the FR-PLAT-003 RLS isolation test against a service Postgres and to fail the pipeline if isolation regresses.
- A staging deploy is shown to roll to the merged SHA; a production deploy is shown to wait for approval and only then roll.
- A rollback drill: re-deploy the previous SHA to staging and confirm the environment reports the rolled-back tag.
- Gates: this FR is the pipeline; its own YAML is linted (`actionlint`) in the CI web/util lane; Dockerfiles are linted (`hadolint`).

## §6 - Implementation skeleton

1. `security-scan.yml`: Trivy (fs + image) and Snyk (deps) jobs; the `.trivyignore` / Snyk policy allowlist convention; a committed-secret scan.
2. `deploy/docker/*.Dockerfile`: the three multi-stage images + `.dockerignore`; lint with hadolint.
3. `cd.yml` integration job: spin up postgres (+ redis when FR-PLAT-006 lands), apply migrations, run the RLS isolation + API integration tests.
4. `cd.yml` build/scan/push jobs: build the three images tagged by SHA, scan, push to the registry.
5. `cd.yml` deploy jobs: `deploy-staging` (auto on main), the `production` Environment with a required-reviewer protection rule, `deploy-prod` gated on approval; record the deployed tag.
6. `deploy/environments/*.md` + `deploy/README.md`: the staging/production environment contracts, the secret list (sourced, not stored), and the rollback runbook.

## §7 - Dependencies

Depends on FR-PLAT-001 (extends its CI skeleton and reuses the `just` gate recipes). Exercises FR-PLAT-003 in the integration stage (migrations + RLS isolation as a pipeline test). Blocks FR-PLAT-005 (observability wires into the deployed environments this FR defines), FR-PLAT-007 (the security controls are enforced through this pipeline's scan and secret sourcing), FR-PLAT-008 (resilience is deployed and smoke-tested here), and FR-PLAT-010 (Terraform/K8s replace the compose-based staging target this FR bootstraps). Consumes the secret store defined by FR-PLAT-007.

## §8 - Example payloads

```yaml
# cd.yml (abridged) - the production approval gate
deploy-prod:
  needs: [deploy-staging]
  environment:
    name: production          # protection rule: required reviewer -> manual approval
  steps:
    - run: ./deploy/roll.sh production ${{ github.sha }}   # same SHA promoted from staging
```

```yaml
# security-scan.yml (abridged) - fail on high/critical, allowlist only
- uses: aquasecurity/trivy-action@...
  with:
    image-ref: ghcr.io/cyberskill/tamthuc-api:${{ github.sha }}
    severity: HIGH,CRITICAL
    exit-code: '1'
    trivyignores: .trivyignore   # every entry has an owner + reason
```

## §9 - Open questions

- Registry and deploy target at MVP: GHCR + a compose-based single host (the cyberos deploy pattern) vs a managed platform. Default: GHCR images + a compose staging target now, so the pipeline is real before FR-PLAT-010 introduces Terraform/K8s; the deploy step is a thin script the IaC FR later replaces without changing stages 1-4.
- Snyk vs Trivy overlap and licensing: run both, or Trivy alone. Default: Trivy for images+fs (open, no seat limit) plus Snyk for richer dependency advisories where a token exists; the gate condition (fail on high/critical) is identical regardless of which reports it.
- Whether integration tests run on every PR or only pre-deploy. Default: on every PR (the RLS isolation test is too important to defer, RISK-5), accepting the extra minutes; move heavier suites behind a label if PR latency becomes a problem.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Unreviewed prod deploy | auto-deploy straight to production | forbidden; production is behind a required-reviewer Environment gate; staging is auto, prod is not |
| Vulnerable image ships | high/critical finding ignored | scan stage fails the build; only a checked-in allowlist entry (owner+reason) passes it |
| RLS regression ships | isolation test not in the pipeline | the FR-PLAT-003 isolation test runs in the integration stage and blocks merge/deploy on failure |
| Secret in repo | credential committed | committed-secret scan fails; secrets are sourced from the store, never the repo (FR-PLAT-007) |
| Unrollbackable deploy | mutable / non-SHA image tags | images are tagged by git SHA; the deployed tag is recorded; rollback re-deploys a prior SHA |
| Staging/prod drift | different images per environment | the same SHA-tagged images are promoted from staging to prod, never rebuilt for prod |

## §11 - Notes

This FR turns the empty-but-gated repo (FR-PLAT-001) into a shipping system, and its one inviolable rule is the manual approval before production - a heritage-and-legal-sensitive surface does not auto-deploy to real users (strategy 4.1, RISK-4/RISK-5 context). Keep `ci.yml` (fast, blocks merge) and `cd.yml` (builds, deploys) separate but complementary, keep the security gate failing on high/critical with only a reviewable allowlist to pass it, and keep images content-addressed by SHA so rollback is a promotion, not a rebuild. The compose-based staging target is a bootstrap; FR-PLAT-010 swaps in Terraform/K8s behind the same pipeline stages.
