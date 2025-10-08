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


def import_and_register_module(module_path: str, instance_name: str = "Agent"):
    """Importa um módulo Python a partir de um caminho de arquivo e registra uma instância.

    Busca o símbolo `instance_name` (por padrão `Agent`) no módulo. Se for uma classe ou
    uma função que retorna um objeto, instancia e registra via register_agent_instance.

    Retorna um dicionário com {'registered': True/False, 'name': <agent_name>, 'error': <msg?>}
    """
    import importlib.util
    import os

    try:
        if not os.path.exists(module_path):
            return {"registered": False, "error": "module_not_found"}

        spec = importlib.util.spec_from_file_location("dynamic_agent", module_path)
        if spec is None:
            return {"registered": False, "error": "spec_failed"}
        mod = importlib.util.module_from_spec(spec)
        loader = spec.loader
        if loader is None:
            return {"registered": False, "error": "no_loader"}
        loader.exec_module(mod)

        if not hasattr(mod, instance_name):
            # fallback: try common names
            for cand in ("Agent", "create_agent", "AgentClass"):
                if hasattr(mod, cand):
                    obj = getattr(mod, cand)
                    break
            else:
                return {"registered": False, "error": "no_agent_symbol"}
        else:
            obj = getattr(mod, instance_name)

        # instantiate if it's a class
        instance = None
        try:
            if isinstance(obj, type):
                instance = obj()
            elif callable(obj):
                instance = obj()
            else:
                instance = obj
        except Exception:
            # if instantiation fails, keep the object as-is
            instance = obj

        # register
        try:
            register_agent_instance(instance, {"status": "imported"})
            name = getattr(instance, "name", instance.__class__.__name__)
            return {"registered": True, "name": name}
        except Exception as e:
            return {"registered": False, "error": f"register_failed: {e}"}

    except Exception as e:
        return {"registered": False, "error": str(e)}
