# app/ai/rag.py

from typing import Dict, Any, Optional, List
from app.ai.emb_model import embed_text
from app.ai.vecstore import get_collection


# ---------------------------------------------------------------
# BUILD CHROMA WHERE CLAUSE
# ---------------------------------------------------------------
def build_where(filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert UI filters into ChromaDB where clause.
    Works correctly with your metadata format.
    """

    if not filters:
        return None

    conditions = []

    for field, value in filters.items():
        if value is None:
            continue

        # Price ranges
        if field == "price_max":
            conditions.append({"price": {"$lte": value}})

        elif field == "price_min":
            conditions.append({"price": {"$gte": value}})

        # Origin, category (exact matches)
        elif field in ("origin", "category"):
            conditions.append({field: value})

        # These fields are stored as comma-separated string
        elif field in ("flavor_profiles", "dietary_features"):
            # convert to lowercase for consistency
            cond = {field: {"$contains": value.lower()}}
            conditions.append(cond)

    if not conditions:
        return None

    return {"$and": conditions}


# ---------------------------------------------------------------
# MAIN RAG RETRIEVAL FUNCTION
# ---------------------------------------------------------------
def retrieve_with_filters(query: str, filters: dict = None, top_k: int = 5):
    """
    Vector retrieval with optional filters.
    Returns: dict with ids, metadatas, distances
    """

    # Compute vector
    embedding = embed_text(query)
    if embedding is None:
        return {"ids": [], "metadatas": [], "distances": []}

    collection = get_collection()
    where = build_where(filters)

    # Query chroma
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where,
        include=["ids", "metadatas", "distances"],
    )

    # Guarantee consistent shape
    return {
        "ids": results.get("ids", [[]])[0],
        "metadatas": results.get("metadatas", [[]])[0],
        "distances": results.get("distances", [[]])[0],
    }