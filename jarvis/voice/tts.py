from __future__ import annotations

import io

import pyttsx3
from openai import OpenAI


class TTS:
    def __init__(self, engine_name: str = "pyttsx3", openai_api_key: str | None = None):
        self.engine_name = engine_name
        self.local_engine = pyttsx3.init() if engine_name == "pyttsx3" else None
        self.openai_client = OpenAI(api_key=openai_api_key) if engine_name == "openai" and openai_api_key else None

    def speak(self, text: str) -> bytes | None:
        if self.engine_name == "pyttsx3":
            assert self.local_engine is not None
            self.local_engine.say(text)
            self.local_engine.runAndWait()
            return None

        if self.engine_name == "openai":
            if self.openai_client is None:
                raise RuntimeError("OpenAI TTS requested but API key is not configured")
            response = self.openai_client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=text,
            )
            data = b"".join(chunk for chunk in response.iter_bytes())
            return io.BytesIO(data).getvalue()

        raise ValueError(f"Unsupported TTS engine: {self.engine_name}")
