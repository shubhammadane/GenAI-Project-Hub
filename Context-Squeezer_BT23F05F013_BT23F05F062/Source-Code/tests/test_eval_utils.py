"""Lightweight tests for the new eval helpers (no network, no models)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from context_squeezer.scorers import Scorer
from eval.data import _to_example
from eval.scoring_cache import CachedScorer


class _CountingScorer(Scorer):
    name = "counting"

    def __init__(self):
        self.calls = 0

    def score(self, text, spans):
        self.calls += 1
        return [1.0 + i for i in range(len(spans))]


class DataParsingTests(unittest.TestCase):
    def test_official_and_hf_context_formats_match(self):
        official = _to_example({"id": "a", "question": "q", "answer": "x",
                                "context": [["Title", ["one.", "two."]]]}, 0)
        hf = _to_example({"id": "a", "question": "q", "answer": "x",
                          "context": {"title": ["Title"], "sentences": [["one.", "two."]]}}, 0)
        self.assertEqual(official.passages, hf.passages)
        self.assertEqual(official.passages, ["Title: one. two."])


class ScoringCacheTests(unittest.TestCase):
    def test_scores_are_reused_for_the_same_question(self):
        base = _CountingScorer()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cache.json"
            cache = CachedScorer(base, path)
            cache.bind("q1")
            first = cache.score("hello world", [(0, 5), (6, 11)])
            second = cache.score("hello world", [(0, 5), (6, 11)])
            self.assertEqual(first, second)
            self.assertEqual(base.calls, 1)
            self.assertEqual(cache.hits, 1)
            cache.save()

            other_base = _CountingScorer()
            reloaded = CachedScorer(other_base, path)
            reloaded.bind("q1")
            self.assertEqual(reloaded.score("hello world", [(0, 5), (6, 11)]), first)
            self.assertEqual(other_base.calls, 0)

    def test_different_questions_are_not_shared(self):
        base = _CountingScorer()
        with tempfile.TemporaryDirectory() as tmp:
            cache = CachedScorer(base, Path(tmp) / "cache.json")
            cache.bind("q1")
            cache.score("hello", [(0, 5)])
            cache.bind("q2")
            cache.score("hello", [(0, 5)])
            self.assertEqual(base.calls, 2)


if __name__ == "__main__":
    unittest.main()
