# Atualização do Projeto Nexo

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

## Rodando no Replit

Passos rápidos para colocar o projeto no Replit:

1. Crie um novo repl a partir do repositório GitHub: https://github.com/srodolfobarbosa-afk/Nexo
2. No Replit, abra o arquivo `.replit` (já presente neste repositório) e garanta que o comando de execução seja `bash run_replit.sh`.
3. Crie um arquivo `.env` na raiz do repl com as variáveis necessárias (ex: `PORT=5000`, `TELEGRAM_BOT_TOKEN=seu_token`, `SUPABASE_URL=...`, `SUPABASE_KEY=...`).
4. Clique em Run. O Replit irá criar o virtualenv, instalar dependências (pode demorar) e iniciar o Gunicorn servindo `src.main:app`.

Notas:
- Se você prefere desenvolvimento sem Gunicorn, altere `run_replit.sh` para executar `python3 src/main.py`.
- Replit tem limites de CPU/memória; use poucos workers/threads no Gunicorn (o script padrão usa 1 worker).
- Para rodar o WebSocket (`src/ws_server.py`) em paralelo no Replit pode ser necessário criar outro repl ou adaptar o processo para múltiplas threads — o Replit tradicional roda apenas um processo web por repl.

Se você já tem uma instância rodando (ex.: https://nexo-kh57.onrender.com), pode apontar serviços externos para essa URL durante testes.

Exemplo mínimo de `.env` para rodar no Replit (NÃO coloque chaves reais em repositórios públicos):

```
PORT=5000
TELEGRAM_BOT_TOKEN=seu_token_aqui
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=pk.XXXXXXXXXXXXXXXX
USE_SUPABASE_AUTH=0
```

Se ocorrerem erros durante a instalação de dependências pesadas (faiss, playwright, modelos grandes), considere:

- Comentar linhas problemáticas em `requirements.txt` temporariamente
- Usar a opção de desenvolvimento: executar `python3 src/main.py` ao invés de gunicorn para evitar problemas de instalação
- Dar boot apenas na API mínima (`src/main.py`) e conectar o bot/serviços externos a essa URL

Problemas comuns no Replit:

- Timeouts de build (instalação de dependências demoradas) — use `pip install -r requirements.txt || true` no script de start (já aplicado)
- Falta de libs de sistema (ex: faiss precisa de compilação) — remova temporariamente ou use dependências pré-compiladas

## Ativando Auto-Construção / Auto-Evolução (autonomia)

O Nexo inclui um loop de "auto-evolution" que pode executar ciclos periódicos de estudo, auto-construção de ferramentas e evolução de agentes.
Ative com cautela — isso dá autonomia ao sistema e pode executar commits ou deploys se configurado.

Variáveis de ambiente relevantes:

- `START_AUTO_EVOLUTION=1` ou `START_AUTO_CONSTRUCTION=1` — inicia o loop `auto_evolution_loop` em background no processo web.
- `AUTO_CONSTRUCTION_ALLOW_DEPLOY=1` — (não implementa automaticamente commits) flag sugerida para permitir que o AutoConstructionModule realize deploys automáticos; use apenas em ambientes controlados.

Para habilitar no Replit/Render, adicione no seu `.env` ou nas variáveis de ambiente do serviço:

```
START_AUTO_EVOLUTION=1
AUTO_CONSTRUCTION_ALLOW_DEPLOY=0
```

Use `AUTO_CONSTRUCTION_ALLOW_DEPLOY=1` somente após revisões manuais e com chaves de GitHub/Deploy seguras.

### Revisando e aplicando staged builds

Quando o sistema gera mudanças em modo STAGING, os artefatos são salvos em `autoconstruct_staging/<staged_id>/`.

1. Liste builds staged via endpoint (rodando localmente):

```
curl http://127.0.0.1:5000/admin/staged_builds
```

2. Revise o diretório `autoconstruct_staging/<staged_id>/` e cheque `meta.json`.

3. Para aplicar um staged build (copiar arquivos para o repositório e opcionalmente commitar), execute:

```
curl -X POST "http://127.0.0.1:5000/admin/apply_staged/<staged_id>" -H "X-ADMIN-TOKEN: $ADMIN_DEPLOY_TOKEN"
```

Certifique-se de setar `ADMIN_DEPLOY_TOKEN` no ambiente (ou em `secrets` no GitHub Actions) antes de aplicar.

### Configurar GitHub Actions secrets

- `GITHUB_TOKEN` — já disponibilizado automaticamente em Actions; usado para criar PRs.
- `ADMIN_DEPLOY_TOKEN` — token simples para proteger o endpoint admin; configure em Settings > Secrets no GitHub.




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

