-- RLS policies aligned to `supabase_schema.sql`
-- Apply in Supabase SQL editor. Adjust JWT claim names and roles as necessary.

-- Helper to read 'sub' claim
CREATE OR REPLACE FUNCTION public.jwt_sub() RETURNS text AS $$
BEGIN
  RETURN (current_setting('request.jwt.claims', true)::json->>'sub');
EXCEPTION WHEN OTHERS THEN
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Allow service_role full access via role check
-- AGENT LOGS: allow inserts by authenticated users matching user_id or service_role
CREATE POLICY agent_logs_insert_policy ON public.agent_logs
  FOR INSERT
  USING (true)
  WITH CHECK (
    (public.jwt_sub() IS NOT NULL AND public.jwt_sub() = NEW.user_id::text)
    OR (current_setting('request.jwt.role', true) = 'service_role')
  );

CREATE POLICY agent_logs_select_policy ON public.agent_logs
  FOR SELECT
  USING (
    (current_setting('request.jwt.role', true) = 'service_role')
    OR (public.jwt_sub() IS NOT NULL)
  );

-- NEXO USER CONTEXT: allow users to manage their own context
CREATE POLICY nexo_user_context_insert ON public.nexo_user_context
  FOR INSERT
  USING (true)
  WITH CHECK (
    (public.jwt_sub() IS NOT NULL AND public.jwt_sub() = NEW.user_id)
    OR (current_setting('request.jwt.role', true) = 'service_role')
  );

CREATE POLICY nexo_user_context_select ON public.nexo_user_context
  FOR SELECT
  USING (
    (public.jwt_sub() IS NOT NULL AND public.jwt_sub() = user_id)
    OR (current_setting('request.jwt.role', true) = 'service_role')
  );

-- NEXO AGENT MEMORY: allow service_role and server-side inserts; restrict select to service_role or owner via agent relation
CREATE POLICY nexo_agent_memory_insert ON public.nexo_agent_memory
  FOR INSERT
  USING (current_setting('request.jwt.role', true) = 'service_role');

CREATE POLICY nexo_agent_memory_select ON public.nexo_agent_memory
  FOR SELECT
  USING (current_setting('request.jwt.role', true) = 'service_role');

-- PROACTIVE TASKS: only service_role can create tasks
CREATE POLICY nexo_proactive_tasks_insert ON public.nexo_proactive_tasks
  FOR INSERT
  USING (current_setting('request.jwt.role', true) = 'service_role');

CREATE POLICY nexo_proactive_tasks_select ON public.nexo_proactive_tasks
  FOR SELECT
  USING (true);

-- AGENT LEARNING MEMORY: restrict to service_role
CREATE POLICY agent_learning_memory_insert ON public.agent_learning_memory
  FOR INSERT
  USING (current_setting('request.jwt.role', true) = 'service_role');

CREATE POLICY agent_learning_memory_select ON public.agent_learning_memory
  FOR SELECT
  USING (current_setting('request.jwt.role', true) = 'service_role');

-- ERROR LOG: allow inserts from service_role or agent processes
CREATE POLICY agent_error_log_insert ON public.agent_error_log
  FOR INSERT
  USING (
    (current_setting('request.jwt.role', true) = 'service_role')
  );

GRANT EXECUTE ON FUNCTION public.jwt_sub() TO authenticated;

-- Notes:
-- - These policies are conservative: prefer service_role for inserts from servers and restrict selects.
-- - If you want agents to write directly with anon/other roles, create more specific policies mapping JWT claims.
