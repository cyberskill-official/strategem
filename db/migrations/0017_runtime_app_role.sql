-- D-DB-001 / TASK-DB-001: restricted LOGIN role for API runtime.
-- Migrations and ops continue to use a privileged role (postgres / DATABASE_URL_MIGRATE).
-- API DATABASE_URL MUST connect as strategem_app (NOSUPERUSER NOBYPASSRLS NOCREATEDB).
--
-- Local default password is `strategem_app` (compose). Rotate before any shared/hosted use:
--   ALTER ROLE strategem_app PASSWORD '<strong>';

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'strategem_app') THEN
    CREATE ROLE strategem_app LOGIN PASSWORD 'strategem_app'
      NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION INHERIT;
  ELSE
    ALTER ROLE strategem_app
      NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION LOGIN INHERIT;
  END IF;
END
$$;

GRANT app_user TO strategem_app;
GRANT USAGE ON SCHEMA public TO strategem_app;

-- Tables introduced after 0009 that need runtime DML (idempotent grants).
GRANT SELECT, INSERT, UPDATE, DELETE ON payment_fulfillments TO app_user, app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON operator_llm_settings TO app_user, app_admin;
