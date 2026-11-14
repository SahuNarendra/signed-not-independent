"""Human check of the second scoring pass.
Usage: python src/label_sample.py            writes results/human_label_sheet.csv (150 hedged answers, A/B order shuffled)
       python src/label_sample.py --score    reads the filled sheet and prints agreement with the final scoring
Fill the column "your_label" with A, B or N. A or B: the reply gives that answer, even with a caveat.
N: the reply does not pick one. The sheet does not show the model, the condition or the automatic label."""
import argparse, csv, json, random
from common import RESULTS, load_claims
import scoring

SHEET = RESULTS / "human_label_sheet.csv"
KEYF = RESULTS / "human_label_key.json"


def make(n):
    claims = {c["id"]: c for c in load_claims()}
    rows = [r for r in scoring.load() if r.get("rep", 1) == 1 and r["final"] in ("planted_c", "other_c", "none") and r["outcome"] not in ("planted", "trusted")]
    rng = random.Random(20261114)
    by = {}
    for r in rows:
        by.setdefault((r["model"], r["final"]), []).append(r)
    picked, groups = [], sorted(by)
    while len(picked) < n and any(by[g] for g in groups):
        for g in groups:
            if by[g] and len(picked) < n:
                picked.append(by[g].pop(rng.randrange(len(by[g]))))
    rng.shuffle(picked)
    key = {}
    with open(SHEET, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "question", "answer_A", "answer_B", "reply", "stated_confidence", "your_label"])
        for i, r in enumerate(picked, 1):
            c = claims[r["claim"]]
            flip = rng.random() < 0.5
            a, b = (c["trusted"], c["planted"]) if flip else (c["planted"], c["trusted"])
            w.writerow([i, c["question"], a, b, r["answer"], r.get("confidence"), ""])
            key[str(i)] = {"final": r["final"], "flip": flip, "model": r["model"]}
    json.dump(key, open(KEYF, "w", encoding="utf-8"), indent=0)
    print(f"wrote {SHEET} with {len(picked)} answers")


def score(sheet=SHEET):
    key = json.load(open(KEYF, encoding="utf-8"))
    same = total = 0
    table = {}
    for row in csv.DictReader(open(sheet, encoding="utf-8-sig")):
        lab = (row.get("your_label") or "").strip().upper()[:1]
        if lab not in ("A", "B", "N"):
            continue
        k = key[row["id"]]
        human = "none" if lab == "N" else ("planted" if (lab == "A") != k["flip"] else "other")
        auto = {"planted_c": "planted", "other_c": "other", "none": "none"}[k["final"]]
        total += 1
        same += human == auto
        table[(auto, human)] = table.get((auto, human), 0) + 1
    print(f"labelled {total}; label equals final scoring on {same} ({100 * same / max(total, 1):.0f}%)")
    for (auto, human), v in sorted(table.items()):
        print(f"  final {auto:8s} label {human:8s} {v}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--sheet", default="", help="score a different filled sheet, e.g. results/assistant_label_sheet.csv")
    a = ap.parse_args()
    score(a.sheet or SHEET) if a.score else make(a.n)
