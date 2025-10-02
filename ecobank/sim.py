"""Simulador EcoBank - gera receitas simuladas e mantém um ledger em memória/arquivo.
Modo seguro: por padrão opera em SIMULATE e grava em autoconstruct_staging/ecobank for inspection.
"""
import os
import json
from datetime import datetime
from threading import Lock

LEDGER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ecobank_ledger.json')
_lock = Lock()

def _load_ledger():
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {'accounts': {}, 'transactions': []}
    return {'accounts': {}, 'transactions': []}

def _save_ledger(data):
    with open(LEDGER_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_account(account_id, initial_balance=0.0):
    with _lock:
        data = _load_ledger()
        if account_id in data['accounts']:
            return False
        data['accounts'][account_id] = float(initial_balance)
        _save_ledger(data)
        return True


def get_balance(account_id):
    data = _load_ledger()
    return data['accounts'].get(account_id, 0.0)


def add_transaction(account_id, amount, description=''):
    with _lock:
        data = _load_ledger()
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
        _save_ledger(data)
        return tx


def simulate_revenue(account_id, base=100.0, factor=1.0):
    # simples: gera uma receita randômica baseada no timestamp
    import time, math
    revenue = base * (1 + math.sin(time.time() / 3600.0)) * factor
    return add_transaction(account_id, revenue, description='simulated_revenue')


def list_transactions(limit=50):
    data = _load_ledger()
    return list(reversed(data['transactions']))[:limit]
