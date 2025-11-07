import os
import pickle
import numpy as np
import faiss
import boto3
from openai import OpenAI

from sqlmodel import Session, select
from app.core.db import engine
from app.models.postgres.menu import MenuItem

# ----------------------------
# Configuration (env variables)
# ----------------------------
S3_BUCKET = os.environ["S3_BUCKET"]
S3_INDEX_KEY = os.environ.get("S3_INDEX_KEY", "embeddings/index.faiss")
S3_META_KEY = os.environ.get("S3_META_KEY", "embeddings/metadata.pkl")
EMB_MODEL = os.environ.get("EMB_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
s3 = boto3.client("s3")

# ------------------------------------
# Step 1 — Load Menu Items from DB
# ------------------------------------
def load_menu_items():
    with Session(engine) as session:
        items = session.exec(select(MenuItem)).all()
        return items

# ------------------------------------
# Step 2 — Generate Embeddings
# ------------------------------------
def embed_text(text: str):
    embedding = client.embeddings.create(
        model=EMB_MODEL,
        input=text
    ).data[0].embedding
    return np.array(embedding, dtype="float32")

def build_vectors(items):
    vectors = []
    metadata = []
    documents = []

    for item in items:
        text = f"{item.title}. {item.description}. Tags: {', '.join(item.tags or [])}"
        vec = embed_text(text)
        vectors.append(vec)
        metadata.append({"id": str(item.id), "title": item.title, "description": item.description})
        documents.append(text)

    vectors = np.vstack(vectors).astype("float32")
    return vectors, metadata, documents

# ------------------------------------
# Step 3 — Build FAISS Index
# ------------------------------------
def build_faiss_index(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index

# ------------------------------------
# Step 4 — Upload to S3
# ------------------------------------
def upload_to_s3(index, metadata, documents):
    # Write FAISS index to memory
    idx_writer = faiss.MemoryIOWriter()
    index.write(idx_writer)
    index_bytes = idx_writer.data

    # Upload FAISS index
    s3.put_object(Bucket=S3_BUCKET, Key=S3_INDEX_KEY, Body=index_bytes)

    # Upload metadata
    bundle = {"meta": metadata, "docs": documents}
    meta_bytes = pickle.dumps(bundle)
    s3.put_object(Bucket=S3_BUCKET, Key=S3_META_KEY, Body=meta_bytes)

    print(f"✅ Uploaded index + metadata to s3://{S3_BUCKET}/embeddings/")

# ------------------------------------
# MAIN
# ------------------------------------
def main():
    print("📦 Loading menu items from DB...")
    items = load_menu_items()
    if not items:
        print("⚠️ No menu items found in database.")
        return

    print(f"🍰 Found {len(items)} menu items.")
    print("🔢 Generating embeddings...")
    vectors, metadata, documents = build_vectors(items)

    print("📚 Building FAISS index...")
    index = build_faiss_index(vectors)

    print("☁️ Uploading to S3...")
    upload_to_s3(index, metadata, documents)

    print("✅ Done! Yorkie AI index is built and uploaded.")

if __name__ == "__main__":
    main()