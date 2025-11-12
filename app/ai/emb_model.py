# app/ai/emb_model.py
import os
from openai import OpenAI

# Load OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "text-embedding-3-small"  # cheap + good

def embed_text(text: str):
    """
    Returns a vector embedding for a text string.
    """
    text = text.strip()
    if not text:
        return None

    resp = client.embeddings.create(
        model=MODEL_NAME,
        input=text
    )

    return resp.data[0].embedding