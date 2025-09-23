import pytest

from src.ws_server import app


def test_health_check():
    # Usa o Flask test client para não requerer servidor externo
    client = app.test_client()
    r = client.get('/status')
    assert r.status_code == 200
    data = r.get_json()
    assert data and 'status' in data
