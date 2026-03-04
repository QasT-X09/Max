from __future__ import annotations

import json
from typing import Any

from jarvis.memory.sqlite_memory import SQLiteMemory
from jarvis.memory.vector_memory import VectorMemory


class ReflectionAgent:
    def __init__(self, sqlite_memory: SQLiteMemory, vector_memory: VectorMemory):
        self.sqlite_memory = sqlite_memory
        self.vector_memory = vector_memory

    def reflect(
        self,
        task: str,
        plan: dict[str, Any] | None,
        result: list[dict[str, Any]] | None,
        error: Exception | None,
    ) -> dict[str, Any]:
        ok_steps = 0
        total_steps = 0
        if result:
            total_steps = len(result)
            ok_steps = sum(1 for s in result if s.get("status") == "ok")

        strategy = {
            "success_ratio": (ok_steps / total_steps) if total_steps else 0,
            "recommendation": "Уточнять аргументы tool и проверять пути в sandbox"
            if error
            else "Сохранить успешный шаблон плана",
            "error": str(error) if error else None,
        }

        self.sqlite_memory.save_task(
            task_text=task,
            plan=plan,
            result_text=json.dumps(result, ensure_ascii=False) if result else None,
            error_text=str(error) if error else None,
            strategy_text=json.dumps(strategy, ensure_ascii=False),
        )
        self.vector_memory.add(
            text=task,
            payload={"plan": plan, "result": result, "strategy": strategy},
        )
        return strategy
