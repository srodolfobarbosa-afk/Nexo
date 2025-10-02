"""Pending transactions manager for EcoBank.

Stores pending transactions in a local JSON file and supports a two-approver
flow before executing the real transaction via the gateway. This avoids
accidental real money operations and requires two admin tokens to approve.
"""
import os
import json
import uuid
from datetime import datetime
from threading import Lock

PENDING_PATH = os.path.join(os.path.dirname(__file__), 'pending_transactions.json')
_lock = Lock()


def _load():
    if os.path.exists(PENDING_PATH):
        try:
            with open(PENDING_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save(data):
    with open(PENDING_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_pending(account_id: str, amount: float, description: str = '', created_by: str | None = None) -> dict:
    with _lock:
        data = _load()
        pid = str(uuid.uuid4())
        item = {
            'id': pid,
            'account_id': account_id,
            'amount': float(amount),
            'description': description,
            'created_by': created_by,
            'created_at': datetime.utcnow().isoformat(),
            'approvals': [],
            'executed': False,
            'executed_at': None,
            'executed_tx': None
        }
        data[pid] = item
        _save(data)
        return item


def list_pending() -> list:
    data = _load()
    return [v for v in data.values() if not v.get('executed')]


def get_pending(pid: str) -> dict | None:
    data = _load()
    return data.get(pid)


def approve_pending(pid: str, approver_token: str, approver_id: str) -> dict:
    """Registers an approval; when two distinct approvers approved, executes tx.

    approver_token is only recorded for audit; validation of token should be
    done by the caller (web endpoint) comparing to env vars ADMIN_DEPLOY_TOKEN and ADMIN_DEPLOY_TOKEN_2.
    """
    from ecobank import gateway

    with _lock:
        data = _load()
        item = data.get(pid)
        if not item:
            raise KeyError('pending_not_found')
        if item.get('executed'):
            return item

        # avoid duplicate approvals by same approver_id
        if approver_id in [a.get('approver_id') for a in item['approvals']]:
            return item

        item['approvals'].append({'approver_id': approver_id, 'token_hint': approver_token[:4] if approver_token else '', 'at': datetime.utcnow().isoformat()})

        # if two distinct approvals, execute
        approver_ids = {a.get('approver_id') for a in item['approvals']}
        if len(approver_ids) >= 2:
            # attempt execution via gateway
            if not gateway.provider_available():
                # cannot execute real tx without provider; leave pending
                data[pid] = item
                _save(data)
                return item
            try:
                tx = gateway.add_transaction(item['account_id'], item['amount'], item['description'])
                item['executed'] = True
                item['executed_at'] = datetime.utcnow().isoformat()
                item['executed_tx'] = tx
            except Exception as e:
                item['execution_error'] = str(e)

        data[pid] = item
        _save(data)
        return item
