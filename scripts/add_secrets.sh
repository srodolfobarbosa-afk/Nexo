#!/usr/bin/env bash
set -euo pipefail

# Este script lê variáveis de ambiente locais e as publica como secrets
# no GitHub e no Vercel via CLI. Execute localmente após exportar as variáveis.

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI não encontrado. Instale: https://cli.github.com/"
  exit 1
fi

if ! command -v vercel >/dev/null 2>&1; then
  echo "vercel CLI não encontrado. Instale: https://vercel.com/docs/cli"
  exit 1
fi

set -x

# GitHub secrets (repo)
gh secret set SUPABASE_URL --body "$SUPABASE_URL" || true
gh secret set SUPABASE_KEY --body "$SUPABASE_KEY" || true
gh secret set OPENAI_API_KEY --body "$OPENAI_API_KEY" || true
gh secret set GEMINI_API_KEY --body "$GEMINI_API_KEY" || true
gh secret set VERCEL_TOKEN --body "$VERCEL_TOKEN" || true

# Vercel env (production)
vercel env add SUPABASE_URL production <<< "$SUPABASE_URL" || true
vercel env add SUPABASE_KEY production <<< "$SUPABASE_KEY" || true
vercel env add OPENAI_API_KEY production <<< "$OPENAI_API_KEY" || true
vercel env add GEMINI_API_KEY production <<< "$GEMINI_API_KEY" || true

echo "Secrets enviados (verifique output para confirmar)."
