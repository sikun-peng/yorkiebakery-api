import os, pickle
import boto3
import faiss
import numpy as np
from openai import OpenAI

S3_BUCKET   = os.environ["S3_BUCKET"]
S3_INDEX_KEY= os.environ.get("S3_INDEX_KEY", "embeddings/index.faiss")
S3_META_KEY = os.environ.get("S3_META_KEY",  "embeddings/metadata.pkl")
EMB_MODEL   = os.environ.get("EMB_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
s3 = boto3.client("s3")

# Load FAISS + metadata at import time → only once (cold start optimization)
idx_bytes = s3.get_object(Bucket=S3_BUCKET, Key=S3_INDEX_KEY)["Body"].read()
_index = faiss.read_index(faiss.MemoryIOReader(idx_bytes))

meta_bytes = s3.get_object(Bucket=S3_BUCKET, Key=S3_META_KEY)["Body"].read()
_bundle = pickle.loads(meta_bytes)
_META = _bundle["meta"]
_DOCS = _bundle["docs"]

def embed(text: str):
    vec = client.embeddings.create(model=EMB_MODEL, input=[text]).data[0].embedding
    return np.array([vec], dtype="float32")

def search(query: str, k: int = 4):
    q = embed(query)
    D, I = _index.search(q, k)
    results = []
    for idx in I[0]:
        if 0 <= idx < len(_META):
            results.append(_META[idx])
    return results