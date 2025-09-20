class Executor:
    def __init__(self):
        self.name = 'Executor'
        from core.api_search import APISearch
        self.api_search = APISearch()

    def falar(self, problema):
        return f"Executor analisou: {problema}"
