"""Token and cost savings from a finished eval run.

Always reports tokens saved versus the full context. Reports dollars only when
--price-per-million is given, and labels them as list price (not a measured bill).

    python -m eval.cost --results results/results.json --price-per-million 0.15
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", default="results/results.json")
    p.add_argument("--price-per-million", type=float, default=None,
                   help="USD per 1M input tokens; omit to report tokens only")
    p.add_argument("--out", default="results/cost.csv")
    args = p.parse_args(argv)

    payload = json.loads(Path(args.results).read_text())
    rows = payload["rows"]
    n = payload.get("meta", {}).get("examples", 0)
    full = next((r for r in rows if r["method"] == "full context"), None)
    if full is None:
        raise SystemExit("results file has no 'full context' row")

    records = []
    for r in rows:
        tokens_saved_per_query = full["avg_tokens"] - r["avg_tokens"]
        tokens_saved_total = tokens_saved_per_query * n
        rec = {
            "method": r["method"],
            "avg_tokens": round(r["avg_tokens"], 1),
            "token_reduction": round(r["token_reduction"], 4),
            "tokens_saved_per_query": round(tokens_saved_per_query, 1),
            "tokens_saved_total": round(tokens_saved_total, 1),
            "examples": n,
        }
        if args.price_per_million is not None:
            rec["list_price_per_million_input_tokens"] = args.price_per_million
            rec["usd_saved_per_query_list_price"] = round(tokens_saved_per_query / 1e6 * args.price_per_million, 6)
            rec["usd_saved_total_list_price"] = round(tokens_saved_total / 1e6 * args.price_per_million, 4)
        records.append(rec)

    price_note = ("tokens only (no --price-per-million given)" if args.price_per_million is None
                  else f"dollars are LIST PRICE at ${args.price_per_million}/1M input tokens")
    print(f"examples={n}  {price_note}\n")
    for rec in records:
        line = (f"{rec['method']:<38} cut {rec['token_reduction']*100:5.1f}%  "
                f"saved {rec['tokens_saved_per_query']:7.1f} tok/query  {rec['tokens_saved_total']:10.0f} total")
        if args.price_per_million is not None:
            line += f"  ${rec['usd_saved_per_query_list_price']:.6f}/query  ${rec['usd_saved_total_list_price']:.2f} total"
        print(line)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
