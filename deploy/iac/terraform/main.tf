# TASK-PLAT-010 — Terraform EXPERIMENTAL scaffold (no live credentials)
# Not production IaC. Wire real cloud providers in ops runbooks before use.
terraform {
  required_version = ">= 1.5"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

resource "null_resource" "strategem_scaffold" {
  triggers = {
    purpose = "iac-scaffold-only-experimental"
  }
}

output "note" {
  value = "EXPERIMENTAL scaffold only — wire real cloud providers in ops runbooks."
}
