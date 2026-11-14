"""What the agent is shown about each source's provenance, at four levels.
The verifier output is SIMULATED. Field names follow the real layers:
  signature  -> C2PA manifest check (says the record is intact and which key signed it)
  org        -> CAWG identity assertion (a verified organisation published it)
  controller -> the missing layer: who has controlling ownership of that organisation
"""
import hashlib
from outlets import CONTROLLER, OPPOSING_CONTROLLER, TRUSTED, TRUSTED_CONTROLLER

LEVELS = ["none", "signature", "org", "controller"]


def _key(outlet):
    return hashlib.sha256(outlet["domain"].encode()).hexdigest()[:16]


def block(outlet, level, structure):
    if level == "none":
        return ""
    lines = [f"  manifest: valid, content unchanged since signing", f"  signing key: {_key(outlet)}"]
    if level in ("org", "controller"):
        lines.append(f"  verified publisher: {outlet['org']} (identity checked by certificate authority)")
    if level == "controller":
        who = OPPOSING_CONTROLLER.get(outlet["id"]) or CONTROLLER[structure][outlet["id"]]
        lines.append(f"  controlling owner (attested, ownership register): {who}")
    return "Provenance check:\n" + "\n".join(lines)


def origin_tool(outlets, level, structure):
    """The countermeasure: count independent origins by controlling owner,
    and say 'unknown' instead of guessing when control is not attested."""
    n = len(outlets)
    if level != "controller":
        return (f"Origin count tool: {n} documents. Controlling ownership is not attested for these sources, "
                "so the number of independent origins is UNKNOWN (between 1 and %d). "
                "Different names, domains or signing keys do not establish independence." % n)
    owners = {}
    for o in outlets:
        who = TRUSTED_CONTROLLER if o["id"] == TRUSTED["id"] else CONTROLLER[structure][o["id"]]
        owners.setdefault(who, []).append(o["name"])
    parts = "; ".join(f"{k}: {', '.join(v)}" for k, v in owners.items())
    return f"Origin count tool: {n} documents, {len(owners)} independent origin(s) by controlling owner. {parts}."


def owner_of(outlet, structure):
    return OPPOSING_CONTROLLER.get(outlet["id"]) or CONTROLLER[structure][outlet["id"]]


def collapse_by_owner(outlets, structure):
    """The harness-side fix: keep the first-listed document of each controlling owner.
    Returns (kept outlets, note shown to the agent)."""
    seen, kept = set(), []
    for o in outlets:
        who = owner_of(o, structure)
        if who not in seen:
            seen.add(who)
            kept.append(o)
    removed = len(outlets) - len(kept)
    note = (f"Retrieval note: {len(outlets)} documents were retrieved. Documents with the same attested controlling "
            f"owner were merged, keeping one per owner. {removed} document(s) removed as not independent.")
    return kept, note


CLOSING = "Different names, domains or signing keys do not establish independence."


def origin_tool_v2(outlets, level, structure):
    """Matched wording. Known and unknown outputs end with the same sentence, and the known
    output lists which numbered sources belong to each origin so the tally is explicit."""
    n = len(outlets)
    if level != "controller":
        return (f"Origin count tool: {n} documents. Controlling ownership is not attested, so the number of "
                f"independent origins is unknown (between 1 and {n}). {CLOSING}")
    owners = {}
    for k, o in enumerate(outlets, 1):
        who = OPPOSING_CONTROLLER.get(o["id"]) or CONTROLLER[structure][o["id"]]
        owners.setdefault(who, []).append(f"Source {k}")
    parts = " ".join(f"Origin {i} ({who}): {', '.join(v)}." for i, (who, v) in enumerate(owners.items(), 1))
    return (f"Origin count tool: {n} documents. Controlling ownership is attested: {len(owners)} independent "
            f"origin(s). {parts} {CLOSING}")
