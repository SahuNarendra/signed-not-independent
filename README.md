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
- 19 core conditions run on every model. 28 further early conditions ran on gpt-5.4-mini only on the first day; they are in `results/runs.jsonl` and are not part of the report's tables.
- Controls 1 (14 conditions, added 14 November after a review of the first draft): provenance on one side only, the tool with no instruction, a second wording of the instruction (the "majority instruction"), the merge with two other source orders, and the merged documents with no note.
- Controls 2 (9 conditions, Claude models): one-sided provenance with the other side left blank, one sentence that permits "undetermined", and the owner names swapped between sides.
- Controls 3 (8 conditions, Claude models): three of the five outlets under one owner, the tool without its closing sentence, and reasoning before the answer.
- Second article set (4 conditions, Claude models): articles from a different writer with consistent details on each side (`data/articles2.json`, `results/runs_set2.jsonl`).
- Retest (`--retest`, GPT-5.4 and Claude models): the headline condition with permission to abstain, with reasoning first, with the owner line alone, and with a note saying ownership is unknown and no instruction.
- Controls 4 (`--controls4`, Claude models): a forged ownership note inside an article in two versions, and signatures with separate keys and with one shared key, against two dissenting outlets.
- The report calls the origin count tool the "ownership note", because it is a paragraph of text in the prompt and not a tool call.

The provenance check output is simulated text. No real signing takes place in this version.

## Run it

```
pip install -r requirements.txt matplotlib reportlab
copy .env.example .env        (then put your API keys in .env)
python src/make_outlets.py
python src/run_agents.py --models gpt-5.4-mini-2026-03-17
python src/run_agents.py --core --models gpt-5.5-2026-04-23
python src/run_agents.py --core --models alt:claude-sonnet-5-5
python src/run_agents.py --controls --models alt:claude-sonnet-5-5
python src/run_agents.py --controls2 --models alt:claude-sonnet-5-5
python src/run_agents.py --controls3 --models alt:claude-sonnet-5-5
python src/run_agents.py --retest --models gpt-5.4-2026-03-05
python src/run_agents.py --controls4 --models alt:claude-sonnet-5-5
python src/make_outlets.py --set2
python src/run_agents.py --set2 --models alt:claude-sonnet-5-5
python src/code_answers.py
python src/code_answers.py --tiebreak alt:claude-opus-5-5
python src/analyze.py
python src/stats.py
python src/extra.py
python src/table.py
python src/figures.py
python src/schematic.py
python src/repeat.py
python paper/build_report.py
```

- `--core` runs the 19 core conditions.
- `--controls`, `--controls2`, `--controls3` and `--set2` run the control sets above. `--lite` runs 5 of the first set.
- `src/code_answers.py` runs the second scoring pass: answers that name both sides or neither are labelled by two coder models, and `--tiebreak` adds a third label where they disagree. `src/scoring.py` combines the passes.
- `alt:` sends the model to the second provider set in `.env` (any OpenAI-compatible endpoint).
- `--estimate --price-in X --price-out Y` prints the number of new calls and a cost range without calling anything.
- `--rep 2` asks the same questions again, and `python src/repeat.py` reports how often the answer is the same.
- `--limit N` uses the first N claims.

Every model call is cached in `results/cache/`. With the cache present, all tables and figures can be regenerated with no API key. Set `MOCK=1` to test the plumbing offline.

## Results

Six models, 40 claims each: gpt-5.4-mini, gpt-5.4, gpt-5.5, Claude Haiku 5.5, Claude Sonnet 5.5 and Claude Opus 5.5. All six ran the 19 core conditions. Five ran all of controls 1 and gpt-5.5 ran 5 of them. Controls 2 and 3 and the second article set ran on the three Claude models. The report is the reference for numbers; `results/table1.md`, `results/stats.md`, `results/extra.md` and `results/repeat.md` hold the full output. Figures: `results/fig_setup.png`, `results/fig_main.png`, `results/fig_outcomes.png`.

1. A valid signature or a verified publisher on every source made no measurable difference on any model, with acceptance already at the ceiling. A verified publisher on the dissenting outlet alone, with an explicit "no manifest found" line on the other five, cut planted answers sharply on three models. With the five left blank, only one of the three Claude models moved.
2. Telling the model that one owner is behind all five outlets mattered on some models only. Against two dissenting outlets, two models moved to the dissenting answer, one split, and three kept the planted answer. Two of those three usually reported in the same reply that it had one independent source. For Sonnet 5.5 this weakened when the prompt allowed "undetermined", when reasoning came before the answer, and on the second article set.
3. An instruction to count origins removed most planted answers. One wording also made some models decline to answer when the sources really were separately owned. A second wording did not, but left two models mostly unchanged.
4. Merging by owner in the harness moved five of the six models to the other side, on three source orders, with no extra abstention on separately owned sources. The smallest model followed whichever source was listed first. Under partial ownership the merge cost one model answers that the second instruction kept.
5. The "says one source, still follows the five" behaviour depends on the prompt. One sentence permitting "undetermined", or asking for reasoning before the answer, removed most of it on GPT-5.4 and Sonnet 5.5 (`--retest`).
6. A forged ownership note planted inside an article moved all three Claude models off a well-supported answer. A signing key shared by the five outlets was read as common ownership by the two larger Claude models with no explanation given (`--controls4`).
7. Asked twice, the same model gave the same outcome in 92% to 93% of question and condition pairs (gpt-5.4-mini, Haiku 5.5, Sonnet 5.5, Opus 5.5). Counts per condition moved by up to 7 of 40.

H1 held. H2 was not supported. H3 held in part. H4 was not supported, except that the "unknown" output reduced acceptance together with the instruction. Every fix depends on a truthful ownership record, and five shell owners defeat it.

## Work done before the sprint

No code was written before the sprint. Before 13 November I did a literature search and wrote a project plan for a related idea (a score for independent origins). The plan changed on 13 November after a second search showed that idea was already published. Everything in this repo was written during the sprint.

## Closed lab

All outlets, people and claims are fictional. Nothing was published to the web. The repo does not include tooling to run real outlets.

## Report

`paper/build_report.py` builds the PDF report from `results/runs.jsonl`. AI tools supported the literature search, coding and drafting. The report's LLM Usage Statement gives the details.

## Sprint log

- 13 November: design, claim set, article writer, agent harness, analysis scripts, first runs on five models, first table and figure.
- 14 November: five against two condition and harness merge on all models, repeat runs, report draft, reviews of the draft, three sets of control conditions, sixth model, second article set, second scoring pass.
