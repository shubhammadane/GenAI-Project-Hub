"""Evaluate compression quality: Information Recovery Rate (IRR) against full context and baselines.

Examples
    # 5-question timing run first (writes caches, does not touch results.json)
    python -m eval.run_eval --data hf --limit 5 --tag timing5 --reader openai \
        --base-url http://localhost:11434/v1 --model llama3.2:3b

    # Full run, both scorers, 200-question fixed subset
    python -m eval.run_eval --data hf --subset-size 200 --seed 42 --reader openai \
        --base-url http://localhost:11434/v1 --model llama3.2:3b --max-calls-per-minute 60

Definitions
    IRR        = mean F1(squeezed context, gold) / mean F1(full context, gold)
    Agreement  = share of questions where the squeezed-context answer equals the full-context answer
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import time
from pathlib import Path

from context_squeezer import HeuristicScorer, SqueezeConfig, Squeezer
from context_squeezer.linguistic import Analyzer
from context_squeezer.tokens import count_tokens, tokenizer_name

from .baselines import LLMLinguaCompressor, truncate
from .data import load_hotpot, load_hotpot_hf_subset
from .metrics import exact_match, f1_score, normalize_answer
from .readers import ENV_BASE_URL, ENV_MODEL, ExtractiveReader, OpenAICompatReader
from .scoring_cache import CachedScorer

HERE = Path(__file__).parent


class Cache:
    """Remembers reader answers so an interrupted run can resume without repeating LLM calls."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}

    def key(self, reader: str, q: str, ctx: str) -> str:
        return hashlib.sha256(f"{reader}\x00{q}\x00{ctx}".encode()).hexdigest()

    def get(self, reader, q, ctx):
        return self.data.get(self.key(reader, q, ctx))

    def put(self, reader, q, ctx, ans):
        self.data[self.key(reader, q, ctx)] = ans

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data))


def make_squeezers(args, out: Path):
    from context_squeezer import HFScorer

    analyzer = Analyzer()
    squeezers: dict[str, Squeezer] = {}
    caches = []
    if "heuristic" in args.scorers:
        squeezers["heuristic"] = Squeezer(scorer=HeuristicScorer(), analyzer=analyzer)
    if "hf" in args.scorers:
        cache = CachedScorer(HFScorer(args.hf_model), out / "surprisal_cache_hf.json")
        squeezers["hf"] = Squeezer(scorer=cache, analyzer=analyzer)
        caches.append(cache)
    return squeezers, caches


def make_reader(args):
    if args.reader == "openai":
        base_url = args.base_url or os.environ.get(ENV_BASE_URL, "").strip()
        model = args.model or os.environ.get(ENV_MODEL, "").strip()
        if not base_url or not model:
            raise SystemExit("--reader openai needs --base-url and --model (or LLM_BASE_URL and LLM_MODEL)")
        return OpenAICompatReader(base_url, model, timeout=args.timeout, retries=args.retries,
                                  max_calls_per_minute=args.max_calls_per_minute)
    return ExtractiveReader()


def _squeeze_fn(sq: Squeezer, ratio: float, **flags):
    def fn(ex):
        if hasattr(sq.scorer, "bind"):
            sq.scorer.bind(ex.id)
        started = time.perf_counter()
        res = sq.squeeze(ex.passages, question=ex.question, config=SqueezeConfig(keep_ratio=ratio, **flags))
        return res.squeezed, (time.perf_counter() - started) * 1000
    return fn


def _truncate_fn(ratio: float):
    def fn(ex):
        text = ex.context_text
        budget = max(1, round(ratio * count_tokens(text)))
        started = time.perf_counter()
        return truncate(text, budget), (time.perf_counter() - started) * 1000
    return fn


def _llmlingua_fn(compressor: LLMLinguaCompressor, ratio: float):
    def fn(ex):
        text = ex.context_text
        budget = max(1, round(ratio * count_tokens(text)))
        started = time.perf_counter()
        return compressor.compress(text, budget), (time.perf_counter() - started) * 1000
    return fn


def build_methods(squeezers, ratios, compressor, ablate_ratio):
    methods = [("full context", lambda ex: (ex.context_text, 0.0))]
    for r in ratios:
        for name in ("heuristic", "hf"):
            if name in squeezers:
                methods.append((f"squeezer-{name} keep={r}", _squeeze_fn(squeezers[name], r)))
        methods.append((f"truncate keep={r}", _truncate_fn(r)))
        if compressor is not None:
            methods.append((f"llmlingua keep={r}", _llmlingua_fn(compressor, r)))
    if ablate_ratio and "heuristic" in squeezers:
        heur = squeezers["heuristic"]
        a = ablate_ratio
        methods += [
            ("ablation: filter only", _squeeze_fn(heur, a, use_word_pruning=False, use_sentence_ranking=False)),
            (f"ablation: words only keep={a}", _squeeze_fn(heur, a, use_sentence_ranking=False)),
            (f"ablation: sentences only keep={a}", _squeeze_fn(heur, a, use_word_pruning=False)),
            (f"ablation: full keep={a}", _squeeze_fn(heur, a)),
            (f"ablation: no protection keep={a}", _squeeze_fn(heur, a, protect=False)),
        ]
    return methods


def evaluate(examples, methods, reader, cache: Cache, caches=(), predictions_path: Path | None = None,
             progress: bool = True):
    acc = {name: {"em": [], "f1": [], "toks": [], "orig": [], "agree": [], "ms": []} for name, _ in methods}
    contexts: dict[str, str] = {}
    questions = []
    run_started = time.perf_counter()

    def context_id(text: str) -> str:
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
        contexts[digest] = text
        return digest

    try:
        for qi, ex in enumerate(examples, 1):
            full_answer = None
            record = {"id": ex.id, "question": ex.question, "gold": ex.answer,
                      "original_ctx": context_id(ex.context_text), "methods": {}}
            q_started = time.perf_counter()
            for name, fn in methods:
                ctx, took = fn(ex)
                ans = cache.get(reader.name, ex.question, ctx)
                if ans is None:
                    ans = reader.answer(ex.question, ctx)
                    cache.put(reader.name, ex.question, ctx, ans)
                if name == "full context":
                    full_answer = ans
                em = exact_match(ans, ex.answer)
                f1 = f1_score(ans, ex.answer)
                agree = float(normalize_answer(ans) == normalize_answer(full_answer if full_answer is not None else ans))
                toks = count_tokens(ctx)
                bucket = acc[name]
                bucket["em"].append(em)
                bucket["f1"].append(f1)
                bucket["toks"].append(toks)
                bucket["orig"].append(count_tokens(ex.context_text))
                bucket["agree"].append(agree)
                bucket["ms"].append(took)
                record["methods"][name] = {"answer": ans, "em": em, "f1": f1, "tokens": toks,
                                           "ctx": context_id(ctx)}
            record["seconds"] = time.perf_counter() - q_started
            cache.save()
            for c in caches:
                c.save()
            questions.append(record)
            if progress:
                elapsed = time.perf_counter() - run_started
                per_q = elapsed / qi
                eta = per_q * (len(examples) - qi) / 60
                print(f"[{qi}/{len(examples)}] {ex.id} {record['seconds']:.1f}s "
                      f"(elapsed {elapsed/60:.1f}m, eta {eta:.1f}m) {ex.question[:60]}", flush=True)
    finally:
        cache.save()
        for c in caches:
            c.save()
        if predictions_path is not None:
            predictions_path.parent.mkdir(parents=True, exist_ok=True)
            predictions_path.write_text(json.dumps({"contexts": contexts, "questions": questions}, indent=2))

    rows = []
    for name, _ in methods:
        b = acc[name]
        rows.append({
            "method": name,
            "avg_tokens": statistics.mean(b["toks"]),
            "token_reduction": 1 - sum(b["toks"]) / sum(b["orig"]),
            "EM": statistics.mean(b["em"]),
            "F1": statistics.mean(b["f1"]),
            "agreement_with_full": statistics.mean(b["agree"]),
            "overhead_ms": statistics.mean(b["ms"]),
        })
    full_f1 = rows[0]["F1"]
    for r in rows:
        r["IRR"] = r["F1"] / full_f1 if full_f1 else float("nan")
    return rows


def print_table(rows):
    cols = ["method", "avg_tokens", "token_reduction", "EM", "F1", "IRR", "agreement_with_full", "overhead_ms"]
    width = max(len(r["method"]) for r in rows)
    print(f"{'method':<{width}}  tokens  cut%    EM     F1     IRR    agree  ms/q")
    for r in rows:
        print(f"{r['method']:<{width}}  {r['avg_tokens']:6.0f}  {r['token_reduction']*100:4.0f}%  "
              f"{r['EM']:.3f}  {r['F1']:.3f}  {r['IRR']:.3f}  {r['agreement_with_full']:.3f}  {r['overhead_ms']:.0f}")
    return cols


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="hf",
                   help="'hf' for the Hugging Face HotpotQA distractor set, or a path to a HotpotQA JSON file")
    p.add_argument("--subset-size", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit", type=int, help="cap the number of examples (for a timing run)")
    p.add_argument("--ratios", type=float, nargs="+", default=[0.6, 0.4, 0.2])
    p.add_argument("--ablate-ratio", type=float, default=0.4, help="0 to skip ablations")
    p.add_argument("--no-baselines", action="store_true", help="skip the truncate baseline")
    p.add_argument("--no-llmlingua", action="store_true")
    p.add_argument("--llmlingua-model", default="gpt2")
    p.add_argument("--scorers", nargs="+", choices=["heuristic", "hf"], default=None)
    p.add_argument("--scorer", choices=["heuristic", "hf"], default=None, help="legacy single-scorer alias")
    p.add_argument("--hf-model", default="Qwen/Qwen2.5-0.5B")
    p.add_argument("--reader", choices=["extractive", "openai"], default="extractive")
    p.add_argument("--base-url")
    p.add_argument("--model")
    p.add_argument("--max-calls-per-minute", type=int, default=None)
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--retries", type=int, default=6)
    p.add_argument("--out", default="results")
    p.add_argument("--tag", default="", help="suffix for results/predictions files")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)

    if args.scorers is None:
        args.scorers = [args.scorer] if args.scorer else ["heuristic", "hf"]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.data in ("hf", "hotpot", "hotpotqa"):
        examples = load_hotpot_hf_subset(args.subset_size, args.seed, ids_path=out / "subset_ids.json")
    else:
        examples = load_hotpot(args.data, args.limit)
    if args.limit:
        examples = examples[:args.limit]

    squeezers, caches = make_squeezers(args, out)
    reader = make_reader(args)
    compressor = None if args.no_llmlingua else LLMLinguaCompressor(args.llmlingua_model)

    cache = Cache(out / "answer_cache.json")
    suffix = f"_{args.tag}" if args.tag else ""

    print(f"examples={len(examples)}  scorers={list(squeezers)}  parser={next(iter(squeezers.values())).analyzer.backend}")
    print(f"reader={reader.name}  tokenizer={tokenizer_name()}  hf_model={args.hf_model}  "
          f"llmlingua={'off' if compressor is None else args.llmlingua_model}")
    if args.max_calls_per_minute:
        print(f"max_calls_per_minute={args.max_calls_per_minute}")

    methods = build_methods(squeezers, args.ratios, compressor, args.ablate_ratio)
    if args.no_baselines:
        methods = [m for m in methods if not m[0].startswith("truncate")]
    rows = evaluate(examples, methods, reader, cache, caches=caches,
                    predictions_path=out / f"predictions{suffix}.json", progress=not args.quiet)
    cols = print_table(rows)

    meta = {
        "data": args.data, "examples": len(examples), "subset_size": args.subset_size, "seed": args.seed,
        "scorers": list(squeezers), "hf_model": args.hf_model if "hf" in squeezers else None,
        "llmlingua": None if compressor is None else args.llmlingua_model,
        "parser": next(iter(squeezers.values())).analyzer.backend,
        "reader": reader.name, "tokenizer": tokenizer_name(), "ratios": args.ratios,
        "ablate_ratio": args.ablate_ratio,
    }
    (out / f"results{suffix}.json").write_text(json.dumps({"meta": meta, "rows": rows}, indent=2))
    with open(out / f"results{suffix}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows({c: r[c] for c in cols} for r in rows)
    print(f"\nSaved {out / f'results{suffix}.json'} and {out / f'results{suffix}.csv'}")


if __name__ == "__main__":
    main()
