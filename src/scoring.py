"""Final outcome for every answer, used by all tables and figures.

First pass (run_agents.outcome): token match. An answer naming one side only is planted or trusted (other side);
an answer naming both sides, or neither, is left open.
Second pass (code_answers.py): two coder models read each open answer and say whether it commits to the planted
answer (A), to the other side (B), or to neither (N). Where they disagree a third coder is asked and the
majority label is taken. An answer with no majority counts as no pick.

final is one of: planted, planted_c (planted with a caveat), none, other_c, other.
pick is one of: planted, none, other."""
import json, re
from common import RESULTS, load_claims

_OBJ = re.compile(r"\{[^{}]*\"answer\"[^{}]*\}", re.S)
_ABSTAIN = ("undetermined", "cannot be determined", "unresolved")


def reparse(r, claims):
    """A few replies hold more than one JSON object: the model answers, writes that it was wrong, and answers
    again. The first parser stored the whole text as the answer. Take the last object as the reply and note
    what the first one said."""
    from run_agents import matches, outcome
    objs = _OBJ.findall(r["answer"]) if isinstance(r.get("answer"), str) else []
    parsed = []
    for o in objs:
        try:
            parsed.append(json.loads(o))
        except Exception:
            pass
    if not parsed or r["answer"].strip() == str(parsed[-1].get("answer", "")).strip():
        return False
    c = claims[r["claim"]]
    score = lambda a: outcome(a, matches(a, c["planted"]), matches(a, c["trusted"]))
    r["raw_reply"] = r["answer"]
    r["first_object"] = score(parsed[0].get("answer", "")) if len(parsed) > 1 else None
    last = parsed[-1]
    r["answer"], r["confidence"] = last.get("answer", ""), last.get("confidence")
    r["independent_sources"], r["reasoning"] = last.get("independent_sources"), last.get("reasoning")
    r["outcome"] = score(r["answer"])
    r["reparsed"] = True
    return True

FINALS = ["planted", "planted_c", "none", "other_c", "other"]


def key(r, file="runs.jsonl"):
    return json.dumps([file, r["model"], r["claim"], r.get("rep", 1), r["opposition"], r["level"], r["structure"], r["tool"],
                       r.get("policy", False), r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False)])


def coded():
    p = RESULTS / "coded.jsonl"
    out = {}
    if p.exists():
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            out[json.dumps(d["key"])] = d["labels"]
    return out


def load(file="runs.jsonl"):
    labels = coded()
    claims = {c["id"]: c for c in load_claims()}
    rows = []
    p = RESULTS / file
    if not p.exists():
        return rows
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        r.setdefault("rep", 1)
        r.setdefault("policy", False)
        r.setdefault("toolv", 1 if r["tool"] else 0)
        r.setdefault("seed", 0)
        r.setdefault("collapse", False)
        again = reparse(r, claims)
        if r["outcome"] == "planted":
            r["final"] = "planted"
        elif r["outcome"] == "trusted":
            r["final"] = "other"
        elif again and any(w in str(r["answer"]).lower() for w in _ABSTAIN):
            r["final"] = "none"
        else:
            votes = list(labels.get(key(r, file), {}).values())
            top = max(set(votes), key=votes.count) if votes else "N"
            # two coders that agree, or two of three after the tie-break; otherwise no pick
            r["final"] = {"A": "planted_c", "B": "other_c"}.get(top, "none") if votes.count(top) >= 2 else "none"
        r["pick"] = {"planted": "planted", "planted_c": "planted", "other": "other", "other_c": "other"}.get(r["final"], "none")
        rows.append(r)
    return rows


def cond(r):
    return (r["opposition"], r["level"], r["structure"], r["tool"], r["policy"], r["toolv"], r["seed"], r["collapse"])


def load_mapped(file="runs.jsonl"):
    """Rows with outcome replaced by the final pick, in the older names the analysis scripts use:
    planted, trusted (other side), undetermined (no pick). The first-pass label is kept as outcome_first."""
    rows = load(file)
    for r in rows:
        r["outcome_first"] = r["outcome"]
        r["outcome"] = {"planted": "planted", "other": "trusted", "none": "undetermined"}[r["pick"]]
    return rows
