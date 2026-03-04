from __future__ import annotations

from pathlib import Path

from jarvis.security.sandbox import SandboxSecurityLayer


class FileSystemAgent:
    def __init__(self, sandbox: SandboxSecurityLayer):
        self.sandbox = sandbox

    def write_text(self, file_path: str, content: str) -> str:
        safe_path = self.sandbox.ensure_parent(file_path)
        safe_path.write_text(content, encoding="utf-8")
        return f"Written file: {safe_path}"

    def read_text(self, file_path: str) -> str:
        safe_path = self.sandbox.resolve_safe_path(file_path)
        return safe_path.read_text(encoding="utf-8")

    def list_dir(self, dir_path: str = ".") -> list[str]:
        safe_dir = self.sandbox.resolve_safe_path(dir_path)
        if not safe_dir.is_dir():
            raise NotADirectoryError(str(safe_dir))
        return [p.name for p in safe_dir.iterdir()]

    def delete_file(self, file_path: str) -> str:
        safe_path = self.sandbox.resolve_safe_path(file_path)
        safe_path.unlink(missing_ok=False)
        return f"Deleted: {safe_path}"
