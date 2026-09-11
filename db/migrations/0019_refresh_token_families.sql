-- AUTH-001 follow-up: refresh-token families for session list / revoke-one / revoke-all.
-- One row per login device/family; rotation updates current_jti; reuse revokes the family.

CREATE TABLE IF NOT EXISTS refresh_token_families (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             uuid NOT NULL REFERENCES users(id),
  current_jti         text NOT NULL,
  expires_at          timestamptz NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),
  last_seen_at        timestamptz NOT NULL DEFAULT now(),
  revoked_at          timestamptz,
  reuse_detected_at   timestamptz,
  label               text
);

CREATE UNIQUE INDEX IF NOT EXISTS refresh_token_families_current_jti_uidx
  ON refresh_token_families (current_jti)
  WHERE revoked_at IS NULL;

CREATE INDEX IF NOT EXISTS refresh_token_families_user_active_idx
  ON refresh_token_families (user_id)
  WHERE revoked_at IS NULL;

COMMENT ON TABLE refresh_token_families IS
  'Refresh families (sessions): rotation updates current_jti; reuse detection revokes the family.';

GRANT SELECT, INSERT, UPDATE ON refresh_token_families TO app_user, app_admin;
