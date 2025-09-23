"""ws_server.py - WebSocket backend para Centro de Comando Nexo

Fornece:
- rota raiz servindo o frontend estático
- /status healthcheck
- /auth/token -> retorna JWT (dev-friendly)
- /api/agents -> lista agentes registrados (protegido por JWT)
- websocket em /ws que envia monitoramento e registra agentes via agent_registry
"""
from flask import Flask, send_from_directory, request, jsonify, make_response
from flask_sock import Sock
try:
    from flask_cors import CORS
except Exception:
    CORS = lambda app: None  # fallback no-op quando a lib não estiver instalada
import json
import time
import os
import psutil
from datetime import datetime
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_supabase_client
from core.agent_registry import register_agent, get_agents
from core.jwt_auth import create_token, verify_token
from agentes.NexoGenesis import NexoGenesisAgent
from agentes.EcoFinance import EcoFinanceAgent
from agentes.APIcreditOptimizer import APIcreditOptimizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ws_server")

app = Flask(__name__, static_folder="../app/static", static_url_path="/static")
CORS(app)
sock = Sock(app)


@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route('/status')
def status():
    """Health check simples do serviço e dos principais componentes."""
    status_info = {
        "status": "ok",
        "supabase": bool(get_supabase_client()),
        "agents_loaded": ['NexoGenesis', 'EcoFinance', 'APIcreditOptimizer']
    }
    return (json.dumps(status_info), 200, {'Content-Type': 'application/json'})


@app.route('/auth/token', methods=['POST'])
def auth_token():
    """Em dev: aceita username/password simples via JSON e retorna um JWT.
    Em produção deve ser substituído por um provedor de identidade.
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    # Credenciais de desenvolvimento (substituir em produção)
    DEV_USER = os.environ.get('AUTH_USERNAME', 'admin')
    DEV_PASS = os.environ.get('AUTH_PASSWORD', 'password')

    if username == DEV_USER and password == DEV_PASS:
        token = create_token(subject=username, scopes=['read:agents'])
        return jsonify({'access_token': token})
    return make_response(jsonify({'error': 'invalid_credentials'}), 401)


@app.route('/api/agents', methods=['GET'])
def api_agents():
    """Retorna agentes registrados. Requer Authorization: Bearer <token>"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return make_response(jsonify({'error': 'missing_token'}), 401)
    token = auth.split(' ', 1)[1]
    try:
        payload = verify_token(token)
    except Exception:
        return make_response(jsonify({'error': 'invalid_token'}), 401)
    agents = get_agents()
    return jsonify({'user': payload.get('sub'), 'agents': agents})


@sock.route('/ws')
def ws(ws):
    """Loop principal do websocket: instancia agentes (tolerante a falhas) e emite dados periodicamente."""
    supabase = get_supabase_client()
    agents = {}

    try:
        nexo = NexoGenesisAgent()
        agents['NexoGenesis'] = nexo
        register_agent('NexoGenesis', {'status': 'active'})
        logger.info("Agente NexoGenesis inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar NexoGenesis: {e}")
        nexo = None
        register_agent('NexoGenesis', {'status': 'error', 'error': str(e)})

    try:
        eco = EcoFinanceAgent()
        agents['EcoFinance'] = eco
        register_agent('EcoFinance', {'status': 'active'})
        logger.info("Agente EcoFinance inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar EcoFinance: {e}")
        eco = None
        register_agent('EcoFinance', {'status': 'error', 'error': str(e)})

    try:
        api_opt = APIcreditOptimizer()
        agents['APIcreditOptimizer'] = api_opt
        register_agent('APIcreditOptimizer', {'status': 'active'})
        logger.info("Agente APIcreditOptimizer inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar APIcreditOptimizer: {e}")
        api_opt = None
        register_agent('APIcreditOptimizer', {'status': 'error', 'error': str(e)})

    api_keys = [k for k in os.environ.keys() if 'KEY' in k]
    api_keys_mem = api_keys.copy()

    while True:
        # Recebe comandos do frontend
        try:
            msg = ws.receive(timeout=0.1)
            if msg:
                data = json.loads(msg)
                if data.get("action") == "adicionar_api_key":
                    api_keys_mem.append(data.get("key"))
                if data.get("action") == "remover_api_key":
                    idx = data.get("index")
                    if isinstance(idx, int) and 0 <= idx < len(api_keys_mem):
                        api_keys_mem.pop(idx)
        except Exception:
            # ignore timeouts/disconnects
            pass

        # Monitor visual simplificado
        monitor_htmls = [
            f"<div><strong>Status NexoGenesis:</strong> {nexo.get_status()['nexo_genesis'] if nexo else 'indisponivel'}</div>",
            f"<div><strong>EcoFinance:</strong> Receita R$ 1000, Despesa R$ 400</div>",
            f"<div><strong>APIcreditOptimizer:</strong> Requests: {api_opt.monitor_api_usage('dummy').get('requests',0) if api_opt else 0}</div>"
        ]
        ws.send(json.dumps({"type": "monitor", "content": monitor_htmls}))

        agentes_cards = [
            {"nome": "NexoGenesis", "status": (nexo.get_status()['nexo_genesis'] if nexo else 'indisponivel'), "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": (nexo.get_status().get('missoes_processadas', 0) if nexo else 0)},
            {"nome": "EcoFinance", "status": ("ativo" if eco else "indisponivel"), "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": 0},
            {"nome": "APIcreditOptimizer", "status": ("ativo" if api_opt else "indisponivel"), "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": 0}
        ]
        ws.send(json.dumps({"type": "agentes_status", "agentes": agentes_cards}))

        financeiro_html = f"<div><strong>Receita:</strong> R$ 1000<br><strong>Despesa:</strong> R$ 400<br><strong>ROI:</strong> 150%</div>"
        ws.send(json.dumps({"type": "financeiro", "graficos": financeiro_html}))

        # Histórico de falhas
        logs = []
        try:
            logs_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'evolution_20250919.json')
            if os.path.exists(logs_path):
                with open(logs_path) as f:
                    for line in f:
                        if 'failed' in line:
                            logs.append({
                                "nivel": "error",
                                "agente": "NexoGenesis",
                                "mensagem": line.strip(),
                                "timestamp": datetime.now().isoformat()
                            })
        except Exception:
            pass
        logs.append({"nivel": "info", "agente": "EcoFinance", "mensagem": "Operação financeira concluída.", "timestamp": datetime.now().isoformat()})
        logs.append({"nivel": "warning", "agente": "APIcreditOptimizer", "mensagem": "Limite de requisições próximo do máximo.", "timestamp": datetime.now().isoformat()})
        ws.send(json.dumps({"type": "historico", "logs": logs}))

        try:
            with open(os.path.join(os.path.dirname(__file__), '..', 'memoria_curto_prazo.json')) as f:
                memoria = json.load(f)
            mapa_html = f"<div><strong>Ciclo:</strong> {memoria.get('ciclo',0)}<br><strong>Evolução:</strong> {memoria.get('evolucao',{})}</div>"
        except Exception:
            mapa_html = "<div>Mapa indisponível</div>"
        ws.send(json.dumps({"type": "mapa_tarefas", "mapa": mapa_html}))

        config_html = f"<strong>API Keys:</strong> {len(api_keys_mem)} cadastradas. <button>Gerenciar</button>"
        ws.send(json.dumps({"type": "config", "config": config_html, "api_keys": api_keys_mem}))

        time.sleep(2)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


