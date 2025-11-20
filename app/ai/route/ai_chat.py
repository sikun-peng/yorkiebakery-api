from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.rag import retrieve_with_filters
from app.ai.chat_model import chat_response

router = APIRouter(prefix="/ai", tags=["AI Chat"])

class ChatRequest(BaseModel):
    message: str
    top_k: int = 5
    filters: dict = {}


def normalize(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
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


def format_yorkie_context(results):
    if not results:
        return "No matching menu items were found."

    lines = []
    for item in results:
        title = item.get("title", "Unknown")
        price = float(item.get("price", 0))
        origin = item.get("origin", "")
        emoji = origin_emoji(origin)

        tags = normalize(item.get("tags"))
        flavors = normalize(item.get("flavor_profiles"))
        diet = normalize(item.get("dietary_features"))

        block = f"{emoji} {title} — ${price:.2f}\n"
        if tags:
            block += f"  • tags: {', '.join(tags)}\n"
        if flavors:
            block += f"  • flavors: {', '.join(flavors)}\n"
        if diet:
            block += f"  • dietary: {', '.join(diet)}\n"

        lines.append(block)

    return "\n".join(lines)


def yorkie_prompt(message: str, cute_context: str):
    return f"""
You are Yorkie 🐶, the cutest bakery puppy helper.

Your job:
- Read the menu context
- Recommend items the user will love
- Be playful, warm, and friendly — BUT still specific

Menu Context:
{cute_context}

User asked: "{message}"

Now answer as Yorkie:
"""


@router.post("/chat")
def chat(req: ChatRequest):
    # 1. Vector search
    results = retrieve_with_filters(req.message, req.filters, top_k=req.top_k)

    # 2. Build Yorkie context + prompt
    cute_context = format_yorkie_context(results)
    prompt = yorkie_prompt(req.message, cute_context)

    # 3. LLM reply
    reply = chat_response(
        system_prompt="You are Yorkie, the adorable pastry-recommending bakery dog.",
        user_message=prompt,
    )

    return {
        "reply": reply,
        "results": results,
    }