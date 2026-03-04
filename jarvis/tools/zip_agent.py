from __future__ import annotations

from pathlib import Path
import zipfile

from jarvis.security.sandbox import SandboxSecurityLayer


class ZipAgent:
    def __init__(self, sandbox: SandboxSecurityLayer):
        self.sandbox = sandbox

    def create_zip(self, source_dir: str, zip_path: str) -> str:
        safe_source = self.sandbox.resolve_safe_path(source_dir)
        safe_zip = self.sandbox.ensure_parent(zip_path)

        with zipfile.ZipFile(safe_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in safe_source.rglob("*"):
                if path.is_file():
                    arcname = path.relative_to(safe_source)
                    zf.write(path, arcname)
        return f"Created zip: {safe_zip}"

    def extract_zip(self, zip_path: str, dest_dir: str) -> str:
        safe_zip = self.sandbox.resolve_safe_path(zip_path)
        safe_dest = self.sandbox.resolve_safe_path(dest_dir)
        safe_dest.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(safe_zip, "r") as zf:
            for member in zf.namelist():
                target = (safe_dest / member).resolve()
                if safe_dest not in target.parents and target != safe_dest:
                    raise PermissionError("Zip contains path traversal payload")
            zf.extractall(safe_dest)
        return f"Extracted {safe_zip} to {safe_dest}"
