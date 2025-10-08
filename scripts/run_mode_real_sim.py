#!/usr/bin/env python3
"""Runner para modo real simulado:
- inicia stub Manus (background thread)
- configura envs locais para apontar para o stub
- executa um fluxo: enviar mensagem -> criar task -> importar bundle -> gerar plano
"""
import time
import requests
import os
import json
from subprocess import Popen
import sys


# Adiciona o diretório raiz do projeto ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def start_stub_subprocess():
    """Start the stub server as a separate process using the script path."""
    script = os.path.join(os.path.dirname(__file__), "stub_manus_api.py")
    # Use Popen to run in background
    proc = Popen(["python3", script])
    return proc


def wait_for_port(url: str, timeout: int = 8) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.25)
    return False


def main():
    proc = start_stub_subprocess()
    try:
        ok = wait_for_port("http://127.0.0.1:5001/tasks", timeout=6)
        if not ok:
            print("Warning: stub did not become available in time")
        else:
            print("Stub Manus started at http://127.0.0.1:5001")

        # simulate creating a task
        payload = {"goal": "Analyze sales last quarter"}
        try:
            r = requests.post("http://127.0.0.1:5001/tasks", json=payload, timeout=3)
            print("Create task status:", r.status_code, r.json())
            tid = r.json().get("id")
        except Exception as e:
            print("Failed to create task on stub:", e)
            tid = None

        # wait and get status if created
        if tid:
            time.sleep(3)
            try:
                r2 = requests.get(f"http://127.0.0.1:5001/tasks/{tid}", timeout=3)
                print("Task status:", r2.status_code, r2.json())
            except Exception as e:
                print("Failed to fetch task status:", e)

        # create a minimal export bundle and call local /api/manus/import
        bundle = {"memories": [{"topic": "sales", "payload": {"q": "Q3", "rev": 1000}}], "docs": {}}
        bundle_path = os.path.abspath("manus_export.json")
        with open(bundle_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False, indent=2)

        # call the Flask app endpoints using test client via import
        from src import ws_server
        app = ws_server.app
        with app.test_client() as c:
            # get dev token
            resp = c.post("/auth/token", json={"username":"admin","password":"password"})
            token = resp.get_json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            resp2 = c.post("/api/manus/import", json={"path": bundle_path}, headers=headers)
            print("import resp:", resp2.status_code, resp2.get_json())

            # request a plan
            resp3 = c.post("/api/manus/plan", json={"description": "Real migration plan please"}, headers=headers)
            print("plan resp:", resp3.status_code)
            try:
                print(resp3.get_json())
            except Exception:
                print(resp3.data)

    finally:
        try:
            proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
