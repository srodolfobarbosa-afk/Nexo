Nexo — sistema de agentes orquestradores

Este repositório contém o projeto Nexo: conjunto de agentes autônomos e ferramentas de orquestração.

Resumo rápido — o que fiz nesta iteração:
- Corrigi imports que impediam a suíte de testes de rodar.
- Adicionei etapas de lint/format, Dockerfile multistage e docker-compose para desenvolvimento.

Principais comandos locais

1. Instalar dependências de desenvolvimento (recomendado em um virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements_dev.txt
```

2. Rodar testes:

```bash
pytest -q
```

5. Inicializar banco local (SQLite) e seed mínimo:

```bash
python scripts/init_db.py
```

3. Rodar localmente com docker-compose:

```bash
# Build e up (development)
docker-compose up --build
```

4. Build Docker standalone:

```bash
docker build -t nexo:latest .
```

Notas de deploy

- Existe workflow GitHub Actions básico em `.github/workflows/consolidated-ci.yml` que roda lint → tests → build.
- Deploy para Render está disponível via secrets `RENDER_SERVICE_ID` e `RENDER_API_KEY`.

Segurança e variáveis de ambiente

- Nunca comite chaves. Use `.env` localmente e configure secrets no GitHub para CI/CD.

Problemas pendentes

- Alguns módulos assumem dependências pesadas em tempo de import. Refatorei os pontos críticos para lazy-imports nos agentes essenciais.
- Recomendado revisar `requirements.txt` de produção (algumas bibliotecas do manifesto são apenas opcionais).

Para detalhes completos do que foi alterado, consulte o CHANGELOG.md e os commits no repositório.

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

