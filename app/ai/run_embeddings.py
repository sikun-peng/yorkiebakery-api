# app/ai/run_embeddings.py

from chromadb import PersistentClient
from sqlmodel import Session, select

from app.core.db import engine
from app.models.postgres.menu import MenuItem
from app.ai.emb_model import embed_text

CHROMA_PATH = "app/ai/vector_store"
COLLECTION_NAME = "menu_items"


def build_embeddings():
    print("📦 Loading menu items...")

    with Session(engine) as session:
        items = session.exec(
            select(MenuItem).where(MenuItem.is_available == True)
        ).all()

    print(f"🔄 Processing {len(items)} items...")

    client = PersistentClient(path=CHROMA_PATH)

    # Remove existing collection safely
    try:
        client.delete_collection(COLLECTION_NAME)
        print("🗑️ Old collection removed.")
    except:
        pass

    collection = client.get_or_create_collection(COLLECTION_NAME)

    ids = []
    embeddings = []
    metadatas = []

    for item in items:
        text = f"{item.title} {item.description or ''}".strip()
        vec = embed_text(text)
        if vec is None:
            continue

        ids.append(str(item.id))
        embeddings.append(vec)

        metadatas.append({
            "title": item.title,
            "origin": item.origin or "",
            "category": item.category or "",
            "price": float(item.price) if item.price else None,
            "tags": ",".join(item.tags or []),
            "flavor_profile": ",".join(item.flavor_profile or []),
            "dietary_restrictions": ",".join(item.dietary_restrictions or []),
        })

    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("✅ Embeddings built successfully!")
    print(f"💾 Stored in {CHROMA_PATH}")


if __name__ == "__main__":
    build_embeddings()