# Secrets custody

- Secrets live in CI secret store / cloud secret manager only.
- Never in git, Docker layers, or client bundles.
- Rotation: JWT secret, master key, API keys — dual-key window for JWT.
