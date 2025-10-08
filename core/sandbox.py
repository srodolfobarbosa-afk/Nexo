"""Helpers para importação sandboxes de módulos de agentes.

Este helper executa um processo Python separado que tenta carregar o módulo
e extrair um símbolo (por exemplo `Agent`), retornando um JSON com resultado.

Nota: isto NÃO substitui uma sandbox kernel-level (container/seccomp). Para
proteção completa, execute o import dentro de um container isolado.
"""
import json
import shlex
import subprocess
import sys
import os
from typing import Dict, Any


def sandbox_import_module(module_path: str, symbol: str = "Agent", timeout: int = 5) -> Dict[str, Any]:
    """Tenta importar module_path em subprocess e busca o símbolo `symbol`.

    Retorna dict: {ok: bool, name: str|None, error: str|None}
    """
    if not os.path.exists(module_path):
        return {"ok": False, "error": "module_not_found"}

    # construímos um pequeno snippet Python que tenta carregar o módulo e inspecionar o símbolo
    snippet = f"""
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('dynamic_agent_sandbox', r'{module_path}')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sym = None
for name in ['{symbol}', 'Agent', 'create_agent', 'AgentClass']:
    if hasattr(mod, name):
        sym = getattr(mod, name)
        break
if sym is None:
    print(json.dumps({{'ok': False, 'error': 'no_agent_symbol'}}))
    sys.exit(0)
try:
    nm = sym.__name__ if hasattr(sym, '__name__') else str(type(sym))
    print(json.dumps({{'ok': True, 'name': nm}}))
except Exception as e:
    print(json.dumps({{'ok': False, 'error': str(e)}}))
"""

    cmd = [sys.executable, "-c", snippet]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = proc.stdout.strip()
        if not out:
            return {"ok": False, "error": "no_output", "stderr": proc.stderr}
        try:
            obj = json.loads(out)
            return obj
        except Exception:
            return {"ok": False, "error": "invalid_json_output", "raw": out}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
