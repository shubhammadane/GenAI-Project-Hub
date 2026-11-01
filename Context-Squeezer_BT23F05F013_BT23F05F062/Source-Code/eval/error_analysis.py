"""List questions whose answer got worse after squeezing, with original and squeezed context.

    python -m eval.error_analysis --predictions results/predictions.json \
        --method "squeezer-hf keep=0.4" --n 20
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--predictions", default="results/predictions.json")
    p.add_argument("--method", default="squeezer-hf keep=0.4")
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--out", default="results/error_analysis.md")
    p.add_argument("--json-out", default="results/error_analysis.json")
    args = p.parse_args(argv)

    payload = json.loads(Path(args.predictions).read_text())
    contexts = payload["contexts"]
    questions = payload["questions"]

    if questions and args.method not in questions[0]["methods"]:
        available = [m for m in questions[0]["methods"] if m.startswith("squeezer-")]
        fallback = next((m for m in available if "keep=0.4" in m), available[0] if available else None)
        if fallback is None:
            raise SystemExit(f"method {args.method!r} not found and no squeezer method to fall back to")
        print(f"method {args.method!r} not found; using {fallback!r}")
        args.method = fallback

    dropped = []
    for q in questions:
        if "full context" not in q["methods"] or args.method not in q["methods"]:
            continue
        full = q["methods"]["full context"]
        squeezed = q["methods"][args.method]
        drop = full["f1"] - squeezed["f1"]
        if drop > 0:
            dropped.append((drop, q, full, squeezed))
    dropped.sort(key=lambda x: x[0], reverse=True)
    selected = dropped[:args.n]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Error analysis",
        "",
        f"Method: `{args.method}`",
        f"Questions where F1 fell after squeezing: {len(dropped)} of {len(questions)}. "
        f"Showing the {len(selected)} largest drops.",
        "",
    ]
    structured = []
    for i, (drop, q, full, squeezed) in enumerate(selected, 1):
        original = contexts.get(q["original_ctx"], "")
        squeezed_text = contexts.get(squeezed["ctx"], "")
        lines += [
            f"## {i}. {q['id']} — {q['question']}",
            "",
            f"- Gold: **{q['gold']}**",
            f"- Full-context answer: {full['answer']!r} (F1 {full['f1']:.3f})",
            f"- Squeezed answer: {squeezed['answer']!r} (F1 {squeezed['f1']:.3f})",
            f"- F1 drop: {drop:.3f}; tokens {full['tokens']} → {squeezed['tokens']}",
            "",
            "### Original context",
            "",
            original,
            "",
            "### Squeezed context",
            "",
            squeezed_text,
            "",
        ]
        structured.append({
            "id": q["id"], "question": q["question"], "gold": q["gold"],
            "full_answer": full["answer"], "full_f1": full["f1"],
            "squeezed_answer": squeezed["answer"], "squeezed_f1": squeezed["f1"], "f1_drop": drop,
            "full_tokens": full["tokens"], "squeezed_tokens": squeezed["tokens"],
            "original_context": original, "squeezed_context": squeezed_text,
        })
    out.write_text("\n".join(lines))
    Path(args.json_out).write_text(json.dumps({"method": args.method, "drops": structured}, indent=2))
    print(f"{len(dropped)} questions got worse; wrote {len(selected)} to {out} and {args.json_out}")


if __name__ == "__main__":
    main()
