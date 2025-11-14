# app/routes/ai.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.rag import retrieve_with_filters
from app.ai.chat_model import chat_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    top_k: int = 5
    filters: dict = {}


def normalize(value):
    """
    Ensure metadata values always become lists of readable strings.
    Handles:
    - already-a-list → keep
    - string → split by comma
    - None → empty list
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [v for v in value if v]

    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]

    return []


def origin_emoji(origin: str):
    emojis = {
        "thai": "🇹🇭🍜",
        "chinese": "🇨🇳🥡",
        "japanese": "🇯🇵🍣",
        "korean": "🇰🇷🔥",
        "american": "🇺🇸🍔",
        "french": "🇫🇷🥐",
        "italian": "🇮🇹🍝",
        "bakery": "🧁",
    }
    return emojis.get((origin or "").lower(), "🍽️")


def format_cute_results(results):
    if not results:
        return "🥺 *sniff sniff…* I couldn’t find anything tasty this time. Try another craving? 🐾"

    response = "🐶 **Woof! Wag wag!! I found some delicious treats for you!** ✨\n\n"

    for item in results:
        title = item.get("title", "Unknown Item")
        price = float(item.get("price", 0.0))
        origin = item.get("origin", "")
        emoji = origin_emoji(origin)

        tags = normalize(item.get("tags"))
        flavors = normalize(item.get("flavor_profile"))
        diet = normalize(item.get("dietary_restrictions"))

        response += f"{emoji} **{title}** — ${price:.2f}\n"

        if tags:
            response += f"   🍥 Tags: {', '.join(tags)}\n"
        if flavors:
            response += f"   🌈 Flavor vibes: {', '.join(flavors)}\n"
        if diet:
            response += f"   🥗 Dietary-friendly: {', '.join(diet)}\n"

        response += "\n"

    response += "🐾 Just tell me what you're craving next! *tail wags excitedly* ✨"
    return response


@router.post("/ai/chat")
def chat(req: ChatRequest):
    results = retrieve_with_filters(req.message, req.filters, top_k=req.top_k)

    pretty_text = format_cute_results(results)

    llm_reply = chat_response(
        system_prompt="You are Yorkie, a friendly bakery pup who describes menu items with joy.",
        user_message=f"User asked: {req.message}\nMenu suggestions:\n{pretty_text}"
    )

    return {
        "reply": llm_reply,
        "results": results
    }