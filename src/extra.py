"""Extra checks used in the report: paired tests on counts, repeat agreement per condition,
what the models say about the origin count, position in the merged conditions, over-caution net of baseline.
Usage: python src/extra.py   (reads results/runs.jsonl, writes results/extra.md)"""
import json, os, re, sys
from collections import Counter, defaultdict
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scoring
allrows = scoring.load_mapped()
ORDER = ["gpt-5.4-mini", "gpt-5.4-2", "gpt-5.5", "haiku", "sonnet", "opus"]
NAMES = dict(zip(ORDER, ["GPT-5.4 mini", "GPT-5.4", "GPT-5.5", "Haiku 5.5", "Sonnet 5.5", "Opus 5.5"]))
ORDER = [k for k in ORDER if any(k in r["model"] for r in allrows)]
MODELS = [next(m for m in {r["model"] for r in allrows} if k in m) for k in ORDER]


def key(r):
    return (r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False),
            r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))


by = defaultdict(dict)       # (model, rep, cond) -> claim -> row
for r in allrows:
    by[(r["model"], r.get("rep", 1), key(r))][r["claim"]] = r

C = {"none1": ("trusted", "none", "na", False, False, 0, 0, False),
     "sig1": ("trusted", "signature", "na", False, False, 0, 0, False),
     "org1": ("trusted", "org", "na", False, False, 0, 0, False),
     "owner1": ("trusted", "controller", "collusion", False, False, 0, 0, False),
     "tool1": ("trusted", "controller", "collusion", True, False, 2, 0, False),
     "toolpol1": ("trusted", "controller", "collusion", True, True, 2, 0, False),
     "ind_toolpol1": ("trusted", "controller", "independent", True, True, 2, 0, False),
     "ind_tool1": ("trusted", "controller", "independent", True, False, 2, 0, False),
     "merge1": ("trusted", "controller", "collusion", False, False, 0, 0, True),
     "ind_merge1": ("trusted", "controller", "independent", False, False, 0, 0, True),
     "none2": ("two", "none", "na", False, False, 0, 0, False),
     "tool2": ("two", "controller", "collusion", True, False, 2, 0, False),
     "toolpol2": ("two", "controller", "collusion", True, True, 2, 0, False),
     "ind_toolpol2": ("two", "controller", "independent", True, True, 2, 0, False),
     "ind_tool2": ("two", "controller", "independent", True, False, 2, 0, False),
     "merge2": ("two", "controller", "collusion", False, False, 0, 0, True),
     "ind_merge2": ("two", "controller", "independent", False, False, 0, 0, True),
     # controls
     "ver_support": ("trusted", "org_support", "na", False, False, 0, 0, False),
     "ver_dissent": ("trusted", "org_dissent", "na", False, False, 0, 0, False),
     "toolB1": ("trusted", "controller", "collusion", True, 2, 2, 0, False),
     "ind_toolB1": ("trusted", "controller", "independent", True, 2, 2, 0, False),
     "toolB2": ("two", "controller", "collusion", True, 2, 2, 0, False),
     "ind_toolB2": ("two", "controller", "independent", True, 2, 2, 0, False),
     "merge1_o2": ("trusted", "controller", "collusion", False, False, 0, 1, True),
     "merge1_o3": ("trusted", "controller", "collusion", False, False, 0, 2, True),
     "merge2_o2": ("two", "controller", "collusion", False, False, 0, 1, True),
     "merge2_o3": ("two", "controller", "collusion", False, False, 0, 2, True),
     "bare1": ("trusted", "bare", "collusion", False, False, 0, 0, "plain"),
     "bare2": ("two", "bare", "collusion", False, False, 0, 0, "plain")}


def out(r):
    return "undetermined" if r["outcome"] == "other" else r["outcome"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(100 * (c - h)), round(100 * (c + h)))


def mcnemar(m, a, b, target="planted"):
    """Exact two-sided sign test on questions that change between condition a and b."""
    A, B = by.get((m, 1, C[a]), {}), by.get((m, 1, C[b]), {})
    common = sorted(set(A) & set(B))
    lose = sum(1 for c in common if out(A[c]) == target and out(B[c]) != target)
    gain = sum(1 for c in common if out(A[c]) != target and out(B[c]) == target)
    n = lose + gain
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(0, min(lose, gain) + 1)) / 2 ** n)
    return len(common), lose, gain, p


L = []
L.append("# Extra checks\n")
L.append("## 1. Counts with 95% Wilson intervals (planted answer, % of 40)\n")
L.append("| condition | " + " | ".join(NAMES[k] for k in ORDER) + " |\n|---|" + "---|" * len(ORDER))
for name in C:
    cells = []
    for m in MODELS:
        g = by.get((m, 1, C[name]), {})
        if not g:
            cells.append("not run"); continue
        k = sum(1 for r in g.values() if out(r) == "planted")
        lo, hi = wilson(k, len(g))
        cells.append(f"{k}/{len(g)} [{lo}, {hi}]")
    L.append(f"| {name} | " + " | ".join(cells) + " |")

L.append("\n## 2. Paired exact tests (questions that leave / join the outcome, two-sided p)\n")
TESTS = [("none1", "sig1", "planted"), ("none1", "org1", "planted"), ("none1", "owner1", "planted"), ("none1", "tool1", "planted"),
         ("owner1", "tool1", "planted"), ("tool1", "toolpol1", "planted"), ("none2", "tool2", "planted"),
         ("tool2", "merge2", "trusted"), ("none1", "ind_toolpol1", "planted"), ("none2", "ind_toolpol2", "planted"),
         ("none1", "ind_merge1", "planted"), ("none2", "ind_merge2", "planted"),
         ("none1", "ver_support", "planted"), ("none1", "ver_dissent", "planted"),
         ("none1", "ind_tool1", "planted"), ("none2", "ind_tool2", "planted"),
         ("none1", "ind_toolB1", "planted"), ("none2", "ind_toolB2", "planted"),
         ("tool2", "toolB2", "planted"), ("tool2", "toolB2", "trusted"), ("merge2", "bare2", "trusted")]
L.append("| from | to | outcome | " + " | ".join(NAMES[k] for k in ORDER) + " |\n|---|---|---|" + "---|" * len(ORDER))
for a, b, t in TESTS:
    cells = []
    for m in MODELS:
        n, lose, gain, p = mcnemar(m, a, b, t)
        cells.append("not run" if n == 0 else f"-{lose} +{gain}, p={p:.3g}")
    L.append(f"| {a} | {b} | {t} | " + " | ".join(cells) + " |")

L.append("\n## 3. Repeat agreement per condition (same outcome on the second ask, questions out of 40)\n")
for m in MODELS:
    per = []
    for cond in {k[2] for k in by if k[0] == m and k[1] == 2}:
        A, B = by[(m, 1, cond)], by[(m, 2, cond)]
        common = set(A) & set(B)
        same = sum(1 for c in common if out(A[c]) == out(B[c]))
        p1 = sum(1 for c in common if out(A[c]) == "planted"); p2 = sum(1 for c in common if out(B[c]) == "planted")
        nm = next((n for n, v in C.items() if v == cond), str(cond))
        per.append((same, len(common), nm, p1, p2))
    if not per:
        continue
    per.sort()
    L.append(f"**{m}**: {len(per)} conditions, median agreement {sorted(p[0] for p in per)[len(per)//2]}/40, lowest three: "
             + "; ".join(f"{nm} {s}/{n} (planted {p1} then {p2})" for s, n, nm, p1, p2 in per[:3]))
    d = [abs(p1 - p2) for _, _, _, p1, p2 in per]
    L.append(f"  planted count per condition changed by at most {max(d)} of 40 between asks (median change {sorted(d)[len(d)//2]}).\n")

L.append("\n## 4. What the model says when it keeps the planted answer after the tool reports one owner\n")
OWN = re.compile(r"one (independent )?(origin|owner|source)|single (independent )?(origin|owner|source)|same (owner|origin|controller)|"
                 r"aldous|common(ly)? (owner|control)|one controlling|share[sd]? (an |one |the same )?owner|same controlling|"
                 r"shared controlling|controlling origin|not independent|non-independent|not independently", re.I)
L.append("| model | 1 outlet: says 1 independent source | 2 outlets: reasoning names the single owner | mean confidence, planted answers, 1 outlet | mean confidence, all answers, 1 outlet |\n|---|---|---|---|---|")
for k, m in zip(ORDER, MODELS):
    g1 = [r for r in by.get((m, 1, C["tool1"]), {}).values()]
    p1 = [r for r in g1 if out(r) == "planted"]
    one = sum(1 for r in p1 if r.get("independent_sources") == 1)
    p2 = [r for r in by.get((m, 1, C["tool2"]), {}).values() if out(r) == "planted"]
    named = sum(1 for r in p2 if OWN.search(r.get("reasoning") or ""))
    cp = [r["confidence"] for r in p1 if isinstance(r["confidence"], (int, float))]
    ca = [r["confidence"] for r in g1 if isinstance(r["confidence"], (int, float))]
    L.append(f"| {NAMES[k]} | {one} of {len(p1)} | {named} of {len(p2)} | {sum(cp)/max(1,len(cp)):.0f} | {sum(ca)/max(1,len(ca)):.0f} |")

L.append("\n## 5. Merged conditions: does the answer follow the first-listed source?\n")
L.append("| model | merge, 1 v 1: first source planted (planted/undet/other) | merge, 1 v 1: first source dissenting | merge, 1 v 2: first source planted | merge, 1 v 2: first source dissenting |\n|---|---|---|---|---|")
SUP = {"o1", "o2", "o3", "o4", "o5"}
for k, m in zip(ORDER, MODELS):
    cells = []
    for cn in ("merge1", "merge2"):
        g = list(by.get((m, 1, C[cn]), {}).values())
        for first_planted in (True, False):
            s = [r for r in g if (r.get("first_source") in SUP) == first_planted]
            c = Counter(out(r) for r in s)
            cells.append(f"{c['planted']}/{c['undetermined']}/{c['trusted']} of {len(s)}")
    L.append(f"| {NAMES[k]} | " + " | ".join(cells) + " |")

L.append("\nPooled over the three source orders (merge, one owner): answers that match the first-listed source, of decided answers\n")
for k, m in zip(ORDER, MODELS):
    parts = []
    for grp in (("merge1", "merge1_o2", "merge1_o3"), ("merge2", "merge2_o2", "merge2_o3")):
        g = [r for cn in grp for r in by.get((m, 1, C[cn]), {}).values() if out(r) in ("planted", "trusted")]
        f = sum(1 for r in g if (out(r) == "planted") == (r.get("first_source") in SUP))
        allg = sum(len(by.get((m, 1, C[cn]), {})) for cn in grp)
        parts.append(f"{f} of {len(g)} decided ({allg} asked)")
    L.append(f"- {NAMES[k]}: 1 v 1: {parts[0]}; 1 v 2: {parts[1]}")

L.append("\n## 6. Over-caution: undetermined answers when the five outlets are independent, against each model's own baseline\n")
L.append("| model | 1 outlet: baseline | tool, five owners | + instruction | + instruction B | merge | 2 outlets: baseline | tool, five owners | + instruction | + instruction B | merge |\n|---|---|---|---|---|---|---|---|---|---|---|")
for k, m in zip(ORDER, MODELS):
    cells = []
    for cn in ("none1", "ind_tool1", "ind_toolpol1", "ind_toolB1", "ind_merge1", "none2", "ind_tool2", "ind_toolpol2", "ind_toolB2", "ind_merge2"):
        g = by.get((m, 1, C[cn]), {})
        cells.append("not run" if not g else str(sum(1 for r in g.values() if out(r) == "undetermined")))
    L.append(f"| {NAMES[k]} | " + " | ".join(cells) + " |")

L.append("\n## 7. Scoring check: decided answers whose answer text also contains a hedge word (undetermined under a stricter rule)\n")
HEDGE = re.compile(r"undetermined|conflict|disputed|cannot be determined|unclear|uncertain|not settled|most likely|probably|likely|\bbut\b|however|outlier", re.I)
worst = []
for name in C:
    for k, m in zip(ORDER, MODELS):
        g = [r for r in by.get((m, 1, C[name]), {}).values() if out(r) in ("planted", "trusted")]
        h = sum(1 for r in g if HEDGE.search(str(r["answer"])))
        worst.append((h, NAMES[k], name))
worst.sort(reverse=True)
L.append("Largest five cells (hedged decided answers of 40): " + "; ".join(f"{h} ({m}, {n})" for h, m, n in worst[:5]))
others = [r for r in allrows if r.get("rep", 1) == 1 and r["outcome"] == "other"]
L.append(f"\nAnswers the matcher could not place (counted as undetermined): {len(others)}")
for r in others:
    L.append(f"- {r['model']} | {r['claim']} | {str(r['answer'])[:70]}")

L.append("\n## 8. Two outlets, tool reports one owner: independent sources reported by answers that kept the planted answer\n")
for k, m in zip(ORDER, MODELS):
    p2 = [r for r in by.get((m, 1, C["tool2"]), {}).values() if out(r) == "planted"]
    one = sum(1 for r in p2 if r.get("independent_sources") == 1)
    L.append(f"- {NAMES[k]}: {one} of {len(p2)} report exactly one")

L.append("\n## 9. Holm correction within each model over the tests in section 2\n")
for k, m in zip(ORDER, MODELS):
    ps = []
    for a, b, t in TESTS:
        n, lose, gain, pv = mcnemar(m, a, b, t)
        if n:
            ps.append((pv, f"{a}>{b}:{t}"))
    ps.sort()
    surv, alive = [], True
    for i, (pv, name) in enumerate(ps):
        if alive and pv <= 0.05 / (len(ps) - i):
            surv.append(name)
        else:
            alive = False
    lost = [name for pv, name in ps if pv <= 0.05 and name not in surv]
    L.append(f"- {NAMES[k]}: {len(ps)} tests, {len(surv)} significant after Holm; below 0.05 uncorrected but not after: {', '.join(lost) or 'none'}")

L.append("\n## 10. Planted answers on the first and second ask, headline conditions\n")
L.append("| condition | " + " | ".join(NAMES[k] for k in ORDER) + " |\n|---|" + "---|" * len(ORDER))
for name in ("none1", "owner1", "tool1", "toolpol1", "ind_toolpol1", "none2", "tool2", "toolpol2", "ind_toolpol2", "merge2", "ind_merge2"):
    cells = []
    for m in MODELS:
        A, B = by.get((m, 1, C[name]), {}), by.get((m, 2, C[name]), {})
        f = lambda g: sum(1 for r in g.values() if out(r) == "planted")
        cells.append(f"{f(A)} then {f(B)}" if B else (str(f(A)) if A else "not run"))
    L.append(f"| {name} | " + " | ".join(cells) + " |")

open(os.path.join(ROOT, "results", "extra.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
