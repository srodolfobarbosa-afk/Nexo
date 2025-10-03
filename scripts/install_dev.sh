#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

if [ ! -d .venv ]; then
  echo "Criando virtualenv .venv..."
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "Atualizando pip e instalando dependências de desenvolvimento..."
python -m pip install --upgrade pip
pip install -r requirements_dev.txt

echo "Instalação de desenvolvimento concluída. Ative o venv com: source .venv/bin/activate"
