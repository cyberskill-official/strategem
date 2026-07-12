-- FR-PLAT-003: RLS isolation harness (psql).
-- Expected to run after 0001..0009 on a clean DB, as a role subject to RLS.
-- Exit non-zero on failure when used with: psql -v ON_ERROR_STOP=1 -f ...
--
-- Variables (set by the Python runner; defaults for manual use):
--   :user_a  UUID of user A
--   :user_b  UUID of user B

\set ON_ERROR_STOP on

-- ── Bootstrap seed as superuser/owner (caller may wrap this) ──────
-- The Python runner performs seed inserts; this file focuses on assertions
-- when session GUCs are set/unset. Kept as documentation + optional manual path.

DO $$
DECLARE
  n bigint;
BEGIN
  -- Fail-closed: no GUC → zero charts
  RESET app.current_user_id;
  RESET app.current_role;
  SELECT count(*) INTO n FROM charts;
  IF n <> 0 THEN
    RAISE EXCEPTION 'FAIL fail-closed charts: expected 0 got %', n;
  END IF;

  SELECT count(*) INTO n FROM queries;
  IF n <> 0 THEN
    RAISE EXCEPTION 'FAIL fail-closed queries: expected 0 got %', n;
  END IF;

  SELECT count(*) INTO n FROM reports;
  IF n <> 0 THEN
    RAISE EXCEPTION 'FAIL fail-closed reports: expected 0 got %', n;
  END IF;

  RAISE NOTICE 'PASS fail-closed unset GUC sees zero user-scoped rows';
END
$$;
