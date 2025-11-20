# app/api/routes/ai_debug.py
from typing import List, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI

from app.ai.emb_model import embed_text
from app.ai.rag import get_collection

router = APIRouter(prefix="/ai", tags=["AI Debug"])

client = OpenAI()


class EmbedTestRequest(BaseModel):
    text: str
    top_k: int = 5


class Neighbor(BaseModel):
    id: Optional[str]
    title: str
    origin: Optional[str]
    category: Optional[str]
    price: Optional[float]
    distance: Optional[float]


class EmbedTestResponse(BaseModel):
    query: str
    embedding_preview: List[float]
    neighbors: List[Neighbor]


@router.post("/embed-test", response_model=EmbedTestResponse)
def embed_test(request: EmbedTestRequest):
    vec = embed_text(request.text)
    if vec is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty or invalid text for embedding.",
        )

    collection = get_collection()
    result = collection.query(
        query_embeddings=[vec],
        n_results=request.top_k,
        include=["metadatas", "ids", "distances"],
    )

    metadatas = result.get("metadatas", [[]])[0]
    ids = result.get("ids", [[]])[0] if result.get("ids") else []
    distances = result.get("distances", [[]])[0] if result.get("distances") else []

    neighbors: List[Neighbor] = []
    for idx, meta in enumerate(metadatas):
        neighbors.append(
            Neighbor(
                id=ids[idx] if idx < len(ids) else None,
                title=meta.get("title", "Unknown"),
                origin=meta.get("origin") or None,
                category=meta.get("category") or None,
                price=meta.get("price"),
                distance=distances[idx] if idx < len(distances) else None,
            )
        )

    return EmbedTestResponse(
        query=request.text,
        embedding_preview=vec[:8],
        neighbors=neighbors,
    )


class ExplainItem(BaseModel):
    title: str
    origin: Optional[str]
    category: Optional[str]
    price: Optional[float]
    flavor_profiles: List[str] = []
    dietary_features: List[str] = []


class ExplainRequest(BaseModel):
    user_message: str
    items: List[ExplainItem]


class ExplainResponse(BaseModel):
    explanations: Dict[str, str]


@router.post("/explain-recommendations", response_model=ExplainResponse)
def explain_recommendations(request: ExplainRequest):
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No items provided for explanation.",
        )

    items_text_lines = []
    for item in request.items:
        line = (
            f"- {item.title} "
            f"[origin={item.origin or 'n/a'}, "
            f"category={item.category or 'n/a'}, "
            f"price={item.price}, "
            f"flavors={','.join(item.flavor_profiles)}, "
            f"diet={','.join(item.dietary_features)}]"
        )
        items_text_lines.append(line)

    items_block = "\n".join(items_text_lines)

    system_prompt = (
        "You are Yorkie Bakery's helpful AI assistant. "
        "The user asked for some recommendation, and we already selected candidate items. "
        "Your job is to explain, in one short sentence per item, WHY each item matches the user's request. "
        "Focus on flavor, style, price, and origin where relevant."
    )

    user_prompt = (
        f"The user originally asked:\n{request.user_message}\n\n"
        f"Here are the candidate items:\n{items_block}\n\n"
        "Return a JSON object of the form:\n"
        "{\n"
        '  \"explanations\": {\n'
        '    \"Item Title 1\": \"One sentence reason...\",\n'
        '    \"Item Title 2\": \"One sentence reason...\"\n'
        "  }\n"
        "}\n"
        "Do not include anything else."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content
    try:
        data = client._client._json_loads(content)  # if this doesn't work, use normal json.loads
    except Exception:
        import json
        data = json.loads(content)

    explanations = data.get("explanations", {})

    return ExplainResponse(explanations=explanations)