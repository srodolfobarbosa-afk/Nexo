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
