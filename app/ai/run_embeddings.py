# app/ai/run_embeddings.py

import os
from dotenv import load_dotenv
from chromadb import PersistentClient
from sqlmodel import Session, select

from app.core.db import engine
from app.models.postgres.menu import MenuItem
from app.ai.emb_model import embed_text


# ------------------------------------------------------------------------------
# FORCE LOAD .env FROM PROJECT ROOT NO MATTER WHERE SCRIPT IS RUN FROM
# ------------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"🔑 Loaded .env from: {ENV_PATH}")
else:
    print(f"⚠️ .env NOT FOUND at: {ENV_PATH}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("DEBUG OPENAI KEY:", OPENAI_API_KEY)


# ------------------------------------------------------------------------------
# CHROMA CONFIG
# ------------------------------------------------------------------------------
CHROMA_PATH = "app/ai/vector_store"
COLLECTION_NAME = "menu_items"


def build_embeddings():
    print("\n📦 Loading menu items from database...")

    with Session(engine) as session:
        # Embed ALL items (real + mock)
        items = session.exec(select(MenuItem)).all()

    print(f"🔄 Processing {len(items)} items for vector embeddings...\n")

    client = PersistentClient(path=CHROMA_PATH)

    # Safely delete old collection
    try:
        client.delete_collection(COLLECTION_NAME)
        print("🗑️ Old vector collection removed.")
    except Exception as e:
        print(f"ℹ️ No previous collection to remove: {e}")

    # Create new collection
    collection = client.get_or_create_collection(COLLECTION_NAME)

    ids = []
    vectors = []
    metadatas = []

    for item in items:
        text = f"{item.title} {item.description or ''}".strip()
        vec = embed_text(text)

        if vec is None:
            print(f"⚠️ Skipping item (no vector): {item.title}")
            continue

        ids.append(str(item.id))
        vectors.append(vec)

        metadatas.append({
            "title": item.title,
            "origin": item.origin or "",
            "category": item.category or "",
            "price": float(item.price) if item.price else None,
            "tags": ",".join(item.tags or []),
            "flavor_profiles": ",".join(item.flavor_profiles or []),
            "dietary_features": ",".join(item.dietary_features or []),
        })

    # Add vectors to Chroma
    collection.add(
        ids=ids,
        embeddings=vectors,
        metadatas=metadatas
    )

    print("\n✅ Embeddings built successfully!")
    print(f"📌 Total embedded items: {len(ids)}")
    print(f"💾 Stored at: {CHROMA_PATH}\n")


if __name__ == "__main__":
    build_embeddings()