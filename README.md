# Nexo — sistema de agentes orquestradores

Este repositório contém o projeto Nexo: conjunto de agentes autônomos e ferramentas de orquestração.

## Resumo rápido — o que fiz nesta iteração:
- Corrigi imports que impediam a suíte de testes de rodar.
- Adicionei etapas de lint/format, Dockerfile multistage e docker-compose para desenvolvimento.

## Instruções de Configuração, Instalação e Execução

### 1) Requisitos mínimos
- Python 3.11+ (recomendado 3.12)
- Git
- Acesso a um projeto Supabase (opcional para persistência/produção)

### 2) Preparar ambiente local (desenvolvimento)
- Copie o template de variáveis de ambiente e edite os valores sensíveis:

  ```bash
  cp .env.example .env
  # Edite .env e coloque suas chaves (NUNCA comite .env)
  ```

- Crie e ative um virtualenv e instale dependências:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

### 3) Principais comandos locais e execução rápida (desenvolvimento)

- **Instalar dependências de desenvolvimento** (recomendado em um virtualenv):

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements_dev.txt
  ```

- **Rodar testes**:

  ```bash
  export PYTHONPATH=$(pwd)
  pytest -q
  ```

- **Inicializar banco local (SQLite) e seed mínimo**:

  ```bash
  python scripts/init_db.py
  ```

- **Rodar localmente com docker-compose**:

  ```bash
  # Build e up (development)
  docker-compose up --build
  ```

- **Build Docker standalone**:

  ```bash
  docker build -t nexo:latest .
  ```

- **Rodar o sistema integrado em background** (script que automatiza venv/install/tests/start):

  ```bash
  ./scripts/auto_run.sh
  ```

  Depois veja logs em `logs/integrated.log`:

  ```bash
  tail -f logs/integrated.log
  ```

### 4) Variáveis de ambiente importantes
- `TELEGRAM_BOT_TOKEN` — token do bot Telegram (dev/prod)
- `SUPABASE_URL`, `SUPABASE_KEY` — credenciais Supabase (se usar Supabase)
- `JWT_SECRET` — segredo forte para tokens JWT (NÃO usar valor padrão)

**Observação de segurança**: se `JWT_SECRET` estiver ausente ou com o valor padrão placeholder, o processo de inicialização irá falhar com uma mensagem clara. Configure um segredo robusto em produção.

### 5) Banco/Supabase
- Há um arquivo `supabase_schema.sql` com esquema sugerido. Para produção, aplique o SQL no seu projeto Supabase. Alguns testes/integrações assumem que certas tabelas existem (tasks, agent_logs, evolution_attempts, etc.).

### 6) Deploy (Render / Heroku / Docker)
- O `Dockerfile` e `Procfile` existem como exemplos. Em plataformas como Render, defina variáveis de ambiente seguras (incl. `JWT_SECRET`) e configure a porta conforme o provedor.
- Em Render, defina a porta via variável `PORT` e o comando de startup padrão já presente no `Procfile`/`start.sh`.

### 7) Troubleshooting rápido
- Erros de schema Supabase: verifique `supabase_schema.sql` e aplique no projeto Supabase (ou pule testes de integração configurando as variáveis).
- Dependências pesadas (torch/playwright): para desenvolvimento rápido use um `requirements_dev.txt` mais enxuto (opção futura).

### 8) Próximos passos sugeridos
- Criar `requirements_dev.txt` para desenvolvimento leve
- Adicionar CI (GitHub Actions) com testes e linter
- Criar script/rotina automática para aplicar `supabase_schema.sql` com confirmação interativa

## Integração Render (Cloud)

Para usar o CloudManager, defina as variáveis de ambiente:

- `RENDER_API_KEY`: Token de acesso à API do Render
- `RENDER_SERVICE_ID`: ID do serviço Render

Endpoints usados:
- `GET https://api.render.com/v1/services/{service_id}` (status)
- `POST https://api.render.com/v1/services/{service_id}/restart` (reiniciar)
- `POST https://api.render.com/v1/services/{service_id}/deploy` (deploy nova imagem)

## SQL para criar tabela evolution_attempts no Supabase

```sql
CREATE TABLE evolution_attempts (
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	timestamp TEXT,
	cycle_number INTEGER,
	mission_prompt TEXT,
	llm_response_raw TEXT,
	success BOOLEAN,
	reason_for_failure TEXT,
	details TEXT
);
```

# EcoGuardians - Centro de Comando de Agentes de IA

## Funcionalidades

- **Monitor visual dividido em 3 partes:** exibe resultados dos agentes em tempo real (imagens, gráficos, status, etc).
- **Status dos agentes:** cartões com nome, status, CPU/RAM, tarefas/hora e ações rápidas.
- **Dashboard financeiro:** gráficos dinâmicos de receita, despesa e ROI.
- **Histórico de falhas e sucessos:** filtragem avançada por nível, agente e tipo, destaques visuais e download de logs.
- **Mapa de orquestração de tarefas:** visualização do fluxo de trabalho dos agentes.
- **Gerenciamento de API Keys:** adicionar, revogar e visualizar chaves diretamente pelo painel.

## Como rodar localmente

1. Instale as dependências:
	```bash
	pip install flask flask-sock psutil
	```
2. Execute o backend WebSocket:
	```bash
	python3 src/ws_server.py
	```
3. Acesse a interface em [http://localhost:8000](http://localhost:8000)

## CI/CD
- O projeto possui workflow automatizado para lint, testes e deploy no Render.
- Todas as mudanças são versionadas e documentadas.

## Estrutura recomendada
- `app/static/index.html` — Interface principal
- `app/static/script.js` — Lógica dinâmica do frontend
- `src/ws_server.py` — Backend WebSocket
- `.env` — Chaves de API e configurações

## Observações
- O painel é proativo: qualquer agente pode enviar visualizações para o monitor.
- Logs, status, financeiro e tarefas são atualizados em tempo real.
- API Keys são gerenciadas de forma segura e flexível.

## Segurança e Variáveis de Ambiente

- **Nunca comite chaves ou segredos diretamente no repositório.** Utilize arquivos `.env` para desenvolvimento local (que devem ser ignorados pelo Git) e configure secrets no GitHub Actions ou no seu provedor de deploy (como Render) para ambientes de CI/CD e produção.
- **Rotação de Chaves**: Se houver suspeita de comprometimento de chaves, siga os passos em `SECURITY_SETUP.md` para rotacioná-las e reemití-las. Utilize o script `scripts/add_secrets.sh` para gerenciar secrets de forma segura.

### Supabase Auth (recomendado para produção)

1. Crie um projeto Supabase e habilite a autenticação (OAuth2 / email).
2. Adicione `SUPABASE_URL` e `SUPABASE_KEY` como secrets no seu ambiente de deploy (Render / GitHub Secrets).
3. Defina `USE_SUPABASE_AUTH=1` no seu ambiente para forçar a aplicação a validar JWTs via Supabase JWKS.
4. **IMPORTANTE**: Defina um `JWT_SECRET` forte para qualquer token HS256 de fallback e **nunca o comite**.

Quando `USE_SUPABASE_AUTH=1`, a rota de desenvolvimento `/auth/token` é desabilitada e o serviço verificará tokens RS256 publicados pelo Supabase.

### Docker e Segurança

- **Build da imagem Docker** (exemplo):

  ```bash
  docker build -t nexo:latest .
  ```

- **Execução em desenvolvimento**:

  ```bash
  docker run --env-file .env -p 8000:8000 nexo:latest
  ```

- **CI/CD**: O GitHub Actions executa testes e uma varredura de secrets. Certifique-se de rotacionar quaisquer chaves comprometidas antes de fazer push.

## Catálogo de Agentes

Este repositório agora inclui um catálogo descrito em `agents_catalog.json` com personas, papéis e ligações entre agentes.

Arquivos novos em `agentes/` são skeletons padronizados (herdam de `core/agent_base.AgentBase`) e expõem um método `handle(payload)` simples. Use esses arquivos como ponto de partida para implementar a lógica de cada agente.

Também existe um organograma visual em `app/static/agents_organogram.svg` para referência.

Próximos passos sugeridos:
- Implementar a lógica detalhada em cada skeleton.
- Atualizar `core/agent_registry.py` para instanciar e registrar automaticamente agentes em startup.
- Criar testes unitários em `tests/` para cada agente (happy path + 1 edge case).

