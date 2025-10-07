import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from langchain.docstore.document import Document
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
except Exception:
    # LangChain/FAISS missing -> tests expect RuntimeError when instantiating VectorMemory
    HuggingFaceEmbeddings = None
    FAISS = None
    Document = None


class VectorMemory:
    """Simple vector memory layer using LangChain + FAISS.

    If LangChain/FAISS are not available, initialization raises RuntimeError.
    """

    def __init__(self, embedding_model: Optional[str] = None):
        if HuggingFaceEmbeddings is None or FAISS is None:
            raise RuntimeError(
                "LangChain/FAISS not installed. Install the requirements."
            )
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model or "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.store = FAISS(embedding_function=self.embeddings.embed_query, index=None)

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        metadata = metadata or {}
        doc = Document(page_content=text, metadata=metadata)
        self.store.add_documents([doc])
        logger.info("Document added to vector memory")

    def query(self, query_text: str, k: int = 4) -> List[Dict[str, Any]]:
        results = self.store.similarity_search_with_score(query_text, k=k)
        out: List[Dict[str, Any]] = []
        for doc, score in results:
            out.append(
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                }
            )
        return out


# Optional Chromadb-based implementation (independent from LangChain).
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except Exception:
    chromadb = None


class ChromadbVectorMemory:
    """Vector memory implementation using Chroma/Chromadb.

    Use this class when chromadb is available.
    """

    def __init__(self, collection_name: str = "nexo_memory"):
        if chromadb is None:
            raise RuntimeError("chromadb not installed")
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def save_idea(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        embedding = self.embedding_fn([text])[0]
        doc_id = str(hash(text))
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            ids=[doc_id],
            metadatas=[metadata or {}],
        )
        return doc_id

    def query_similar(self, query: str, k: int = 3):
        embedding = self.embedding_fn([query])[0]
        results = self.collection.query(query_embeddings=[embedding], n_results=k)
        docs = results.get("documents", [])
        metas = results.get("metadatas", [])
        return list(zip(docs, metas))
