import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ws_server import app


def run():
    client = app.test_client()
    # get dev token
    r = client.post("/auth/token", json={"username": "admin", "password": "password"})
    tok = r.get_json().get("access_token")
    headers = {"Authorization": f"Bearer {tok}"}

    r2 = client.post("/api/manus/plan", json={"description": "Plano de migracao rapido"}, headers=headers)
    print("PLAN status", r2.status_code)
    print(r2.get_json())

    r3 = client.post("/api/manus/export", headers=headers)
    print("EXPORT status", r3.status_code)
    print(r3.get_json())

if __name__ == "__main__":
    run()
