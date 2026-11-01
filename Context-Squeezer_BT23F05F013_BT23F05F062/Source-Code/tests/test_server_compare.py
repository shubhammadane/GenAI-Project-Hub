import os
import unittest
from unittest import mock

from context_squeezer.tokens import count_tokens

TEXT = (
    "The Eiffel Tower is in Paris. It was completed in 1889 for the World's Fair. "
    "The tower is made of iron and stands 330 metres tall. Visitors can climb it. "
    "The Louvre is also in Paris. It holds the Mona Lisa. "
    "The Seine runs through the city. Many people walk along its banks. "
)
KEY = "sk-test-secret-do-not-leak"
ENV = {"LLM_BASE_URL": "http://example.test/v1", "LLM_MODEL": "test-model", "LLM_API_KEY": KEY}


class CompareEndpointTests(unittest.TestCase):
    def setUp(self):
        try:
            import server
        except ImportError:
            self.skipTest("flask not installed")
        self.server = server
        self.client = server.app.test_client()

    def test_compare_returns_both_answers_tokens_and_times(self):
        calls = []

        class FakeReader:
            def answer(self, question, context):
                calls.append(context)
                return "full answer" if context == TEXT else "squeezed answer"

        with mock.patch.dict(os.environ, ENV, clear=False), \
                mock.patch.object(self.server, "get_reader", return_value=FakeReader()):
            r = self.client.post("/api/compare",
                                 json={"context": TEXT, "question": "Where is the tower?", "keep_ratio": 0.2})

        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(len(calls), 2)
        self.assertEqual(body["full"]["answer"], "full answer")
        self.assertEqual(body["squeezed"]["answer"], "squeezed answer")
        self.assertFalse(body["match"])
        self.assertEqual(body["full"]["tokens"], count_tokens(TEXT))
        self.assertIsInstance(body["squeezed"]["tokens"], int)
        self.assertGreater(body["squeezed"]["tokens"], 0)
        self.assertGreaterEqual(body["full"]["ms"], 0)
        self.assertGreaterEqual(body["squeezed"]["ms"], 0)
        self.assertGreaterEqual(body["squeeze_ms"], 0)
        self.assertLessEqual(body["keep_ratio"], 0.2)
        self.assertGreater(body["keep_ratio"], 0)
        self.assertNotIn(KEY, r.get_data(as_text=True))

    def test_match_is_reported_when_answers_agree(self):
        class FakeReader:
            def answer(self, question, context):
                return "Paris"

        with mock.patch.dict(os.environ, ENV, clear=False), \
                mock.patch.object(self.server, "get_reader", return_value=FakeReader()):
            r = self.client.post("/api/compare",
                                 json={"context": TEXT, "question": "Where?", "keep_ratio": 0.4})

        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["match"])

    def test_info_disables_button_and_explains_without_key(self):
        with mock.patch.dict(os.environ, {"LLM_BASE_URL": "", "LLM_MODEL": "", "LLM_API_KEY": ""}, clear=False):
            info = self.client.get("/api/info").get_json()
            self.assertFalse(info["llm"]["available"])
            self.assertIn("API key", info["llm"]["reason"])
            r = self.client.post("/api/compare",
                                 json={"context": TEXT, "question": "Where?", "keep_ratio": 0.4})

        self.assertEqual(r.status_code, 503)
        self.assertIn("API key", r.get_json()["error"])

    def test_info_never_sends_the_key(self):
        with mock.patch.dict(os.environ, ENV, clear=False):
            r = self.client.get("/api/info")
            body = r.get_json()

        self.assertTrue(body["llm"]["available"])
        self.assertEqual(body["llm"]["model"], "test-model")
        self.assertNotIn(KEY, r.get_data(as_text=True))
        self.assertNotIn("api_key", r.get_data(as_text=True).lower())


if __name__ == "__main__":
    unittest.main()
