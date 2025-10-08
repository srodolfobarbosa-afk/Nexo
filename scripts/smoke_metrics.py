"""Smoke test para os endpoints de métricas em src.ws_server"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ws_server import app


def run():
    client = app.test_client()
    # postar métrica
    r = client.post("/api/metrics", json={"name": "test_smoke", "value": 123, "meta": {"env": "smoke"}})
    print("POST status:", r.status_code, r.get_json())
    # buscar métricas
    r2 = client.get("/api/metrics?limit=10")
    print("GET status:", r2.status_code, r2.get_json())


if __name__ == "__main__":
    run()
