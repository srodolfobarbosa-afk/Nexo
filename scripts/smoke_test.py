import os
import time

import requests

BASE = os.environ.get("BASE", "http://127.0.0.1:5000")


def get_token():
    r = requests.post(
        f"{BASE}/auth/token",
        json={
            "username": os.environ.get("AUTH_USERNAME", "admin"),
            "password": os.environ.get("AUTH_PASSWORD", "password"),
        },
    )
    try:
        return r.json().get("access_token")
    except Exception:
        return None


def call_revenue(token):
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/api/revenue", headers=h)
    print("/api/revenue", r.status_code, r.text[:200])


def call_memory(token):
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/api/memory", headers=h)
    print("/api/memory", r.status_code)


if __name__ == "__main__":
    print("Smoke test (assumes local Flask server running at http://127.0.0.1:5000)")
    token = get_token()
    print("token", bool(token))
    if token:
        call_revenue(token)
        call_memory(token)
