import ollama
import json

MODEL = "llama3"

SYSTEM_PROMPT = """
Ты планировщик действий для ассистента.
Верни ТОЛЬКО JSON без текста.

Формат:
{
  "action": "tool_name",
  "args": {}
}

Доступные действия:
- open_calculator
- open_browser
- answer
"""

def plan_action(user_text: str):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    content = response["message"]["content"].strip()

    try:
        data = json.loads(content)
    except Exception:
        data = {"action": "answer", "args": {"text": content}}

    return data