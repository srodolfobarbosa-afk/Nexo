"""Vector store stub: provides a simple in-memory fallback and an interface
to plug an actual vector DB (Chroma, Weaviate, Pinecone).
"""
from typing import List, Dict
import numpy as np

class VectorStore:
    def __init__(self, dim: int = 1536):
        self.dim = dim
        self.store = []  # list of (id, vector, metadata)

    def add(self, id: str, vector: List[float], metadata: Dict = None):
        self.store.append((id, np.array(vector, dtype=float), metadata or {}))

    def search(self, query_vector: List[float], top_k: int = 5):
        q = np.array(query_vector, dtype=float)
        scores = []
        for id, v, m in self.store:
            # cosine similarity
            denom = (np.linalg.norm(q) * np.linalg.norm(v)) or 1e-9
            score = float(np.dot(q, v) / denom)
            scores.append((id, score, m))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
