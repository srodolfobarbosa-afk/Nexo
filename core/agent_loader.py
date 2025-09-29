"""Descobre e registra agentes do pacote `agentes` de forma tolerante.

Função principal: `discover_and_register_all()` — tenta importar todos os módulos
em `agentes`, busca classes que herdam de `core.agent_base.AgentBase`, tenta
instanciá-las e registra via `core.agent_registry.register_agent_instance`.
"""
import importlib
import inspect
import pkgutil
import sys
from typing import List

from core.agent_base import AgentBase
from core.agent_registry import register_agent, register_agent_instance


def discover_and_register_all():
    """Descobre módulos em pacote `agentes` e registra instâncias ou placeholders."""
    try:
        import agentes
    except Exception as e:
        # pacote não encontrado
        register_agent('agentes_package', {'status': 'error', 'error': f'cannot_import_agentes: {e}'})
        return

    pkg_path = getattr(agentes, '__path__', None)
    if not pkg_path:
        return

    for finder, name, ispkg in pkgutil.iter_modules(pkg_path):
        full_name = f"agentes.{name}"
        try:
            mod = importlib.import_module(full_name)
        except Exception as e:
            # register module as error placeholder
            register_agent(name, {'status': 'error', 'error': f'import_error: {e}'})
            continue

        # inspect module for AgentBase subclasses
        for obj_name, obj in inspect.getmembers(mod, inspect.isclass):
            try:
                if obj is AgentBase:
                    continue
                if issubclass(obj, AgentBase):
                    agent_name = getattr(obj, 'name', obj.__name__)
                    try:
                        inst = obj()
                        register_agent_instance(inst, {'status': 'idle'})
                    except Exception as e:
                        # if instantiation fails, register error
                        register_agent(agent_name, {'status': 'error', 'error': str(e)})
            except TypeError:
                # obj is not inspectable as subclass
                continue
