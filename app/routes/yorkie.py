from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from app.utils.vecstore import search

client = OpenAI()

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

def yorkie_voice(context: str, question: str):
    return f"""
You are Yorkie, the cutest bakery puppy helper 🐶🍰💗
Use this menu context to recommend items:
{context}

Customer: {question}
Yorkie:
"""

@router.post("/chat")
def chat(req: ChatRequest):
    items = search(req.question)
    context = "\n".join([f"- {i['title']}: {i['description']}" for i in items])

    msg = yorkie_voice(context, req.question)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":msg}]
    )
    return {"answer": resp.choices[0].message.content}