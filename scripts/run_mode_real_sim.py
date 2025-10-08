#!/usr/bin/env python3
"""Runner para modo real simulado:
- inicia stub Manus (background thread)
- configura envs locais para apontar para o stub
- executa um fluxo: enviar mensagem -> criar task -> importar bundle -> gerar plano
"""
import threading
import time
import requests
import os
import json
from subprocess import Popen


def start_stub():
    # run the stub as a module
    import scripts.stub_manus_api as stub
    stub.app.run(port=5001)


def main():
    # start stub in a thread
    t = threading.Thread(target=start_stub, daemon=True)
    t.start()
    time.sleep(1)
    print("Stub Manus started at http://127.0.0.1:5001")

    # simulate creating a task
    payload = {"goal": "Analyze sales last quarter"}
    r = requests.post("http://127.0.0.1:5001/tasks", json=payload)
    print("Create task status:", r.status_code, r.json())
    tid = r.json().get("id")

    # wait and get status
    time.sleep(3)
    r2 = requests.get(f"http://127.0.0.1:5001/tasks/{tid}")
    print("Task status:", r2.status_code, r2.json())

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
        resp = c.post('/auth/token', json={'username':'admin','password':'password'})
        token = resp.get_json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        resp2 = c.post('/api/manus/import', json={'path': bundle_path}, headers=headers)
        print('import resp:', resp2.status_code, resp2.get_json())

        # request a plan
        resp3 = c.post('/api/manus/plan', json={'description': 'Real migration plan please'}, headers=headers)
        print('plan resp:', resp3.status_code)
        try:
            print(resp3.get_json())
        except Exception:
            print(resp3.data)


if __name__ == "__main__":
    main()
