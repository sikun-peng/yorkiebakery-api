# app/ai/chat_model.py
from openai import OpenAI

# Uses your OPENAI_API_KEY automatically
client = OpenAI()

def chat_response(system_prompt: str, user_message: str) -> str:
    """
    Generate a friendly Yorkie chat reply using GPT.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=200,
    )

    return completion.choices[0].message.content.strip()