"""Run with:  python -m unittest discover -s tests -v   (from the project root)"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from context_squeezer import Squeezer, SqueezeConfig
from context_squeezer.tokens import count_tokens
from eval.baselines import random_drop, truncate
from eval.data import load_hotpot
from eval.metrics import exact_match, f1_score
from eval.readers import ExtractiveReader

TEXT = (
    "Furthermore, it is worth noting that the Brindle Harbour lighthouse was automated in 1987, "
    "after which the last keeper left the island. "
    "The weather on the island is basically very mild and quite pleasant in most of the year. "
    "The server did not respond within 30 seconds, and the retry limit was 5.\n\n"
    "Moreover, the harbour authority, as previously stated, does not allow vessels longer than 40 metres "
    "to dock after 22:00."
)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.sq = Squeezer()

    def test_full_keep_only_removes_filler(self):
        r = self.sq.squeeze(TEXT, keep_ratio=1.0)
        self.assertNotIn("Furthermore", r.squeezed)
        self.assertNotIn("as previously stated", r.squeezed)
        self.assertIn("1987", r.squeezed)
        self.assertLessEqual(r.squeezed_tokens, r.original_tokens)

    def test_budget_is_respected(self):
        for ratio in (0.7, 0.5, 0.3):
            r = self.sq.squeeze(TEXT, question="When was the lighthouse automated?", keep_ratio=ratio)
            self.assertTrue(r.budget_met, ratio)
            self.assertLessEqual(r.squeezed_tokens, r.budget_tokens)

    def test_numbers_and_negations_survive_word_pruning(self):
        r = self.sq.squeeze(TEXT, keep_ratio=0.6, use_sentence_ranking=False)
        for must in ("1987", "30", "not", "40", "22:00"):
            self.assertIn(must, r.squeezed)

    def test_without_protection_can_lose_them(self):
        a = self.sq.squeeze(TEXT, keep_ratio=0.35, use_sentence_ranking=False, protect=True)
        b = self.sq.squeeze(TEXT, keep_ratio=0.35, use_sentence_ranking=False, protect=False)
        self.assertIn("not", a.squeezed)
        self.assertLessEqual(b.squeezed_tokens, a.squeezed_tokens + 3)

    def test_question_steers_sentence_choice(self):
        a = self.sq.squeeze(TEXT, question="When was the lighthouse automated?", keep_ratio=0.3,
                            use_word_pruning=False)
        b = self.sq.squeeze(TEXT, question="How long until the server stops retrying?", keep_ratio=0.3,
                            use_word_pruning=False)
        self.assertIn("1987", a.squeezed)
        self.assertIn("retry", b.squeezed)

    def test_ablation_flags_disable_stages(self):
        r = self.sq.squeeze(TEXT, keep_ratio=0.3, use_filter=False, use_word_pruning=False,
                            use_sentence_ranking=False)
        self.assertEqual(r.squeezed.split(), TEXT.split())

    def test_segments_reassemble_original_text(self):
        r = self.sq.squeeze(TEXT, keep_ratio=0.4)
        self.assertEqual("".join(s["t"] for s in r.segments), TEXT)
        self.assertEqual({s["s"] for s in r.segments} - {"kept", "filler", "entropy", "sentence", "punct"}, set())

    def test_list_of_passages_and_empty_input(self):
        r = self.sq.squeeze(["First passage here.", "Second passage here."], keep_ratio=1.0)
        self.assertIn("\n", r.squeezed)
        e = self.sq.squeeze("", keep_ratio=0.5)
        self.assertEqual(e.squeezed, "")

    def test_to_dict_is_json_serialisable(self):
        import json
        json.dumps(self.sq.squeeze(TEXT, keep_ratio=0.5).to_dict())


class EvalTests(unittest.TestCase):
    def test_metrics(self):
        self.assertEqual(exact_match("The Harrowgate Group", "harrowgate group"), 1.0)
        self.assertAlmostEqual(f1_score("Marta Okonkwo", "Okonkwo"), 2 / 3)
        self.assertEqual(f1_score("", "x"), 0.0)

    def test_baselines_meet_budget(self):
        words = " ".join(f"word{i}" for i in range(200))
        budget = count_tokens(words) // 3
        self.assertLessEqual(count_tokens(truncate(words, budget)), budget)
        self.assertLessEqual(count_tokens(random_drop(words, budget)), budget)

    def test_sample_data_loads_and_reader_runs(self):
        data = load_hotpot(Path(__file__).resolve().parent.parent / "eval" / "sample_data.json")
        self.assertEqual(len(data), 6)
        ans = ExtractiveReader().answer(data[0].question, data[0].context_text)
        self.assertEqual(ans, "1987")


class ServerTests(unittest.TestCase):
    def test_api(self):
        try:
            import server
        except ImportError:
            self.skipTest("flask not installed")
        c = server.app.test_client()
        ok = c.post("/api/squeeze", json={"context": TEXT, "keep_ratio": 0.5})
        self.assertEqual(ok.status_code, 200)
        self.assertIn("squeezed", ok.get_json())
        self.assertEqual(c.post("/api/squeeze", json={"context": " "}).status_code, 400)
        self.assertEqual(c.post("/api/squeeze", json={"context": "a", "keep_ratio": "x"}).status_code, 400)
        self.assertEqual(c.get("/").status_code, 200)


if __name__ == "__main__":
    unittest.main()
