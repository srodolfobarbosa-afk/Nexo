"""Um registrador simples de agentes em memória.

Serve para expor estado atual dos agentes via API. Não substitui um store persistente.
"""

import logging
import threading

logger = logging.getLogger("agent_registry")

_lock = threading.Lock()
_agents = {}


def register_agent(name: str, meta: dict = None):
    with _lock:
        _agents[name] = meta or {"status": "active", "meta": {}}
        logger.info(f"Agent registered: {name}")


def register_agent_instance(agent, meta: dict = None):
    """Registra uma instância de agente (preferencialmente AgentBase).

    Aceita qualquer objeto com atributo `name` e opcional `to_dict()`.
    """
    try:
        name = getattr(agent, "name", agent.__class__.__name__)
        info = meta or {}
        if hasattr(agent, "to_dict"):
            info["meta"] = agent.to_dict()
        register_agent(name, info)
    except Exception as e:
        logger.error(f"Falha ao registrar instância de agente: {e}")


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
            _agents[name]["status"] = status
            if meta:
                _agents[name]["meta"].update(meta)
        else:
            _agents[name] = {"status": status, "meta": meta or {}}
