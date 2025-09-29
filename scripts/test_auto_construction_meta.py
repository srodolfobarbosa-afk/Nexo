import json
import logging
from core.auto_construction import AutoConstructionModule


def llm_stub(prompt, context):
    """
    Retorna uma resposta JSON simulada que instrui o módulo a usar auto-construction.
    """
    simulated = {
        "action": "auto_construct",
        "agent_name": "AgenteTeste",
        "description": "Criar um agente teste mínimo que retorne OK",
        "requirements": ["arquivo: agentes/test_agent.py", "metodo: handle"],
        "response": "Entendido. Vou construir a funcionalidade.",
        "use_auto_construction": True
    }
    return json.dumps(simulated)


def run_smoke():
    logging.basicConfig(level=logging.INFO)
    ac = AutoConstructionModule(llm_stub)
    res = ac.auto_construct_from_meta("Contexto de teste: validar criação de agente.", "Criar AgenteTeste", allow_deploy=False)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_smoke()
