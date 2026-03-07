import sqlite3
from datetime import datetime

DB_PATH = "jarvis_memory.db"


def init_db():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_text TEXT,
        action TEXT,
        response TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_memory(user_text, action, response):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history (user_text, action, response, timestamp)
    VALUES (?, ?, ?, ?)
    """, (user_text, action, response, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_last_commands(limit=5):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_text FROM history
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    return [r[0] for r in rows]