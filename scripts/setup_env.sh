#!/usr/bin/env bash
# Script mínimo para instalar dependências do projeto em um ambiente Debian/Ubuntu
set -euo pipefail

echo "Atualizando apt e instalando dependências do sistema..."
sudo apt-get update -y
sudo apt-get install -y build-essential python3-dev python3-venv git curl

echo "Criando venv..."
python3 -m venv .venv
source .venv/bin/activate

echo "Atualizando pip e instalando dependências do requirements.txt"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Instalação concluída. Ative o venv com: source .venv/bin/activate"
