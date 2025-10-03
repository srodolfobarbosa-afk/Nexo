#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

if [ ! -f supabase_schema.sql ]; then
  echo "Arquivo supabase_schema.sql não encontrado no repositório."
  exit 1
fi

if command -v supabase >/dev/null 2>&1; then
  echo "Usando supabase CLI para aplicar schema..."
  # Esta operação exige que o usuário já esteja autenticado via supabase login
  supabase db remote set $SUPABASE_URL --project-ref ${SUPABASE_PROJECT:-}
  supabase db query < supabase_schema.sql
  echo "Schema aplicado via supabase CLI."
  exit 0
fi

if [ -n "${SUPABASE_URL-}" ] && [ -n "${SUPABASE_KEY-}" ]; then
  echo "Tentando aplicar schema via psql (requer que SUPABASE_URL seja um connection string compatível)."
  # Supabase fornece normalmente uma URL REST; para psql, recomendamos o uso da connection string PG
  if [ -z "${PG_CONNECTION_STRING-}" ]; then
    echo "Aviso: PG_CONNECTION_STRING não definido. Configure para usar psql com o banco Supabase." >&2
    exit 1
  fi
  psql "$PG_CONNECTION_STRING" -f supabase_schema.sql
  echo "Schema aplicado via psql."
  exit 0
fi

echo "Nenhuma ferramenta disponível para aplicar o schema. Instale supabase CLI ou defina PG_CONNECTION_STRING e psql." >&2
exit 2
