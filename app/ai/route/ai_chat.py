# app/ai/route/ai_chat.py

from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.rag import retrieve_with_filters
from app.ai.chat_model import chat_response
from app.ai.vecstore import get_collection
from app.ai.emb_model import embed_text


router = APIRouter(prefix="/ai", tags=["AI Chat"])


class ChatRequest(BaseModel):
    message: str
    top_k: int = 5
    filters: dict = {}


def normalize(value):
    if not value:
        return []
    if isinstance(value, list):
        return [v.strip() for v in value if v.strip()]
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


def origin_emoji(origin: str):
    mapping = {
        "thai": "🇹🇭🍜",
        "chinese": "🇨🇳🥡",
        "japanese": "🇯🇵🍡",
        "korean": "🇰🇷🔥",
        "american": "🇺🇸🍪",
        "french": "🇫🇷🥐",
        "italian": "🇮🇹🍰",
        "bakery": "🧁",
        "fusion": "🌏✨",
    }
    return mapping.get((origin or "").lower(), "🍽️")


def format_yorkie_context(items):
    if not items:
        return "No matching menu items were found."

    blocks = []
    for meta in items:
        block = f"{origin_emoji(meta.get('origin'))} {meta.get('title')} — ${float(meta.get('price', 0)):.2f}\n"

        for key, label in [
            ("tags", "tags"),
            ("flavor_profiles", "flavors"),
            ("dietary_features", "dietary"),
        ]:
            vals = normalize(meta.get(key))
            if vals:
                block += f"  • {label}: {', '.join(vals)}\n"

        blocks.append(block)

    return "\n".join(blocks)


def yorkie_prompt(message: str, ctx: str):
    return f"""
You are Yorkie 🐶 the pastry helper.

Menu Context:
{ctx}

User said: "{message}"

Reply as Yorkie:
""".strip()


@router.post("/chat")
def chat(req: ChatRequest):
    """
    Chatbot RAG endpoint — fallback mode keeps rag.py untouched.
    """

    try:
        # Normal path — exact same rag.py behavior
        rag_results = retrieve_with_filters(req.message, req.filters, top_k=req.top_k)
        items = rag_results.get("metadatas", [])
    except Exception as e:
        print(f"[WARN] ai_chat fallback (rag include issue): {e}")

        # SAFE fallback (same as /ai/demo)
        embedding = embed_text(req.message)
        col = get_collection()

        qr = col.query(
            query_embeddings=[embedding],
            n_results=req.top_k,
            include=["metadatas", "distances"],  # SAFE
        )

        items = qr.get("metadatas", [[]])[0]
        rag_results = {
            "ids": [],
            "metadatas": items,
            "distances": qr.get("distances", [[]])[0]
        }

    # Convert items → text context
    context = format_yorkie_context(items)

    # Create final Yorkie prompt
    prompt = yorkie_prompt(req.message, context)

    # LLM response
    reply = chat_response(
        system_prompt="You are Yorkie, cute pastry dog 🍪",
        user_message=prompt,
    )

    return {"reply": reply, "results": rag_results}