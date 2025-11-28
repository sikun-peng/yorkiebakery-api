# app/ai/filters.py
from typing import Dict, Any, List, Optional


# ============================================================
# Build ChromaDB "where" filter (vector DB pre-filtering)
# ============================================================
def build_where(filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert interpreted filters → ChromaDB where clause.
    Handles:
        - price_max → {"price": {"$lte": value}}
        - price_min → {"price": {"$gte": value}}
        - origin/category → exact match
        - flavor_profiles/dietary_features → array contains
    """
    if not filters:
        return None

    conditions = []

    for key, value in filters.items():
        if value is None:
            continue

        # ---- Price filters ----
        if key == "price_max":
            conditions.append({"price": {"$lte": value}})
            continue

        if key == "price_min":
            conditions.append({"price": {"$gte": value}})
            continue

        # ---- Exact fields ----
        if key in ("origin", "category"):
            conditions.append({key: value})
            continue

        # ---- Array membership ----
        if key in ("flavor_profiles", "dietary_features"):
            if isinstance(value, str) and value.strip():
                conditions.append({key: {"$contains": value}})
            continue

    if not conditions:
        return None

    return {"$and": conditions}


# ============================================================
# Strict backend filter (after vector retrieval)
# ============================================================
def apply_all_filters(items: List[dict], filters: Dict[str, Any]) -> List[dict]:
    """
    Apply strict backend filtering AFTER vector retrieval.
    Supports:
      - price_min
      - price_max
      - origin
      - category
      - flavor_profiles (list contains)
      - dietary_features (list contains)
    """

    if not filters:
        return items

    def match(item: dict) -> bool:

        # ---- Price filters ----
        if filters.get("price_min") is not None:
            if item.get("price") is None or item["price"] < filters["price_min"]:
                return False

        if filters.get("price_max") is not None:
            if item.get("price") is None or item["price"] > filters["price_max"]:
                return False

        # ---- Exact match fields ----
        for key in ("origin", "category"):
            if filters.get(key):
                if item.get(key) != filters[key]:
                    return False

        # ---- List fields ----
        for key in ("flavor_profiles", "dietary_features"):
            f = filters.get(key)
            if f:
                arr = item.get(key, [])

                # Convert CSV string to list
                if isinstance(arr, str):
                    arr = [x.strip() for x in arr.split(",")]

                if f not in arr:
                    return False

        return True

    return [i for i in items if match(i)]