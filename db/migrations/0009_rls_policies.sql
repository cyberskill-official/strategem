-- FR-PLAT-003: fail-closed RLS.
-- Deny by default: ENABLE + FORCE with no permissive policy → zero rows visible.
-- Owner policies key on app.current_user_id (SET LOCAL per request; see db/rls/session.md).
-- Admin bypass is an explicit separate policy on role app_admin + app.current_role = 'admin'.

-- App roles used by policies (table owner still subject to FORCE RLS).
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_admin') THEN
    CREATE ROLE app_admin NOLOGIN;
  END IF;
END
$$;

-- Grant DML to app roles so policies can apply (migrations run as superuser/owner).
GRANT SELECT, INSERT, UPDATE, DELETE ON users, queries, charts, reports, audit_logs TO app_user, app_admin;
GRANT SELECT ON knowledge_patterns TO app_user, app_admin;
GRANT INSERT, UPDATE, DELETE ON knowledge_patterns TO app_admin;
GRANT USAGE, SELECT ON SEQUENCE audit_logs_id_seq TO app_user, app_admin;

-- ── users (self row only; admin sees all) ──────────────────────────
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

CREATE POLICY users_owner ON users
  USING (id = current_setting('app.current_user_id', true)::uuid)
  WITH CHECK (id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY users_admin ON users TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');

-- ── queries ────────────────────────────────────────────────────────
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries FORCE ROW LEVEL SECURITY;

CREATE POLICY queries_owner ON queries
  USING (user_id = current_setting('app.current_user_id', true)::uuid)
  WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY queries_admin ON queries TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');

-- ── charts ─────────────────────────────────────────────────────────
ALTER TABLE charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE charts FORCE ROW LEVEL SECURITY;

CREATE POLICY charts_owner ON charts
  USING (user_id = current_setting('app.current_user_id', true)::uuid)
  WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY charts_admin ON charts TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');

-- ── reports ────────────────────────────────────────────────────────
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports FORCE ROW LEVEL SECURITY;

CREATE POLICY reports_owner ON reports
  USING (user_id = current_setting('app.current_user_id', true)::uuid)
  WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY reports_admin ON reports TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');

-- ── audit_logs (own rows; admin full) ──────────────────────────────
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_owner ON audit_logs
  USING (user_id = current_setting('app.current_user_id', true)::uuid)
  WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);

CREATE POLICY audit_logs_admin ON audit_logs TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');

-- ── knowledge_patterns: world-readable; admin/curator write only ───
ALTER TABLE knowledge_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_patterns FORCE ROW LEVEL SECURITY;

CREATE POLICY knowledge_patterns_read ON knowledge_patterns
  FOR SELECT
  USING (true);

CREATE POLICY knowledge_patterns_admin_write ON knowledge_patterns
  FOR ALL
  TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');
