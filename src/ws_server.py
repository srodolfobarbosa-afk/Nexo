"""ws_server.py - WebSocket backend para Centro de Comando Nexo

Fornece:
- rota raiz servindo o frontend estático
- /status healthcheck
- /auth/token -> retorna JWT (dev-friendly)
- /api/agents -> lista agentes registrados (protegido por JWT)
- websocket em /ws que envia monitoramento e registra agentes via agent_registry
"""

from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_sock import Sock

try:
    from flask_cors import CORS
except Exception:
    CORS = lambda app: None  # fallback no-op quando a lib não estiver instalada
import json
import logging
import os
import sys
import time
from datetime import datetime

import psutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agentes.APIcreditOptimizer import APIcreditOptimizer
from agentes.EcoFinance import EcoFinanceAgent
from agentes.NexoGenesis import NexoGenesisAgent
from core import sqlite_client
from core.agent_loader import discover_and_register_all
from core.agent_registry import get_agents, register_agent
from core.database import get_supabase_client
from core.jwt_auth import create_token, require_jwt, verify_token
from core.mission_runner import start_background

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ws_server")

app = Flask(__name__, static_folder="../app/static", static_url_path="/static")
CORS(app)
sock = Sock(app)

# Segurança em runtime: evitar uso de JWT_SECRET padrão quando Supabase Auth estiver ativado
if os.environ.get("USE_SUPABASE_AUTH", "0") in ("1", "true", "True"):
    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret or jwt_secret in ("change_this_secret", "default_jwt_secret", ""):
        logger.warning(
            "USING DEFAULT JWT_SECRET OR JWT_SECRET NOT SET while USE_SUPABASE_AUTH=1. This is insecure in production."
        )


# Registrar agentes iniciais em estado 'idle' para exponibilizar via API sem conexão WS
try:
    # discover and register agents dynamically
    discover_and_register_all()
except Exception:
    # não falhar se o registrador estiver indisponível
    pass


# Iniciar mission runner no primeiro request/do ciclo de vida do Flask.
def _maybe_start_mission_runner():
    try:
        start_flag = os.environ.get("START_MISSION_RUNNER", "1")
        if start_flag in ("1", "true", "True"):
            logger.info("Inicializando mission runner (startup wrapper)")
            start_background(interval=int(os.environ.get("MISSION_INTERVAL", "6")))
        else:
            logger.info("Mission runner desativado via START_MISSION_RUNNER env")
    except Exception as e:
        logger.error(f"Erro ao iniciar mission runner: {e}")


# Flask versions differ in lifecycle hooks. Prefer `before_first_request` when available,
# otherwise try `before_serving`. As a robust fallback, wrap the WSGI app so we start
# the runner on the first handled request in this process (works with gunicorn workers).
_runner_started = {"started": False}
if hasattr(app, "before_first_request"):

    @app.before_first_request
    def _start_runner_on_first_request():
        _maybe_start_mission_runner()

elif hasattr(app, "before_serving"):

    @app.before_serving
    def _start_runner_on_first_request():
        _maybe_start_mission_runner()

else:
    # WSGI wrapper fallback: call once before delegating to original WSGI app
    _orig_wsgi = app.wsgi_app

    def _wsgi_start_wrapper(environ, start_response):
        if not _runner_started["started"]:
            try:
                _maybe_start_mission_runner()
            except Exception:
                pass
            _runner_started["started"] = True
        return _orig_wsgi(environ, start_response)

    app.wsgi_app = _wsgi_start_wrapper


@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/status")
def status():
    """Health check simples do serviço e dos principais componentes."""
    # Checagem de conectividade com Supabase (pode ser lenta se houver timeout)
    supabase_client = None
    supabase_ok = False
    try:
        supabase_client = get_supabase_client()
        if supabase_client:
            # tentativa simples de listar 1 registro em uma tabela conhecida
            try:
                supabase_client.table("agent_error_log").select("id").limit(1).execute()
                supabase_ok = True
            except Exception:
                supabase_ok = False
    except Exception:
        supabase_ok = False

    status_info = {
        "status": "ok",
        "supabase": supabase_ok,
        "agents_loaded": ["NexoGenesis", "EcoFinance", "APIcreditOptimizer"],
    }
    return (json.dumps(status_info), 200, {"Content-Type": "application/json"})


@app.route("/auth/token", methods=["POST"])
def auth_token():
    """Em dev: aceita username/password simples via JSON e retorna um JWT.
    Em produção deve ser substituído por um provedor de identidade.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    # Se estamos usando Supabase/Auth em produção, não permitir o token dev
    if os.environ.get("USE_SUPABASE_AUTH", "0") in ("1", "true", "True"):
        return make_response(
            jsonify(
                {
                    "error": "dev_token_disabled",
                    "msg": "Use identity provider (Supabase/OIDC) to obtain tokens",
                }
            ),
            403,
        )

    # Credenciais de desenvolvimento (substituir em produção)
    DEV_USER = os.environ.get("AUTH_USERNAME", "admin")
    DEV_PASS = os.environ.get("AUTH_PASSWORD", "password")

    if username == DEV_USER and password == DEV_PASS:
        token = create_token(subject=username, scopes=["read:agents"])
        return jsonify({"access_token": token})
    return make_response(jsonify({"error": "invalid_credentials"}), 401)


@app.route("/api/agents", methods=["GET"])
@require_jwt
def api_agents():
    """Retorna agentes registrados. Requer Authorization: Bearer <token>"""
    from flask import g

    payload = g.jwt_payload
    agents = get_agents()
    return jsonify({"user": payload.get("sub"), "agents": agents})


@app.route("/api/memory", methods=["GET"])
@require_jwt
def api_memory():
    """Retorna memórias de longo prazo (persistidas) - protegido por JWT."""
    from flask import g

    payload = g.jwt_payload
    try:
        # listar memórias (limit param opcional)
        limit = int(request.args.get("limit", "50"))
        from core.sqlite_client import Memory, get_session

        s = get_session()
        rows = s.query(Memory).order_by(Memory.created_at.desc()).limit(limit).all()
        s.close()
        items = [
            {
                "id": r.id,
                "key": r.key,
                "data": r.data,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        return jsonify({"user": payload.get("sub"), "memories": items})
    except Exception as e:
        logger.error(f"Erro ao buscar memórias: {e}")
        return make_response(jsonify({"error": "internal_error"}), 500)


@app.route("/api/revenue", methods=["GET"])
@require_jwt
def api_revenue():
    """Retorna receita total acumulada."""
    from flask import g

    payload = g.jwt_payload
    try:
        total = sqlite_client.get_total_revenue()
        return jsonify({"user": payload.get("sub"), "total_revenue": total})
    except Exception as e:
        logger.error(f"Erro ao calcular receita: {e}")
        return make_response(jsonify({"error": "internal_error"}), 500)


@app.route("/api/missions/start", methods=["POST"])
@require_jwt
def api_missions_start():
    """Força o start do mission runner nesta instância."""
    from flask import g

    payload = g.jwt_payload
    try:
        interval = int(
            request.json.get("interval", os.environ.get("MISSION_INTERVAL", "6"))
        )
        _maybe_start_mission_runner()
        return jsonify(
            {"user": payload.get("sub"), "status": "started", "interval": interval}
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar mission runner via API: {e}")
        return make_response(jsonify({"error": "internal_error"}), 500)


@app.route("/api/missions/stop", methods=["POST"])
@require_jwt
def api_missions_stop():
    """Para o mission runner (por processo)."""
    from flask import g

    payload = g.jwt_payload
    try:
        from core.mission_runner import stop_runner

        stop_runner()
        return jsonify({"user": payload.get("sub"), "status": "stopped"})
    except Exception as e:
        logger.error(f"Erro ao parar mission runner via API: {e}")
        return make_response(jsonify({"error": "internal_error"}), 500)


@sock.route("/ws")
def ws(ws):
    """Loop principal do websocket: instancia agentes (tolerante a falhas) e emite dados periodicamente."""
    supabase = get_supabase_client()
    agents = {}

    try:
        # Instanciar o NexoGenesis usando a classe importada no topo do arquivo
        nexo = NexoGenesisAgent()
        agents["NexoGenesis"] = nexo
        try:
            from core.agent_registry import register_agent_instance

            register_agent_instance(nexo, {"status": "active"})
        except Exception:
            register_agent("NexoGenesis", {"status": "active"})
        logger.info("Agente NexoGenesis inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar NexoGenesis: {e}")
        nexo = None
        register_agent("NexoGenesis", {"status": "error", "error": str(e)})

    try:
        eco = EcoFinanceAgent()
        agents["EcoFinance"] = eco
        try:
            from core.agent_registry import register_agent_instance

            register_agent_instance(eco, {"status": "active"})
        except Exception:
            register_agent("EcoFinance", {"status": "active"})
        logger.info("Agente EcoFinance inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar EcoFinance: {e}")
        eco = None
        register_agent("EcoFinance", {"status": "error", "error": str(e)})

    try:
        api_opt = APIcreditOptimizer()
        agents["APIcreditOptimizer"] = api_opt
        try:
            from core.agent_registry import register_agent_instance

            register_agent_instance(api_opt, {"status": "active"})
        except Exception:
            register_agent("APIcreditOptimizer", {"status": "active"})
        logger.info("Agente APIcreditOptimizer inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar APIcreditOptimizer: {e}")
        api_opt = None
        register_agent("APIcreditOptimizer", {"status": "error", "error": str(e)})

    api_keys = [k for k in os.environ.keys() if "KEY" in k]
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
            f"<div><strong>APIcreditOptimizer:</strong> Requests: {api_opt.monitor_api_usage('dummy').get('requests', 0) if api_opt else 0}</div>",
        ]
        ws.send(json.dumps({"type": "monitor", "content": monitor_htmls}))

        agentes_cards = [
            {
                "nome": "NexoGenesis",
                "status": (
                    nexo.get_status()["nexo_genesis"] if nexo else "indisponivel"
                ),
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "tarefasHora": (
                    nexo.get_status().get("missoes_processadas", 0) if nexo else 0
                ),
            },
            {
                "nome": "EcoFinance",
                "status": ("ativo" if eco else "indisponivel"),
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "tarefasHora": 0,
            },
            {
                "nome": "APIcreditOptimizer",
                "status": ("ativo" if api_opt else "indisponivel"),
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "tarefasHora": 0,
            },
        ]
        ws.send(json.dumps({"type": "agentes_status", "agentes": agentes_cards}))

        financeiro_html = f"<div><strong>Receita:</strong> R$ 1000<br><strong>Despesa:</strong> R$ 400<br><strong>ROI:</strong> 150%</div>"
        ws.send(json.dumps({"type": "financeiro", "graficos": financeiro_html}))

        # Histórico de falhas
        logs = []
        try:
            logs_path = os.path.join(
                os.path.dirname(__file__), "..", "logs", "evolution_20250919.json"
            )
            if os.path.exists(logs_path):
                with open(logs_path) as f:
                    for line in f:
                        if "failed" in line:
                            logs.append(
                                {
                                    "nivel": "error",
                                    "agente": "NexoGenesis",
                                    "mensagem": line.strip(),
                                    "timestamp": datetime.now().isoformat(),
                                }
                            )
        except Exception:
            pass
        logs.append(
            {
                "nivel": "info",
                "agente": "EcoFinance",
                "mensagem": "Operação financeira concluída.",
                "timestamp": datetime.now().isoformat(),
            }
        )
        logs.append(
            {
                "nivel": "warning",
                "agente": "APIcreditOptimizer",
                "mensagem": "Limite de requisições próximo do máximo.",
                "timestamp": datetime.now().isoformat(),
            }
        )
        ws.send(json.dumps({"type": "historico", "logs": logs}))

        try:
            with open(
                os.path.join(
                    os.path.dirname(__file__), "..", "memoria_curto_prazo.json"
                )
            ) as f:
                memoria = json.load(f)
            mapa_html = f"<div><strong>Ciclo:</strong> {memoria.get('ciclo', 0)}<br><strong>Evolução:</strong> {memoria.get('evolucao', {})}</div>"
        except Exception:
            mapa_html = "<div>Mapa indisponível</div>"
        ws.send(json.dumps({"type": "mapa_tarefas", "mapa": mapa_html}))

        config_html = f"<strong>API Keys:</strong> {len(api_keys_mem)} cadastradas. <button>Gerenciar</button>"
        ws.send(
            json.dumps(
                {"type": "config", "config": config_html, "api_keys": api_keys_mem}
            )
        )

        time.sleep(2)
