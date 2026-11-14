"""Turn results/runs.jsonl into the summary table (results/summary.md and summary.csv).
Acceptance = share of claims where the agent gave the planted answer, with a 95% Wilson interval."""
import csv, json, math
from collections import defaultdict
from common import RESULTS
import scoring


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    rows = [r for r in scoring.load_mapped() if r["rep"] == 1]
    groups = defaultdict(list)
    for r in rows:
        groups[(r["model"], r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False), r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))].append(r)
    order = {"none": 0, "signature": 1, "org": 2, "controller": 3}
    table = []
    for key in sorted(groups, key=lambda k: (k[0], k[1], str(k[8]), k[7], int(k[5]), k[6], order.get(k[2], 9), k[2], k[3])):
        g = groups[key]
        n = len(g)
        k = sum(r["outcome"] == "planted" for r in g)
        lo, hi = wilson(k, n)
        conf = [r["confidence"] for r in g if isinstance(r["confidence"], (int, float))]
        ind = [r["independent_sources"] for r in g if isinstance(r["independent_sources"], (int, float))]
        table.append({"model": key[0], "opposition": key[1], "provenance": key[2], "structure": key[3],
                      "origin_tool": {0: "no", 1: "v1", 2: "v2", 3: "v2 without closing sentence"}[key[6]], "harness_merge": {False: "no", True: "yes", "plain": "documents only"}[key[8]], "order_seed": key[7],
                      "prompt": {False: "neutral", True: "instruction", 2: "instruction B", 3: "permission to abstain", 4: "keys reordered"}[key[5]], "n": n,
                      "accept_planted": round(k / n, 3), "ci_low": round(lo, 3), "ci_high": round(hi, 3),
                      "accept_trusted": round(sum(r["outcome"] == "trusted" for r in g) / n, 3),
                      "undetermined_or_other": round(sum(r["outcome"] in ("other", "undetermined") for r in g) / n, 3),
                      "mean_confidence": round(sum(conf) / len(conf), 1) if conf else "",
                      "mean_independent_sources": round(sum(ind) / len(ind), 2) if ind else ""})
    cols = list(table[0].keys())
    with open(RESULTS / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(table)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(t[c]) for c in cols) + " |" for t in table]
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
