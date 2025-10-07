import os
from typing import Optional

import requests


def get_secret_from_env(key: str) -> Optional[str]:
    return os.environ.get(key)


def get_secret_from_provider(key: str) -> Optional[str]:
    """If SECRETS_PROVIDER_URL and SECRETS_PROVIDER_TOKEN are set, try to fetch the secret.

    Expected behavior: GET {SECRETS_PROVIDER_URL}/secrets/{key} with header
    Authorization: Bearer {SECRETS_PROVIDER_TOKEN}
    Response is expected to be JSON {"value": "the-secret"}.
    """
    url = os.environ.get("SECRETS_PROVIDER_URL")
    token = os.environ.get("SECRETS_PROVIDER_TOKEN")
    if not url or not token:
        return None
    try:
        full = url.rstrip("/") + f"/secrets/{key}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        resp = requests.get(full, headers=headers, timeout=5)
        if resp.status_code == 200:
            j = resp.json()
            # support both {"value": ...} and direct string
            if isinstance(j, dict) and "value" in j:
                return j.get("value")
            if isinstance(j, str):
                return j
    except Exception:
        return None
    return None


def get_secret(key: str) -> Optional[str]:
    # Prefer environment first (explicit local/runtime override)
    v = get_secret_from_env(key)
    if v:
        return v
    # Try remote provider (if configured)
    return get_secret_from_provider(key)
