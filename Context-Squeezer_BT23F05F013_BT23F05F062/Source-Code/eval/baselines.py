"""Compression baselines at the same token budget, so Context Squeezer has something to beat."""
from __future__ import annotations

import random

from context_squeezer.tokens import count_tokens

_LLMLINGUA_PATCHED = False


def _patch_llmlingua_for_new_transformers() -> None:
    """Make llmlingua 0.2.x work with transformers>=5.

    transformers 5 replaced the legacy tuple of (key, value) pairs returned as
    ``past_key_values`` with a ``DynamicCache``. llmlingua indexes and iterates
    that value as if it were the old tuple. This reimplementation of ``get_ppl``
    converts between the two representations. On transformers 4.x the original
    method is left untouched.
    """
    global _LLMLINGUA_PATCHED
    if _LLMLINGUA_PATCHED:
        return
    from llmlingua import PromptCompressor

    try:
        from transformers.cache_utils import DynamicCache
    except Exception:  # pragma: no cover - very old transformers
        _LLMLINGUA_PATCHED = True
        return
    if hasattr(DynamicCache, "from_legacy_cache"):
        _LLMLINGUA_PATCHED = True  # transformers 4.x: llmlingua already works
        return

    import torch

    def get_ppl(self, text, granularity="sentence", input_ids=None, attention_mask=None,
                past_key_values=None, return_kv=False, end=None, condition_mode="none",
                condition_pos_id=0):
        if input_ids is None:
            tokenized = self.tokenizer(text, return_tensors="pt")
            input_ids = tokenized["input_ids"].to(self.device)
            attention_mask = tokenized["attention_mask"].to(self.device)
        past_length = past_key_values[0][0].shape[2] if past_key_values is not None else 0
        if end is None:
            end = input_ids.shape[1]
        end = min(end, past_length + self.max_position_embeddings)
        cache = DynamicCache(tuple((k, v) for k, v in past_key_values)) if past_key_values is not None else None
        with torch.no_grad():
            response = self.model(
                input_ids[:, past_length:end],
                attention_mask=attention_mask[:, :end],
                past_key_values=cache,
                use_cache=True,
            )
        new_cache = response.past_key_values
        if hasattr(new_cache, "layers"):
            new_cache = tuple((layer.keys, layer.values) for layer in new_cache.layers)
        shift_logits = response.logits[..., :-1, :].contiguous()
        shift_labels = input_ids[..., past_length + 1:end].contiguous()
        active = (attention_mask[:, past_length:end] == 1)[..., :-1].view(-1)
        active_logits = shift_logits.view(-1, shift_logits.size(-1))[active]
        active_labels = shift_labels.view(-1)[active]
        loss = torch.nn.CrossEntropyLoss(reduction="none")(active_logits, active_labels)
        if condition_mode == "before":
            loss = loss[:condition_pos_id]
        elif condition_mode == "after":
            loss = loss[condition_pos_id:]
        res = loss.mean() if granularity == "sentence" else loss
        return (res, new_cache) if return_kv else res

    PromptCompressor.get_ppl = get_ppl
    _LLMLINGUA_PATCHED = True


class LLMLinguaCompressor:
    """Wrapper around the llmlingua package, compressed to a target token budget."""

    def __init__(self, model_name: str = "gpt2", device: str = "cpu", use_llmlingua2: bool = False):
        _patch_llmlingua_for_new_transformers()
        from llmlingua import PromptCompressor

        self.name = f"llmlingua:{model_name}"
        self.pc = PromptCompressor(model_name=model_name, device_map=device, use_llmlingua2=use_llmlingua2)

    def compress(self, text: str, budget: int) -> str:
        result = self.pc.compress_prompt(text, target_token=max(1, int(budget)))
        return result["compressed_prompt"] or text


def truncate(text: str, budget: int) -> str:
    """Keep the first words that fit the budget."""
    words = text.split()
    lo, hi = 0, len(words)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if count_tokens(" ".join(words[:mid])) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return " ".join(words[:lo])


def random_drop(text: str, budget: int, seed: int = 0) -> str:
    """Drop words uniformly at random until the budget is met (original order kept)."""
    words = text.split()
    order = list(range(len(words)))
    random.Random(seed).shuffle(order)

    def build(k: int) -> str:
        gone = set(order[:k])
        return " ".join(w for i, w in enumerate(words) if i not in gone)

    lo, hi = 0, len(words)
    while lo < hi:
        mid = (lo + hi) // 2
        if count_tokens(build(mid)) <= budget:
            hi = mid
        else:
            lo = mid + 1
    return build(lo)
