import chromadb
from chromadb.config import Settings
import os

CHROMA_PATH = os.getenv("CHROMA_PATH", "app/ai/vector_store")

_client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(allow_reset=True)
)

def get_collection():
    """Return the persistent ChromaDB collection used for menu embeddings."""
    return _client.get_or_create_collection(
        name="menu_items",
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,
    )