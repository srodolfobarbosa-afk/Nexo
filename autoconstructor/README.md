Autoconstructor prototype

Este diretório contém um protótipo mínimo de orquestrador e agent que pode criar PRs automaticamente usando o GitHub API.

Como funciona (seguro por padrão)
- O serviço FastAPI expõe POST /intents com payload que descreve o repo, arquivo e conteúdo a ser alterado.
- Se `GITHUB_TOKEN` NÃO estiver definido, o sistema roda em modo dry-run e não cria branches/PRs.
- Para operar de fato, defina `GITHUB_TOKEN` com permissão para criar branches e PRs.

Exemplo de uso (dry-run):

1) Instale dependências em um venv:

```bash
python -m venv venv
source venv/bin/activate
pip install -r autoconstructor/requirements.txt
```

2) Rode localmente:

```bash
uvicorn autoconstructor.app:app --reload
```

3) Envie um POST para testar:

```bash
curl -X POST http://127.0.0.1:8000/intents -H "Content-Type: application/json" -d '{"repo":"srodolfobarbosa-afk/Nexo","file_path":"test_autopr.md","file_content":"Hello from agent","pr_title":"Test PR from agent"}'
```

Se quiser que o agent crie PRs reais, exporte `GITHUB_TOKEN` no ambiente antes de executar o serviço.

Segurança e próximas etapas
- Não armazene o token em texto puro no repositório.
- Implementar confirmação humana antes de efetivar PRs em produção.
- Adicionar validações de segurança e testes automatizados.

Auto-apply (executar PRs reais)
- O endpoint `/intents` agora aceita um campo `auto_apply` (boolean). Por padrão é `false`.
- Para que o agent efetive mudanças e crie PRs reais, você precisa:
	1) Definir `GITHUB_TOKEN` no ambiente (ou configurar `SECRETS_PROVIDER_URL` e `SECRETS_PROVIDER_TOKEN`).
	2) Enviar `{"auto_apply": true}` no payload do POST `/intents`.

Exemplo mínimo (real - cuidado):

```bash
export GITHUB_TOKEN="ghp_..."
curl -X POST http://127.0.0.1:8000/intents -H "Content-Type: application/json" -d '{"repo":"owner/repo","file_path":"path.txt","file_content":"hi","pr_title":"auto PR","auto_apply":true}'
```

O serviço tentará criar um branch e abrir um PR. Se algo falhar, o serviço retornará o erro.

IMPORTANTE: configure políticas de revisão e proteção antes de permitir merges automáticos.
