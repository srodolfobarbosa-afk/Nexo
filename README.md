eu QUERO QUERO  faça o NexoGenesis "rodar de verdade" e que o sistema fique vivo, auto-construa e opere automaticamente.# Atualização do Projeto Nexo

## Instruções de Configuração

(Adicione aqui as instruções de configuração do README_UPDATE.md)

## Instruções de Instalação

(Adicione aqui as instruções de instalação do README_UPDATE.md)

## Instruções de Execução

(Adicione aqui as instruções de execução do README_UPDATE.md)

## Instruções de Testes

(Adicione aqui as instruções de testes do README_UPDATE.md)

## Instruções de Deploy Automático

(Adicione aqui as instruções de deploy automático do README_UPDATE.md)

## Quick local / production notes

- DO NOT commit real secrets. Use `.env` (ignored) and a secrets manager in production.
- Build the Docker image (example):

	docker build -t nexo:latest .

- Run (development):

	docker run --env-file .env -p 8000:8000 nexo:latest

- CI: GitHub Actions runs tests and a secrets scan. Ensure you rotate any compromised keys before pushing.

## Supabase Auth (recommended for production)

1. Create a Supabase project and enable Auth (OAuth2 / email).
2. Add `SUPABASE_URL` and `SUPABASE_KEY` to your deployment secrets (Render / GitHub Secrets).
3. Set `USE_SUPABASE_AUTH=1` in your environment to force the app to validate JWTs via Supabase JWKS.
4. IMPORTANT: set a strong `JWT_SECRET` for any HS256 fallback tokens and never commit it.

When `USE_SUPABASE_AUTH=1`, the `/auth/token` dev route is disabled and the service will verify RS256 tokens published by Supabase.

## Catálogo de Agentes

Este repositório agora inclui um catálogo descrito em `agents_catalog.json` com personas, papéis e ligações entre agentes.

Arquivos novos em `agentes/` são skeletons padronizados (herdam de `core/agent_base.AgentBase`) e expõem um método `handle(payload)` simples. Use esses arquivos como ponto de partida para implementar a lógica de cada agente.

Também existe um organograma visual em `app/static/agents_organogram.svg` para referência.

Próximos passos sugeridos:
- Implementar a lógica detalhada em cada skeleton.
- Atualizar `core/agent_registry.py` para instanciar e registrar automaticamente agentes em startup.
- Criar testes unitários em `tests/` para cada agente (happy path + 1 edge case).

### Segurança: chaves expostas

Se você colou chaves/segredos neste repositório (ou em qualquer chat público), **assuma que elas estão comprometidas**. Rode os passos em `SECURITY_SETUP.md` para rotacionar e reemitir chaves. Use o script `scripts/add_secrets.sh` para publicar secrets no GitHub/Vercel via CLI (execute localmente e NÃO comite suas chaves).

