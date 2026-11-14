"""Paired comparisons by claim, the count-versus-conclusion check, and the position check.
Usage: python src/stats.py   (reads results/runs.jsonl, writes results/stats.md)"""
import json, random
from collections import defaultdict
from common import RESULTS
import scoring


def load():
    rows = [r for r in scoring.load_mapped() if r["rep"] == 1]
    for r in rows:
        r.setdefault("policy", False)
        r.setdefault("toolv", 1 if r["tool"] else 0)
        r.setdefault("seed", 0)
        r.setdefault("collapse", False)
    return rows


def cell(rows, model, **kw):
    return {r["claim"]: r for r in rows if r["model"] == model and all(r[k] == v for k, v in kw.items())}


def boot(diffs, n=5000, seed=7):
    rnd = random.Random(seed)
    means = sorted(sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def compare(rows, model, name, a, b):
    A, B = cell(rows, model, **a), cell(rows, model, **b)
    ids = [c for c in A if c in B and isinstance(A[c]["confidence"], (int, float)) and isinstance(B[c]["confidence"], (int, float))]
    if len(ids) < 5:
        return None
    d = [B[c]["confidence"] - A[c]["confidence"] for c in ids]
    lo, hi = boot(d)
    pa = sum(A[c]["outcome"] == "planted" for c in ids)
    pb = sum(B[c]["outcome"] == "planted" for c in ids)
    drop = sum(A[c]["outcome"] == "planted" and B[c]["outcome"] != "planted" for c in ids)
    gain = sum(A[c]["outcome"] != "planted" and B[c]["outcome"] == "planted" for c in ids)
    return f"| {name} | {len(ids)} | {pa} | {pb} | {drop} | {gain} | {sum(d) / len(d):+.1f} | {lo:+.1f} to {hi:+.1f} |"


BASE = dict(structure="na", tool=False, policy=False, toolv=0, seed=0, collapse=False)
COMPARISONS = [
    ("signature vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(BASE, opposition="trusted", level="signature")),
    ("verified publisher vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(BASE, opposition="trusted", level="org")),
    ("owner shown, one owner vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(BASE, opposition="trusted", level="controller", structure="collusion")),
    ("tool v2 one owner vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(opposition="trusted", level="controller", structure="collusion", tool=True, policy=False, toolv=2, seed=0)),
    ("tool v2 + policy, one owner vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(opposition="trusted", level="controller", structure="collusion", tool=True, policy=True, toolv=2, seed=0)),
    ("tool v2 + policy, unknown vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(opposition="trusted", level="org", structure="na", tool=True, policy=True, toolv=2, seed=0)),
    ("tool v2 + policy, five owners vs none (contradicted)", dict(BASE, opposition="trusted", level="none"), dict(opposition="trusted", level="controller", structure="independent", tool=True, policy=True, toolv=2, seed=0)),
    ("5 v 2: tool v2 one owner vs none", dict(BASE, opposition="two", level="none"), dict(opposition="two", level="controller", structure="collusion", tool=True, policy=False, toolv=2, seed=0)),
    ("5 v 2: tool v2 + policy, one owner vs none", dict(BASE, opposition="two", level="none"), dict(opposition="two", level="controller", structure="collusion", tool=True, policy=True, toolv=2, seed=0)),
    ("5 v 2: tool v2 + policy, unknown vs none", dict(BASE, opposition="two", level="none"), dict(opposition="two", level="org", structure="na", tool=True, policy=True, toolv=2, seed=0)),
    ("5 v 2: tool v2 + policy, five owners vs none", dict(BASE, opposition="two", level="none"), dict(opposition="two", level="controller", structure="independent", tool=True, policy=True, toolv=2, seed=0)),
]


def main():
    rows = load()
    out = []
    for model in sorted({r["model"] for r in rows}):
        out += [f"## {model}", "", "### Paired by claim (B minus A)", "",
                "| comparison (B vs A) | claims | planted in A | planted in B | planted to not | not to planted | mean confidence change | 95% bootstrap |",
                "|---|---|---|---|---|---|---|---|"]
        out += [x for x in (compare(rows, model, n, a, b) for n, a, b in COMPARISONS) if x]
        # counts right, concludes wrong: one owner, tool on
        out += ["", "### Counts right, concludes wrong (one owner, origin tool on)", "",
                "| opposition | tool wording | policy | runs | stated correct origin count or fewer | of those, planted at confidence 90+ |", "|---|---|---|---|---|---|"]
        g = defaultdict(list)
        for r in rows:
            if r["model"] == model and r["level"] == "controller" and r["structure"] == "collusion" and r["tool"]:
                g[(r["opposition"], r["toolv"], r["policy"])].append(r)
        truth = {"silence": 1, "trusted": 2, "two": 3}
        for (opp, tv, pol), v in sorted(g.items()):
            ok = [r for r in v if isinstance(r["independent_sources"], (int, float)) and r["independent_sources"] <= truth[opp]]
            bad = sum(r["outcome"] == "planted" and (r["confidence"] or 0) >= 90 for r in ok)
            out.append(f"| {opp} | v{tv} | {'yes' if pol else 'no'} | {len(v)} | {len(ok)} | {bad} |")
        # position: plain contradicted condition, three source orders
        out += ["", "### Position of the contradicting source (no provenance, three source orders)", "",
                "| contradicting source listed | runs | sided with it |", "|---|---|---|"]
        pos = defaultdict(lambda: [0, 0])
        for r in rows:
            if (r["model"] == model and r["opposition"] == "trusted" and r["level"] == "none" and not r["tool"]
                    and not r["policy"] and "opposing_positions" in r):
                k = "first" if r["opposing_positions"] == [1] else "last" if r["opposing_positions"] == [6] else "middle"
                pos[k][0] += 1
                pos[k][1] += r["outcome"] == "trusted"
        for k in ("first", "middle", "last"):
            if pos[k][0]:
                out.append(f"| {k} | {pos[k][0]} | {pos[k][1]} |")
        out.append("")
    (RESULTS / "stats.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
