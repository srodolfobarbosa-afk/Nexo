#!/usr/bin/env python3
"""
Sincroniza o arquivo local de backup `local_supabase_backup.json` com o Supabase.

Uso:
  python tools/sync_to_supabase.py

O script tenta usar `core.supabase_client.get_supabase_client()` e insere registros
não sincronizados em suas tabelas correspondentes. Ele atualiza um campo `synced`
no arquivo local para evitar reenvios.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_FILE = ROOT / 'local_supabase_backup.json'

def load_backup():
    if not BACKUP_FILE.exists():
        print('Arquivo de backup não encontrado:', BACKUP_FILE)
        return {}
    return json.loads(BACKUP_FILE.read_text(encoding='utf-8'))

def save_backup(data):
    BACKUP_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def main():
    try:
        from core.supabase_client import get_supabase_client
    except Exception as e:
        print('Erro ao importar core.supabase_client:', e)
        return
    client = get_supabase_client()
    if not client:
        print('Supabase não configurado. Defina SUPABASE_URL e SUPABASE_KEY.')
        return
    data = load_backup()
    changed = False
    for table, rows in data.items():
        for r in rows:
            if r.get('_synced'):
                continue
            payload = dict(r)
            payload.pop('_synced', None)
            try:
                client.table(table).insert(payload).execute()
                r['_synced'] = True
                print(f'Inserido em {table}: {payload.get("id") or payload.get("message","<no-id>")}')
                changed = True
            except Exception as e:
                print(f'Falha ao inserir em {table}:', e)
    if changed:
        save_backup(data)
        print('Backup atualizado localmente com flags de sync.')
    else:
        print('Nada novo para sincronizar')

if __name__ == '__main__':
    main()
