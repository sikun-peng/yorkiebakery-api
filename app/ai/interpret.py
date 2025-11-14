# app/ai/interpret.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You convert natural food requests into structured filters.
Return JSON ONLY. If a field is not specified, return null.
Fields:
- origin (e.g., french, japanese, thai, chinese)
- category (e.g., dessert, drink, pastry, bread, entree)
- flavor_profile (word like sweet, nutty, spicy, light, rich)
- dietary_restrictions (string or null)
- price_max (number or null)
"""

def interpret_message(message: str) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content