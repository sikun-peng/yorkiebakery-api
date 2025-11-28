from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.interpret import parse_query_filters
from app.ai.rag import retrieve_with_filters
from app.ai.filters import apply_all_filters
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai/demo")


class DemoRequest(BaseModel):
    message: str


@router.post("")
def ai_demo(request: DemoRequest):
    """
    Handles general AI menu queries (RAG text-based search).
    Steps:
      1️⃣ Extract filters using LLM
      2️⃣ Perform vector retrieval
      3️⃣ Apply backend filtering (price/origin/flavor)
      4️⃣ Return structured response for the React Debug Panel
    """

    # 1️⃣ Parse user query into filters (price, category, etc.)
    parsed_filters = parse_query_filters(request.message)

    # 2️⃣ Retrieve from Chroma (no filters yet)
    # Use try/except to ensure invalid includes don't break the pipeline
    try:
        vector_items = retrieve_with_filters(
            query=request.message,
            filters=None,    # disable Chroma filtering initially
            top_k=50         # retrieve more for filtering
        )
    except ValueError as e:
        # If "ids" or other invalid include keys cause error, log and retry clean
        logger.warning(f"Chroma query failed: {e}. Retrying with safe include set.")
        from app.ai.vecstore import get_collection
        from app.ai.emb_model import embed_text

        collection = get_collection()
        embedding = embed_text(request.message)

        vector_items = collection.query(
            query_embeddings=[embedding],
            n_results=50,
            include=["metadatas", "distances"],  # ✅ only valid include keys
        )

        # unify structure
        vector_items = vector_items.get("metadatas", [[]])[0]

    # 3️⃣ Apply backend filters
    final_items = apply_all_filters(vector_items, parsed_filters)

    # 4️⃣ Return full debug payload
    return {
        "query": request.message,
        "filters": parsed_filters,
        "items": final_items,
        "raw_vector_results": vector_items,
    }