import pytest
import requests

BASE_URL = "http://localhost:5000"

def test_health_check():
    r = requests.get(f"{BASE_URL}/status")
    assert r.status_code == 200
    assert "status" in r.json()
