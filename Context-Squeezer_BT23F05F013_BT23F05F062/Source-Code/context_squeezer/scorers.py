"""Stage 2: word-level information scoring (surprisal, in bits).

A scorer receives the full text and the character spans of its tokens and
returns one surprisal value per span. Predictable words get low values and are
pruned first. Two scorers are provided:

* HFScorer       - a small local causal language model (Hugging Face
                   transformers). This is the real Stage 2 from the project
                   proposal.
* HeuristicScorer - no model needed. A frequency and word-length heuristic that
                   keeps the pipeline runnable anywhere. It is a stand-in, not
                   a language model, and results with it should be labelled so.
"""
from __future__ import annotations

import bisect
import math
from collections import Counter

from .linguistic import STOPWORDS


class Scorer:
    name = "base"

    def score(self, text: str, spans: list[tuple[int, int]]) -> list[float]:
        raise NotImplementedError


class HeuristicScorer(Scorer):
    name = "heuristic (no model)"

    def score(self, text: str, spans: list[tuple[int, int]]) -> list[float]:
        seen: Counter[str] = Counter()
        out: list[float] = []
        for a, b in spans:
            w = text[a:b]
            low = w.lower().strip(".,;:!?\"'()[]")
            if not low or not any(c.isalnum() for c in low):
                out.append(0.5)
                continue
            if low in STOPWORDS:
                s = 1.5
            else:
                s = 4.0 + 0.45 * min(len(low), 12)  # longer words tend to be rarer
            if any(c.isdigit() for c in low):
                s += 4.0
            elif w[0].isupper():
                s += 1.5
            s -= 1.2 * min(seen[low], 3)  # repeated mentions are more predictable
            seen[low] += 1
            out.append(max(s, 0.2))
        return out


def _load_causal_lm(cls, model_name: str, torch):
    """Load a causal LM in float32, across transformers that use `dtype` or `torch_dtype`."""
    try:
        return cls.from_pretrained(model_name, dtype=torch.float32)
    except TypeError:  # older transformers only know torch_dtype
        return cls.from_pretrained(model_name, torch_dtype=torch.float32)


class HFScorer(Scorer):
    """Per-word surprisal from a small causal LM, e.g. Qwen2.5-0.5B/1.5B, Llama-3.2-1B, SmolLM2.

    Long inputs are scored in overlapping windows so every word sees context.
    """

    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B", device: str | None = None,
                 window: int = 512, overlap: int = 64):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if window <= overlap:
            raise ValueError("window must be larger than overlap")
        self._torch = torch
        self.name = f"hf:{model_name}"
        self.tok = AutoTokenizer.from_pretrained(model_name)
        self.model = _load_causal_lm(AutoModelForCausalLM, model_name, torch)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()
        self.window = window
        self.overlap = overlap
        # Use the tokenizer's BOS when it has one; fall back to the model config.
        # Some tokenizers (Qwen2.5) define neither, in which case no BOS is prepended.
        self.bos = self.tok.bos_token_id
        if self.bos is None:
            self.bos = getattr(self.model.config, "bos_token_id", None)

    def _token_surprisals(self, ids: list[int]) -> list[float]:
        torch = self._torch
        n = len(ids)
        out = [0.0] * n
        prefix = [self.bos] if self.bos is not None else []
        start = 0
        while start < n:
            end = min(start + self.window, n)
            chunk = ids[start:end]
            inp = torch.tensor([prefix + chunk], device=self.device)
            tgt = torch.tensor(chunk, device=self.device)
            with torch.inference_mode():
                logits = self.model(inp).logits[0, :-1]
                bits = torch.nn.functional.cross_entropy(logits.float(), tgt, reduction="none") / math.log(2)
            vals = bits.tolist()
            # The first `overlap` tokens of a later window were already scored with more left
            # context by the previous window; keep those earlier values (causal -> left context).
            skip = self.overlap if start > 0 else 0
            for k in range(skip, len(chunk)):
                out[start + k] = vals[k]
            if end == n:
                break
            start += self.window - self.overlap
        return out

    def score(self, text: str, spans: list[tuple[int, int]]) -> list[float]:
        enc = self.tok(text, add_special_tokens=False, return_offsets_mapping=True)
        ids, offsets = enc["input_ids"], enc["offset_mapping"]
        sur = self._token_surprisals(ids)
        starts = [a for a, _ in spans]
        out = [0.0] * len(spans)
        # A word can be split into several sub-word tokens; sum their surprisals.
        for (a, b), x in zip(offsets, sur):
            while a < b and text[a].isspace():
                a += 1
            if a >= b:
                continue
            k = bisect.bisect_right(starts, a) - 1
            if k >= 0 and spans[k][0] <= a < spans[k][1]:
                out[k] += x
        return out
