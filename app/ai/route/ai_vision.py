# app/ai/route/ai_vision.py

import base64
import re
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI

from app.ai.emb_model import embed_text
from app.ai.rag import get_collection

router = APIRouter(prefix="/ai", tags=["AI Vision"])

client = OpenAI()


class VisionMatch(BaseModel):
    id: Optional[str]
    title: str
    origin: Optional[str]
    category: Optional[str]
    price: Optional[float]
    tags: List[str]
    flavor_profiles: List[str]
    dietary_features: List[str]
    distance: Optional[float]   # NEW


class VisionResponse(BaseModel):
    vision_description: str
    matches: List[VisionMatch]


@router.post("/vision", response_model=VisionResponse)
async def analyze_image(file: UploadFile = File(...)):
    # ---------------------------------------------------------------
    # VALIDATE FILE
    # ---------------------------------------------------------------
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG and PNG images are supported.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file.",
        )

    # Encode to data URL
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{b64}"

    # ---------------------------------------------------------------
    # CALL VISION MODEL (YOUR ORIGINAL PROMPT — UNMODIFIED)
    # ---------------------------------------------------------------
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are Yorkie Bakery’s friendly vision assistant. "
                                "Look at the image and describe what type of food it MOST resembles. "
                                "You do NOT need to reject the image, even if it contains meat or is not a bakery item. "
                                "Describe it in bakery terms (shape, color, filling, texture, size) and guess what pastry or dessert it is closest to. "
                                "Examples: "
                                "- If you see a pork bun, describe it as a soft steamed or baked bun similar to Japanese or Chinese bakery buns. "
                                "- If you see a savory food, describe its closest pastry equivalent. "
                                "- If you see fruit, describe the flavor profile. "

                                "Never say “I can't assist.” "
                                "Always give a helpful 1–2 sentence bakery-style interpretation."
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vision model error: {e}",
        )

    vision_text = completion.choices[0].message.content.strip()

    # ---------------------------------------------------------------
    # NORMALIZE VISION TEXT BEFORE EMBEDDING (Critical Fix)
    # ---------------------------------------------------------------
    normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", vision_text).lower().strip()

    # handle singular/plural issues like macaron(s)
    if "macaron" in normalized and "macarons" not in normalized:
        normalized = normalized.replace("macaron", "macarons")

    vec = embed_text(normalized)
    if vec is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute embedding for the vision description.",
        )

    # ---------------------------------------------------------------
    # VECTOR SEARCH (with distances!)
    # ---------------------------------------------------------------
    collection = get_collection()
    result = collection.query(
        query_embeddings=[vec],
        n_results=5,
        include=["metadatas", "distances"],
    )

    metadatas = result["metadatas"][0]
    ids = result["ids"][0]
    distances = result["distances"][0]

    matches: List[VisionMatch] = []

    # ---------------------------------------------------------------
    # BUILD RESULTS
    # ---------------------------------------------------------------
    for i, meta in enumerate(metadatas):
        tags = (meta.get("tags") or "").split(",") if meta.get("tags") else []
        flavors = (meta.get("flavor_profiles") or "").split(",") if meta.get("flavor_profiles") else []
        diet = (meta.get("dietary_features") or "").split(",") if meta.get("dietary_features") else []

        matches.append(
            VisionMatch(
                id=ids[i],
                title=meta.get("title", "Unknown"),
                origin=meta.get("origin"),
                category=meta.get("category"),
                price=meta.get("price"),
                tags=[t for t in tags if t],
                flavor_profiles=[f for f in flavors if f],
                dietary_features=[d for d in diet if d],
                distance=float(distances[i]),
            )
        )

    # ---------------------------------------------------------------
    # OPTIONAL: Boost exact keyword matches for accuracy
    # ---------------------------------------------------------------
    key_terms = normalized.split()

    for m in matches:
        title = m.title.lower()

        # if the title contains any word from the description, boost it
        if any(k in title for k in key_terms):
            m.distance *= 0.5  # reduce distance → higher rank

    # re-sort
    matches = sorted(matches, key=lambda x: x.distance)

    return VisionResponse(
        vision_description=vision_text,
        matches=matches,
    )