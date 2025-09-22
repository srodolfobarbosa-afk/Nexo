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
