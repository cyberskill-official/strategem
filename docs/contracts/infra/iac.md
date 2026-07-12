# Infrastructure as code (FR-PLAT-010)

Terraform modules + Kubernetes manifests under `deploy/iac/` (scaffolded).

## Layout

```
deploy/iac/
  terraform/
    main.tf          # provider + remote state skeleton
    variables.tf
  k8s/
    namespace.yaml
    api-deployment.yaml
    web-deployment.yaml
```

## Principles

- No secrets in git; inject via sealed secrets / external secrets operator
- Staging then prod promotion (FR-PLAT-004 CD)
- Chart calculation engines scale independently of API/web
