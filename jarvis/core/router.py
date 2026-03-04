from __future__ import annotations

import json
from typing import Any

import requests
from openai import OpenAI

from jarvis.core.classifier import TaskClassifier


class LLMRouter:
    def __init__(
        self,
        classifier: TaskClassifier,
        complexity_threshold: int,
        ollama_url: str,
        ollama_model: str,
        openai_model: str,
        openai_api_key: str | None,
    ):
        self.classifier = classifier
        self.complexity_threshold = complexity_threshold
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model
        self.openai_model = openai_model
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

    def choose_backend(self, task: str) -> str:
        return "openai" if self.classifier.is_complex(task, self.complexity_threshold) else "ollama"

    def generate(self, task: str, system_prompt: str) -> str:
        backend = self.choose_backend(task)
        if backend == "openai" and self.openai_client:
            return self._generate_openai(task, system_prompt)
        return self._generate_ollama(task, system_prompt)

    def _generate_ollama(self, task: str, system_prompt: str) -> str:
        payload = {
            "model": self.ollama_model,
            "format": "json",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task},
            ],
            "stream": False,
        }
        response = requests.post(f"{self.ollama_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data["message"]["content"]

    def _generate_openai(self, task: str, system_prompt: str) -> str:
        assert self.openai_client is not None
        response = self.openai_client.responses.create(
            model=self.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task},
            ],
            response_format={"type": "json_object"},
        )
        text = response.output_text
        # Guard against accidental non-JSON wrapper
        json.loads(text)
        return text
