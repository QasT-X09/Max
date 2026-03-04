from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    # Paths
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    ALLOWED_DIRECTORY: Path = field(
        default_factory=lambda: Path(os.getenv("JARVIS_ALLOWED_DIRECTORY", Path(__file__).resolve().parents[2] / "sandbox")).resolve()
    )
    LOG_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2] / "jarvis" / "logs")
    DB_PATH: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2] / "jarvis" / "memory" / "jarvis.db")
    FAISS_INDEX_PATH: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2] / "jarvis" / "memory" / "faiss.index")

    # Voice
    VOICE_MODE: bool = os.getenv("JARVIS_VOICE_MODE", "1") == "1"
    WAKE_WORD: str = os.getenv("JARVIS_WAKE_WORD", "джарвис")
    STT_MODEL_NAME: str = os.getenv("JARVIS_STT_MODEL", "small")
    TTS_ENGINE: str = os.getenv("JARVIS_TTS_ENGINE", "pyttsx3")  # pyttsx3|openai

    # LLM routing
    OLLAMA_MODEL: str = os.getenv("JARVIS_OLLAMA_MODEL", "llama3.1")
    OLLAMA_URL: str = os.getenv("JARVIS_OLLAMA_URL", "http://localhost:11434")
    OPENAI_MODEL: str = os.getenv("JARVIS_OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    COMPLEXITY_THRESHOLD: int = int(os.getenv("JARVIS_COMPLEXITY_THRESHOLD", "8"))

    # Runtime
    MAX_REPLAN_ATTEMPTS: int = int(os.getenv("JARVIS_MAX_REPLAN", "2"))
    TOP_K_MEMORY: int = int(os.getenv("JARVIS_TOP_K_MEMORY", "5"))

    def ensure_paths(self) -> None:
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.ALLOWED_DIRECTORY.mkdir(parents=True, exist_ok=True)
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_paths()
