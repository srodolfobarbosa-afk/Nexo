#!/usr/bin/env python3
"""
Ferramenta simples para armazenar segredos localmente de forma criptografada.

Requisitos: `pip install cryptography`

Como funciona:
- Você define uma `MASTER_KEY` via variável de ambiente (ex: `export MASTER_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")`).
- O arquivo criptografado ficará em `.secrets.json.enc` na raiz do repositório (não comitar).
- Use `set`, `get`, `list`, `delete` para manipular segredos.

Aviso de segurança:
- Este é um utilitário local. Para produção, use o gerenciador de segredos da sua hospedagem (Render secrets, AWS Secrets Manager, Vault).
"""
import os
import sys
import json
from pathlib import Path

try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None

ROOT = Path(__file__).resolve().parents[1]
SECRETS_PATH = ROOT / '.secrets.json.enc'

def require_master_key():
    key = os.environ.get('MASTER_KEY')
    if not key:
        print('Erro: defina a variável de ambiente MASTER_KEY antes de usar (veja README).')
        sys.exit(2)
    return key.encode() if isinstance(key, str) else key

def load_secrets(master_key):
    if not SECRETS_PATH.exists():
        return {}
    if Fernet is None:
        print('cryptography não instalado; instale com: pip install cryptography')
        sys.exit(3)
    f = Fernet(master_key)
    data = f.decrypt(SECRETS_PATH.read_bytes())
    return json.loads(data.decode('utf-8'))

def save_secrets(master_key, data):
    if Fernet is None:
        print('cryptography não instalado; instale com: pip install cryptography')
        sys.exit(3)
    f = Fernet(master_key)
    blob = json.dumps(data, indent=2).encode('utf-8')
    SECRETS_PATH.write_bytes(f.encrypt(blob))

def cmd_set(args):
    master_key = require_master_key()
    secrets = load_secrets(master_key)
    key = args[0]
    value = args[1]
    secrets[key] = value
    save_secrets(master_key, secrets)
    print(f'Segredo "{key}" salvo em {SECRETS_PATH}')

def cmd_get(args):
    master_key = require_master_key()
    secrets = load_secrets(master_key)
    key = args[0]
    val = secrets.get(key)
    if val is None:
        print('Chave não encontrada')
        sys.exit(1)
    print(val)

def cmd_list(args):
    master_key = require_master_key()
    secrets = load_secrets(master_key)
    for k in sorted(secrets.keys()):
        print(k)

def cmd_delete(args):
    master_key = require_master_key()
    secrets = load_secrets(master_key)
    key = args[0]
    if key in secrets:
        del secrets[key]
        save_secrets(master_key, secrets)
        print(f'Chave {key} removida')
    else:
        print('Chave não encontrada')

def usage():
    print('''Uso:
  tools/secret_store.py set KEY VALUE   # salva um segredo
  tools/secret_store.py get KEY         # obtém um segredo
  tools/secret_store.py list            # lista chaves
  tools/secret_store.py delete KEY      # remove uma chave

Exemplo de criação de MASTER_KEY (apenas uma vez):
  export MASTER_KEY=$(python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
)
''')

def main():
    if len(sys.argv) < 2:
        usage(); sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == 'set' and len(args) >= 2:
        cmd_set(args)
    elif cmd == 'get' and len(args) == 1:
        cmd_get(args)
    elif cmd == 'list':
        cmd_list(args)
    elif cmd == 'delete' and len(args) == 1:
        cmd_delete(args)
    else:
        usage(); sys.exit(1)

if __name__ == '__main__':
    main()
