from core.agent_base import AgentBase


class Analyzer(AgentBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'Analyzer'
        from core.api_search import APISearch
        self.api_search = APISearch()

    def handle(self, problema):
        """Entrada principal padronizada: retorna plano de correção aprovado ou padrão."""
        response = self.llm_correction_plan(problema)
        if not isinstance(response, dict) or 'approved' not in response:
            response = self.default_correction_plan(problema)
        return {"agent": self.name, "input": problema, "plan": response}

    def llm_correction_plan(self, problema):
        return {"plan": "Corrigir X", "issues": ["Faltou chave 'approved'"]}

    def default_correction_plan(self, problema):
        return {
            "approved": True,
            "plan": f"Plano padrão para: {problema}",
            "issues": []
        }
