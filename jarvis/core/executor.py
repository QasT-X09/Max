from __future__ import annotations

import logging
from typing import Any, Callable


class ToolExecutionError(RuntimeError):
    pass


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")
        self._tools[name] = fn

    def get(self, name: str) -> Callable[..., Any]:
        if name in {"python", "exec", "run_python", "eval"}:
            raise PermissionError("Arbitrary Python execution is blocked")
        if name not in self._tools:
            raise KeyError(f"Unknown tool '{name}'")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())


class Executor:
    def __init__(self, registry: ToolRegistry, logger: logging.Logger):
        self.registry = registry
        self.logger = logger

    def execute_plan(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for idx, step in enumerate(plan["steps"]):
            tool_name = step["tool"]
            args = step.get("args", {})
            self.logger.info("Executing step %s with tool=%s args=%s", idx, tool_name, args)
            try:
                tool = self.registry.get(tool_name)
                output = tool(**args)
                entry = {"step": idx, "tool": tool_name, "status": "ok", "output": output}
            except Exception as exc:
                entry = {"step": idx, "tool": tool_name, "status": "error", "error": str(exc)}
                self.logger.exception("Step failed: %s", tool_name)
                results.append(entry)
                raise ToolExecutionError(str(exc)) from exc
            results.append(entry)
        return results
