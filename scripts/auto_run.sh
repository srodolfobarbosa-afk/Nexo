#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

echo "[nexo] Iniciando auto-run"

# 1) Cria virtualenv se não existir
if [ ! -d ".venv" ]; then
  echo "Criando virtualenv .venv..."
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2) Atualiza pip e instala dependências
echo "Instalando dependências..."
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# 3) Rodar testes rápidos
if command -v pytest >/dev/null 2>&1; then
  echo "Executando testes (pytest -q)..."
  # Garantir que o PYTHONPATH inclui o root do repositório para import local
  export PYTHONPATH="$ROOT_DIR":${PYTHONPATH-}
  PYTHONPATH="$ROOT_DIR" pytest -q || {
    echo "Alguns testes falharam; reveja os logs e corrija antes de prosseguir."
    # Continuar mesmo se falhar para facilitar dev iteration
  }
else
  echo "pytest não encontrado; pulando etapa de testes"
fi

# 4) Preparar .env
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "Arquivo .env não encontrado — copiando .env.example -> .env (preencha valores sensíveis)"
    cp .env.example .env
  else
    echo "Arquivo .env.example ausente; crie um .env manualmente antes de rodar em produção."
  fi
fi

# 5) Iniciar o sistema integrado (run_integrated_system.py) e redirecionar logs
LOG_DIR=logs
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/integrated.log"

echo "Iniciando run_integrated_system.py (logs em $LOG_FILE)"
nohup python3 run_integrated_system.py > "$LOG_FILE" 2>&1 &
PID=$!
echo "Sistema iniciado com PID $PID"
echo "Para ver logs: tail -f $LOG_FILE"
