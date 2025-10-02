-- Supabase schema skeleton for Nexo / EcoGuardians
-- Use this file to initialize your Supabase DB (psql or Supabase SQL editor).
-- WARNING: Review policies and secrets before running in production.

-- Enable pgvector extension (if using pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  persona jsonb,
  created_at timestamptz DEFAULT now()
);

-- Tasks / missions (short lived)
CREATE TABLE IF NOT EXISTS tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner text, -- JWT sub or service
  title text,
  payload jsonb,
  status text DEFAULT 'pending',
  created_at timestamptz DEFAULT now()
);

-- Memories - short term (fast writes)
CREATE TABLE IF NOT EXISTS memories_short (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner text,
  key text,
  data jsonb,
  created_at timestamptz DEFAULT now()
);

-- Memories - long term (archival)
CREATE TABLE IF NOT EXISTS memories_long (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner text,
  summary text,
  data jsonb,
  created_at timestamptz DEFAULT now()
);

-- Vector embeddings (pgvector)
CREATE TABLE IF NOT EXISTS embeddings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner text,
  doc_id text,
  embedding vector(1536), -- adjust dimension to your model
  metadata jsonb,
  created_at timestamptz DEFAULT now()
);

-- Agent audit logs (append-only)
CREATE TABLE IF NOT EXISTS agent_audit (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid,
  event_type text,
  details jsonb,
  created_at timestamptz DEFAULT now()
);

-- Example RLS policies
-- Note: replace 'auth.role()' checks with your project's logic (Supabase provides 'auth.uid()' etc.)

-- Enable row level security on tasks and memories
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories_short ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories_long ENABLE ROW LEVEL SECURITY;

-- Policy: allow users to insert/select their own rows if owner matches jwt sub
CREATE POLICY "tasks_owner_policy" ON tasks
  FOR ALL
  USING (owner = current_setting('jwt.claims.sub', true))
  WITH CHECK (owner = current_setting('jwt.claims.sub', true));

CREATE POLICY "memories_short_owner_policy" ON memories_short
  FOR ALL
  USING (owner = current_setting('jwt.claims.sub', true))
  WITH CHECK (owner = current_setting('jwt.claims.sub', true));

CREATE POLICY "memories_long_owner_policy" ON memories_long
  FOR ALL
  USING (owner = current_setting('jwt.claims.sub', true))
  WITH CHECK (owner = current_setting('jwt.claims.sub', true));

-- Agent audit: allow inserts from service role only (no public read)
ALTER TABLE agent_audit ENABLE ROW LEVEL SECURITY;
CREATE POLICY "agent_audit_insert_service_only" ON agent_audit
  FOR INSERT
  USING (current_setting('is_service_role', true) = '1')
  WITH CHECK (current_setting('is_service_role', true) = '1');

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_embeddings_docid ON embeddings(doc_id);
CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner);

-- Notes:
-- 1) Supabase uses JWT claims; set 'jwt.claims.sub' or adapt policies to 'auth.uid()' as appropriate.
-- 2) To run with Supabase, open your project SQL editor and run this file.
-- 3) Review and tighten policies before production; consider using service_role key only for server-side operations.
-- Supabase Schema para Nexo (produção)

-- Tabela de agentes
create table if not exists agents (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    tipo text not null,
    criado_em timestamp with time zone default now(),
    status text
);

-- Tabela de memórias dos agentes
create table if not exists nexo_agent_memory (
    id uuid primary key default gen_random_uuid(),
    agent_id uuid references agents(id),
    conteudo jsonb not null,
    criado_em timestamp with time zone default now()
);

-- Tabela de contexto do usuário
create table if not exists nexo_user_context (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    contexto jsonb,
    atualizado_em timestamp with time zone default now()
);

-- Tabela de tarefas proativas
create table if not exists nexo_proactive_tasks (
    id uuid primary key default gen_random_uuid(),
    descricao text not null,
    status text,
    criado_em timestamp with time zone default now()
);

-- Tabela de logs dos agentes
create table if not exists agent_logs (
    id uuid primary key default gen_random_uuid(),
    level text,
    message text,
    details jsonb,
    criado_em timestamp with time zone default now()
);

-- Tabela de memória de aprendizado
create table if not exists agent_learning_memory (
    id uuid primary key default gen_random_uuid(),
    agent_id uuid references agents(id),
    conteudo jsonb,
    criado_em timestamp with time zone default now()
);

-- Tabela de logs de erro
create table if not exists agent_error_log (
    id uuid primary key default gen_random_uuid(),
    agent_id uuid references agents(id),
    erro text,
    detalhes jsonb,
    criado_em timestamp with time zone default now()
);

-- Tabela de log geral (legado)
create table if not exists nexo_log (
    id serial primary key,
    mensagem text,
    tipo text,
    resultado text,
    criado_em timestamp with time zone default now()
);

-- Exemplo de ativação de RLS
alter table agents enable row level security;
alter table nexo_agent_memory enable row level security;
alter table nexo_user_context enable row level security;
alter table nexo_proactive_tasks enable row level security;
alter table agent_logs enable row level security;
alter table agent_learning_memory enable row level security;
alter table agent_error_log enable row level security;
alter table nexo_log enable row level security;

-- Exemplo de política básica (ajuste conforme necessário)
create policy if not exists "Allow all read" on agents for select using (true);
create policy if not exists "Allow all insert" on agents for insert with check (true);
-- Repita para as demais tabelas conforme necessidade
