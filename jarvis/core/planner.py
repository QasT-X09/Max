from __future__ import annotations

import json
from typing import Any

from jarvis.core.router import LLMRouter


class PlanValidationError(ValueError):
    pass


class Planner:
    def __init__(self, router: LLMRouter, max_replans: int = 2):
        self.router = router
        self.max_replans = max_replans

    def create_plan(self, task: str) -> dict[str, Any]:
        system_prompt = (
            "Ты планировщик JSON ReAct. Верни только JSON формата: "
            '{"steps":[{"tool":"tool_name","args":{}}]}. '
            "Без markdown и комментариев."
        )
        last_error = ""
        for attempt in range(self.max_replans + 1):
            prompt_task = task if attempt == 0 else f"{task}\nИсправь план с учетом ошибки валидации: {last_error}"
            raw = self.router.generate(prompt_task, system_prompt)
            try:
                plan = json.loads(raw)
                self.validate_plan(plan)
                return plan
            except (json.JSONDecodeError, PlanValidationError) as exc:
                last_error = str(exc)
        raise PlanValidationError(f"Failed to create valid plan after replanning. Last error: {last_error}")

    @staticmethod
    def validate_plan(plan: dict[str, Any]) -> None:
        if not isinstance(plan, dict):
            raise PlanValidationError("Plan must be an object")
        steps = plan.get("steps")
        if not isinstance(steps, list) or not steps:
            raise PlanValidationError("Plan must contain non-empty 'steps' list")
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise PlanValidationError(f"Step #{i} must be an object")
            if "tool" not in step or not isinstance(step["tool"], str) or not step["tool"].strip():
                raise PlanValidationError(f"Step #{i} has invalid 'tool'")
            if "args" not in step or not isinstance(step["args"], dict):
                raise PlanValidationError(f"Step #{i} has invalid 'args'")
