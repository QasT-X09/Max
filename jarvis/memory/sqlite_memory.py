from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteMemory:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    task_text TEXT NOT NULL,
                    plan_json TEXT,
                    result_text TEXT,
                    error_text TEXT,
                    strategy_text TEXT
                );

                CREATE TABLE IF NOT EXISTS kv_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def save_task(
        self,
        task_text: str,
        plan: dict[str, Any] | None,
        result_text: str | None,
        error_text: str | None,
        strategy_text: str | None,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks(task_text, plan_json, result_text, error_text, strategy_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task_text,
                    json.dumps(plan, ensure_ascii=False) if plan else None,
                    result_text,
                    error_text,
                    strategy_text,
                ),
            )
            return int(cursor.lastrowid)

    def save_kv(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO kv_memory(key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key)
                DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                """,
                (key, value),
            )

    def get_kv(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM kv_memory WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

    def recent_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
