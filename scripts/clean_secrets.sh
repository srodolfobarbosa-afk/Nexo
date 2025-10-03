#!/usr/bin/env bash
# Script para detectar ocorrências óbvias de segredos em arquivos do repositório
# NÃO reescreve o histórico automaticamente - apenas detecta e reporta

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
cd "$ROOT"

echo "Procurando por padrões de chaves no repositório..."

# padrões simples — adapte conforme necessário
GREP_PATTERN='AIza|sk-|eyJ|gsk_|SUPABASE_KEY|OPENAI_API_KEY|GEMINI_API_KEY|GOOGLE_API_KEY|SECRET_KEY'

git grep -n --exclude-dir=.git -e "$GREP_PATTERN" || echo "Nenhuma correspondência óbvia encontrada com padrão simples."

echo "Listagem de arquivos que contêm 'SUPABASE_KEY' (exemplo):"
git grep -l "SUPABASE_KEY" || true

echo "Recomendações:
 - Revogue as chaves expostas imediatamente
 - Reescreva o histórico (git filter-repo ou BFG) se as chaves foram commitadas
 - Substitua por GitHub Secrets e adicione um .env.example sem valores" 

exit 0
