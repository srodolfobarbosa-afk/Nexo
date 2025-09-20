class Analyzer:
    def __init__(self):
        self.name = 'Analyzer'
        from core.api_search import APISearch
        self.api_search = APISearch()

    def falar(self, problema):
        response = self.llm_correction_plan(problema)
        if not isinstance(response, dict) or 'approved' not in response:
            response = self.default_correction_plan(problema)
        return f"Analyzer analisou: {problema} | Plano: {response}"

    def llm_correction_plan(self, problema):
        return {"plan": "Corrigir X", "issues": ["Faltou chave 'approved'"]}

    def default_correction_plan(self, problema):
        return {
            "approved": True,
            "plan": f"Plano padrão para: {problema}",
            "issues": []
        }
