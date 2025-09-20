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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_supabase_client
from agentes.NexoGenesis import NexoGenesisAgent
from agentes.EcoFinance import EcoFinanceAgent
from agentes.APIcreditOptimizer import APIcreditOptimizer

app = Flask(__name__, static_folder="../app/static", static_url_path="/static")
sock = Sock(app)

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@sock.route('/ws')
def ws(ws):
    # Instanciar agentes reais
    nexo = NexoGenesisAgent()
    eco = EcoFinanceAgent()
    api_opt = APIcreditOptimizer()
    supabase = get_supabase_client()
    while True:
        # Monitor visual dividido em 3 partes
        monitor_htmls = [
            f"<div><strong>Status NexoGenesis:</strong> {nexo.get_status()['nexo_genesis']}</div>",
            f"<div><strong>EcoFinance:</strong> Receita R$ 1000, Despesa R$ 400</div>",
            f"<div><strong>APIcreditOptimizer:</strong> Requests: {api_opt.monitor_api_usage('dummy').get('requests',0)}</div>"
        ]
        ws.send(json.dumps({
            "type": "monitor",
            "content": monitor_htmls
        }))
        # Status dos agentes (CPU/RAM reais do sistema)
        agentes_cards = [
            {"nome": "NexoGenesis", "status": nexo.get_status()['nexo_genesis'], "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": nexo.get_status().get('missoes_processadas', 0)},
            {"nome": "EcoFinance", "status": "ativo", "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": 0},
            {"nome": "APIcreditOptimizer", "status": "ativo", "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "tarefasHora": 0}
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
        # Histórico de falhas (exemplo: leitura de logs)
        falhas = []
        try:
            with open('../logs/evolution_20250919.json') as f:
                for line in f:
                    if 'failed' in line:
                        falhas.append(line)
        except Exception:
            pass
        historico_html = f"<span style='color:red'>{len(falhas)} falhas críticas</span>, <span style='color:green'>98% sucesso</span>"
        ws.send(json.dumps({
            "type": "historico",
            "historico": historico_html
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
        api_keys = [k for k in os.environ.keys() if 'KEY' in k]
        config_html = f"<strong>API Keys:</strong> {len(api_keys)} cadastradas. <button>Gerenciar</button>"
        ws.send(json.dumps({
            "type": "config",
            "config": config_html
        }))
        time.sleep(2)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
