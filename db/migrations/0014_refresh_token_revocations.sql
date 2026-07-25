-- TT-024: durable refresh-token revocation (jti denylist).
-- Replaces in-process RevocationStore for production / DATABASE_URL deployments.

CREATE TABLE IF NOT EXISTS refresh_token_revocations (
  jti        text PRIMARY KEY,
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS refresh_token_revocations_expires_idx
  ON refresh_token_revocations (expires_at);

-- Not user-scoped: any authenticated backend may check/insert by jti.
-- Keep FORCE off so service role can revoke without impersonating the token subject.
GRANT SELECT, INSERT, DELETE ON refresh_token_revocations TO app_user, app_admin;
