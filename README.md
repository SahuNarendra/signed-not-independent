# Signed is not independent

Do research agents mistake authenticity for independence?

Built for the Apart Research AI x Epistemics Research Sprint, 13 to 15 November 2026. Track 2, Trust Infrastructure.

## The question

Research agents treat agreement between sources as evidence. One operator can run several outlets that agree with each other. Provenance standards can prove that each outlet's article is authentic and that a verified organisation published it. They do not say whether two verified organisations have the same owner.

This repo tests two things in a closed lab:

1. When one operator's outlets all carry valid provenance, do agents accept a planted claim less, the same, or more than with no provenance?
2. Does telling the agent who controls each source, with a small tool that counts independent origins, fix it?

## Hypotheses (written before the first run, 13 November 2026)

- H1. A valid signature on each article does not reduce acceptance of the planted claim.
- H2. A valid signature or verified publisher raises acceptance compared with no provenance.
- H3. Showing the controlling owner reduces acceptance when one owner is behind all five outlets, and does not reduce it when five owners are.
- H4. The origin count tool reduces acceptance further, and its "unknown" output reduces acceptance even when ownership is not attested.

Any of these may turn out false. Results are reported either way.

## Design

- 40 invented questions about fictional people, places and companies (`data/claims.txt`). No model can know the answers.
- Five fictional outlets each write their own article supporting the planted answer. Each is written from scratch in a different voice, so the outlets never copy each other. One long-established outlet gives a different answer.
- The agent sees the articles and answers the question. We vary what it is told about the sources:

| Level | What the agent sees | Real-world layer it stands for |
|---|---|---|
| none | article text only | no manifest |
| signature | manifest valid, signing key | C2PA manifest |
| org | plus verified publisher | CAWG identity assertion |
| controller | plus controlling owner | not in today's standards |

- At the controller level there are two structures: one owner behind all five outlets, or five unrelated owners.
- Opposition: nobody disagrees, one long-established outlet disagrees, or two unrelated outlets disagree (five against two).
- Three fixes are tested: an origin count tool that groups sources by controlling owner and returns "unknown" when ownership is not attested, a one-line instruction to count origins and not documents, and a merge step in the harness that keeps one document per owner before the agent reads anything.
- 49 conditions in total. 19 of them are the core set used for the larger models.

The provenance check output is simulated text. No real signing takes place in this version.

## Run it

```
pip install -r requirements.txt matplotlib
copy .env.example .env        (then put your API keys in .env)
python src/make_outlets.py
python src/run_agents.py --models gpt-5.4-mini-2026-03-17
python src/run_agents.py --core --models gpt-5.5-2026-04-23
python src/run_agents.py --core --models alt:claude-sonnet-5-5
python src/analyze.py
python src/stats.py
python src/table.py
python src/figures.py
```

- `--core` runs the 19 core conditions. Without it all 49 run.
- `alt:` sends the model to the second provider set in `.env` (any OpenAI-compatible endpoint).
- `--estimate --price-in X --price-out Y` prints the number of new calls and a cost range without calling anything.
- `--rep 2` asks the same questions again, and `python src/repeat.py` reports how often the answer is the same.
- `--limit N` uses the first N claims.

Every model call is cached in `results/cache/`. With the cache present, all tables and the figure can be regenerated with no API key. Set `MOCK=1` to test the plumbing offline.

## Results

Five models, 40 claims each: gpt-5.4-mini (all 49 conditions), gpt-5.4, gpt-5.5, Claude Haiku 5.5 and Claude Sonnet 5.5 (19 core conditions each). Main table: `results/table1.md`. Figure: `results/fig_outcomes.png`. Paired statistics: `results/stats.md`. Repeat check: `results/repeat.md`.

1. A valid signature or a verified publisher made no measurable difference on any model.
2. Telling the agent that one owner is behind all five outlets did matter, and models differed: two kept the planted answer, two mostly abstained, one moved to the answer with more independent origins behind it.
3. An instruction to count origins removed most planted answers but made some models abstain when the sources really were independent.
4. Merging by owner in the harness worked best. With one owner, four of the five models dropped the planted answer almost completely. With five real owners, all five kept it.
5. Asked twice, the same model gave the same outcome in 88% (Haiku 5.5) and 93% (gpt-5.4-mini) of question and condition pairs.

H1 held. H2 was not supported. H3 and H4 held for some models only.

## Work done before the sprint

No code was written before the sprint. Before 13 November I did a literature search and wrote a project plan for a related idea (a score for independent origins). The plan changed on 13 November after a second search showed that idea was already published. Everything in this repo was written during the sprint.

## Closed lab

All outlets, people and claims are fictional. Nothing was published to the web. The repo does not include tooling to run real outlets.

## Report

`paper/build_report.py` builds the PDF report from `results/runs.jsonl`. AI tools supported the literature search, coding and drafting. The report's LLM Usage Statement gives the details.

## Sprint log

- 13 November: design, claim set, article writer, agent harness, analysis scripts, first runs on five models, first table and figure.
- 14 November: five against two condition and harness merge on all five models, repeat runs, report draft.
