from __future__ import annotations

import re


class TaskClassifier:
    COMPLEX_KEYWORDS = {
        "стратег",
        "оптимиз",
        "сравни",
        "архитект",
        "несколько",
        "долгосроч",
        "причин",
        "почему",
        "план",
        "анализ",
    }

    def estimate_complexity(self, task: str) -> int:
        words = re.findall(r"\w+", task.lower(), flags=re.UNICODE)
        score = min(10, max(1, len(words) // 3))
        keyword_hits = sum(1 for w in words if any(k in w for k in self.COMPLEX_KEYWORDS))
        score += min(4, keyword_hits)
        if any(char.isdigit() for char in task):
            score += 1
        return min(10, score)

    def is_complex(self, task: str, threshold: int) -> bool:
        return self.estimate_complexity(task) >= threshold
