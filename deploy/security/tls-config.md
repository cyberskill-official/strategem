# TLS

- Minimum TLS **1.3** at the edge (no 1.0/1.1/1.2 for user-data routes).
- HSTS enabled (`Strict-Transport-Security`).
- Certificates via platform ACME / secret manager (FR-PLAT-007 secrets.md).
