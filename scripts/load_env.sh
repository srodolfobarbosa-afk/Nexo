#!/usr/bin/env bash
set -euo pipefail

# Carrega .env no ambiente atual (execução local)
if [ ! -f .env ]; then
  echo ".env não encontrado. Copie .env.example para .env e preencha os valores."
  exit 1
fi

export $(grep -v '^#' .env | xargs)
echo "Variáveis de ambiente carregadas no shell atual (subprocesso)." 
