from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.docstore.document import Document
except Exception:
    # Lazy import fallback for environments without langchain
    HuggingFaceEmbeddings = None
    FAISS = None
    Document = None


class VectorMemory:
    """Camada simples de memória vetorial usando LangChain + FAISS.

    - add(text, metadata) -> armazena embedding e retorna id
    - query(query_text, k=4) -> retorna k documentos mais próximos
    """

    def __init__(self, embedding_model: Optional[str] = None):
        if HuggingFaceEmbeddings is None or FAISS is None:
            raise RuntimeError("LangChain/FAISS não está instalado. Instale as dependências no requirements.")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model or "sentence-transformers/all-MiniLM-L6-v2")
        self.store = FAISS(embedding_function=self.embeddings.embed_query, index=None)

    def add(self, text: str, metadata: Dict[str, Any] | None = None):
        metadata = metadata or {}
        doc = Document(page_content=text, metadata=metadata)
        self.store.add_documents([doc])
        logger.info("Documento adicionado à memória vetorial")

    def query(self, query_text: str, k: int = 4) -> List[Dict[str, Any]]:
        results = self.store.similarity_search_with_score(query_text, k=k)
        out = []
        for doc, score in results:
            out.append({"text": doc.page_content, "metadata": doc.metadata, "score": float(score)})
        return out
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
