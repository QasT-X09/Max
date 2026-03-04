from __future__ import annotations

from pathlib import Path


class SandboxViolationError(PermissionError):
    """Raised when access to a path is outside allowed sandbox."""


class SandboxSecurityLayer:
    def __init__(self, allowed_directory: Path):
        self.allowed_directory = allowed_directory.resolve()

    def resolve_safe_path(self, user_path: str | Path) -> Path:
        candidate = Path(user_path)
        if not candidate.is_absolute():
            candidate = self.allowed_directory / candidate
        resolved = candidate.resolve()
        self._assert_in_sandbox(resolved)
        return resolved

    def _assert_in_sandbox(self, path: Path) -> None:
        if self.allowed_directory == path:
            return
        if self.allowed_directory not in path.parents:
            raise SandboxViolationError(
                f"Path '{path}' is outside ALLOWED_DIRECTORY '{self.allowed_directory}'"
            )

    def ensure_parent(self, user_path: str | Path) -> Path:
        path = self.resolve_safe_path(user_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
