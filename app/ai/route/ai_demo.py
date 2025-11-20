from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.rag import retrieve_with_filters

router = APIRouter(prefix="/ai/demo")

class DemoRequest(BaseModel):
    message: str
    origin: str | None = None
    category: str | None = None

@router.post("")
def ai_demo(request: DemoRequest):
    # Build filters for ChromaDB
    filters = {}
    if request.origin:
        filters["origin"] = request.origin
    if request.category:
        filters["category"] = request.category

    # Run retrieval
    items = retrieve_with_filters(
        query=request.message,
        filters=filters,
        top_k=5
    )

    return {
        "query": request.message,
        "filters": filters,
        "items": items
    }