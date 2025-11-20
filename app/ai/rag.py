from typing import List, Dict, Any
from app.ai.emb_model import embed_text
from app.ai.vecstore import get_collection

def retrieve_with_filters(query: str, filters: dict = None, top_k: int = 5):
    collection = get_collection()

    q_emb = embed_text(query)

    if q_emb is None:
        return []

    where = {"$and": []}

    if filters:
        for key, val in filters.items():
            if val:
                where["$and"].append({key: val})

    if not where["$and"]:
        where = None

    res = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        where=where,
        include=["metadatas", "distances"],
    )

    metas = res.get("metadatas", [[]])[0]
    return metas