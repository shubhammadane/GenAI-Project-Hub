"""Dataset loading. Accepts HotpotQA distractor-format JSON (official file or Hugging Face export),
or the Hugging Face `hotpotqa/hotpot_qa` dataset directly."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Example:
    id: str
    question: str
    answer: str
    passages: list[str]

    @property
    def context_text(self) -> str:
        return "\n\n".join(self.passages)


def _to_example(item, fallback_id) -> Example:
    ctx = item["context"]
    if isinstance(ctx, dict):  # Hugging Face format: {"title": [...], "sentences": [[...], ...]}
        pairs = list(zip(ctx["title"], ctx["sentences"]))
    else:  # official format: [[title, [sentences]], ...]
        pairs = [(t, s) for t, s in ctx]
    passages = [f"{title}: {' '.join(s.strip() for s in sents)}" for title, sents in pairs]
    return Example(str(item.get("_id", item.get("id", fallback_id))), item["question"], item["answer"], passages)


def load_hotpot(path: str | Path, limit: Optional[int] = None) -> list[Example]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    out: list[Example] = []
    for i, item in enumerate(raw):
        out.append(_to_example(item, i))
        if limit and len(out) >= limit:
            break
    return out


def load_hotpot_hf_subset(size: int = 200, seed: int = 42, split: str = "validation",
                          config: str = "distractor", ids_path: str | Path | None = None) -> list[Example]:
    """Load a deterministic random subset of the Hugging Face HotpotQA distractor set.

    The chosen ids are written to `ids_path` and reused on later runs so the subset is
    stable even if the dataset ordering changes.
    """
    from datasets import load_dataset

    ds = load_dataset("hotpotqa/hotpot_qa", config, split=split)
    all_ids = list(ds["id"])
    saved = None
    if ids_path and Path(ids_path).exists():
        payload = json.loads(Path(ids_path).read_text())
        saved = payload["ids"] if isinstance(payload, dict) else payload

    if saved:
        position = {qid: i for i, qid in enumerate(all_ids)}
        indices = [position[qid] for qid in saved if qid in position]
    else:
        rng = random.Random(seed)
        indices = sorted(rng.sample(range(len(ds)), min(size, len(ds))))
        saved = [all_ids[i] for i in indices]
        if ids_path:
            path = Path(ids_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({
                "dataset": "hotpotqa/hotpot_qa", "config": config, "split": split,
                "seed": seed, "size": len(saved), "ids": saved,
            }, indent=2))
    return [_to_example(ds[i], i) for i in indices]
