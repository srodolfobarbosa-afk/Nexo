# Inicialização automática do workspace Nexo

Este projeto inclui um script conveniente `init_workspace.sh` que cria um virtualenv, gera um arquivo `requirements_clean.txt` com heurísticas simples para resolver conflitos e, opcionalmente, instala as dependências.

Passos rápidos

1. Em um terminal na raiz do projeto, torne o script executável (apenas 1 vez):

   chmod +x init_workspace.sh

2. Rodar em modo "dry-run" (cria o .venv e gera `requirements_clean.txt`):

   ./init_workspace.sh

3. Para realmente instalar as dependências dentro do venv:

   ./init_workspace.sh --install

Observações

- O script não força upgrades em pacotes do sistema. Se o pip falhar devido a dependências do sistema (por exemplo: build de wheels), instale os pacotes do SO necessários (gcc, build-essential, libpq-dev, etc.).
- Após a instalação, crie seu `.env` a partir de `.env.example` e preencha segredos.
- Para inicializar o banco ou dados de seed: verifique `scripts/init_db.py` (se existir) ou consulte README.

Próximos passos sugeridos (opcionais)

- Adicionar um `Makefile` target `init` que chame `./init_workspace.sh --install`.
- Configurar integração com Docker para evitar problemas de build local de dependências pesadas.

## Deploy para Render

O repositório inclui um workflow GitHub Actions (`.github/workflows/render-deploy.yml`) que tenta disparar um deploy no Render quando houver push para a branch `main`.

Passos mínimos para habilitar:

- Ative a integração GitHub no painel do Render (recomendado). Assim, pushs para a branch configurada disparam deploys automaticamente.
- Ou configure os GitHub Secrets abaixo para permitir que o workflow chame a API do Render:
   - `RENDER_SERVICE_ID` — ID do serviço no Render (ex: srv-abcde12345)
   - `RENDER_API_TOKEN` — API token do Render com permissões de deploy

Com os secrets configurados, o workflow fará um POST para `https://api.render.com/v1/services/{service_id}/deploys` para iniciar o deploy.

Nota: o `render.yaml` no repositório contém a configuração esperada pelo Render. Em ambientes com dependências pesadas (PyTorch, triton, sentence-transformers), prefira usar `requirements_prod.txt` no seu build para imagens menores.
