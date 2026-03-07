import sqlite3
import ollama
from datetime import datetime

DB_PATH = "jarvis_memory.db"
MODEL = "llama3"

def init_reflection_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reflections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        action TEXT,
        result TEXT,
        reflection TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def reflect(task, action, result):

    prompt = f"""
Проанализируй выполнение задачи ассистента.

Задача пользователя:
{task}

Выполненное действие:
{action}

Результат:
{result}

Ответь кратко:
1. Успешно ли выполнена задача?
2. Что можно улучшить?
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    reflection_text = response["message"]["content"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reflections (task, action, result, reflection, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (task, action, result, reflection_text, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return reflection_text