"""Time-to-first-token (TTFT) with and without squeezing, measured with a streaming reader.

    python -m eval.latency --data hf --n 20 --reader openai \
        --base-url http://localhost:11434/v1 --model llama3.2:3b \
        --scorer hf --hf-model Qwen/Qwen2.5-0.5B --price-per-million 0.15

Reports mean and median TTFT for full context and for squeezed context, plus
tokens and (only if --price-per-million is given) list-price cost savings.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from pathlib import Path

from context_squeezer import HeuristicScorer, SqueezeConfig, Squeezer
from context_squeezer.tokens import count_tokens

from .data import load_hotpot_hf_subset
from .readers import ENV_BASE_URL, ENV_MODEL, OpenAICompatReader
from .scoring_cache import CachedScorer


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="hf")
    p.add_argument("--subset-size", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--keep-ratio", type=float, default=0.4)
    p.add_argument("--scorer", choices=["heuristic", "hf"], default="hf")
    p.add_argument("--hf-model", default="Qwen/Qwen2.5-0.5B")
    p.add_argument("--base-url", default=None, help="or set LLM_BASE_URL")
    p.add_argument("--model", default=None, help="or set LLM_MODEL")
    p.add_argument("--max-calls-per-minute", type=int, default=None)
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--retries", type=int, default=6)
    p.add_argument("--price-per-million", type=float, default=None,
                   help="USD per 1M input tokens; dollars are labelled list price")
    p.add_argument("--out", default="results")
    args = p.parse_args(argv)

    args.base_url = args.base_url or os.environ.get(ENV_BASE_URL, "").strip()
    args.model = args.model or os.environ.get(ENV_MODEL, "").strip()
    if not args.base_url or not args.model:
        raise SystemExit("latency needs --base-url and --model (or LLM_BASE_URL and LLM_MODEL)")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    examples = load_hotpot_hf_subset(args.subset_size, args.seed, ids_path=out / "subset_ids.json")[:args.n]

    if args.scorer == "hf":
        from context_squeezer import HFScorer

        scorer = CachedScorer(HFScorer(args.hf_model), out / "surprisal_cache_hf.json")
    else:
        scorer = HeuristicScorer()
    squeezer = Squeezer(scorer=scorer)
    reader = OpenAICompatReader(args.base_url, args.model, timeout=args.timeout, retries=args.retries,
                                max_calls_per_minute=args.max_calls_per_minute, stream=True)

    rows = []
    for i, ex in enumerate(examples, 1):
        if hasattr(scorer, "bind"):
            scorer.bind(ex.id)
        full_ctx = ex.context_text
        reader.answer(ex.question, full_ctx)
        full = {"ttft_ms": reader.last_ttft_ms, "total_ms": reader.last_latency_ms,
                "tokens": count_tokens(full_ctx)}

        started = time.perf_counter()
        res = squeezer.squeeze(ex.passages, question=ex.question, config=SqueezeConfig(keep_ratio=args.keep_ratio))
        squeeze_ms = (time.perf_counter() - started) * 1000
        reader.answer(ex.question, res.squeezed)
        squeezed = {"ttft_ms": reader.last_ttft_ms, "total_ms": reader.last_latency_ms,
                    "tokens": count_tokens(res.squeezed), "squeeze_ms": squeeze_ms}
        rows.append({"id": ex.id, "question": ex.question, "full": full, "squeezed": squeezed})
        if hasattr(scorer, "save"):
            scorer.save()
        print(f"[{i}/{len(examples)}] full ttft={full['ttft_ms']:.0f}ms  "
              f"squeezed ttft={squeezed['ttft_ms']:.0f}ms  tokens {full['tokens']}->{squeezed['tokens']}",
              flush=True)

    def stats(key, sub):
        vals = [r[sub][key] for r in rows if r[sub].get(key) is not None]
        return {"mean": statistics.mean(vals) if vals else None,
                "median": statistics.median(vals) if vals else None, "n": len(vals)}

    summary = {
        "examples": len(rows),
        "keep_ratio": args.keep_ratio,
        "scorer": scorer.name,
        "reader": reader.name,
        "full_ttft_ms": stats("ttft_ms", "full"),
        "squeezed_ttft_ms": stats("ttft_ms", "squeezed"),
        "full_total_ms": stats("total_ms", "full"),
        "squeezed_total_ms": stats("total_ms", "squeezed"),
        "squeeze_ms": stats("squeeze_ms", "squeezed"),
        "avg_full_tokens": statistics.mean(r["full"]["tokens"] for r in rows),
        "avg_squeezed_tokens": statistics.mean(r["squeezed"]["tokens"] for r in rows),
    }
    summary["tokens_saved_per_query"] = summary["avg_full_tokens"] - summary["avg_squeezed_tokens"]
    if args.price_per_million is not None:
        summary["list_price_per_million_input_tokens"] = args.price_per_million
        summary["usd_saved_per_query_list_price"] = summary["tokens_saved_per_query"] / 1e6 * args.price_per_million

    print("\nTTFT summary (ms)")
    for label, key in (("full context", "full_ttft_ms"), ("squeezed", "squeezed_ttft_ms")):
        s = summary[key]
        if s["mean"] is not None:
            print(f"  {label:<14} mean {s['mean']:8.1f}  median {s['median']:8.1f}  (n={s['n']})")
    print(f"  tokens/query  {summary['avg_full_tokens']:.0f} -> {summary['avg_squeezed_tokens']:.0f} "
          f"(saved {summary['tokens_saved_per_query']:.0f})")
    if args.price_per_million is not None:
        print(f"  list-price saving ${summary['usd_saved_per_query_list_price']:.6f}/query "
              f"at ${args.price_per_million}/1M input tokens")

    path = out / "latency.json"
    path.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
