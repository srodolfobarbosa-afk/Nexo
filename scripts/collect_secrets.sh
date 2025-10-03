#!/usr/bin/env bash
set -euo pipefail

echo "Este script coleta segredos localmente e escreve no arquivo .env (NÃO será comitado)."
echo "Digite os valores solicitados. Para valores secretos, eles não serão exibidos enquanto você digita."

OUTFILE=".env"
if [ -f "$OUTFILE" ]; then
  echo ".env já existe. Deseja sobrescrever? [y/N]"
  read -r CONF
  if [[ ! "$CONF" =~ ^[Yy]$ ]]; then
    echo "Abortando. Nenhuma alteração foi feita."
    exit 0
  fi
fi

read -p "SUPABASE_URL: " SUPABASE_URL
read -s -p "SUPABASE_KEY (hidden): " SUPABASE_KEY
echo
read -s -p "OPENAI_API_KEY (hidden, press enter if none): " OPENAI_API_KEY
echo
read -s -p "GEMINI_API_KEY (hidden, press enter if none): " GEMINI_API_KEY
echo
read -s -p "HUGGINGFACE_API_KEY (hidden, press enter if none): " HUGGINGFACE_API_KEY
echo
read -p "GOOGLE_API_KEY (press enter if none): " GOOGLE_API_KEY
read -p "GOOGLE_SEARCH_API_KEY (press enter if none): " GOOGLE_SEARCH_API_KEY
read -p "GOOGLE_CSE_ID (press enter if none): " GOOGLE_CSE_ID
read -s -p "VERCEL_TOKEN (hidden, press enter if none): " VERCEL_TOKEN
echo
read -s -p "GITHUB_TOKEN / PAT (hidden, press enter if none): " GITHUB_TOKEN
echo
read -s -p "SECRET_KEY (hidden, press enter if none): " SECRET_KEY
echo
read -p "NEXO_LLM_PROVIDER (ex: google|openai): " NEXO_LLM_PROVIDER
read -s -p "GROQ_API_KEY (hidden, press enter if none): " GROQ_API_KEY
echo

cat > "$OUTFILE" <<EOF
# Auto-generated .env (created by scripts/collect_secrets.sh)
SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_KEY="${SUPABASE_KEY}"
OPENAI_API_KEY="${OPENAI_API_KEY}"
GEMINI_API_KEY="${GEMINI_API_KEY}"
HUGGINGFACE_API_KEY="${HUGGINGFACE_API_KEY}"
GOOGLE_API_KEY="${GOOGLE_API_KEY}"
GOOGLE_SEARCH_API_KEY="${GOOGLE_SEARCH_API_KEY}"
GOOGLE_CSE_ID="${GOOGLE_CSE_ID}"
VERCEL_TOKEN="${VERCEL_TOKEN}"
GITHUB_TOKEN="${GITHUB_TOKEN}"
SECRET_KEY="${SECRET_KEY}"
NEXO_LLM_PROVIDER="${NEXO_LLM_PROVIDER}"
GROQ_API_KEY="${GROQ_API_KEY}"

START_MISSION_RUNNER=1
MISSION_INTERVAL=6
EOF

chmod 600 "$OUTFILE" || true
echo ".env criado/atualizado com sucesso. Verifique o arquivo e não o comite."
