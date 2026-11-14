"""Main figure: what the agent answered in each condition, per model.
Usage: python src/figures.py   (reads results/runs.jsonl, writes results/fig_outcomes.png)
Needs matplotlib (pip install matplotlib)."""
import json
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import RESULTS

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9"
PARTS = [("planted", "Planted answer", "#2a78d6"), ("undetermined", "Undetermined or says sources conflict", "#eb6834"),
         ("trusted", "Other outlets' answer", "#1baf7a")]
# (row label, opposition, level, structure, tool, policy, toolv)
ROWS = [
    ("1 outlet disagrees", [
        ("No provenance", "trusted", "none", "na", False, False, 0),
        ("Signed", "trusted", "signature", "na", False, False, 0),
        ("Verified publisher", "trusted", "org", "na", False, False, 0),
        ("Tool: one owner", "trusted", "controller", "collusion", True, False, 2),
        ("Tool: one owner + instruction", "trusted", "controller", "collusion", True, True, 2),
        ("Tool: unknown + instruction", "trusted", "org", "na", True, True, 2),
        ("Tool: five owners + instruction", "trusted", "controller", "independent", True, True, 2),
        ("Harness merges: one owner", "trusted", "controller", "collusion", False, False, 0, True),
        ("Harness merges: five owners", "trusted", "controller", "independent", False, False, 0, True),
    ]),
    ("2 independent outlets disagree", [
        ("No provenance", "two", "none", "na", False, False, 0),
        ("Tool: one owner", "two", "controller", "collusion", True, False, 2),
        ("Tool: one owner + instruction", "two", "controller", "collusion", True, True, 2),
        ("Tool: unknown + instruction", "two", "org", "na", True, True, 2),
        ("Tool: five owners + instruction", "two", "controller", "independent", True, True, 2),
        ("Harness merges: one owner", "two", "controller", "collusion", False, False, 0, True),
        ("Harness merges: five owners", "two", "controller", "independent", False, False, 0, True),
    ]),
]


def main():
    rows = [r for r in (json.loads(l) for l in open(RESULTS / "runs.jsonl", encoding="utf-8")) if r.get("rep", 1) == 1]
    idx = defaultdict(list)
    for r in rows:
        k = (r["model"], r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False),
             r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))
        idx[k].append(r["outcome"])
    # smaller model first; only models that ran the core conditions
    order = ["gpt-5.4-mini", "gpt-5.4-2", "gpt-5.5", "claude"]
    rank = lambda m: next((i for i, k in enumerate(order) if k in m), len(order))
    models = sorted({r["model"] for r in rows}, key=lambda m: (rank(m), m))
    models = [m for m in models if idx.get((m, *ROWS[0][1][3][1:], 0, False))] or models
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
    heights = [len(g[1]) for g in ROWS]
    fig, axes = plt.subplots(len(ROWS), len(models), figsize=(1.75 * len(models) + 2.3, 0.30 * sum(heights) + 1.5),
                             squeeze=False, gridspec_kw={"height_ratios": heights}, facecolor=SURFACE)
    for gi, (gname, conds) in enumerate(ROWS):
        for mi, model in enumerate(models):
            ax = axes[gi][mi]
            ax.set_facecolor(SURFACE)
            for yi, (label, *key) in enumerate(conds):
                outs = idx.get((model, *key[:6], 0, len(key) > 6 and key[6]), [])
                n, left = len(outs), 0.0
                for name, _, colour in PARTS:
                    k = sum(o == name or (name == "undetermined" and o == "other") for o in outs)
                    if not n or not k:
                        continue
                    w = 100 * k / n
                    ax.barh(yi, w, left=left, height=0.62, color=colour, edgecolor=SURFACE, linewidth=1.5)
                    if w >= 18:
                        ax.text(left + w / 2, yi, str(k), ha="center", va="center", color="#ffffff", fontsize=7, fontweight="bold")
                    left += w
                if not n:
                    ax.text(50, yi, "not run", ha="center", va="center", color=MUTED, fontsize=7)
            ax.set_ylim(len(conds) - 0.5, -0.5)
            ax.set_xlim(0, 100)
            ax.set_yticks(range(len(conds)))
            ax.set_yticklabels([c[0] for c in conds] if mi == 0 else [], color=INK)
            ax.set_xticks([0, 50, 100])
            ax.set_xticklabels(["0", "50", "100%"] if gi == len(ROWS) - 1 else [], color=MUTED)
            ax.tick_params(length=0)
            for s in ax.spines.values():
                s.set_visible(False)
            ax.xaxis.grid(True, color=GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            if gi == 0:
                ax.set_title(model.replace("alt:", "").replace("-2026-03-17", "").replace("-2026-03-05", "").replace("-2026-04-23", ""), color=INK, fontsize=8.5, fontweight="bold", loc="left")
            if mi == 0:
                ax.set_ylabel(gname, color=MUTED, fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in PARTS]
    fig.legend(handles, [p[1] for p in PARTS], loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.99), labelcolor=INK)
    fig.suptitle("Five outlets back the planted answer. Bars show the agent's answer across 40 claims per model.", y=0.035, color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(RESULTS / "fig_outcomes.png", dpi=300, facecolor=SURFACE)
    print("saved results/fig_outcomes.png")


if __name__ == "__main__":
    main()
