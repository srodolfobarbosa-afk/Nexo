import importlib
import pytest

def test_nexogenesis_import():
    """Verifica se o NexoGenesis carrega sem erro."""
    try:
        import agentes.NexoGenesis
    except Exception as e:
        pytest.fail(f"NexoGenesis não carregou: {e}")

def test_agente_resposta():
    """Simula uma resposta de agente"""
    from agentes.NexoGenesis import NexoGenesisAgent
    agente = NexoGenesisAgent()
    resposta = agente.processar("teste simples")
    assert isinstance(resposta, str)
    assert len(resposta) > 0

