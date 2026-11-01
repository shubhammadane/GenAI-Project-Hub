"""Language-model scorer tests.

These download and run a small causal LM (Qwen2.5-0.5B by default), so they are
skipped when torch/transformers are unavailable. Override the model with the
SQUEEZER_TEST_HF_MODEL environment variable.
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from context_squeezer.linguistic import TOKEN_RE


def _hf_available() -> bool:
    import importlib.util

    return importlib.util.find_spec("torch") is not None and importlib.util.find_spec("transformers") is not None


TEXT = (
    "The daily report said that the system works and the value is stable in the table. "
    "However the chromodynamics renormalization and the epistemology of photosynthesis remain unclear. "
    "The measurement in 1987 recorded 384752 events and 42 samples."
)
PREDICTABLE = ["the", "that", "and", "is", "in", "said", "works"]
RARE = ["chromodynamics", "renormalization", "epistemology", "photosynthesis"]


@unittest.skipUnless(_hf_available(), "torch/transformers not installed")
class HFScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from context_squeezer import HFScorer

        cls.scorer = HFScorer(os.environ.get("SQUEEZER_TEST_HF_MODEL", "Qwen/Qwen2.5-0.5B"))

    def _surprisals(self):
        spans = [(m.start(), m.end()) for m in TOKEN_RE.finditer(TEXT)]
        values = self.scorer.score(TEXT, spans)
        return [(TEXT[a:b], v) for (a, b), v in zip(spans, values)]

    def test_predictable_words_are_cheaper_than_rare_words_and_numbers(self):
        scored = self._surprisals()
        by_word = {}
        for word, value in scored:
            by_word.setdefault(word.strip(".,").lower(), []).append(value)

        def mean(words):
            vals = [v for w in words for v in by_word.get(w, [])]
            self.assertTrue(vals, f"no scores found for {words}")
            return sum(vals) / len(vals)

        predictable = mean(PREDICTABLE)
        rare = mean(RARE)
        numbers = mean(["1987", "384752", "42"])
        self.assertLess(predictable, rare,
                        f"predictable={predictable:.2f} should be below rare={rare:.2f}")
        self.assertLess(predictable, numbers,
                        f"predictable={predictable:.2f} should be below numbers={numbers:.2f}")

    def test_every_span_gets_a_finite_score(self):
        # Covers windowing: the text is long enough to need more than one window.
        long_text = (TEXT + " ") * 12
        spans = [(m.start(), m.end()) for m in TOKEN_RE.finditer(long_text)]
        values = self.scorer.score(long_text, spans)
        self.assertEqual(len(values), len(spans))
        self.assertTrue(all(v >= 0 and v == v for v in values))
        self.assertTrue(any(v > 0 for v in values))


if __name__ == "__main__":
    unittest.main()
