# app/ai/agent_router.py

import json
from typing import List

from app.ai.interpret import interpret_message
from app.ai.rag import retrieve_with_filters
from app.ai.chat_model import chat_response
from app.ai.trace_models import AIDebugTrace, ParsedFilters, RetrievedItem


def _parse_filters(raw_json: str) -> ParsedFilters:
    """
    interpret_message returns a JSON string.
    We parse it into ParsedFilters.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        data = {}

    # Normalize flavor_profiles to list
    fp = data.get("flavor_profiles")
    if isinstance(fp, str):
        fp = [fp]
    elif fp is None:
        fp = None

    return ParsedFilters(
        origin=data.get("origin"),
        category=data.get("category"),
        flavor_profiles=fp,
        dietary_features=data.get("dietary_features"),
        price_max=data.get("price_max"),
    )


def _filters_to_chroma_where(parsed: ParsedFilters) -> dict:
    where = {}
    if parsed.origin:
        where["origin"] = parsed.origin
    if parsed.category:
        where["category"] = parsed.category
    if parsed.dietary_features:
        # Simple “contains substring” style. You can refine later.
        where["dietary_features"] = {"$contains": parsed.dietary_features}
    # You can’t directly do numeric comparisons with Chroma where yet,
    # so price_max can be handled in Python after retrieval.
    return where


def _choose_agent(user_message: str, filters: ParsedFilters) -> str:
    """
    Extremely simple routing logic. You can improve later.
    """
    msg_lower = user_message.lower()

    # If we have any structured filters -> recommendation use case
    if any([
        filters.origin,
        filters.category,
        filters.flavor_profiles,
        filters.dietary_features,
        filters.price_max is not None,
    ]):
        return "RecommendationAgent"

    # Keywords: recommendation / suggest / something
    if any(k in msg_lower for k in ["recommend", "suggest", "something to eat", "what should i get"]):
        return "RecommendationAgent"

    # Could later add NutritionAgent, PriceAgent, etc.
    return "ChatAgent"


def run_ai_pipeline(user_message: str, top_k: int = 5) -> AIDebugTrace:
    """
    Main entry point for the AI Demo.
    - Parses filters via LLM
    - Chooses an agent
    - Does retrieval (if needed)
    - Calls LLM for final response
    - Returns a full debug trace
    """
    # 1) Interpret message into filters
    raw_filter_json_str = interpret_message(user_message)
    parsed_filters = _parse_filters(raw_filter_json_str)

    # 2) Choose agent
    agent = _choose_agent(user_message, parsed_filters)

    # 3) Retrieve candidates (if agent needs them)
    retrieved_raw = []
    if agent == "RecommendationAgent":
        where = _filters_to_chroma_where(parsed_filters)
        retrieved_raw = retrieve_with_filters(user_message, filters=where, top_k=top_k)

        # Apply price_max filter in Python
        if parsed_filters.price_max is not None:
            max_price = parsed_filters.price_max
            retrieved_raw = [
                r for r in retrieved_raw
                if r.get("price") is None or r["price"] <= max_price
            ]

    retrieved_items: List[RetrievedItem] = []
    for r in retrieved_raw:
        retrieved_items.append(
            RetrievedItem(
                id=str(r.get("id", "")) if "id" in r else "",
                title=r.get("title", ""),
                origin=r.get("origin") or None,
                category=r.get("category") or None,
                price=r.get("price"),
                tags=(r.get("tags", "") or "").split(",") if r.get("tags") else [],
                flavor_profiles=(r.get("flavor_profiles", "") or "").split(",") if r.get("flavor_profiles") else [],
                dietary_features=(r.get("dietary_features", "") or "").split(",") if r.get("dietary_features") else [],
            )
        )

    # 4) Build system prompt with context
    context_lines = []
    for item in retrieved_items:
        context_lines.append(
            f"- {item.title} (${item.price or 'N/A'}) "
            f"[origin={item.origin}, category={item.category}, "
            f"flavors={','.join(item.flavor_profiles)}, "
            f"diet={','.join(item.dietary_features)}]"
        )

    context_block = "\n".join(context_lines) if context_lines else "No menu items were retrieved."

    system_prompt = f"""
You are Yorkie Bakery's helpful AI assistant.

The user is asking: "{user_message}"

You have access to the following candidate menu items:

{context_block}

Instructions:
- If candidate items are available, base your recommendations on them.
- Be specific about item names and why they match the user's taste.
- If no items are available, suggest what type of items they might like in general.
- Keep the answer concise and friendly.
"""

    # 5) Final LLM answer
    final_answer = chat_response(system_prompt=system_prompt, user_message=user_message)

    return AIDebugTrace(
        user_message=user_message,
        agent=agent,
        filters=parsed_filters,
        retrieved_items=retrieved_items,
        llm_system_prompt=system_prompt.strip(),
        llm_final_answer=final_answer,
        raw_filter_json=json.loads(raw_filter_json_str),
        notes="First version of AI demo pipeline with simple agent routing.",
    )