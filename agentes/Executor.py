from core.agent_base import AgentBase


class Executor(AgentBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'Executor'
        from core.api_search import APISearch
        self.api_search = APISearch()

    def handle(self, problema):
        return {"agent": self.name, "input": problema, "result": f"Executor analisou: {problema}"}
