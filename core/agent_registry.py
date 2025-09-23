"""Registry simples para agentes: registro em memória, healthchecks e listagem.
"""
import threading
from typing import Dict
import time

_agents: Dict[str, Dict] = {}
_lock = threading.Lock()

def register_agent(name: str, info: Dict):
    with _lock:
        _agents[name] = info.copy()

def update_agent(name: str, info: Dict):
    with _lock:
        if name in _agents:
            _agents[name].update(info)
        else:
            _agents[name] = info.copy()

def get_agents() -> Dict:
    with _lock:
        return {k: v.copy() for k, v in _agents.items()}

def deregister_agent(name: str):
    with _lock:
        _agents.pop(name, None)

def health_report() -> Dict:
    with _lock:
        now = time.time()
        report = {}
        for name, info in _agents.items():
            status = info.get('status', 'unknown')
            last_seen = info.get('last_seen', None)
            report[name] = {'status': status, 'last_seen': last_seen}
        return report
"""Um registrador simples de agentes em memória.

Serve para expor estado atual dos agentes via API. Não substitui um store persistente.
"""
import threading
import logging

logger = logging.getLogger('agent_registry')

_lock = threading.Lock()
_agents = {}


def register_agent(name: str, meta: dict = None):
    with _lock:
        _agents[name] = meta or {'status': 'active', 'meta': {}}
        logger.info(f'Agent registered: {name}')


def unregister_agent(name: str):
    with _lock:
        if name in _agents:
            del _agents[name]


def get_agents():
    with _lock:
        return dict(_agents)


def update_agent_status(name: str, status: str, meta: dict = None):
    with _lock:
        if name in _agents:
            _agents[name]['status'] = status
            if meta:
                _agents[name]['meta'].update(meta)
        else:
            _agents[name] = {'status': status, 'meta': meta or {}}
