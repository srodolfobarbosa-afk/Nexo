"""EcoBank stub: manages financial movements in a safe, testable way.

In production integrate with real payment provider and KYC.
"""
from typing import Dict
import logging

log = logging.getLogger('ecobank')

class EcoBank:
    def __init__(self):
        self._balance = 0.0

    def credit(self, amount: float, reason: str = '') -> Dict:
        if amount <= 0:
            raise ValueError('amount must be positive')
        self._balance += amount
        log.info('Credited %s: %s', amount, reason)
        return {'status':'ok','balance':self._balance}

    def debit(self, amount: float, reason: str = '') -> Dict:
        if amount <= 0:
            raise ValueError('amount must be positive')
        if amount > self._balance:
            log.warning('Insufficient balance for debit %s', amount)
            return {'status':'insufficient_funds','balance':self._balance}
        self._balance -= amount
        log.info('Debited %s: %s', amount, reason)
        return {'status':'ok','balance':self._balance}

    def get_balance(self) -> float:
        return self._balance
