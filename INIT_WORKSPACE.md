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
