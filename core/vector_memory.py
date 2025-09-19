import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class VectorMemory:
    def __init__(self, collection_name="nexo_memory"):
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def salvar_ideia(self, texto, metadados=None):
        embedding = self.embedding_fn([texto])[0]
        doc_id = str(hash(texto))
        self.collection.add(
            embeddings=[embedding],
            documents=[texto],
            ids=[doc_id],
            metadatas=[metadados or {}]
        )
        return doc_id

    def buscar_similaridade(self, consulta, k=3):
        embedding = self.embedding_fn([consulta])[0]
        resultados = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        docs = resultados.get("documents", [])
        metas = resultados.get("metadatas", [])
        return list(zip(docs, metas))
