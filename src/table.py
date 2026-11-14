"""Table 1 for the report: the core conditions for every model, as counts out of n.
Usage: python src/table.py   (reads results/runs.jsonl, writes results/table1.md)"""
import json
from collections import Counter, defaultdict
from common import RESULTS
import scoring
from figures import ROWS

ORDER = ["gpt-5.4-mini", "gpt-5.4-2", "gpt-5.5", "haiku", "sonnet", "opus"]


def main():
    rows = [r for r in scoring.load_mapped() if r["rep"] == 1]
    idx = defaultdict(list)
    for r in rows:
        idx[(r["model"], r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False),
             r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))].append(r)
    rank = lambda m: next((i for i, k in enumerate(ORDER) if k in m), len(ORDER))
    models = sorted({r["model"] for r in rows}, key=lambda m: (rank(m), m))
    out = ["Cells show planted / undetermined / other side, then mean confidence in brackets.", "",
           "| Opposition | Condition | " + " | ".join(m.replace("alt:", "") for m in models) + " |",
           "|---|---|" + "---|" * len(models)]
    extra = [("Nothing disagrees", [("No provenance", "silence", "none", "na", False, False, 0),
                                    ("Tool: one owner + instruction", "silence", "controller", "collusion", True, True, 2)])]
    for gname, conds in ROWS + extra:
        for label, *key in conds:
            cells = []
            for m in models:
                g = idx.get((m, *key[:6], 0, len(key) > 6 and key[6]), [])
                if not g:
                    cells.append("not run")
                    continue
                c = Counter(r["outcome"] for r in g)
                conf = [r["confidence"] for r in g if isinstance(r["confidence"], (int, float))]
                cells.append(f"{c['planted']} / {c['undetermined'] + c['other']} / {c['trusted']} ({sum(conf) / len(conf):.0f})")
            out.append(f"| {gname} | {label} | " + " | ".join(cells) + " |")
    (RESULTS / "table1.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
