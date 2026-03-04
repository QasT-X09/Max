from __future__ import annotations


class WakeWordDetector:
    def __init__(self, wake_word: str):
        self.wake_word = wake_word.lower().strip()

    def is_activated(self, text: str) -> bool:
        return self.wake_word in text.lower()
