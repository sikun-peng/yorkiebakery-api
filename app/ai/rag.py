# app/ai/rag.py

from chromadb import PersistentClient
from app.ai.emb_model import embed_text

CHROMA_PATH = "app/ai/vector_store"
COLLECTION_NAME = "menu_items"


def get_collection():
    client = PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)


def retrieve_with_filters(query: str, filters: dict = None, top_k: int = 5):
    collection = get_collection()
    vec = embed_text(query)
    if vec is None:
        return []

    where = {k: v for k, v in (filters or {}).items() if v}

    result = collection.query(
        query_embeddings=[vec],
        n_results=top_k,
        where=where if where else None,
    )

    return result.get("metadatas", [[]])[0]