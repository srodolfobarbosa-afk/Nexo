#!/usr/bin/env bash
# Inicializador automático do workspace Nexo
# Uso:
#  ./init_workspace.sh         -> dry-run (cria venv e gera requirements_clean.txt)
#  ./init_workspace.sh --install -> executa a instalação completa das dependências

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQ_FILE="$ROOT_DIR/requirements.txt"
CLEAN_REQ="$ROOT_DIR/requirements_clean.txt"

INSTALL=false
for arg in "$@"; do
  case "$arg" in
    --install) INSTALL=true ;;
    --help) echo "Uso: $0 [--install]"; exit 0 ;;
  esac
done

echo "[nexo-init] Diretório do projeto: $ROOT_DIR"

if [ ! -f "$REQ_FILE" ]; then
  echo "[nexo-init] Não encontrei $REQ_FILE. Abortando." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[nexo-init] Criando virtualenv em $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
else
  echo "[nexo-init] Virtualenv já existe em $VENV_DIR"
fi

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

echo "[nexo-init] Atualizando pip/setuptools/wheel no venv..."
"$PY" -m pip install --upgrade pip setuptools wheel >/dev/null

echo "[nexo-init] Gerando $CLEAN_REQ (resolvendo conflitos automáticos comuns)..."
"$PY" - <<'PY'
import re
from pathlib import Path
root = Path(".").resolve()
req = root / 'requirements.txt'
out = root / 'requirements_clean.txt'
lines = []
if not req.exists():
    raise SystemExit(f'requirements.txt não encontrado em {root}')
raw = req.read_text(encoding='utf-8').splitlines()

# Heurística simples para resolver conflitos de uvicorn:
# - Se existir uma linha com 'uvicorn>=' e também uma linha com 'uvicorn[standard]==',
#   substituímos a linha fixada por uma faixa compatível 'uvicorn[standard]>=0.23,<1'
# - Removemos duplicatas exatas (mantendo a primeira ocorrência)
seen = set()
has_uv_ge = any(re.match(r'\s*uvicorn\s*(?:\[standard\])?\s*>?=', l) for l in raw)

for l in raw:
    s = l.strip()
    if not s or s.startswith('#'):
        lines.append(l)
        continue
    key = s
    # normalize uvicorn[standard]==0.22.0 or uvicorn==0.22.0
    if re.match(r"^uvicorn(?:\[standard\])?==", s) and has_uv_ge:
        # replace pinned uvicorn with a safer range
        repl = 'uvicorn[standard]>=0.23,<1'
        if repl not in seen:
            lines.append(repl)
            seen.add(repl)
        continue
    if s in seen:
        continue
    lines.append(l)
    seen.add(s)

out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Gerado: {out}')
PY

echo "[nexo-init] Arquivo $CLEAN_REQ criado. (modo dry-run concluído)"

if [ "$INSTALL" = true ]; then
  echo "[nexo-init] Iniciando instalação das dependências com $PIP (isso pode demorar)..."
  "$PIP" install -r "$CLEAN_REQ"
  if [ -f "$ROOT_DIR/requirements_dev.txt" ]; then
    echo "[nexo-init] Instalando dependências de desenvolvimento..."
    "$PIP" install -r "$ROOT_DIR/requirements_dev.txt"
  fi

  # Instalar o pacote local (se houver pyproject/setup)
  if [ -f "$ROOT_DIR/pyproject.toml" ] || [ -f "$ROOT_DIR/setup.py" ]; then
    echo "[nexo-init] Instalando pacote local (editable)..."
    "$PIP" install -e .
  fi

  echo "[nexo-init] Instalação concluída. Considere executar scripts de inicialização adicionais (ex.: scripts/init_db.py)."
else
  cat <<MSG

[nexo-init] Modo dry-run: não instalei pacotes por padrão.
Para instalar as dependências, reexecute com:

  ./init_workspace.sh --install

Isso criará o venv, instalará as dependências e o pacote local (se aplicável).

MSG
fi

echo "[nexo-init] Fim."
