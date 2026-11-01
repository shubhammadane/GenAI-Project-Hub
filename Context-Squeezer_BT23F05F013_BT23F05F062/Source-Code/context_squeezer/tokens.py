"""Token counting.

Uses tiktoken (cl100k_base) when it is installed and its vocabulary can be
loaded. Otherwise falls back to a rough character-based estimate so the
pipeline still runs offline. The fallback is only an approximation of what a
commercial LLM API would bill, so `tokenizer_name()` is shown in the demo.
"""
from __future__ import annotations

import math
import re

_ENC = None
_TRIED = False

_CHUNK = re.compile(r"\d+|[^\W\d_]+|[^\w\s]|_")


def _load():
    global _ENC, _TRIED
    if _TRIED:
        return _ENC
    _TRIED = True
    try:
        import tiktoken

        _ENC = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _ENC = None
    return _ENC


def tokenizer_name() -> str:
    return "tiktoken/cl100k_base" if _load() is not None else "approximate (install tiktoken for exact counts)"


def is_exact() -> bool:
    return _load() is not None


def count_tokens(text: str) -> int:
    if not text:
        return 0
    enc = _load()
    if enc is not None:
        try:
            return len(enc.encode(text, disallowed_special=()))
        except Exception:
            pass
    total = 0
    for chunk in _CHUNK.findall(text):
        if chunk.isdigit():
            total += math.ceil(len(chunk) / 3)
        elif chunk[0].isalpha():
            total += max(1, math.ceil(len(chunk) / 5))
        else:
            total += 1
    return total
