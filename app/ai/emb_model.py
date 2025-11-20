# app/ai/emb_model.py

import os
import re
from dotenv import load_dotenv

# Always load .env when this module is imported
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)
print("🔑 Loaded .env for emb_model from:", ENV_PATH)

from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
print("DEBUG API KEY IN emb_model:", api_key)

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY is missing. Check your .env file.")

client = OpenAI(api_key=api_key)

MODEL_NAME = "text-embedding-3-small"


# ---------------------------------------------------------------
# CLEAN + NORMALIZE TEXT BEFORE EMBEDDING  (CRITICAL FIX)
# ---------------------------------------------------------------
def _normalize(text: str) -> str:
    # Normalize whitespace & lowercase
    text = text.lower().strip()

    # Remove extra punctuation (embedding noise)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Special-case bakery singular/plural issues
    if "macaron" in text and "macarons" not in text:
        text = text.replace("macaron", "macarons")

    return text.strip()


def embed_text(text: str):
    if not text:
        return None

    # --- normalize BEFORE embedding ---
    text = _normalize(text)

    if not text:
        return None

    # Safety: prevent extremely long raw text from hurting vector quality
    if len(text) > 2048:
        text = text[:2048]

    resp = client.embeddings.create(
        model=MODEL_NAME,
        input=text
    )

    return resp.data[0].embedding