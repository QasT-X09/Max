from __future__ import annotations

import json
from pathlib import Path

import numpy as np

try:
    import faiss
except ImportError as exc:  # pragma: no cover
    raise ImportError("faiss is required for VectorMemory. Install faiss-cpu.") from exc


class VectorMemory:
    def __init__(self, index_path: Path, dim: int = 384):
        self.index_path = index_path
        self.dim = dim
        self.meta_path = self.index_path.with_suffix(".meta.json")
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()

    def _load_or_create_index(self):
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatL2(self.dim)

    def _load_metadata(self) -> list[dict]:
        if self.meta_path.exists():
            return json.loads(self.meta_path.read_text(encoding="utf-8"))
        return []

    def _persist(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _embed(text: str, dim: int) -> np.ndarray:
        # Локальный детерминированный embedding без внешних API.
        vec = np.zeros(dim, dtype=np.float32)
        for i, ch in enumerate(text.lower()):
            vec[(ord(ch) + i) % dim] += 1.0
        norm = np.linalg.norm(vec)
        return vec if norm == 0 else vec / norm

    def add(self, text: str, payload: dict) -> int:
        vector = self._embed(text, self.dim).reshape(1, -1)
        self.index.add(vector)
        self.metadata.append({"text": text, "payload": payload})
        self._persist()
        return len(self.metadata) - 1

    def search(self, text: str, top_k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        query = self._embed(text, self.dim).reshape(1, -1)
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query, k)
        results: list[dict] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue
            item = self.metadata[idx]
            results.append(
                {
                    "id": int(idx),
                    "distance": float(dist),
                    "text": item["text"],
                    "payload": item["payload"],
                }
            )
        return results
