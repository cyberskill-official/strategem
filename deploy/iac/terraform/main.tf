# TASK-PLAT-010 — Terraform skeleton (no live credentials)
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
    purpose = "iac-scaffold-only"
  }
}

output "note" {
  value = "Scaffold only — wire real cloud providers in ops runbooks."
}
