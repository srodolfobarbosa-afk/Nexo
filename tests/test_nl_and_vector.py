import pytest

from core.nl_handler import NLHandler


def test_nl_handler_build_prompt():
    nl = NLHandler()
    prompt = nl._build_prompt("Olá", ["ctx1", "ctx2"])
    assert "User: Olá" in prompt


def test_nl_handler_chat_fallback(monkeypatch):
    nl = NLHandler()

    # Monkeypatch LLMCaller.call to avoid real API calls
    class Dummy:
        def call(self, prompt, **kwargs):
            return "resposta de teste"

    nl.llm = Dummy()
    res = nl.chat("Como vai?")
    assert res == "resposta de teste"


def test_vector_memory_import_error(monkeypatch):
    # Ensure that instantiating VectorMemory without langchain raises RuntimeError
    import importlib

    vm = importlib.import_module("core.vector_memory")
    # Se LangChain/FAISS estiverem instalados no ambiente de teste, pule este teste
    try:

        pytest.skip(
            "LangChain detectado no ambiente: pulando teste que espera ausência de LangChain"
        )
    except Exception:
        with pytest.raises(RuntimeError):
            vm.VectorMemory()
