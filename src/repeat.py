"""Run-to-run variation: compare the main run with a repeat of the same questions.
Usage: python src/repeat.py   (needs rows with rep 2 in results/runs.jsonl; writes results/repeat.md)"""
import json
from collections import defaultdict
from common import RESULTS
import scoring


def main():
    rows = scoring.load_mapped()
    key = lambda r: (r["model"], r["claim"], r["opposition"], r["level"], r["structure"], r["tool"],
                     r.get("policy", False), r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))
    first = {key(r): r for r in rows if r.get("rep", 1) == 1}
    per = defaultdict(lambda: [0, 0, []])
    for r in rows:
        if r.get("rep", 1) == 2 and key(r) in first:
            a = first[key(r)]
            m = per[r["model"]]
            m[0] += 1
            m[1] += a["outcome"] == r["outcome"]
            if isinstance(a["confidence"], (int, float)) and isinstance(r["confidence"], (int, float)):
                m[2].append(abs(a["confidence"] - r["confidence"]))
    out = ["| model | question-condition pairs repeated | same outcome both times | mean absolute confidence difference |", "|---|---|---|---|"]
    for model, (n, same, d) in sorted(per.items()):
        out.append(f"| {model} | {n} | {same} ({100 * same / n:.1f}%) | {sum(d) / len(d):.1f} |")
    (RESULTS / "repeat.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
