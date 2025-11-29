# app/ai/preference_extractor.py

import re
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI

client = OpenAI()


# Keyword mappings for preference extraction
FLAVOR_KEYWORDS = {
    "fruity": ["fruity", "fruit", "fresh fruit", "tropical"],
    "sweet": ["sweet", "sugary", "candy"],
    "savory": ["savory", "salty"],
    "creamy": ["creamy", "cream", "rich"],
    "light": ["light", "airy", "fluffy"],
    "chocolate": ["chocolate", "chocolatey", "cocoa"],
    "nutty": ["nutty", "almond", "hazelnut", "pistachio"],
    "citrus": ["citrus", "lemon", "orange", "lime"],
    "berry": ["berry", "strawberry", "blueberry", "raspberry"],
    "matcha": ["matcha", "green tea"],
    "coffee": ["coffee", "espresso", "mocha"],
    "vanilla": ["vanilla"],
    "caramel": ["caramel", "toffee"],
}

DIETARY_KEYWORDS = {
    "vegetarian": ["vegetarian", "veggie"],
    "vegan": ["vegan", "plant-based"],
    "gluten-free": ["gluten-free", "gluten free", "no gluten"],
    "dairy-free": ["dairy-free", "dairy free", "no dairy", "lactose free"],
    "nut-free": ["nut-free", "nut free", "no nuts"],
    "low-sugar": ["low sugar", "less sugar", "sugar-free"],
}

AVOID_KEYWORDS = {
    "nuts": ["no nuts", "avoid nuts", "without nuts", "nut allergy"],
    "dairy": ["no dairy", "avoid dairy", "without dairy", "lactose intolerant"],
    "gluten": ["no gluten", "avoid gluten", "without gluten"],
    "eggs": ["no eggs", "avoid eggs", "without eggs"],
    "sugar": ["no sugar", "avoid sugar", "less sweet"],
}

CATEGORY_KEYWORDS = {
    "pastry": ["pastry", "pastries", "baked goods"],
    "drink": ["drink", "drinks", "beverage", "beverages"],
    "cake": ["cake", "cakes"],
    "cookie": ["cookie", "cookies"],
    "dessert": ["dessert", "desserts"],
}


def extract_personal_context(message: str) -> Dict[str, Any]:
    """
    Extract personal context from message using LLM (names, etc.)

    Args:
        message: User message text

    Returns:
        Dictionary with personal context like {"name": "Spencer"}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Extract personal information from the user's message.
Only extract clear, explicit information. Return JSON with these optional fields:
- "name": user's name if mentioned (e.g., "my name is Spencer" -> "Spencer")

Return empty {} if no personal information is found.
Examples:
"hi my name is spencer" -> {"name": "Spencer"}
"I love chocolate" -> {}
"call me John" -> {"name": "John"}"""
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=50,
        )

        result = json.loads(response.choices[0].message.content)
        # Only return if there's actual data
        return result if result else {}
    except Exception as e:
        # Silently fail - personal context extraction is nice-to-have
        return {}


def extract_preferences(message: str) -> Dict[str, List[str]]:
    """
    Extract user preferences from a message using keyword matching.

    Args:
        message: User message text

    Returns:
        Dictionary with extracted preferences:
        {
            "flavors": [...],
            "dietary": [...],
            "avoid": [...],
            "categories": [...],
            "name": "..." (optional)
        }
    """
    message_lower = message.lower()
    preferences = {
        "flavors": [],
        "dietary": [],
        "avoid": [],
        "categories": []
    }

    # Extract flavors
    for flavor, keywords in FLAVOR_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            preferences["flavors"].append(flavor)

    # Extract dietary preferences
    for dietary, keywords in DIETARY_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            preferences["dietary"].append(dietary)

    # Extract things to avoid
    for avoid_item, keywords in AVOID_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            preferences["avoid"].append(avoid_item)

    # Extract category preferences
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            preferences["categories"].append(category)

    # Extract personal context (name, etc.) using LLM
    personal_context = extract_personal_context(message)
    if personal_context:
        preferences.update(personal_context)

    # Remove empty lists (but keep string values like name)
    preferences = {k: v for k, v in preferences.items() if v}

    return preferences


def format_preferences_for_context(preferences: Dict[str, Any]) -> str:
    """
    Format preferences into a human-readable string for context.

    Args:
        preferences: Dictionary of preferences

    Returns:
        Formatted string
    """
    if not preferences:
        return ""

    lines = []

    # Personal context (name)
    if preferences.get("name"):
        lines.append(f"Customer name: {preferences['name']}")

    if preferences.get("flavors"):
        lines.append(f"Prefers flavors: {', '.join(preferences['flavors'])}")

    if preferences.get("dietary"):
        lines.append(f"Dietary needs: {', '.join(preferences['dietary'])}")

    if preferences.get("avoid"):
        lines.append(f"Avoids: {', '.join(preferences['avoid'])}")

    if preferences.get("categories"):
        lines.append(f"Interested in: {', '.join(preferences['categories'])}")

    if preferences.get("last_viewed"):
        items = preferences["last_viewed"][-3:]  # Last 3 items
        lines.append(f"Recently viewed: {', '.join(items)}")

    return "\n".join(lines)


def merge_preferences(
    existing: Dict[str, Any],
    new: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge new preferences with existing ones, avoiding duplicates.

    Args:
        existing: Existing preferences dictionary
        new: New preferences to merge

    Returns:
        Merged preferences dictionary
    """
    merged = existing.copy() if existing else {}

    for key, values in new.items():
        # Handle string values (like name)
        if isinstance(values, str):
            merged[key] = values
            continue

        if key not in merged:
            merged[key] = []

        if isinstance(merged[key], list):
            # Add only unique values
            existing_set = set(merged[key])
            for value in values:
                if value not in existing_set:
                    merged[key].append(value)
        else:
            merged[key] = values

    return merged
