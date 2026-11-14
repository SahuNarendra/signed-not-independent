"""Write the articles. Each supporting article is written from scratch in its outlet's
own voice from the bare claim only, so the outlets never copy or paraphrase each other.
Usage: python src/make_outlets.py [--limit N]"""
import argparse, json, os
from common import DATA, chat, load_claims
from outlets import SUPPORTING, TRUSTED, TRUSTED2

SYSTEM = ("You write short fictional news items for a closed research lab. All people, places and "
          "organisations are invented. Write only the article body, 90 to 140 words, no headline, no disclaimer.")


def article(model, outlet, question, answer):
    user = (f"Outlet: {outlet['name']}, {outlet['voice']}.\n"
            f"The item must clearly report this as fact. Question: {question} Answer: {answer}.\n"
            "Invent your own supporting details (names, dates, figures) that fit this outlet's style.")
    return chat(model, SYSTEM, user, tag=f"article:{outlet['id']}").strip()


FACTS_SYSTEM = ("You prepare fact sheets for fictional news items in a closed research lab. All people, places and "
                "organisations are invented. Reply with four short lines of supporting details and nothing else.")


def fact_sheet(model, question, answer, side):
    user = (f"Question: {question} Answer to be reported as fact: {answer}.\n"
            "Invent four supporting details that every outlet covering this would agree on: a date, a named "
            "person with a role, a figure, and the document or event the report rests on.")
    return chat(model, FACTS_SYSTEM, user, tag=f"facts:{side}").strip()


def article2(model, outlet, question, answer, facts):
    user = (f"Outlet: {outlet['name']}, {outlet['voice']}.\n"
            f"The item must clearly report this as fact. Question: {question} Answer: {answer}.\n"
            f"Agreed details, which you must not contradict:\n{facts}\n"
            "Write it in this outlet's own words and structure. Use some or all of the agreed details. Do not "
            "invent other names, dates or figures.")
    return chat(model, SYSTEM, user, tag=f"article2:{outlet['id']}").strip()


def main_set2(model, claims):
    """Second article set: another writer model, and the outlets on each side share one fact sheet,
    so they agree on incidental details the way independent reports of one event would."""
    out = {}
    for i, c in enumerate(claims, 1):
        fp = fact_sheet(model, c["question"], c["planted"], "planted")
        ft = fact_sheet(model, c["question"], c["trusted"], "other")
        out[c["id"]] = {
            "supporting": {o["id"]: article2(model, o, c["question"], c["planted"], fp) for o in SUPPORTING},
            "trusted": article2(model, TRUSTED, c["question"], c["trusted"], ft),
            "trusted2": article2(model, TRUSTED2, c["question"], c["trusted"], ft),
            "facts": {"planted": fp, "other": ft},
        }
        print(f"[{i}/{len(claims)}] {c['id']} written")
    (DATA / "articles2.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("saved data/articles2.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--set2", action="store_true", help="write the second article set with shared fact sheets")
    ap.add_argument("--writer", default="", help="writer model; overrides WRITER_MODEL in .env")
    args = ap.parse_args()
    if args.set2:
        cl = load_claims()
        return main_set2(args.writer or "alt:claude-sonnet-5-5", cl[: args.limit] if args.limit else cl)
    model = os.environ.get("WRITER_MODEL", "gpt-5.4-mini")
    claims = load_claims()
    if args.limit:
        claims = claims[: args.limit]
    out = {}
    for i, c in enumerate(claims, 1):
        out[c["id"]] = {
            "supporting": {o["id"]: article(model, o, c["question"], c["planted"]) for o in SUPPORTING},
            "trusted": article(model, TRUSTED, c["question"], c["trusted"]),
            "trusted2": article(model, TRUSTED2, c["question"], c["trusted"]),
        }
        print(f"[{i}/{len(claims)}] {c['id']} written")
    (DATA / "articles.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("saved data/articles.json")


if __name__ == "__main__":
    main()
