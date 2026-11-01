"""Fast proxy evaluation: token reduction and answer retention, no LLM calls.

    python -m eval.proxy_eval --limit 100 --hf-limit 30 --hf-timebox-min 30

Proxy metrics (NOT Information Recovery Rate):
    token_reduction  = 1 - sum(compressed tokens) / sum(original tokens)
    answer_retention = share of scored questions whose normalized gold answer is
                       still a substring of the normalized compressed context.
                       Questions whose gold answer is yes/no (or empty) are skipped.

The fast pass uses only the heuristic scorer, truncate and random-drop. The optional
second pass runs the squeezer with the small local HF scorer on a smaller subset,
time-boxed, and reuses results/surprisal_cache_hf.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

# The dataset and Qwen2.5-0.5B are already cached. Never download anything here.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from context_squeezer import HeuristicScorer, SqueezeConfig, Squeezer  # noqa: E402
from context_squeezer.linguistic import Analyzer  # noqa: E402
from context_squeezer.tokens import count_tokens, tokenizer_name  # noqa: E402

from .baselines import random_drop, truncate  # noqa: E402
from .data import load_hotpot_hf_subset  # noqa: E402
from .metrics import normalize_answer  # noqa: E402
from .scoring_cache import CachedScorer  # noqa: E402

FAST_METHODS = ("squeezer-heuristic", "truncate", "random-drop")
CSV_COLS = [
    "method", "keep_ratio", "n_questions", "skipped_yes_no", "skipped_empty", "n_scored",
    "sum_original_tokens", "sum_compressed_tokens", "avg_compressed_tokens",
    "token_reduction", "answer_retention", "elapsed_s", "status",
]


def _empty_acc() -> dict:
    return {"orig": 0, "toks": 0, "retained": 0, "scored": 0,
            "skipped_yes_no": 0, "skipped_empty": 0, "elapsed": 0.0}


def _check_retention(answer: str, ctx: str):
    """Return (skip_reason, retained). One of them is None."""
    gold = normalize_answer(answer)
    if gold in ("yes", "no"):
        return "yes_no", None
    if not gold:
        return "empty", None
    return None, gold in normalize_answer(ctx)


def _skip_counts(examples) -> tuple[int, int]:
    yes_no = sum(1 for ex in examples if normalize_answer(ex.answer) in ("yes", "no"))
    empty = sum(1 for ex in examples if not normalize_answer(ex.answer))
    return yes_no, empty


def _add(acc: dict, ex, ctx: str, took: float) -> None:
    reason, hit = _check_retention(ex.answer, ctx)
    acc["orig"] += count_tokens(ex.context_text)
    acc["toks"] += count_tokens(ctx)
    acc["elapsed"] += took
    if reason == "yes_no":
        acc["skipped_yes_no"] += 1
    elif reason == "empty":
        acc["skipped_empty"] += 1
    else:
        acc["scored"] += 1
        acc["retained"] += int(bool(hit))


def _rows(acc: dict, n_questions: int, status: str) -> list[dict]:
    rows = []
    for (method, ratio), a in acc.items():
        scored = a["scored"]
        rows.append({
            "method": method,
            "keep_ratio": ratio,
            "n_questions": n_questions,
            "skipped_yes_no": a["skipped_yes_no"],
            "skipped_empty": a["skipped_empty"],
            "n_scored": scored,
            "sum_original_tokens": a["orig"],
            "sum_compressed_tokens": a["toks"],
            "avg_compressed_tokens": round(a["toks"] / n_questions, 1) if n_questions else None,
            "token_reduction": round(1 - a["toks"] / a["orig"], 6) if a["orig"] else None,
            "answer_retention": round(a["retained"] / scored, 6) if scored else None,
            "elapsed_s": round(a["elapsed"], 3),
            "status": status,
        })
    rows.sort(key=lambda r: (r["method"], -r["keep_ratio"]))
    return rows


def run_fast(examples, ratios, analyzer) -> list[dict]:
    sq = Squeezer(scorer=HeuristicScorer(), analyzer=analyzer)
    acc = {(m, r): _empty_acc() for m in FAST_METHODS for r in ratios}
    for ex in examples:
        orig = count_tokens(ex.context_text)
        for r in ratios:
            budget = max(1, round(r * orig))
            t0 = time.perf_counter()
            sq_ctx = sq.squeeze(ex.passages, question=ex.question,
                                config=SqueezeConfig(keep_ratio=r)).squeezed
            t_sq = time.perf_counter() - t0
            t0 = time.perf_counter()
            tr_ctx = truncate(ex.context_text, budget)
            t_tr = time.perf_counter() - t0
            t0 = time.perf_counter()
            rd_ctx = random_drop(ex.context_text, budget, seed=42)
            t_rd = time.perf_counter() - t0
            _add(acc[("squeezer-heuristic", r)], ex, sq_ctx, t_sq)
            _add(acc[("truncate", r)], ex, tr_ctx, t_tr)
            _add(acc[("random-drop", r)], ex, rd_ctx, t_rd)
    return _rows(acc, len(examples), "complete")


def run_hf(examples, ratios, analyzer, out: Path, timebox_s: float):
    from context_squeezer import HFScorer

    started = time.perf_counter()
    acc = {("squeezer-hf", r): _empty_acc() for r in ratios}
    cache = CachedScorer(HFScorer("Qwen/Qwen2.5-0.5B"), out / "surprisal_cache_hf.json")
    sq = Squeezer(scorer=cache, analyzer=analyzer)
    completed = 0
    status = "complete"
    error = None
    try:
        for ex in examples:
            if time.perf_counter() - started >= timebox_s:
                status = "partial"
                break
            cache.bind(ex.id)
            for r in ratios:
                t0 = time.perf_counter()
                ctx = sq.squeeze(ex.passages, question=ex.question,
                                 config=SqueezeConfig(keep_ratio=r)).squeezed
                _add(acc[("squeezer-hf", r)], ex, ctx, time.perf_counter() - t0)
            completed += 1
            cache.save()
    except Exception as e:  # keep the fast results and report the failure
        status = "error"
        error = f"{type(e).__name__}: {e}"
    finally:
        try:
            cache.save()
        except Exception:
            pass
    return _rows(acc, completed, status), completed, status, error, time.perf_counter() - started


def save(rows, meta, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "proxy_results.json").write_text(json.dumps({"meta": meta, "rows": rows}, indent=2))
    with open(out / "proxy_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r[c] is None else r[c]) for c in CSV_COLS})


def make_chart(rows, path: Path, hf_limit: int, hf_completed: int) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = {
        "squeezer-heuristic": "Squeezer (heuristic)",
        "truncate": "Truncate",
        "random-drop": "Random drop",
        "squeezer-hf": "Squeezer (HF)",
    }
    markers = {"squeezer-heuristic": "o", "truncate": "^", "random-drop": "s",
               "squeezer-hf": "D"}
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for method in dict.fromkeys(r["method"] for r in rows):
        pts = [(r["token_reduction"] * 100, r["answer_retention"] * 100, r["keep_ratio"])
               for r in rows
               if r["method"] == method and r["token_reduction"] is not None
               and r["answer_retention"] is not None]
        if not pts:
            continue
        pts.sort(key=lambda p: p[0])
        label = labels.get(method, method)
        if method == "squeezer-hf":
            if hf_completed < hf_limit:
                label += f" (n={hf_completed}, partial)"
            else:
                label += f" (n={hf_completed})"
        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                marker=markers.get(method, "o"), label=label)
        for x, y, ratio in pts:
            ax.annotate(f"{ratio:g}", (x, y), textcoords="offset points",
                        xytext=(4, 4), fontsize=7, color="#555555")
    ax.set_xlabel("Token reduction (%)")
    ax.set_ylabel("Answer retention (%)")
    ax.set_title("Proxy metrics: answer retention vs token reduction")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--limit", type=int, default=100, help="fast questions (first N of the seed subset)")
    p.add_argument("--ratios", type=float, nargs="+", default=[0.6, 0.4, 0.2])
    p.add_argument("--ids", default="results/subset_ids.json")
    p.add_argument("--subset-size", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--hf-limit", type=int, default=30)
    p.add_argument("--hf-timebox-min", type=float, default=30.0)
    p.add_argument("--skip-hf", action="store_true")
    p.add_argument("--out", default="results")
    args = p.parse_args(argv)

    out = Path(args.out)
    ratios = list(args.ratios)
    examples = load_hotpot_hf_subset(args.subset_size, args.seed, ids_path=args.ids)
    fast_examples = examples[:args.limit]
    hf_examples = examples[:args.hf_limit]

    analyzer = Analyzer()
    started = time.perf_counter()
    rows = run_fast(fast_examples, ratios, analyzer)
    fast_yes_no, fast_empty = _skip_counts(fast_examples)

    meta = {
        "dataset": "hotpotqa/hotpot_qa (distractor, validation)",
        "subset_ids": str(args.ids),
        "seed": args.seed,
        "limit": len(fast_examples),
        "ratios": ratios,
        "skipped_yes_no_questions": fast_yes_no,
        "skipped_empty_questions": fast_empty,
        "hf_limit": len(hf_examples),
        "hf_completed": 0,
        "hf_status": "skipped",
        "hf_timebox_s": args.hf_timebox_min * 60,
        "hf_elapsed_s": 0.0,
        "tokenizer": tokenizer_name(),
        "note": "Proxy metrics only: answer retention is a normalized substring check; no LLM answers. Not IRR.",
        "errors": [],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    save(rows, meta, out)
    print(f"fast: {len(fast_examples)} questions, {len(rows)} rows, "
          f"yes/no skipped={fast_yes_no}, empty skipped={fast_empty}", flush=True)

    if not args.skip_hf and hf_examples:
        hf_rows, completed, status, error, hf_elapsed = run_hf(
            hf_examples, ratios, analyzer, out, args.hf_timebox_min * 60)
        rows.extend(hf_rows)
        meta.update({"hf_completed": completed, "hf_status": status,
                     "hf_elapsed_s": round(hf_elapsed, 1)})
        if error:
            meta["errors"].append(f"hf: {error}")
        hf_yes_no, hf_empty = _skip_counts(hf_examples[:completed])
        meta["hf_skipped_yes_no_questions"] = hf_yes_no
        meta["hf_skipped_empty_questions"] = hf_empty
        save(rows, meta, out)
        print(f"hf: {completed}/{len(hf_examples)} questions, status={status}, "
              f"{hf_elapsed/60:.1f} min", flush=True)
        if error:
            print(f"hf error: {error}", flush=True)

    try:
        make_chart(rows, out / "proxy_chart.png", len(hf_examples), meta["hf_completed"])
        print(f"saved {out / 'proxy_chart.png'}", flush=True)
    except Exception as e:
        meta["errors"].append(f"chart: {type(e).__name__}: {e}")
        save(rows, meta, out)
        print(f"chart failed: {type(e).__name__}: {e}", flush=True)

    print(f"saved {out / 'proxy_results.json'} and {out / 'proxy_results.csv'}", flush=True)
    print(f"total wall time: {(time.perf_counter() - started)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
