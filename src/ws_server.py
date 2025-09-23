# ws_server.py - WebSocket backend para Centro de Comando EcoGuardians
from flask import Flask, send_from_directory
from flask_sock import Sock
import json
import time
import random
import os
import psutil
from datetime import datetime
import glob
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_supabase_client
from agentes.NexoGenesis import NexoGenesisAgent
from agentes.EcoFinance import EcoFinanceAgent
from agentes.APIcreditOptimizer import APIcreditOptimizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ws_server")

app = Flask(__name__, static_folder="../app/static", static_url_path="/static")
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
        "agents_loaded": [k for k in [
            'NexoGenesis', 'EcoFinance', 'APIcreditOptimizer'
        ]]
    }
    return (json.dumps(status_info), 200, {'Content-Type': 'application/json'})

@sock.route('/ws')
def ws(ws):
    # Instanciar agentes reais (tolerante a falhas individuais)
    supabase = get_supabase_client()
    agents = {}
    try:
        nexo = NexoGenesisAgent()
        agents['NexoGenesis'] = nexo
        logger.info("Agente NexoGenesis inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar NexoGenesis: {e}")
        nexo = None
    try:
        eco = EcoFinanceAgent()
        agents['EcoFinance'] = eco
        logger.info("Agente EcoFinance inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar EcoFinance: {e}")
        eco = None
    try:
        api_opt = APIcreditOptimizer()
        agents['APIcreditOptimizer'] = api_opt
        logger.info("Agente APIcreditOptimizer inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao inicializar APIcreditOptimizer: {e}")
        api_opt = None
    api_keys = [k for k in os.environ.keys() if 'KEY' in k]
    # API Keys gerenciadas em memória (mock)
    api_keys_mem = api_keys.copy()
    while True:
        # Recebe comandos do frontend
        try:
            msg = ws.receive(timeout=0.1)
            if msg:
                data = json.loads(msg)
                if data.get("action") == "adicionar_api_key":
                    api_keys_mem.append(data["key"])
                if data.get("action") == "remover_api_key":
                    idx = data["index"]
                    if 0 <= idx < len(api_keys_mem):
                        api_keys_mem.pop(idx)
        except Exception as e:
            # Tratar exceções de desconexão ou timeout
            # Se o cliente se desconectar, ws.receive() pode levantar uma exceção
            # ou retornar None/vazio dependendo da implementação do flask_sock
            # Para simplicidade, vamos apenas passar, mas em produção, você pode querer logar ou quebrar o loop
            pass
        # Monitor visual dividido em 3 partes
        monitor_htmls = [
            f"<div><strong>Status NexoGenesis:</strong> {nexo.get_status()['nexo_genesis'] if nexo else 'indisponivel'}</div>",
            f"<div><strong>EcoFinance:</strong> Receita R$ 1000, Despesa R$ 400</div>",
            f"<div><strong>APIcreditOptimizer:</strong> Requests: {api_opt.monitor_api_usage('dummy').get('requests',0) if api_opt else 0}</div>"
        ]
        ws.send(json.dumps({
            "type": "monitor",
            "content": monitor_htmls
        }))
        # Status dos agentes (CPU/RAM reais do sistema)
        agentes_cards = [
            {"nome": "NexoGenesis", "status": (nexo.get_status()['nexo_genesis'] if nexo else 'indisponivel'), "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": (nexo.get_status().get('missoes_processadas', 0) if nexo else 0)},
            {"nome": "EcoFinance", "status": ("ativo" if eco else "indisponivel"), "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": 0},
            {"nome": "APIcreditOptimizer", "status": ("ativo" if api_opt else "indisponivel"), "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": 0}
        ]
        ws.send(json.dumps({
            "type": "agentes_status",
            "agentes": agentes_cards
        }))
        # Dashboard financeiro (exemplo: dados do EcoFinance)
        financeiro_html = f"<div><strong>Receita:</strong> R$ 1000<br><strong>Despesa:</strong> R$ 400<br><strong>ROI:</strong> 150%</div>"
        ws.send(json.dumps({
            "type": "financeiro",
            "graficos": financeiro_html
        }))
        # Histórico de falhas detalhado para filtragem
        logs = []
        try:
            with open('../logs/evolution_20250919.json') as f:
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
        # Exemplo de log info/warning
        logs.append({"nivel": "info", "agente": "EcoFinance", "mensagem": "Operação financeira concluída.", "timestamp": datetime.now().isoformat()})
        logs.append({"nivel": "warning", "agente": "APIcreditOptimizer", "mensagem": "Limite de requisições próximo do máximo.", "timestamp": datetime.now().isoformat()})
        ws.send(json.dumps({
            "type": "historico",
            "logs": logs
        }))
        # Mapa de tarefas (exemplo: ciclo de evolução)
        try:
            with open('../memoria_curto_prazo.json') as f:
                memoria = json.load(f)
            mapa_html = f"<div><strong>Ciclo:</strong> {memoria.get('ciclo',0)}<br><strong>Evolução:</strong> {memoria.get('evolucao',{})}</div>"
        except Exception:
            mapa_html = "<div>Mapa indisponível</div>"
        ws.send(json.dumps({
            "type": "mapa_tarefas",
            "mapa": mapa_html
        }))
        # Configurações (API Keys)
        config_html = f"<strong>API Keys:</strong> {len(api_keys_mem)} cadastradas. <button>Gerenciar</button>"
        ws.send(json.dumps({
            "type": "config",
            "config": config_html,
            "api_keys": api_keys_mem
        }))
        time.sleep(2)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


# Forçando novo deploy no Render


