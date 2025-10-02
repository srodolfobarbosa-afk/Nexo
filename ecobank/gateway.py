"""EcoBank gateway: provider abstraction for real financial operations.

This module loads a provider implementation based on the ECON_BANK_PROVIDER
environment variable. Providers must implement the functions:
  - create_account(account_id, initial_balance)
  - get_balance(account_id)
  - add_transaction(account_id, amount, description)
  - list_transactions(limit)

By default, the gateway refuses to perform real operations unless a provider
is configured and credentials are present. This prevents accidental money ops.
"""
import importlib
import os
from typing import Any

PROVIDER_NAME = os.environ.get("ECON_BANK_PROVIDER")


def _load_provider():
    if not PROVIDER_NAME:
        return None
    try:
        mod = importlib.import_module(f"ecobank.providers.{PROVIDER_NAME}")
        return mod
    except Exception as e:
        raise RuntimeError(f"Failed to load ecobank provider '{PROVIDER_NAME}': {e}")


def provider_available() -> bool:
    return PROVIDER_NAME is not None


def create_account(account_id: str, initial_balance: float = 0.0) -> Any:
    provider = _load_provider()
    if provider is None:
        raise RuntimeError("No ECON_BANK_PROVIDER configured. Refuse to perform real operations.")
    return provider.create_account(account_id, initial_balance)


def get_balance(account_id: str) -> float:
    provider = _load_provider()
    if provider is None:
        raise RuntimeError("No ECON_BANK_PROVIDER configured. Refuse to perform real operations.")
    return provider.get_balance(account_id)


def add_transaction(account_id: str, amount: float, description: str = "") -> Any:
    provider = _load_provider()
    if provider is None:
        raise RuntimeError("No ECON_BANK_PROVIDER configured. Refuse to perform real operations.")
    return provider.add_transaction(account_id, amount, description)


def list_transactions(limit: int = 50):
    provider = _load_provider()
    if provider is None:
        raise RuntimeError("No ECON_BANK_PROVIDER configured. Refuse to perform real operations.")
    return provider.list_transactions(limit)
