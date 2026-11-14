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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
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
