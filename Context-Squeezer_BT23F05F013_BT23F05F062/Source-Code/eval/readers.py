"""Readers: the 'downstream LLM' that answers a question from (compressed) context.

* ExtractiveReader    - offline, rule-based. Only for smoke-testing the harness.
                        It is NOT a language model and says nothing about real accuracy.
* OpenAICompatReader  - any OpenAI-compatible chat endpoint: Ollama
                        (http://localhost:11434/v1), vLLM, LM Studio, Groq, OpenAI, ...
"""
from __future__ import annotations

import math
import os
import re
import time

ENV_BASE_URL = "LLM_BASE_URL"
ENV_MODEL = "LLM_MODEL"
ENV_API_KEY = "LLM_API_KEY"

STOP = set("a an the of in on at to for by with from and or is are was were be been which who whom what when where "
           "how many much did does do has have had it its this that as".split())


def env_reader_config() -> tuple[str, str, str]:
    """Endpoint, model and key from the environment, shared by the demo and the eval scripts."""
    return (os.environ.get(ENV_BASE_URL, "").strip(),
            os.environ.get(ENV_MODEL, "").strip(),
            os.environ.get(ENV_API_KEY, "").strip())


def llm_status() -> dict:
    """Configuration status for the demo. Never includes the key."""
    base_url, model, api_key = env_reader_config()
    if not api_key:
        return {"available": False,
                "reason": "No API key is set (LLM_API_KEY), so the demo cannot ask a language model."}
    if not base_url or not model:
        return {"available": False,
                "reason": "The language model endpoint is not configured (set LLM_BASE_URL and LLM_MODEL)."}
    return {"available": True, "reason": "", "model": model}


def _stem(w: str) -> str:
    return w[:5]


def _sentences(text: str) -> list[str]:
    out = []
    for s in re.split(r"(?<=[.!?])\s+|\n+", text):
        s = re.sub(r"^[^:.\n]{1,60}:\s+", "", s.strip())  # drop the "Title:" prefix of a passage
        if s:
            out.append(s)
    return out


class Reader:
    name = "reader"

    def answer(self, question: str, context: str) -> str:
        raise NotImplementedError


class ExtractiveReader(Reader):
    name = "extractive-rules (smoke test only)"

    def answer(self, question: str, context: str) -> str:
        sents = _sentences(context)
        if not sents:
            return ""
        q_words = [w for w in re.findall(r"\w+", question.lower()) if w not in STOP and w not in ("year", "many", "much")]
        q_stems = {_stem(w) for w in q_words}
        sent_stems = [{_stem(w) for w in re.findall(r"\w+", s.lower())} for s in sents]
        n = len(sents)
        idf = {q: math.log(1 + n / (1 + sum(1 for ss in sent_stems if q in ss))) for q in q_stems}
        # prefer the sentence holding the rarest question term, then the one matching the most terms
        def key(i):
            hit = [idf[q] for q in q_stems if q in sent_stems[i]]
            return (max(hit) if hit else 0.0, sum(hit))
        best = sents[max(range(n), key=key)]

        wh = question.lower().split()[0] if question.split() else ""
        q_lower = question.lower()
        if "how many" in q_lower or wh in ("when",) or "what year" in q_lower or "which year" in q_lower or "in which year" in q_lower:
            nums = re.findall(r"\d[\d,.]*", best)
            nums = [x.rstrip(".,") for x in nums if x.rstrip(".,") not in question]
            if "how many" not in q_lower:
                years = [x for x in nums if re.fullmatch(r"\d{4}", x)]
                nums = years or nums
            return nums[0] if nums else ""
        # who / where / which / what: first capitalised phrase that is not part of the question
        q_set = {w for w in re.findall(r"\w+", question.lower())}
        for m in re.finditer(r"[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*", best):
            words = m.group().split()
            keep = [w for w in words if w.lower() not in q_set and w.lower() not in STOP]
            if keep and len(keep) == len(words):
                return m.group()
            if keep and all(w.lower() in q_set or w.lower() in STOP for w in words[:-len(keep)]):
                return " ".join(keep)
        return ""


class OpenAICompatReader(Reader):
    def __init__(self, base_url: str, model: str, api_key: str | None = None, timeout: int = 120,
                 retries: int = 6, max_calls_per_minute: int | None = None, stream: bool = False):
        import requests

        self._requests = requests
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key or os.environ.get(ENV_API_KEY, "")
        self.timeout = timeout
        self.retries = retries
        self.max_calls_per_minute = max_calls_per_minute
        self.stream = stream
        self._calls: list[float] = []
        self.last_ttft_ms: float | None = None
        self.last_latency_ms: float | None = None
        self.name = f"openai-compatible:{model}"

    def _throttle(self) -> None:
        if not self.max_calls_per_minute:
            return
        now = time.monotonic()
        self._calls = [t for t in self._calls if now - t < 60]
        if len(self._calls) >= self.max_calls_per_minute:
            wait = 60 - (now - self._calls[0]) + 0.05
            if wait > 0:
                time.sleep(wait)
            now = time.monotonic()
            self._calls = [t for t in self._calls if now - t < 60]
        self._calls.append(time.monotonic())

    def _post(self, payload: dict):
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        last = None
        for attempt in range(self.retries):
            self._throttle()
            started = time.perf_counter()
            try:
                r = self._requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers,
                                        timeout=self.timeout, stream=self.stream)
                if r.status_code == 429 or 500 <= r.status_code < 600:
                    retry_after = r.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2 ** attempt
                    last = RuntimeError(f"HTTP {r.status_code}")
                    time.sleep(max(delay, 1.0))
                    continue
                r.raise_for_status()
                return r, started
            except self._requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                if status is not None and 400 <= status < 500 and status != 429:
                    raise RuntimeError(f"Reader rejected the request (HTTP {status}). Check the URL, model and API key.")
                last = e
                time.sleep(2 ** attempt)
            except Exception as e:  # network errors, timeouts
                last = e
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Reader request failed after {self.retries} attempts: {last}")

    def answer(self, question: str, context: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 64,
            "messages": [
                {"role": "system", "content": "Answer the question using only the context. Reply with the shortest "
                                              "possible answer (a few words), with no explanation."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"},
            ],
        }
        if self.stream:
            payload["stream"] = True
        r, started = self._post(payload)
        self.last_ttft_ms = None
        if not self.stream:
            self.last_latency_ms = (time.perf_counter() - started) * 1000
            return r.json()["choices"][0]["message"]["content"].strip()

        pieces: list[str] = []
        ttft = None
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
                delta = obj["choices"][0].get("delta", {})
                piece = delta.get("content")
            except Exception:
                continue
            if piece:
                if ttft is None:
                    ttft = (time.perf_counter() - started) * 1000
                pieces.append(piece)
        self.last_ttft_ms = ttft
        self.last_latency_ms = (time.perf_counter() - started) * 1000
        return "".join(pieces).strip()
