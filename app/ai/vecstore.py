# Disable Chroma telemetry BEFORE importing chromadb
import os
os.environ["ANONYMIZED_TELEMETRY"] = "FALSE"
os.environ["CHROMADB_TELEMETRY"] = "FALSE"
os.environ["OTEL_SDK_DISABLED"] = "true"

import chromadb
from chromadb.config import Settings

CHROMA_PATH = os.getenv("CHROMA_PATH", "app/ai/vector_store")

_client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(
        allow_reset=True,
        anonymized_telemetry=False
    )
)

def get_collection():
    return _client.get_or_create_collection(
        name="menu_items",
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,
    )