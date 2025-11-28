# app/ai/chat_model.py
from openai import OpenAI
from typing import List, Dict, Any, Optional

# Uses your OPENAI_API_KEY automatically
client = OpenAI()

def chat_response(
    system_prompt: str,
    user_message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generate a friendly Yorkie chat reply using GPT with optional conversation history.

    Args:
        system_prompt: System prompt to set AI behavior
        user_message: Current user message
        conversation_history: Optional list of previous messages
                             Format: [{"role": "user/assistant", "content": "..."}]

    Returns:
        AI response string
    """
    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history if provided
    if conversation_history:
        # Take only the last 10 messages (5 turns) to stay within token limits
        recent_history = conversation_history[-10:]
        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=200,
    )

    return completion.choices[0].message.content.strip()