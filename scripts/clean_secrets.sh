#!/usr/bin/env bash
set -euo pipefail

# Remove arquivos sensíveis do índice e cria seeds sanitizados localmente.
# Atenção: este script NÃO reescreve o histórico. Para purgar histórico, use git-filter-repo ou BFG (ex: instruções no relatório).

SENSITIVE_FILES=( ".secrets.baseline" ".secrets.current" "nexo_data.db" "memoria_curto_prazo.json" )

echo "Removendo arquivos sensíveis do índice git (sem reescrever histórico)"
for f in "${SENSITIVE_FILES[@]}"; do
  if [ -e "$f" ]; then
    git rm --cached --ignore-unmatch "$f" || true
    echo "Removido do índice: $f"
  else
    echo "Não encontrado: $f"
  fi
done

echo "Adicionando entradas ao .gitignore (se ainda não presentes)"
grep -qxF ".secrets.*" .gitignore || echo ".secrets.*" >> .gitignore
grep -qxF "memoria_curto_prazo.json" .gitignore || echo "memoria_curto_prazo.json" >> .gitignore

echo "Criando seeds sanitizados (se aplicável)"
if [ -f "memoria_curto_prazo.json" ]; then
  cp memoria_curto_prazo.json memoria_curto_prazo.json.bak || true
  jq '(.ciclo, .evolucao) |= (0, {})' memoria_curto_prazo.json.bak > memoria_curto_prazo.json || true
  echo "memoria_curto_prazo.json sanitizado criado"
fi

echo "Commit sugerido: git add .gitignore && git commit -m 'chore: remove arquivos sensíveis do índice e adiciona .gitignore'"

echo "Para PURGAR histórico use: git-filter-repo ou BFG. Consulte o relatório de segurança gerado pelo assistente."
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
