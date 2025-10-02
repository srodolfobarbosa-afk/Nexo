"""Example provider for EcoBank gateway.

This provider is intentionally simple: it stores data in a local JSON file
under the project directory. It's useful for demos and local testing only.
To use a production provider, implement the same API against your bank/gateway.
"""
import os
import json
from datetime import datetime
from threading import Lock

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..')
LEDGER_FILE = os.path.abspath(os.path.join(BASE, 'ecobank_provider_example.json'))
_lock = Lock()


def _load():
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'accounts': {}, 'transactions': []}


def _save(data):
    with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_account(account_id, initial_balance=0.0):
    with _lock:
        data = _load()
        if account_id in data['accounts']:
            return False
        data['accounts'][account_id] = float(initial_balance)
        _save(data)
        return True


def get_balance(account_id):
    data = _load()
    return data['accounts'].get(account_id, 0.0)


def add_transaction(account_id, amount, description=''):
    with _lock:
        data = _load()
        balance = data['accounts'].get(account_id, 0.0)
        balance += float(amount)
        data['accounts'][account_id] = balance
        tx = {
            'account_id': account_id,
            'amount': float(amount),
            'description': description,
            'timestamp': datetime.utcnow().isoformat()
        }
        data['transactions'].append(tx)
        _save(data)
        return tx


def list_transactions(limit=50):
    data = _load()
    return list(reversed(data['transactions']))[:limit]
