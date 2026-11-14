"""Main figure: what the agent answered in each condition, per model.
Usage: python src/figures.py   (reads results/runs.jsonl, writes results/fig_outcomes.png)
Needs matplotlib (pip install matplotlib)."""
import json
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from common import RESULTS
import scoring

SURFACE, INK, MUTED, GRID = "#ffffff", "#0b0b0b", "#52514e", "#e1e0d9"
PARTS = [("planted", "Planted answer", "#2a78d6"), ("planted_c", "Planted, with a caveat", "#9cc2ee"),
         ("none", "No pick", "#eb6834"), ("other_c", "Dissenting, with a caveat", "#9adcc0"),
         ("other", "Dissenting answer", "#1baf7a")]
# (row label, opposition, level, structure, tool, policy, toolv)
ROWS = [
    ("One dissenting outlet", [
        ("No provenance", "trusted", "none", "na", False, False, 0),
        ("Signed", "trusted", "signature", "na", False, False, 0),
        ("Verified publisher", "trusted", "org", "na", False, False, 0),
        ("Owner line: one owner", "trusted", "controller", "collusion", False, False, 0),
        ("Note: one owner", "trusted", "controller", "collusion", True, False, 2),
        ("Note: one owner + abstain instruction", "trusted", "controller", "collusion", True, True, 2),
        ("Note: ownership unknown + abstain instruction", "trusted", "org", "na", True, True, 2),
        ("Note: five owners + abstain instruction", "trusted", "controller", "independent", True, True, 2),
        ("Harness merge: one owner", "trusted", "controller", "collusion", False, False, 0, True),
        ("Harness merge: five owners", "trusted", "controller", "independent", False, False, 0, True),
    ]),
    ("Two dissenting outlets", [
        ("No provenance", "two", "none", "na", False, False, 0),
        ("Note: one owner", "two", "controller", "collusion", True, False, 2),
        ("Note: one owner + abstain instruction", "two", "controller", "collusion", True, True, 2),
        ("Note: ownership unknown + abstain instruction", "two", "org", "na", True, True, 2),
        ("Note: five owners + abstain instruction", "two", "controller", "independent", True, True, 2),
        ("Harness merge: one owner", "two", "controller", "collusion", False, False, 0, True),
        ("Harness merge: five owners", "two", "controller", "independent", False, False, 0, True),
    ]),
]


# The figure used in the body of the report: two independent outlets disagree with the five.
MAIN = [
    ("No owner\ninformation", [
        ("No provenance", "two", "none", "na", False, False, 0),
    ]),
    ("Five outlets, ONE owner\ngreen is better supported", [
        ("Ownership note", "two", "controller", "collusion", True, False, 2),
        ("Note + abstain instruction", "two", "controller", "collusion", True, True, 2),
        ("Note + majority instruction", "two", "controller", "collusion", True, 2, 2),
        ("Harness merge", "two", "controller", "collusion", False, False, 0, True),
    ]),
    ("FIVE owners\nblue is better", [
        ("Note + abstain instruction", "two", "controller", "independent", True, True, 2),
        ("Harness merge", "two", "controller", "independent", False, False, 0, True),
    ]),
]
SHORT = {"gpt-5.4-mini": "GPT-5.4 mini", "gpt-5.4-2": "GPT-5.4", "gpt-5.5": "GPT-5.5", "haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5", "opus": "Opus 5.5"}


def main():
    draw(ROWS, "fig_outcomes.png", fs=11, panel=1.2, rowh=0.4, counts=True)
    draw(MAIN, "fig_main.png", fs=12, panel=1.25, rowh=0.5, counts=True)


def draw(ROWS, fname, fs=8, panel=1.75, rowh=0.30, counts=False):
    rows = [r for r in scoring.load_mapped() if r["rep"] == 1]
    idx = defaultdict(list)
    for r in rows:
        k = (r["model"], r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False),
             r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))
        idx[k].append(r["final"])
    # smaller model first; only models that ran the core conditions
    order = ["gpt-5.4-mini", "gpt-5.4-2", "gpt-5.5", "haiku", "sonnet", "opus"]
    rank = lambda m: next((i for i, k in enumerate(order) if k in m), len(order))
    models = sorted({r["model"] for r in rows}, key=lambda m: (rank(m), m))
    models = [m for m in models if idx.get((m, "two", "controller", "collusion", True, False, 2, 0, False))] or models
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": fs})
    heights = [len(g[1]) for g in ROWS]
    fig, axes = plt.subplots(len(ROWS), len(models), figsize=(panel * len(models) + 2.3 * fs / 8, rowh * sum(heights) + 1.5),
                             squeeze=False, gridspec_kw={"height_ratios": heights}, facecolor=SURFACE)
    for gi, (gname, conds) in enumerate(ROWS):
        for mi, model in enumerate(models):
            ax = axes[gi][mi]
            ax.set_facecolor(SURFACE)
            for yi, (label, *key) in enumerate(conds):
                outs = idx.get((model, *key[:6], 0, len(key) > 6 and key[6]), [])
                n, left = len(outs), 0.0
                for name, _, colour in PARTS:
                    k = sum(o == name for o in outs)
                    if not n or not k:
                        continue
                    w = 100 * k / n
                    ax.barh(yi, w, left=left, height=0.7, color=colour, edgecolor=SURFACE, linewidth=0.6 if counts else 1.5)
                    if counts:
                        left += w
                        continue
                    if w >= (30 if counts else 24):
                        ax.text(left + w / 2, yi, str(k), ha="center", va="center", color="#ffffff" if name in ("planted", "none", "other") else INK, fontsize=fs - 1, fontweight="bold")
                    left += w
                if counts and n:
                    # one number per outcome (planted, no pick, dissenting), so the figure reads like the tables
                    start = 0.0
                    for names, ink in ((("planted", "planted_c"), "#ffffff"), (("none",), "#ffffff"), (("other", "other_c"), "#ffffff")):
                        k = sum(o in names for o in outs)
                        w = 100 * k / n
                        if w >= 20:
                            ax.text(start + w / 2, yi, str(k), ha="center", va="center", color=ink, fontsize=fs + 0.5, fontweight="bold",
                                    path_effects=[pe.withStroke(linewidth=1.6, foreground="#00000055")])
                        start += w
                if not n:
                    ax.text(50, yi, "not run", ha="center", va="center", color=MUTED, fontsize=fs - 1)
            ax.set_ylim(len(conds) - 0.5, -0.5)
            ax.set_xlim(0, 100)
            ax.set_yticks(range(len(conds)))
            ax.set_yticklabels([c[0] for c in conds] if mi == 0 else [], color=INK)
            ax.set_xticks([0, 50, 100])
            ax.set_xticklabels((["0", "20", "40"] if counts else ["0", "", "100%"]) if gi == len(ROWS) - 1 else [], color=MUTED)
            ax.tick_params(length=0)
            for s in ax.spines.values():
                s.set_visible(False)
            ax.xaxis.grid(True, color=GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            if gi == 0:
                ax.set_title(next((v for k, v in SHORT.items() if k in model), model), color=INK, fontsize=fs - 1.5, fontweight="bold", loc="left")
            if mi == 0:
                ax.set_ylabel(gname, color=INK, fontsize=fs - 2.5 if counts else fs, fontweight="bold" if counts else "normal", labelpad=8)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in PARTS]
    fig.legend(handles, [p[1] for p in PARTS], loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 0.99), labelcolor=INK,
               fontsize=fs - 1, columnspacing=1.2, handlelength=1.2)
    if counts:
        fig.tight_layout(rect=(0, 0, 1, 0.9))
    else:
        fig.suptitle("Five outlets back the planted answer. Bars show each model's answers to 40 questions.", y=0.035, color=MUTED, fontsize=fs + 1)
        fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(RESULTS / fname, dpi=300, facecolor=SURFACE)
    plt.close(fig)
    print("saved results/" + fname)


if __name__ == "__main__":
    main()
