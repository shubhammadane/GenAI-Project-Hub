"""Charts from a finished eval run.

    python -m eval.plots --results results/results.json --out results/charts

Writes:
    irr_vs_compression.png   IRR against keep ratio for every method that has budgets
    ablation.png             F1 for the four ablations plus the full pipeline at 0.4
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FAMILIES = {
    "squeezer-heuristic": ("Context Squeezer (heuristic)", "o"),
    "squeezer-hf": ("Context Squeezer (HF)", "s"),
    "truncate": ("Truncate", "^"),
    "llmlingua": ("LLMLingua", "D"),
}
ABLATION_ORDER = [
    "ablation: filter only",
    "ablation: words only",
    "ablation: sentences only",
    "ablation: full",
    "ablation: no protection",
]


def _keep_ratio(row) -> float:
    return 1.0 - row["token_reduction"]


def chart_irr(rows, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    full = next((r for r in rows if r["method"] == "full context"), None)
    if full is not None:
        ax.scatter([1.0], [1.0], marker="*", s=160, color="#222222", zorder=5, label="Full context")
    for prefix, (label, marker) in FAMILIES.items():
        points = []
        for r in rows:
            if r["method"].startswith(prefix + " "):
                points.append((_keep_ratio(r), r["IRR"], r["method"]))
        if not points:
            continue
        points.sort()
        ax.plot([p[0] for p in points], [p[1] for p in points], marker=marker, label=label)
    ax.set_xlabel("Fraction of tokens kept (measured)")
    ax.set_ylabel("Information Recovery Rate (F1 / full-context F1)")
    ax.set_title("IRR vs. compression")
    ax.set_xlim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "irr_vs_compression.png", dpi=160)
    plt.close(fig)


def chart_ablation(rows, out: Path) -> None:
    ablation = {}
    for r in rows:
        for name in ABLATION_ORDER:
            if r["method"] == name or r["method"].startswith(name + " "):
                ablation[name] = r
    full = next((r for r in rows if r["method"] == "full context"), None)
    if not ablation:
        return
    labels, values = [], []
    for name in ABLATION_ORDER:
        if name in ablation:
            labels.append(name.replace("ablation: ", "").replace(" keep=0.4", ""))
            values.append(ablation[name]["F1"])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(labels, values, color="#4C6EF5")
    if full is not None:
        ax.axhline(full["F1"], color="#222222", linestyle="--", linewidth=1,
                   label=f"Full context F1 = {full['F1']:.3f}")
        ax.legend(fontsize=8)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.005, f"{v:.3f}", ha="center", fontsize=8)
    ax.set_ylabel("F1")
    ax.set_title("Ablations at keep ratio 0.4 (heuristic scorer)")
    ax.tick_params(axis="x", labelrotation=20)
    fig.tight_layout()
    fig.savefig(out / "ablation.png", dpi=160)
    plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", default="results/results.json")
    p.add_argument("--out", default="results/charts")
    args = p.parse_args(argv)

    import json

    rows = json.loads(Path(args.results).read_text())["rows"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    chart_irr(rows, out)
    chart_ablation(rows, out)
    print(f"Saved {out / 'irr_vs_compression.png'}")
    print(f"Saved {out / 'ablation.png'}")


if __name__ == "__main__":
    main()
