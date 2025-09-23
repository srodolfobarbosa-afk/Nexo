#!/usr/bin/env python3
"""
Valida endpoints básicos do serviço e tenta persistir no Supabase.

Uso:
  python tools/validate_deploy.py --base https://<your-service>.onrender.com

O script testa: `/status`, `/auth/token` (se credenciais informadas), `/chat`, `/objective`.
Se `SUPABASE_URL` e `SUPABASE_KEY` estiverem no ambiente, tenta escrever em `chat`.
"""
import argparse
import os
import sys
import requests
import json

def req(path, method='get', **kwargs):
    try:
        r = getattr(requests, method)(path, timeout=10, **kwargs)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', required=True, help='Base URL do serviço (ex: https://meu-app.onrender.com)')
    p.add_argument('--auth-user')
    p.add_argument('--auth-pass')
    args = p.parse_args()
    base = args.base.rstrip('/')

    print('Testando /status...')
    code, text = req(base + '/status')
    print(code, text[:200])

    token = None
    if args.auth_user and args.auth_pass:
        print('Testando /auth/token...')
        code, text = req(base + '/auth/token', method='post', json={'username':args.auth_user,'password':args.auth_pass})
        print(code, text[:200])
        if code == 200:
            try:
                token = json.loads(text).get('access_token')
            except Exception:
                pass

    headers = {'Authorization': f'Bearer {token}'} if token else {}

    print('Testando /objective (GET)...')
    code, text = req(base + '/objective', headers=headers)
    print(code, text[:400])

    print('Testando /chat (POST)...')
    payload = {'message': 'Validação automática: teste de deploy'}
    code, text = req(base + '/chat', method='post', json=payload, headers=headers)
    print(code, text[:400])

    # Tentativa de persistência em Supabase se configurado
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    if supabase_url and supabase_key:
        print('Tentando gravar no Supabase via REST...')
        endpoint = supabase_url.rstrip('/') + '/rest/v1/chat'
        body = {'user_id':'validate_script','message':'validation record','reply':'ok','metadata':{'source':'validate_deploy.py'}}
        try:
            r = requests.post(endpoint, headers={'apikey':supabase_key,'Content-Type':'application/json','Authorization':f'Bearer {supabase_key}'}, json=body, timeout=10)
            print('Supabase write', r.status_code, r.text[:400])
        except Exception as e:
            print('Supabase write exception', e)
    else:
        print('SUPABASE_URL/SUPABASE_KEY não configurados; pulando persistência direta.')

if __name__ == '__main__':
    main()
