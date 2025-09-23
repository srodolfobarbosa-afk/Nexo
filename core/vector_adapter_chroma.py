"""Adapter to use Chroma if available, otherwise fallback to in-memory VectorStore.
"""
import logging
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except Exception:
    CHROMA_AVAILABLE = False

from .vector_store import VectorStore

log = logging.getLogger('vector_adapter')

class VectorAdapter:
    def __init__(self, dim: int = 1536):
        self.dim = dim
        if CHROMA_AVAILABLE:
            try:
                self.client = chromadb.Client(Settings())
                self.collection = self.client.create_collection('nexo')
                log.info('Chroma client initialized')
            except Exception:
                log.exception('Failed to init Chroma; using fallback')
                self.collection = None
                self.store = VectorStore(dim=dim)
        else:
            log.info('Chroma not available; using in-memory vector store')
            self.collection = None
            self.store = VectorStore(dim=dim)

    def add(self, id: str, vector, metadata: dict = None):
        if self.collection:
            try:
                self.collection.add(ids=[id], embeddings=[vector], metadatas=[metadata or {}])
                return
            except Exception:
                log.exception('Chroma add failed; falling back')
        self.store.add(id, vector, metadata)

    def search(self, vector, top_k: int = 5):
        if self.collection:
            try:
                res = self.collection.query(query_embeddings=[vector], n_results=top_k)
                return res
            except Exception:
                log.exception('Chroma query failed; falling back')
        return self.store.search(vector, top_k=top_k)
