---
id: TASK-PLAT-010
title: "Infrastructure as code - Terraform + Kubernetes manifests, horizontal autoscaling for the stateless calculation services, and Celery workers for background tasks (batch reports)"
module: PLAT
priority: SHOULD
status: done
phase: P2
slice: 1
lang: iac
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-22, Grok-39, strategy 4.1]
related_frs: [TASK-PLAT-004, TASK-PLAT-005, TASK-PLAT-006, TASK-PLAT-009, TASK-REPORT-002]
depends_on: [TASK-PLAT-004]
blocks: []
new_paths:
  - deploy/terraform/main.tf
  - deploy/terraform/variables.tf
  - deploy/terraform/network.tf
  - deploy/terraform/database.tf
  - deploy/terraform/redis.tf
  - deploy/k8s/engine-deployment.yaml
  - deploy/k8s/api-deployment.yaml
  - deploy/k8s/web-deployment.yaml
  - deploy/k8s/celery-worker.yaml
  - deploy/k8s/hpa.yaml
  - deploy/k8s/ingress.yaml
  - deploy/README-iac.md
---

## §1 - Description (BCP-14 normative)

This task is infrastructure as code: the runtime environment defined as versioned, reviewable Terraform and Kubernetes manifests, with horizontal autoscaling for the stateless calculation services and Celery workers for background tasks. It replaces the compose-based staging bootstrap TASK-PLAT-004 introduced with a declared, reproducible topology behind the same pipeline stages. It owns the infrastructure definitions and the autoscaling/worker topology; it does NOT own the pipeline that applies them (TASK-PLAT-004), the metrics that drive scaling decisions (TASK-PLAT-005), or the backup/DR policy on the data tier (TASK-PLAT-009), though it provisions the substrate all three run on.

All infrastructure SHALL be declared as code: the network, the managed Postgres (TASK-PLAT-003), the Redis instance (TASK-PLAT-006), and the compute SHALL be provisioned by Terraform, and the three deployables (the Rust engine service, the Python API, the Next.js web app) SHALL run as Kubernetes workloads defined by checked-in manifests. No production resource SHALL be created or modified by hand outside the IaC; a change to the infrastructure is a change to a file, reviewed and applied through the TASK-PLAT-004 pipeline. The stateless calculation services (the engine service and the API) SHALL scale horizontally via a HorizontalPodAutoscaler keyed on CPU/latency, so load is met by adding replicas rather than by manual intervention; stateful components (Postgres, Redis) are managed services, not autoscaled pods.

Background tasks SHALL run on Celery workers separate from the request-serving pods, so a long job (a batch report, a warming pass, a scheduled drill) never blocks the hot path. Batch report generation (TASK-REPORT-002) SHALL be a Celery task, not a synchronous request. The manifests SHALL be environment-parameterized (staging vs production) from the same source with per-environment values, SHALL set resource requests/limits, health/readiness probes, and SHALL source secrets from the secret manager (TASK-PLAT-007), never from a committed value. The IaC SHALL be idempotent and drift-detectable: a plan against the live state SHALL report no unexpected drift, and applying twice SHALL be a no-op the second time.

## §2 - Why this design (rationale for humans)

Hand-built infrastructure is the thing you cannot rebuild. The compose-based staging target TASK-PLAT-004 bootstrapped is fine for getting a pipeline real, but a production surface that real users and sensitive data depend on needs to be reproducible, reviewable, and rebuildable from source - which is exactly what Terraform + Kubernetes manifests provide (Grok-22, Grok-39). Declaring the whole topology as code means a disaster-recovery rebuild (TASK-PLAT-009) is `terraform apply` against a new region rather than an archaeology project, an audit of what is running is a `git log`, and an infrastructure change gets the same review a code change gets. The rule that no production resource is touched by hand is what keeps the code and the reality in sync; the moment someone clicks a console button, the IaC is a lie.

Autoscaling the stateless calculation services is the right shape because those services are exactly stateless - a chart cast is a pure function of its input, so more load is simply more replicas, and the HPA turns a traffic spike into pods rather than a page. The stateful pieces stay managed services precisely because they are not horizontally trivial. Separating Celery workers from the request pods is the standard move that keeps a heavy batch report or a warming pass from stealing latency from a user waiting on a chart: background work belongs on background workers, and making batch report generation a Celery task (rather than a synchronous endpoint) is what lets the API stay responsive under a report load. Parameterizing staging and production from one source keeps the two environments honest - they differ by values, not by drift.

## §3 - Contract (Terraform / K8s / autoscaling / workers)

### Terraform (`deploy/terraform/*`)

| File | Provisions |
|---|---|
| `main.tf` | providers, backend/state, module wiring |
| `network.tf` | VPC/subnets, security groups, the multi-AZ layout (TASK-PLAT-009 topology) |
| `database.tf` | managed Postgres (TASK-PLAT-003), automated backups + PITR hooks (TASK-PLAT-009) |
| `redis.tf` | managed Redis (TASK-PLAT-006 cache + TASK-API-003 counters) |
| `variables.tf` | per-environment parameters (staging vs production) |

### Kubernetes workloads (`deploy/k8s/*`)

```yaml
# hpa.yaml (abridged) - autoscale the stateless calculation services
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: tamthuc-api }
spec:
  scaleTargetRef: { kind: Deployment, name: tamthuc-api }
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
```

- `engine-deployment.yaml`, `api-deployment.yaml`: the stateless services, each with resource requests/limits, readiness/liveness probes, and an HPA (`hpa.yaml`).
- `web-deployment.yaml`: the Next.js app.
- `celery-worker.yaml`: background workers (batch reports, warming, scheduled jobs), separate from request pods, scaled independently.
- `ingress.yaml`: routing + TLS termination (TASK-PLAT-007 TLS 1.3).

### Background tasks (Celery)

Batch report generation (TASK-REPORT-002), cache warming (TASK-PLAT-006), and scheduled ops jobs run as Celery tasks on the worker deployment, brokered via Redis; a task never runs on a request-serving pod.

## §4 - Acceptance criteria

1. `terraform plan` against an empty target proposes the full topology (network, managed Postgres, managed Redis, compute) and `terraform apply` provisions it; a second `apply` is a no-op (idempotent).
2. The three deployables run as Kubernetes workloads from the checked-in manifests with resource requests/limits and readiness/liveness probes; a rollout is declarative.
3. The stateless calculation services (engine, API) scale out under load via the HPA (replicas increase past `minReplicas` toward `maxReplicas`) and scale back in when load drops; a load test demonstrates it.
4. Celery workers run on a separate deployment; a batch report (TASK-REPORT-002) executes as a background task and does not block or degrade the request-serving pods (a report load leaves chart-cast latency within SLO).
5. Staging and production are parameterized from one source (differ by values only); a drift check reports no unexpected drift between the manifests/state and the live environment.
6. No production resource exists outside the IaC, and no secret is a committed value (secrets sourced from the TASK-PLAT-007 manager); a scan confirms both.

## §5 - Verification

- A CI `terraform validate` + `terraform plan` (against a test/staging state) and a `kubeval`/`kubeconform` lint of the manifests run in the TASK-PLAT-004 pipeline; a `plan` showing unexpected drift fails.
- A load test in staging drives the HPA to add replicas and confirms scale-in afterward; the p95 chart-cast latency (TASK-PLAT-005) stays within SLO during the spike.
- A background-task test enqueues a batch report and confirms it runs on a Celery worker, not a request pod, and does not raise request-path latency.
- A drift/secret check: `terraform plan` is clean on an unchanged tree; a scan confirms no committed secret and no hand-created production resource.
- Gates: `terraform validate`, `tflint`, `kubeconform`, and the pipeline lint stages; the manifests deploy cleanly to staging behind the existing TASK-PLAT-004 stages.

## §6 - Implementation skeleton

1. `deploy/terraform/*`: providers + remote state; the network (multi-AZ), managed Postgres, and managed Redis modules; per-environment variables.
2. `deploy/k8s/*-deployment.yaml`: the engine, API, and web workloads with probes and resource requests/limits; `ingress.yaml` with TLS termination.
3. `deploy/k8s/hpa.yaml`: HPAs on the stateless engine + API services keyed on CPU/latency.
4. `deploy/k8s/celery-worker.yaml`: the background-worker deployment (batch reports, warming, scheduled jobs), brokered via Redis, scaled independently.
5. Parameterize staging vs production from one source; source secrets from the TASK-PLAT-007 manager.
6. Wire the IaC apply behind the TASK-PLAT-004 deploy stages (replacing the compose bootstrap) and add the validate/plan/lint gates; document in `deploy/README-iac.md`.

## §7 - Dependencies

Depends on TASK-PLAT-004 (the pipeline that validates and applies this IaC; PLAT-010 swaps the compose staging target for the declared topology behind the same deploy stages). Provisions the substrate for TASK-PLAT-003 (managed Postgres), TASK-PLAT-006 (managed Redis, also the TASK-API-003 counter store and the Celery broker), and TASK-PLAT-009 (the multi-AZ + cross-region topology the backup/DR policy runs on). Feeds and is fed by TASK-PLAT-005 (autoscaling decisions read latency/CPU metrics; the HPA is observable there) and hosts the TASK-REPORT-002 batch reports as Celery tasks. Sources secrets from TASK-PLAT-007.

## §8 - Example payloads

```yaml
# celery-worker.yaml (abridged) - background tasks off the hot path
apiVersion: apps/v1
kind: Deployment
metadata: { name: tamthuc-celery }
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: worker
          image: ghcr.io/cyberskill/tamthuc-api:${SHA}
          command: ["celery", "-A", "tamthuc_api.tasks", "worker", "-Q", "reports,warming,ops"]
```

```
# infra change flow - never by hand
edit deploy/terraform/*.tf  ->  PR  ->  terraform plan (reviewed)  ->  merge  ->  pipeline apply
```

## §9 - Open questions

- Kubernetes distribution / managed vs self-hosted, and single vs multi-cloud. Default: a managed Kubernetes on the same cloud as the managed Postgres/Redis at MVP; the manifests stay portable so the cluster provider is a values change. Aligns with the strategy 4.1 "any managed Postgres works" posture.
- HPA signal: CPU-only vs custom latency/queue-depth metrics. Default: CPU utilization first (simple, works with stock HPA), adding a custom latency or Celery-queue-depth metric via the TASK-PLAT-005 metrics once the scaling behavior is understood.
- Whether the compose bootstrap is retired or kept for local dev. Default: keep a compose file for local development, but production/staging are Kubernetes from the IaC; the compose staging target TASK-PLAT-004 bootstrapped is retired once this lands.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Hand-built infra | a production resource created via a console | forbidden; all infra is Terraform/K8s from source; a drift check catches out-of-band resources |
| Config drift | manifests/state diverge from the live environment | `terraform plan` reports drift and fails CI; apply-twice is a no-op |
| Hot path blocked by batch work | a batch report runs on a request pod | background tasks run on separate Celery workers; a report load leaves chart-cast latency within SLO |
| No autoscale under load | fixed replicas, manual scaling | the stateless services carry an HPA; a spike adds replicas, not a page |
| Secret in a manifest | a credential committed as a value | forbidden; secrets sourced from the TASK-PLAT-007 manager; a scan confirms none committed |
| Staging/prod divergence | environments defined separately | one parameterized source; environments differ by values, not by drift |

## §11 - Notes

This task turns the running system into code: Terraform for the substrate (network, managed Postgres, managed Redis, compute), Kubernetes manifests for the three deployables, an HPA on the stateless calculation services, and Celery workers for background tasks so batch reports never steal latency from a chart cast. The inviolable rule is that no production resource lives outside the IaC - an infra change is a reviewed file change applied through the TASK-PLAT-004 pipeline, which is what keeps the code and the reality in sync and makes a TASK-PLAT-009 DR rebuild an `apply` rather than an excavation. It is pure IaC, parameterized for staging and production from one source, sourcing secrets from the TASK-PLAT-007 manager.
