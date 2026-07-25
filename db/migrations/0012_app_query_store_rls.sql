-- TT-008: fail-closed RLS on app_query_store (product payload store).
-- user_id remains text (supports 'anon' free-cast rows); compare GUC as text.
-- Admin bypass matches 0009 pattern (app_admin + app.current_role = 'admin').

GRANT SELECT, INSERT, UPDATE, DELETE ON app_query_store TO app_user, app_admin;

ALTER TABLE app_query_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_query_store FORCE ROW LEVEL SECURITY;

CREATE POLICY app_query_store_owner ON app_query_store
  USING (user_id = current_setting('app.current_user_id', true))
  WITH CHECK (user_id = current_setting('app.current_user_id', true));

CREATE POLICY app_query_store_admin ON app_query_store TO app_admin
  USING (current_setting('app.current_role', true) = 'admin')
  WITH CHECK (current_setting('app.current_role', true) = 'admin');
