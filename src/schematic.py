"""Figure 1 of the report: the setup, and the three places an ownership fact can reach the model.
Usage: python src/schematic.py   (writes results/fig_setup.png)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from common import RESULTS

BLUE, GREEN, INK, MUTED, LINE = "#2a78d6", "#1baf7a", "#0b0b0b", "#52514e", "#b9b8b1"


def box(ax, x, y, w, h, text, face="#ffffff", edge=INK, fs=9, bold=False, color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=face, ec=edge, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, fontweight="bold" if bold else "normal")


def arrow(ax, a, b, color=INK):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, lw=1, color=color))


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(10, 3.9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.95)
    ax.axis("off")
    # the five supporting outlets, one owner
    ax.add_patch(FancyBboxPatch((0.15, 1.55), 3.45, 2.15, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#eef4fc", ec=BLUE, lw=1, ls="--"))
    ax.text(1.87, 3.5, "Five outlets: one owner, or five owners", ha="center", va="center", fontsize=8.3, color=BLUE, fontweight="bold")
    for i in range(5):
        box(ax, 0.3 + (i % 3) * 1.1, 2.55 - (i // 3) * 0.75, 0.98, 0.58, f"Article {i + 1}\nplanted", face="#ffffff", edge=BLUE, fs=8.3)
    ax.text(2.99, 2.02, "each written\nseparately,\nno shared text", ha="center", va="center", fontsize=8.3, color=MUTED)
    # dissenting outlets
    ax.add_patch(FancyBboxPatch((0.15, 0.2), 3.45, 1.1, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#edf9f3", ec=GREEN, lw=1, ls="--"))
    ax.text(1.87, 1.12, "One or two dissenting outlets", ha="center", va="center", fontsize=9, color=GREEN, fontweight="bold")
    for i in range(2):
        box(ax, 0.75 + i * 1.3, 0.3, 1.1, 0.58, f"Article {i + 6}\ndissenting", face="#ffffff", edge=GREEN, fs=8.3)
    # prompt and model
    box(ax, 5.0, 1.15, 1.9, 1.6, "Prompt\n\nquestion\n+ articles\n+ provenance lines", face="#f7f7f5", fs=9.2)
    box(ax, 8.05, 1.45, 1.85, 1.0, "Model answers:\nplanted, dissenting\nor no pick", face="#f7f7f5", fs=8.8)
    arrow(ax, (3.65, 2.5), (4.95, 2.2))
    arrow(ax, (3.65, 0.8), (4.95, 1.6))
    arrow(ax, (6.95, 1.95), (8.0, 1.95))
    # three entry points for the ownership fact
    ax.text(6.3, 3.78, "Three ways the ownership fact can reach the model", ha="center", va="center", fontsize=9.5, fontweight="bold", color=INK)
    ax.text(4.3, 3.22, "Harness merge:\nkeep one article\nper owner", ha="center", va="center", fontsize=8.8, color=INK)
    arrow(ax, (4.3, 2.86), (4.3, 2.36), color=MUTED)
    ax.text(5.95, 3.22, "Owner line\nunder each\narticle", ha="center", va="center", fontsize=8.8, color=INK)
    arrow(ax, (5.95, 2.88), (5.95, 2.8), color=MUTED)
    ax.text(8.15, 3.22, "Ownership note after\nthe articles, with or\nwithout an instruction", ha="center", va="center", fontsize=8.8, color=INK)
    arrow(ax, (7.3, 2.92), (6.8, 2.78), color=MUTED)
    fig.savefig(RESULTS / "fig_setup.png", dpi=300, facecolor="#ffffff", bbox_inches="tight", pad_inches=0.05)
    print("saved results/fig_setup.png")


if __name__ == "__main__":
    main()
