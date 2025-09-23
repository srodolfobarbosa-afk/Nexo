ENGINEER ONBOARDING — Nexo / EcoGuardians

Visão Geral
-----------
Este repositório contém o Nexo/EcoGuardians: um sistema de agentes autônomos projetado para evoluir, executar missões e gerar receitas. O objetivo final é operar como uma "IA viva" com memória persistente, integrações com LLMs, banco vetorial e persistência no Supabase.

Objetivo do Projeto
-------------------
- Sistema vivo com agentes ativos
- Geração real de receitas via EcoBank
- Segurança e auditoria (RLS no Supabase)
- Memória de longo prazo persistida e consultável
- Agentes conversacionais em linguagem natural
- Execução automática de missões
- Auto-evolução e auto-construção contínuas

Resumo do que já foi implementado
---------------------------------
- Rota `/chat` que aceita mensagem em JSON e retorna resposta (usa `core/llm_caller` com fallback local se não houver LLM)
- Proteção do mission runner: só cria tarefas se `START_MISSION_RUNNER=1` e Supabase estiver configurado
- `core/supabase_client` grava em `local_supabase_backup.json` quando Supabase indisponível
- `core/database` valida credenciais Supabase (consulta leve)
- `PROJECT_OBJECTIVE.md` e endpoints `/objective` para consultar/atualizar o objetivo
- Migração SQL `supabase_migrations/001_create_tables.sql` para criar tabelas mínimas
- Scripts e docs: `tools/deploy_instructions.sh`, `DEPLOY_RENDER.md`

Arquitetura e componentes
------------------------
- Web/API: `src/ws_server.py` (Flask + Flask-Sock + endpoints REST + SSE)
- Agentes: módulos em `agentes/` (NexoGenesis, EcoFinance, etc.)
- Persistência: Supabase (primária) + `local_supabase_backup.json` (fallback)
- Runner: `core/mission_runner.py` — cria e processa tarefas
- LLM Caller: `core/llm_caller.py` — prioriza Gemini/OpenAI/Groq com fallback local
- Helpers: `core/jwt_auth.py`, `core/supabase_client.py`, `core/database.py`, `core/project_objective.py`

Como rodar local (desenvolvimento)
----------------------------------
1. Crie um virtualenv e instale dependências:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Opcional: exporte variáveis de ambiente (uso local com fallbacks):
```bash
export DISABLE_TELEGRAM=1
export START_MISSION_RUNNER=0
export AUTH_USERNAME=admin
export AUTH_PASSWORD=password
# SUPABASE_URL/SUPABASE_KEY se quiser testar persistência real
```
3. Rodar Gunicorn (servidor):
```bash
nohup gunicorn --config gunicorn_config.py src.ws_server:app -b 0.0.0.0:8000 > gunicorn.out 2>&1 &
```
4. Rodar sistema integrado em background (opcional):
```bash
nohup python3 run_integrated_system.py > integrated_run.out 2>&1 &
```
5. Testar endpoints:
```bash
curl http://127.0.0.1:8000/status
curl -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -d '{"message":"Olá"}'
```

Como preparar Supabase (produção)
---------------------------------
1. No painel do Supabase, crie o projeto e gere uma `anon` ou `service_role` key.
2. No SQL Editor do Supabase, rode `supabase_migrations/001_create_tables.sql` para criar `tasks`, `agent_logs`, `chat`.
3. (Recomendado) Crie políticas RLS para cada tabela — eu posso gerar exemplos abaixo.

Deploy no Render
-----------------
- `render.yaml` está presente e `startCommand` usa: `gunicorn --bind 0.0.0.0:$PORT src.ws_server:app`.
- No painel do Render, defina as env vars:
  - `SUPABASE_URL` = https://<project>.supabase.co
  - `SUPABASE_KEY` = <anon or service_role>
  - `START_MISSION_RUNNER` = 0 (iniciar em standby)
  - `DISABLE_TELEGRAM` = 1
  - `AUTH_USERNAME` / `AUTH_PASSWORD`
- Redeploy e verifique logs. Quando tudo OK, altere `START_MISSION_RUNNER` para `1` para ativar execução automática.

Segurança (recomendações)
-------------------------
- Rotacione chaves imediatamente se expostas.
- Use RLS no Supabase para restringir inserções/leituras por role.
- Use `service_role` apenas para tarefas administrativas, e `anon` para a aplicação conforme as policies.
- Habilite registro/auditoria na tabela `agent_logs`.

Exemplo de políticas RLS (template)
-----------------------------------
Posso gerar políticas detalhadas; exemplo mínimo para permitir inserção por `anon`:
```sql
-- Exemplo: permitir inserts públicos em 'chat' apenas via anon key
ALTER TABLE public.chat ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow anon inserts" ON public.chat FOR INSERT USING (true) WITH CHECK (true);
```
(OBS: revisar antes de usar em produção. Melhor criar policies mais restritivas.)

Checklist para entregar o objetivo final
---------------------------------------
- [ ] Rotacionar chaves e configurar secrets no Render
- [ ] Rodar migrations no Supabase
- [ ] Validar endpoints `/status`, `/auth/token`, `/chat`, `/api/missions/*`
- [ ] Ativar `START_MISSION_RUNNER=1` e monitorar tarefas
- [ ] Integrar banco vetorial (LangChain/Chroma/Weaviate) para memórias semânticas
- [ ] Conectar LLMs (Gemini/OpenAI) e validar respostas
- [ ] Implementar RLS e auditoria completa
- [ ] Validar geração de receita (integração EcoBank) em ambiente de staging
- [ ] Planejar auto-evolução: pipeline de avaliação/merge + geração automática de código (CI controlado)

Próximos passos recomendados
----------------------------
1. Rotacione as chaves expostas agora.
2. Execute as migrations no Supabase.
3. Configure Render com as env vars e reinicie com `START_MISSION_RUNNER=0`.
4. Valide persistência e então ative o runner.
5. Eu posso gerar PRs, scripts e políticas RLS automáticas — diga o que prefere.

Notas finais
-----------
Este documento é o ponto de partida para qualquer engenheiro que for trabalhar no projeto. Atualize-o sempre que fizer mudanças de arquitetura ou procedimentos de deploy.

---
Arquivo gerado automaticamente em: (workspace)

Registro de trabalho (como contribuir rapidamente)
-------------------------------------------------
- Arquivo de registro local: `WORK_LOG.md` na raiz do repositório.
- Script utilitário: `tools/log_work.py` — append no `WORK_LOG.md` e tenta gravar em `agent_logs` no Supabase.

Como usar o script:
```bash
python tools/log_work.py "Corrigi o mission_runner para checar SUPABASE" --author "seunome"
```

Se as variáveis `SUPABASE_URL` e `SUPABASE_KEY` estiverem configuradas, o script tentará persistir o registro na tabela `agent_logs`.

RLS e políticas
---------------
Um exemplo de políticas RLS está em `supabase_migrations/rls_example.sql`. Revise e ajuste os nomes de roles e as claims do JWT (`sub`) conforme seu provedor de identidades.

Armazenamento seguro de segredos (local)
--------------------------------------
Para evitar que chaves fiquem espalhadas em ambiente de desenvolvimento, existe um utilitário local `tools/secret_store.py` que criptografa segredos com uma `MASTER_KEY` e os salva em `.secrets.json.enc`.

Importante:
- Nunca comite `.secrets.json.enc` ou chaves no repositório.
- Em produção, use o gerenciador de segredos do provedor (Render secrets, AWS Secrets Manager, HashiCorp Vault).

Exemplo rápido:
```bash
# Gere uma master key (uma vez)
export MASTER_KEY=$(python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
)

# Salvar uma chave (ex: SUPABASE_KEY) localmente (criptografado)
python tools/secret_store.py set SUPABASE_KEY "minha-chave-aqui"

# Recuperar
python tools/secret_store.py get SUPABASE_KEY
```

Se preferir não usar o utilitário local, armazene as chaves apenas no painel do Render como secrets.

Validação automatizada de deploy
--------------------------------
Incluí um utilitário `tools/validate_deploy.py` que executa testes básicos:
- `/status` (saúde)
- `/auth/token` (gera token se credenciais fornecidas)
- `/objective` (GET)
- `/chat` (POST)

Uso:
```bash
python tools/validate_deploy.py --base https://<your-service>.onrender.com --auth-user admin --auth-pass <password>
```

O script também tenta gravar diretamente no Supabase via REST se `SUPABASE_URL` e `SUPABASE_KEY` estiverem no ambiente.
