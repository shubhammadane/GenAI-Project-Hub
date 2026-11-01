"""Persistent per-question cache for Stage 2 surprisal scores.

The HF scorer is expensive and its scores depend only on the text + model, not on
the keep ratio. run_eval binds the question id before squeezing and the wrapper
stores one entry per (question id, scorer name), so the model runs once per
question instead of once per ratio.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from context_squeezer.scorers import Scorer


class CachedScorer(Scorer):
    def __init__(self, base: Scorer, path: str | Path):
        self.base = base
        self.name = base.name
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}
        self._key = None
        self.hits = 0
        self.misses = 0

    def bind(self, key: str) -> None:
        self._key = str(key)

    def _key_now(self) -> str:
        return f"{self._key}|{self.name}"

    def score(self, text: str, spans: list[tuple[int, int]]) -> list[float]:
        key = self._key_now()
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
        record = self.data.get(key)
        if record and record.get("text") == digest and len(record.get("scores", [])) == len(spans):
            self.hits += 1
            return record["scores"]
        self.misses += 1
        scores = self.base.score(text, spans)
        self.data[key] = {"text": digest, "scores": scores}
        return scores

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data))
