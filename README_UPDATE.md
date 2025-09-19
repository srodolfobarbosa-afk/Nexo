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
# Atualização do Projeto Nexo

## Passo 1: Configurar o ambiente
Copie o arquivo `.env.example` para `.env` e preencha suas chaves reais.

```bash
cp .env.example .env
nano .env
```

## Passo 2: Instalar dependências
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Passo 3: Rodar localmente
```bash
bash start.sh
```

## Passo 4: Testar
```bash
pytest tests/
```

## Passo 5: Deploy Automático
- O GitHub Actions (`.github/workflows/auto-deploy.yml`) já está configurado.
- A cada `git push` na branch `main`, os testes serão executados e o deploy preparado.
