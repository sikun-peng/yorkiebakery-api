# app/ai/interpret.py

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You convert natural food requests into structured filters.
Return JSON ONLY. If a field is not specified, return null.
Fields:
- origin (e.g., french, japanese, thai, chinese)
- category (e.g., dessert, drink, pastry, bread, entree)
- flavor_profiles (single keyword like sweet, nutty, spicy)
- dietary_features (vegan, vegetarian, gluten_free, contains_dairy)
- price_max (number or null)
- price_min (number or null)
"""

def interpret_message(message: str) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content

    # Convert model JSON string → python dict
    if isinstance(raw, str):
        raw = json.loads(raw)

    return raw


def parse_query_filters(message: str) -> dict:
    """
    Converts natural language → structured filters using OpenAI.
    Ensures that the return value is always a valid dict and normalized.
    """

    try:
        raw = interpret_message(message)

        return {
            "origin": raw.get("origin"),
            "category": raw.get("category"),
            "flavor_profiles": raw.get("flavor_profiles"),
            "dietary_features": raw.get("dietary_features"),
            "price_max": raw.get("price_max"),
            "price_min": raw.get("price_min"),
        }

    except Exception as e:
        print("interpret error → fallback", e)
        return {}