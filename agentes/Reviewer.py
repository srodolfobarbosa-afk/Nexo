class Reviewer:
    def __init__(self):
        self.name = 'Reviewer'
        from core.api_search import APISearch
        self.api_search = APISearch()

    def falar(self, problema):
        return f"Reviewer analisou: {problema}"
