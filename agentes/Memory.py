class Memory:
    def __init__(self):
        self.name = 'Memory'
        from core.api_search import APISearch
        self.api_search = APISearch()

    def falar(self, problema):
        return f"Memory analisou: {problema}"
