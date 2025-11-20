# app/ai/emb_model.py

import os
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


def embed_text(text: str):
    text = text.strip()
    if not text:
        return None

    resp = client.embeddings.create(
        model=MODEL_NAME,
        input=text
    )

    return resp.data[0].embedding