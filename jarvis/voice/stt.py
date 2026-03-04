from __future__ import annotations

from pathlib import Path

import whisper


class WhisperSTT:
    def __init__(self, model_name: str = "small"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str | Path, language: str = "ru") -> str:
        result = self.model.transcribe(str(audio_path), language=language)
        return result.get("text", "").strip()
