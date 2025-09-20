#!/bin/bash
# Script para atualizar e sincronizar o Nexo no Render

echo "Atualizando dependências..."
pip install -r requirements.txt

echo "Sincronizando variáveis de ambiente..."
if [ -f .env ]; then
  cp .env /etc/environment
  echo "Variáveis de ambiente copiadas para /etc/environment."
else
  echo "Arquivo .env não encontrado! Configure antes de prosseguir."
fi

echo "Realizando pull do repositório..."
git pull origin main

echo "Reiniciando aplicação..."
# Comando padrão para Flask, ajuste conforme seu servidor
export FLASK_APP=nexo.py
flask run --host=0.0.0.0 --port=5000

echo "Nexo atualizado e rodando no Render!"
