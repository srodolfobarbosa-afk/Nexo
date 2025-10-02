#!/usr/bin/env bash
set -euo pipefail

# Script de start para Replit
# - cria/ativa .venv
# - instala dependências listadas em requirements.txt (não-fatal)
# - inicia gunicorn servindo src.main:app na porta $PORT (default 5000)

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_DIR="$ROOT_DIR"/.venv
PYTHON=${VIRTUAL_ENV:-"$VENV_DIR/bin/python"}

export PORT=${PORT:-5000}

echo "[replit] Iniciando Nexo no Replit (porta $PORT)"

# Criar virtualenv se não existir
if [ ! -d "$VENV_DIR" ]; then
  echo "[replit] Criando virtualenv em $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "[replit] pip --version: $(pip --version)"

# Instalar dependências (não-fatal: continua se falhar)
if [ -f requirements.txt ]; then
  echo "[replit] Instalando dependências (isso pode demorar)..."
  pip install --upgrade pip setuptools wheel || true
  pip install -r requirements.txt || true
else
  echo "[replit] requirements.txt não encontrado, pulando instalação"
fi

# Ajustes e variáveis úteis
export FLASK_ENV=production

echo "[replit] Iniciando gunicorn (1 worker) para servir src.main:app"
# Usamos bind 0.0.0.0:$PORT para Replit
exec gunicorn "src.main:app" --bind "0.0.0.0:$PORT" --workers 1 --threads 2 --timeout 120
#!/usr/bin/env bash
set -euo pipefail

# Script de start específico para Replit
# - cria um virtualenv simples
# - instala dependências mínimas listadas em requirements.txt
# - exporta variáveis de ambiente de exemplo (o usuário deve editar .env no Replit)
# - inicia o servidor Flask via gunicorn para processar o app em src.main

# Criar venv local
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências (silencioso para Replit)
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi

# Carregar .env se existir
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

# Garantir PORT para Replit
: "${PORT:=5000}"
export PORT

# Comando padrão: rodar gunicorn apontando para o app em src.main
# Use 1 worker para evitar problemas de memória/CPU no Replit gratuito
exec gunicorn "src.main:app" --bind "0.0.0.0:${PORT}" --workers 1 --threads 4
