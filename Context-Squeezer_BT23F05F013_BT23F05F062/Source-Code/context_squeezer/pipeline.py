"""The Context Squeezer pipeline: filler removal -> information scoring -> budgeting."""
from __future__ import annotations

import dataclasses
import math
import re
import time
from dataclasses import dataclass, field
from typing import Optional, Union

from .linguistic import STOPWORDS, Analyzer, Tok, mark_fillers
from .scorers import HeuristicScorer, Scorer
from .tokens import count_tokens, tokenizer_name

NO_SPACE_BEFORE = set(".,;:!?)]}%")


@dataclass
class SqueezeConfig:
    keep_ratio: float = 0.4           # fraction of the original tokens to keep (0.4 = cut 60%)
    use_filter: bool = True           # stage 1: remove filler phrases
    use_word_pruning: bool = True     # stage 2: drop low-surprisal words
    use_sentence_ranking: bool = True  # stage 3: drop low-density / low-relevance sentences
    protect: bool = True              # never prune numbers, entities, negations in stage 2
    sentence_slack: float = 1.5       # sentences are kept up to slack * budget, words are pruned to budget
    relevance_weight: float = 1.0     # weight of question relevance in sentence ranking


@dataclass
class SqueezeResult:
    original: str
    squeezed: str
    original_tokens: int
    squeezed_tokens: int
    budget_tokens: int
    budget_met: bool
    stage_tokens: dict
    segments: list
    backend: str
    scorer: str
    tokenizer: str
    timings_ms: dict = field(default_factory=dict)

    @property
    def keep_ratio(self) -> float:
        return self.squeezed_tokens / self.original_tokens if self.original_tokens else 1.0

    @property
    def reduction(self) -> float:
        return 1.0 - self.keep_ratio

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["keep_ratio"] = self.keep_ratio
        d["reduction"] = self.reduction
        return d


def render(toks: list[Tok]) -> str:
    """Join the tokens that are still kept into text."""
    out: list[str] = []
    prev: Optional[Tok] = None
    for t in toks:
        if t.status != "kept":
            continue
        if prev is None:
            sep = ""
        elif t.para != prev.para:
            sep = "\n"
        elif t.i == prev.i + 1 and t.start == prev.end:
            sep = ""
        elif t.kind == "punct" and t.text in NO_SPACE_BEFORE:
            sep = ""
        elif prev.kind == "punct" and prev.text in "([{":
            sep = ""
        else:
            sep = " "
        out.append(sep + t.text)
        prev = t
    return "".join(out)


def _norm(w: str) -> str:
    return w[:-1] if len(w) > 3 and w.endswith("s") else w


def _query_terms(question: str) -> set[str]:
    return {_norm(w) for w in re.findall(r"\w+", question.lower()) if w not in STOPWORDS and len(w) > 1}


class Squeezer:
    def __init__(self, scorer: Optional[Scorer] = None, analyzer: Optional[Analyzer] = None):
        self.scorer = scorer or HeuristicScorer()
        self.analyzer = analyzer or Analyzer()

    # ------------------------------------------------------------------
    def squeeze(self, context: Union[str, list[str]], question: Optional[str] = None,
                config: Optional[SqueezeConfig] = None, **overrides) -> SqueezeResult:
        cfg = dataclasses.replace(config or SqueezeConfig(), **overrides)
        cfg.keep_ratio = min(1.0, max(0.02, cfg.keep_ratio))
        if isinstance(context, (list, tuple)):
            text = "\n\n".join(p.strip() for p in context if p and p.strip())
        else:
            text = context or ""
        timings: dict[str, float] = {}

        t0 = time.perf_counter()
        toks, _sents = self.analyzer.analyze(text)
        timings["parse"] = (time.perf_counter() - t0) * 1000
        orig_tokens = count_tokens(text)
        budget = max(1, round(cfg.keep_ratio * orig_tokens))
        stage = {"original": orig_tokens}
        budget_met = True

        if toks:
            t0 = time.perf_counter()
            if cfg.use_filter:
                mark_fillers(text, toks)
            timings["filter"] = (time.perf_counter() - t0) * 1000
            stage["after_filter"] = count_tokens(render(toks))
            stage["after_sentences"] = stage["after_filter"]

            needs_more = (cfg.use_word_pruning or cfg.use_sentence_ranking) and stage["after_filter"] > budget
            if needs_more:
                t0 = time.perf_counter()
                sur = self.scorer.score(text, [(t.start, t.end) for t in toks])
                for t, s in zip(toks, sur):
                    t.surprisal = s
                timings["score"] = (time.perf_counter() - t0) * 1000

                t0 = time.perf_counter()
                budget_met = self._budget(toks, question, cfg, budget, stage)
                timings["budget"] = (time.perf_counter() - t0) * 1000
            squeezed = render(toks)
        else:
            squeezed = ""
            stage["after_filter"] = stage["after_sentences"] = 0

        sq_tokens = count_tokens(squeezed)
        stage["final"] = sq_tokens
        return SqueezeResult(
            original=text, squeezed=squeezed, original_tokens=orig_tokens, squeezed_tokens=sq_tokens,
            budget_tokens=budget, budget_met=budget_met and (sq_tokens <= budget or sq_tokens >= orig_tokens),
            stage_tokens=stage, segments=_segments(text, toks), backend=self.analyzer.backend,
            scorer=self.scorer.name, tokenizer=tokenizer_name(),
            timings_ms={k: round(v, 2) for k, v in timings.items()},
        )

    # ------------------------------------------------------------------
    def _budget(self, toks: list[Tok], question, cfg: SqueezeConfig, budget: int, stage: dict) -> bool:
        by_sent: dict[int, list[Tok]] = {}
        for t in toks:
            by_sent.setdefault(t.sent, []).append(t)
        live = [s for s, ts in by_sent.items() if any(t.kind == "word" and t.status == "kept" for t in ts)]
        scores = self._sentence_scores(by_sent, live, question, cfg)

        if cfg.use_sentence_ranking and len(live) > 1:
            cap = budget * cfg.sentence_slack if cfg.use_word_pruning else budget
            kept: set[int] = set()
            total = 0
            for s in sorted(live, key=lambda s: -scores[s]):
                cost = count_tokens(render(by_sent[s])) + 1
                if not kept or total + cost <= cap:
                    kept.add(s)
                    total += cost
            for s in live:
                if s not in kept:
                    for t in by_sent[s]:
                        if t.status == "kept":
                            t.status = "sentence"
            stage["after_sentences"] = count_tokens(render(toks))

        if not cfg.use_word_pruning:
            return count_tokens(render(toks)) <= budget

        while True:
            cands = [t for t in toks if t.status == "kept"
                     and not (cfg.protect and t.protected)
                     and not (t.kind == "punct" and t.text in ".?!")]
            cands.sort(key=lambda t: -5.0 if t.kind == "punct" else t.surprisal - (1.0 if t.func else 0.0))

            def tokens_after(k: int) -> int:
                for j, t in enumerate(cands):
                    t.status = ("punct" if t.kind == "punct" else "entropy") if j < k else "kept"
                return count_tokens(render(toks))

            if tokens_after(len(cands)) > budget:
                remaining = [s for s in live if any(t.status == "kept" for t in by_sent[s])]
                if cfg.use_sentence_ranking and len(remaining) > 1:
                    tokens_after(0)
                    worst = min(remaining, key=lambda s: scores[s])
                    for t in by_sent[worst]:
                        if t.status == "kept":
                            t.status = "sentence"
                    continue
                return False
            lo, hi = 0, len(cands)
            while lo < hi:
                mid = (lo + hi) // 2
                if tokens_after(mid) <= budget:
                    hi = mid
                else:
                    lo = mid + 1
            tokens_after(lo)
            return True

    # ------------------------------------------------------------------
    @staticmethod
    def _sentence_scores(by_sent, live, question, cfg) -> dict[int, float]:
        dens: dict[int, float] = {}
        words: dict[int, set[str]] = {}
        for s in live:
            ws = [t for t in by_sent[s] if t.kind == "word" and t.status == "kept"]
            dens[s] = sum(t.surprisal for t in ws) / len(ws)
            words[s] = {_norm(t.text.lower()) for t in ws}
        top = max(dens.values()) if dens else 1.0
        rel = {s: 0.0 for s in live}
        q = _query_terms(question) if question else set()
        if q and cfg.relevance_weight > 0 and live:
            n = len(live)
            idf = {w: math.log(1 + n / (1 + sum(1 for s in live if w in words[s]))) for w in q}
            total = sum(idf.values())
            for s in live:
                rel[s] = sum(idf[w] for w in q if w in words[s]) / total
        return {s: dens[s] / (top or 1.0) + cfg.relevance_weight * rel[s] for s in live}


def _segments(text: str, toks: list[Tok]) -> list[dict]:
    """Runs of text with the status of what happened to them, for highlighting."""
    segs: list[dict] = []

    def push(txt: str, status: str, prot: bool):
        if segs and segs[-1]["s"] == status and segs[-1]["p"] == prot:
            segs[-1]["t"] += txt
        else:
            segs.append({"t": txt, "s": status, "p": prot})

    pos = 0
    for t in toks:
        gap = text[pos:t.start]
        if gap:
            push(gap, t.status, False)
        push(text[t.start:t.end], t.status, t.protected and t.status == "kept")
        pos = t.end
    if text[pos:]:
        push(text[pos:], "kept", False)
    return segs
