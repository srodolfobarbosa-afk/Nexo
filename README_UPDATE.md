Atualização do Projeto Nexo — Guia rápido
=========================================

Este documento descreve como configurar, executar e fazer deploy do projeto Nexo
em um ambiente de desenvolvimento e produção.

1) Requisitos mínimos
- Python 3.11+ (recomendado 3.12)
- Git
- Acesso a um projeto Supabase (opcional para persistência/produção)

2) Preparar ambiente local (dev)
- Copie o template de variáveis de ambiente e edite os valores sensíveis:

  cp .env.example .env
  # Edite .env e coloque suas chaves (NUNCA comite .env)

- Crie e ative um virtualenv e instale dependências:

  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt

3) Execução rápida (dev)
- Testes unitários:

  export PYTHONPATH=$(pwd)
  pytest -q

- Rodar o sistema integrado em background (script que automatiza venv/install/tests/start):

  ./scripts/auto_run.sh

  Depois veja logs em `logs/integrated.log`:

  tail -f logs/integrated.log

4) Variáveis de ambiente importantes
- TELEGRAM_BOT_TOKEN — token do bot Telegram (dev/prod)
- SUPABASE_URL, SUPABASE_KEY — credenciais Supabase (se usar Supabase)
- JWT_SECRET — segredo forte para tokens JWT (NÃO usar valor padrão)

Observação de segurança: se `JWT_SECRET` estiver ausente ou com o valor padrão placeholder, o processo de inicialização irá falhar com uma mensagem clara. Configure um segredo robusto em produção.

5) Banco/Supabase
- Há um arquivo `supabase_schema.sql` com esquema sugerido. Para produção, aplique o SQL no seu projeto Supabase. Alguns testes/integrations assumem que certas tabelas existem (tasks, agent_logs, evolution_attempts, etc.).

6) Deploy (Render / Heroku / Docker)
- O `Dockerfile` e `Procfile` existem como exemplos. Em plataformas como Render, defina variáveis de ambiente seguras (incl. JWT_SECRET) e configure a porta conforme o provedor.
- Em Render, defina a porta via variável `PORT` e o comando de startup padrão já presente no `Procfile`/`start.sh`.

7) Troubleshooting rápido
- Erros de schema Supabase: verifique `supabase_schema.sql` e aplique no projeto Supabase (ou pule testes de integração configurando as variáveis).
- Dependências pesadas (torch/playwright): para desenvolvimento rápido use um `requirements_dev.txt` mais enxuto (opção futura).

8) Próximos passos sugeridos
- Criar `requirements_dev.txt` para desenvolvimento leve
- Adicionar CI (GitHub Actions) com testes e linter
- Criar script/rotina automática para aplicar `supabase_schema.sql` com confirmação interativa

Se quiser que eu implemente algum dos próximos passos, escolha um e eu implemento (uma opção por vez).
## Integração Render (Cloud)

Para usar o CloudManager, defina as variáveis de ambiente:

- RENDER_API_KEY: Token de acesso à API do Render
- RENDER_SERVICE_ID: ID do serviço Render

Endpoints usados:
- GET https://api.render.com/v1/services/{service_id} (status)
- POST https://api.render.com/v1/services/{service_id}/restart (reiniciar)
- POST https://api.render.com/v1/services/{service_id}/deploy (deploy nova imagem)
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
