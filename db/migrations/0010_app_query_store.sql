-- COV-010: product query/chart/report payload store (survives process restart).
-- Full orchestrator result JSON; does not replace RLS domain tables for multi-tenant SaaS.

CREATE TABLE IF NOT EXISTS app_query_store (
  id             uuid PRIMARY KEY,
  user_id        text NOT NULL DEFAULT 'anon',
  payload        jsonb NOT NULL,
  systems        text[] NOT NULL DEFAULT '{}',
  question_type  text,
  report_id      text,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS app_query_store_user_created_idx
  ON app_query_store (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS app_query_store_report_idx
  ON app_query_store (report_id)
  WHERE report_id IS NOT NULL;
