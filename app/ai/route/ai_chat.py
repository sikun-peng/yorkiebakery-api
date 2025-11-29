# app/ai/route/ai_chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.ai.rag import retrieve_with_filters
from app.ai.chat_model import chat_response
from app.ai.vecstore import get_collection
from app.ai.emb_model import embed_text
from app.ai.session_manager import (
    get_or_create_session,
    add_message,
    get_conversation_history,
    update_preferences,
    get_session_preferences,
)
from app.ai.preference_extractor import (
    extract_preferences,
    format_preferences_for_context,
    merge_preferences,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/ai", tags=["AI Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
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


def yorkie_prompt(message: str, ctx: str, preferences_text: str = ""):
    """Build Yorkie prompt with context and preferences"""
    pref_section = f"\nUser Preferences:\n{preferences_text}\n" if preferences_text else ""

    return f"""
You are Yorkie 🐶 the pastry helper.

Menu Context:
{ctx}
{pref_section}
User said: "{message}"

Reply as Yorkie:
""".strip()


@router.post("/chat")
def chat(req: ChatRequest):
    """
    Chatbot RAG endpoint with session memory and preference tracking.
    """

    # 1. Get or create session
    session = get_or_create_session(session_id=req.session_id)
    session_id = session.session_id

    # 2. Extract preferences from user message
    new_prefs = extract_preferences(req.message)
    if new_prefs:
        update_preferences(session_id, new_prefs)

    # 3. Get current preferences
    current_prefs = get_session_preferences(session_id)

    # 4. Get conversation history (increased from 10 to 20 for better context)
    history = get_conversation_history(session_id, limit=20)

    # 5. Retrieve menu items using RAG
    try:
        # Normal path — exact same rag.py behavior
        rag_results = retrieve_with_filters(req.message, req.filters, top_k=req.top_k)
        items = rag_results.get("metadatas", [])
    except Exception as e:
        logger.warning(f"RAG fallback - include issue: {e}")

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

    # 6. Track viewed items
    item_titles = [item.get("title") for item in items if item.get("title")]
    if item_titles:
        if "last_viewed" not in current_prefs:
            current_prefs["last_viewed"] = []
        # Keep only unique + last 10 items
        for title in item_titles:
            if title not in current_prefs["last_viewed"]:
                current_prefs["last_viewed"].append(title)
        current_prefs["last_viewed"] = current_prefs["last_viewed"][-10:]
        update_preferences(session_id, current_prefs)

    # 7. Convert items → text context
    context = format_yorkie_context(items)

    # 8. Format preferences for context
    preferences_text = format_preferences_for_context(current_prefs)

    # 9. Create final Yorkie prompt
    prompt = yorkie_prompt(req.message, context, preferences_text)

    # 10. Save user message to history
    add_message(session_id, "user", req.message)

    # 11. LLM response with conversation history
    reply = chat_response(
        system_prompt="""You are Yorkie 🐶, the friendly pastry assistant for Yorkie Bakery.

Your personality:
- Warm, helpful, and enthusiastic about pastries
- Remember personal details users share (names, occasions, preferences)
- Reference previous conversations naturally
- Be conversational and genuine

Your responsibilities:
- Help customers find the perfect pastries based on their preferences
- Remember what they've viewed and discussed before
- Suggest items that match their tastes and needs
- Keep responses concise (2-3 sentences max)

Important: Pay attention to the conversation history and user preferences provided. Use this context to give personalized, relevant recommendations.""",
        user_message=prompt,
        conversation_history=history,
    )

    # 12. Save AI response to history
    add_message(session_id, "assistant", reply, metadata={
        "items_shown": item_titles[:5],  # Top 5 items
        "filters_used": req.filters,
    })

    return {
        "reply": reply,
        "results": rag_results,
        "session_id": session_id,
        "preferences": current_prefs,
    }