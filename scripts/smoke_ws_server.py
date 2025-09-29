"""Smoke test: importa o Flask app de `src.ws_server` e faz uma chamada para /status."""
from src import ws_server


def run_smoke():
    app = ws_server.app
    client = app.test_client()
    resp = client.get('/status')
    print('status_code:', resp.status_code)
    print('json:', resp.get_json())


if __name__ == '__main__':
    run_smoke()
