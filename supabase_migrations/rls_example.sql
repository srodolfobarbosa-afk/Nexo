-- Example RLS policies for Supabase (Postgres)
-- Use the SQL editor in Supabase or psql to apply. Adjust role names and JWT claim keys as needed.

-- Enable row level security on target tables
ALTER TABLE IF EXISTS public.chat ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.agent_logs ENABLE ROW LEVEL SECURITY;

-- Simple helper: extract 'sub' claim from request JWT (adjust if you use another claim)
CREATE OR REPLACE FUNCTION public.jwt_sub() RETURNS text AS $$
BEGIN
  RETURN (current_setting('request.jwt.claims', true)::json->>'sub');
EXCEPTION WHEN OTHERS THEN
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- CHAT: allow inserts when the JWT sub matches NEW.user_id (or allow service_role)
CREATE POLICY chat_insert_on_user ON public.chat
  FOR INSERT
  USING (true)
  WITH CHECK (
    (public.jwt_sub() IS NOT NULL AND public.jwt_sub() = NEW.user_id)
    OR (current_setting('request.jwt.role', true) = 'service_role')
  );

CREATE POLICY chat_select_on_user ON public.chat
  FOR SELECT
  USING (
    (public.jwt_sub() IS NOT NULL AND public.jwt_sub() = user_id)
    OR (current_setting('request.jwt.role', true) = 'service_role')
  );

-- TASKS: allow inserts only for service_role (server-side) or a specific role
CREATE POLICY tasks_insert_service ON public.tasks
  FOR INSERT
  USING (current_setting('request.jwt.role', true) = 'service_role');

-- AGENT_LOGS: allow insert for authenticated users and service_role for admin
CREATE POLICY agent_logs_insert ON public.agent_logs
  FOR INSERT
  USING (true)
  WITH CHECK (
    (public.jwt_sub() IS NOT NULL AND public.jwt_sub() = NEW.user_id)
    OR (current_setting('request.jwt.role', true) = 'service_role')
  );

-- Grant execute on helper to authenticated
GRANT EXECUTE ON FUNCTION public.jwt_sub() TO authenticated;

-- Notes:
-- - Test these policies carefully. Use Supabase SQL editor to run sample queries.
-- - If you don't use Supabase Auth, adapt the checks to match your authentication flow.
-- - Keep service_role key secret and only use it server-side for administrative operations.
