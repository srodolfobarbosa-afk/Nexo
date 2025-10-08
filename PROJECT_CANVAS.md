# PROJECT CANVAS — EcoGuardians (Nexo)

Visão rápida
------------
Nome do projeto: EcoGuardians — Sistema de Agentes IA Autônomos (código: Nexo)
Resumo: conjunto de agentes autônomos para monitoramento, análise e execução de oportunidades econômicas e ambientais. Arquitetura híbrida: backend Python (Flask/FastAPI), frontend estático, armazenamento em Supabase/Postgres, LLMs com fallback.

Status atual (resumo rápido)
---------------------------
- Repositório inicializado e analisado
- Script de init (`init_workspace.sh`) criado para gerenciar venv e `requirements_clean.txt`
- `requirements_prod.txt` criado para builds enxutos
- `Dockerfile` hardened para evitar installs pesadas por padrão
- Workflow GitHub Actions `render-deploy.yml` criado para build→push→deploy em Render (usa GHCR)
- `INFRASTRUCTURE_MAP.md` adicionado com guia para infra grátis
- `agentes/StarterAgent.py` adicionado (SQLite fallback; Supabase compat)

Principais pastas e arquivos
---------------------------
- agentes/ — código dos agentes (StarterAgent, etc.)
- agentes/StarterAgent.py — agente inicial leve, persistência SQLite/Supabase
- core/ — lógica central (agent_base, loaders, integradores)
- src/ — web server (`src.ws_server` ou similar)
- Dockerfile, requirements_prod.txt, requirements_clean.txt
- .github/workflows/ci.yml (lint/test) e render-deploy.yml (deploy to Render)
- INFRASTRUCTURE_MAP.md — mapa de infra gratuito
- PROJECT_CANVAS.md — este arquivo

Lista de agentes (resumo)
-------------------------
- EcoFinance — analisa oportunidades econômicas, sugestões de investimento
- EcoGuard — monitora eventos ambientais e aciona alertas
- MarketWatchAgent — recebe feeds de mercado e sinaliza mudanças
- Analyzer / Reviewer / Executor — papéis auxiliares para revisão, execução e validação
- StarterAgent — exemplo leve para testes locais (persistência + echo LLM fallback)

Contractos e APIs (entrada/saída)
---------------------------------
- Agent.ask(prompt: str) -> str
- Agent.save_message(role, content, meta)
- HTTP endpoints (a criar):
  - POST /agent/ask { "prompt": "..." } -> { "answer": "..." }
  - GET /agent/history -> [{id, role, content, meta}, ...]

Requisitos/Variáveis de Ambiente
--------------------------------
- SUPABASE_URL, SUPABASE_KEY — (opcional) para persistência remota
- OPENAI_API_KEY, GOOGLE_API_KEY — (opcional) providers LLM
- RENDER_SERVICE_ID, RENDER_API_TOKEN — (opcional) para deploy via API

Política de dependências
------------------------
- `requirements_prod.txt`: dependências mínimas para produção e CI/Render
- `requirements_clean.txt`: lista extensa (dev / experimental) — NÃO usar em CI sem build-arg
- Evitar instalar pacotes ML pesados em CI por padrão (torch, triton, faiss)

Checklists e progresso
----------------------
- [x] init script e docs
- [x] requirements_prod.txt criado
- [x] Dockerfile atualizado para builds enxutos
- [x] workflow render-deploy.yml criado (push para GHCR + trigger Render)
- [x] INFRASTRUCTURE_MAP.md criado
- [x] StarterAgent implementado e testado localmente
- [ ] Implementar LLM fallback chain (OpenAI -> Google -> local)
- [ ] Criar endpoints HTTP para o StarterAgent (FastAPI/Flask)
- [ ] Adicionar testes unitários e integração no CI
- [ ] Criar migração SQL para Supabase e instruções de seed
- [ ] Configurar deploy automático no Render (ou integração GitHub-Render)

Segurança e backups
------------------
- Mantenha as chaves (Supabase, OpenAI, Render) apenas em GitHub Secrets
- Adicionar instruções para rotacionar tokens em `SECURITY.md`
- Backup: criar runner para gerar ZIP do repositório periodicamente (script de backup opcional)

Operação gratuita (dicas práticas)
----------------------------------
- Use Vercel para frontend estático; Render para workers persistentes; Supabase como DB gratuito.
- Limite chamadas a LLMs com cache e rate-limits. Habilite fallback local.
- Use GHCR para imagens e evite builds pesados no CI.

Próximos passos recomendados (curto prazo)
-----------------------------------------
1. Implementar `agentes/llm_provider.py` (fallback chain) — posso gerar agora.
2. Criar `api/starter_agent.py` (endpoints REST com FastAPI) + tests — posso implementar e integrar ao CI.
3. Documentar migração Supabase (SQL) e adicionar script `scripts/init_supabase.sql`.

Como eu (assistente) vou manter o projeto organizado para você
-----------------------------------------------------------
- Em cada nova interação posso gerar/atualizar artefatos (código, docs, workflows) e testar localmente.
- Se quiser um snapshot exportável, peço permissão e gero um ZIP pronto para baixar.
- Posso também gerar um diagrama Mermaid ou um README final para apresentação.

O que deseja agora?
--------------------
- Responda uma opção:
  - `LLM` → eu implemento `agentes/llm_provider.py` com fallback e testes mínimos.
  - `API` → eu implemento `api/starter_agent.py` (FastAPI) com endpoints /agent/ask e /agent/history e testes.
  - `DIAGRAMA` → eu gero um diagrama Mermaid da arquitetura.
  - `ZIP` → eu gero um ZIP do repositório pronto para download (peça de arquivo preparado).

