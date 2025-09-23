#!/usr/bin/env python3
"""
Simple helper for engineers to register work done locally and optionally persist to Supabase.

Usage:
  python tools/log_work.py "Fixed mission runner gating" --author "ana"

This appends an entry to WORK_LOG.md and, if Supabase is configured via
`SUPABASE_URL` and `SUPABASE_KEY`, will try to insert a record into `agent_logs`.
"""
import os
import sys
import json
from datetime import datetime

WORK_LOG = os.path.join(os.path.dirname(__file__), '..', 'WORK_LOG.md')

def append_local(message, author):
    ts = datetime.utcnow().isoformat() + 'Z'
    line = f"- [{ts}] {author}: {message}\n"
    path = os.path.abspath(WORK_LOG)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line)
    print(f"Registro gravado localmente em {path}")

def try_persist_supabase(message, author):
    try:
        from core.supabase_client import get_supabase_client
    except Exception:
        print("core.supabase_client não disponível; pulando persistência remota")
        return False
    client = get_supabase_client()
    if not client:
        print("Supabase não configurado; pulando persistência remota")
        return False
    payload = {
        'user_id': author or 'unknown',
        'level': 'info',
        'message': message,
        'metadata': {'source': 'tools/log_work.py'}
    }
    try:
        res = client.table('agent_logs').insert(payload).execute()
        print("Registro persistido no Supabase (agent_logs)")
        return True
    except Exception as e:
        print(f"Falha ao persistir no Supabase: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: tools/log_work.py \"mensagem\" --author \"nome\"")
        sys.exit(1)
    message = sys.argv[1]
    author = 'unknown'
    if '--author' in sys.argv:
        try:
            author = sys.argv[sys.argv.index('--author') + 1]
        except Exception:
            pass
    append_local(message, author)
    try_persist_supabase(message, author)

if __name__ == '__main__':
    main()
