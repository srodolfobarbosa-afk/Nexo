from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import LangChain + FAISS-based implementation
try:
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.docstore.document import Document
    _LANGCHAIN_AVAILABLE = True
except Exception:
    HuggingFaceEmbeddings = None
    FAISS = None
    Document = None
    _LANGCHAIN_AVAILABLE = False

# Try to import ChromaDB as an optional fallback implementation
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    _CHROMADB_AVAILABLE = True
except Exception:
    chromadb = None
    Settings = None
    embedding_functions = None
    _CHROMADB_AVAILABLE = False


class VectorMemory:
    """Primary VectorMemory API.

    This class intentionally requires LangChain + FAISS. If those
    dependencies are not present, instantiating `VectorMemory()` will
    raise RuntimeError. Tests and upstream code depend on this behavior.
    """

    def __init__(self, embedding_model: Optional[str] = None):
        if not _LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain/FAISS não está instalado. Instale as dependências no requirements.")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model or "sentence-transformers/all-MiniLM-L6-v2")
        self.store = FAISS(embedding_function=self.embeddings.embed_query, index=None)

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None):
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


class ChromaVectorMemory:
    """Optional Chromadb-based implementation.

    This is exposed separately as `ChromaVectorMemory`. It will only be
    functional when chromadb is installed and configured.
    """

    def __init__(self, collection_name: str = "nexo_memory"):
        if not _CHROMADB_AVAILABLE:
            raise RuntimeError("chromadb não está disponível. Instale chromadb para usar ChromaVectorMemory.")
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def salvar_ideia(self, texto: str, metadados: Optional[Dict[str, Any]] = None) -> str:
        embedding = self.embedding_fn([texto])[0]
        doc_id = str(hash(texto))
        self.collection.add(
            embeddings=[embedding],
            documents=[texto],
            ids=[doc_id],
            metadatas=[metadados or {}]
        )
        return doc_id

    def buscar_similaridade(self, consulta: str, k: int = 3):
        embedding = self.embedding_fn([consulta])[0]
        resultados = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        docs = resultados.get("documents", [])
        metas = resultados.get("metadatas", [])
        return list(zip(docs, metas))
