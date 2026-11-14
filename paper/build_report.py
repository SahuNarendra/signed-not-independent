"""Build the report PDF in the layout of the official Apart template:
title (footnote: research conducted at the sprint), author and affiliation, With Apart Research, Abstract,
1 Introduction, 2 Related Work, 3 Methods, 4 Results, 5 Discussion and Limitations, 6 Conclusion, Code and Data,
Author Contributions, References, Appendix, LLM Usage Statement.
Usage: python paper/build_report.py [output.pdf]     (needs reportlab; reads results/runs.jsonl and results/fig_outcomes.png)
Tables 2 and A2 are computed from results/runs.jsonl, so they fill in as more models are run."""
import json, os, sys
from collections import Counter, defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OSF = os.path.join(HERE, "fonts") + os.sep
pdfmetrics.registerFont(TTFont("Serif", OSF + "OldStandard-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", OSF + "OldStandard-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", OSF + "OldStandard-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BoldItalic", OSF + "OldStandard-Bold.ttf"))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold", italic="Serif-Italic", boldItalic="Serif-BoldItalic")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "signed-not-independent-report-draft.pdf")

S = dict(
    title=ParagraphStyle("t", fontName="Serif-Bold", fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=10),
    author=ParagraphStyle("a", fontName="Serif", fontSize=11, leading=14, alignment=TA_CENTER),
    withapart=ParagraphStyle("w", fontName="Serif-Bold", fontSize=11, leading=14, alignment=TA_CENTER, spaceBefore=6, spaceAfter=14),
    h1=ParagraphStyle("h1", fontName="Serif-Bold", fontSize=14, leading=17, spaceBefore=12, spaceAfter=5, keepWithNext=1),
    h2=ParagraphStyle("h2", fontName="Serif-Bold", fontSize=13, leading=16, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    body=ParagraphStyle("b", fontName="Serif", fontSize=11, leading=13.2, alignment=TA_JUSTIFY, spaceAfter=5),
    bullet=ParagraphStyle("bl", fontName="Serif", fontSize=11, leading=13.2, leftIndent=18, firstLineIndent=-12, spaceAfter=3),
    note=ParagraphStyle("n", fontName="Serif", fontSize=10, leading=12, alignment=TA_LEFT, spaceAfter=4),
    cap=ParagraphStyle("c", fontName="Serif", fontSize=10, leading=12, alignment=TA_JUSTIFY, spaceBefore=3, spaceAfter=8),
    ref=ParagraphStyle("r", fontName="Serif", fontSize=10, leading=12, leftIndent=14, firstLineIndent=-14, spaceAfter=2),
    cell=ParagraphStyle("cell", fontName="Serif", fontSize=9, leading=11),
    cellb=ParagraphStyle("cellb", fontName="Serif-Bold", fontSize=9, leading=11),
)


def P(t, st="body"):
    return Paragraph(t, S[st])


def figure(path, caption, width=6.5):
    img = Image(path)
    r = img.imageHeight / img.imageWidth
    img.drawWidth = width * inch
    img.drawHeight = width * r * inch
    return [img, P(caption, "cap")]


def table(rows, caption, colw=None, bold_first_col=False):
    data = [[Paragraph(str(c), S["cellb"] if (i == 0 or (bold_first_col and j == 0)) else S["cell"]) for j, c in enumerate(row)]
            for i, row in enumerate(rows)]
    t = Table(data, colWidths=colw, hAlign="LEFT")
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black), ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                           ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return KeepTogether([P(caption, "cap"), t, Spacer(1, 8)])


# ---------- numbers read from the results file ----------
rows = [r for r in (json.loads(l) for l in open(os.path.join(ROOT, "results", "runs.jsonl"), encoding="utf-8")) if r.get("rep", 1) == 1]
idx = defaultdict(list)
for r in rows:
    idx[(r["model"], r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False),
         r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))].append(r)
ORDER = [("gpt-5.4-mini", "GPT-5.4 mini"), ("gpt-5.4-2", "GPT-5.4"), ("gpt-5.5", "GPT-5.5"), ("haiku", "Haiku 5.5"), ("sonnet", "Sonnet 5.5")]
MODELS = [(next(m for m in {r["model"] for r in rows} if k in m), name) for k, name in ORDER if any(k in r["model"] for r in rows)]


def cellstr(model, opp, level, structure, tool, policy, toolv, collapse=False, conf=False):
    g = idx.get((model, opp, level, structure, tool, policy, toolv, 0, collapse), [])
    if not g:
        return "not run"
    c = Counter(r["outcome"] for r in g)
    s = f"{c['planted']} / {c['undetermined'] + c['other']} / {c['trusted']}"
    if conf:
        v = [r["confidence"] for r in g if isinstance(r["confidence"], (int, float))]
        s += f" ({sum(v) / len(v):.0f})"
    return s


def results_rows(conds, conf=False):
    out = [["Against", "What the agent is given"] + [n for _, n in MODELS]]
    for opp_label, label, key in conds:
        out.append([opp_label, label] + [cellstr(m, *key, conf=conf) for m, _ in MODELS])
    return out


T1 = [("1 outlet", "No provenance", ("trusted", "none", "na", False, False, 0)),
      ("1 outlet", "Signed", ("trusted", "signature", "na", False, False, 0)),
      ("1 outlet", "Verified publisher", ("trusted", "org", "na", False, False, 0)),
      ("1 outlet", "Tool: one owner", ("trusted", "controller", "collusion", True, False, 2)),
      ("1 outlet", "Tool: one owner + instruction", ("trusted", "controller", "collusion", True, True, 2)),
      ("1 outlet", "Tool: five owners + instruction", ("trusted", "controller", "independent", True, True, 2)),
      ("2 outlets", "No provenance", ("two", "none", "na", False, False, 0)),
      ("2 outlets", "Tool: one owner", ("two", "controller", "collusion", True, False, 2)),
      ("2 outlets", "Tool: one owner + instruction", ("two", "controller", "collusion", True, True, 2)),
      ("2 outlets", "Tool: five owners + instruction", ("two", "controller", "independent", True, True, 2))]
T2 = [("1 outlet", "Harness merge, one owner (agent sees 1 v 1)", ("trusted", "controller", "collusion", False, False, 0, True)),
      ("1 outlet", "Harness merge, five owners (5 v 1)", ("trusted", "controller", "independent", False, False, 0, True)),
      ("2 outlets", "Harness merge, one owner (1 v 2)", ("two", "controller", "collusion", False, False, 0, True)),
      ("2 outlets", "Harness merge, five owners (5 v 2)", ("two", "controller", "independent", False, False, 0, True))]
TA = [("1 outlet", "Tool: unknown + instruction", ("trusted", "org", "na", True, True, 2)),
      ("2 outlets", "Tool: unknown + instruction", ("two", "org", "na", True, True, 2)),
      ("none", "No provenance", ("silence", "none", "na", False, False, 0)),
      ("none", "Tool: one owner + instruction", ("silence", "controller", "collusion", True, True, 2))]
W = [0.7 * inch, 1.9 * inch] + [3.9 * inch / max(1, len(MODELS))] * len(MODELS)

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=1 * inch, rightMargin=1 * inch, topMargin=1 * inch, bottomMargin=1 * inch,
                        title="Signed is not independent", author="Narendra Sahu")
st = []
st.append(P("Signed is not independent: what research agents do with provenance when one operator runs the majority<super>1</super>", "title"))
st.append(P("Narendra Sahu<br/>Independent security researcher", "author"))
st.append(P("With<br/>Apart Research", "withapart"))
st.append(P("<super>1</super> Research conducted at the AI x Epistemics Research Sprint, November 2026.", "note"))

st.append(P("Abstract", "h1"))
st.append(P("When five outlets agree, does it matter to a research agent that one operator runs all five? An operator can run several outlets that agree without sharing any text, which defeats copy detection. Provenance standards show that an article is authentic and who published it, not whether two publishers share an owner. In a closed lab, five fictional outlets each wrote their own article supporting a planted answer to 40 invented questions, and one or two other outlets disagreed. Five models from two vendors answered. A valid signature or a verified publisher made no measurable difference on any model: the planted answer was given in 34 to 40 of 40 cases with or without them. Ownership information did matter, but its use depended on the model. When a tool reported one owner behind the five outlets against two independent outlets, one model moved to the better-supported answer in 38 of 40 cases, two mostly abstained, and two kept the planted answer in 34 and 35 of 40 while stating that the five outlets were one origin. An instruction to count origins removed most planted answers but made two models abstain on 12 to 34 of 40 cases where the sources really were independent. Merging sources by owner in the harness gave the better-supported answer in 22 to 39 of 40 cases across the five models, with no loss on independent sources. Provenance needs an ownership layer, and the origin count belongs in the harness."))

st.append(P("1. Introduction", "h1"))
st.append(P("Counting how many sources agree only works if the sources are independent. Running many outlets is now cheap for one operator. In September 2026 Anthropic reported about 70 news sites that looked unrelated and were tied to one operator account through shared infrastructure (Anthropic 2026). Research agents read such sites and report what most of them say."))
st.append(P("Recent work shows that agents and LLM judges count copies and paraphrases of one report as confirmation, and proposes detectors based on shared text (Zhou et al. 2026; Metales et al. 2026; Gao et al. 2026). An operator who has each outlet write its own article shares no text. Metales et al. name this case, collusion without copying, as the open problem, and Bara (2026) shows that an aggregator which sees only the reports cannot tell replication from corroboration."))
st.append(P("Provenance is the usual answer. A C2PA manifest shows that content is intact and which tool signed it. A CAWG identity assertion adds a verified publisher. Neither says who controls the publisher, so two verified publishers can have one owner. We call this the <b>independence gap</b>: a provenance record proves authenticity and identity, and corroboration needs independence. We ask what agents do with each kind of information."))
st.append(P("<b>Threat model.</b> The adversary is one operator with several outlets. Each outlet writes its own article from the bare claim, in its own voice, with its own invented details. The operator can sign every article and can obtain a verified publisher identity for every outlet. The defender is a research agent, or the harness around it, that sees the retrieved articles and whatever provenance comes with them."))
st.append(P("<b>Contributions.</b>"))
st.append(P("1. <b>A test without shared text.</b> A closed-lab test of how agents use provenance at three levels (signature, verified publisher, controlling owner) when one operator is behind an agreeing majority that never shares text.", "bullet"))
st.append(P("2. <b>Today's provenance does not help.</b> On five models, the two levels that standards carry today did not change what the agent concluded.", "bullet"))
st.append(P("3. <b>Ownership helps, unevenly.</b> The missing level, common control, changed conclusions, with three behaviours across models: ignore, abstain, or re-weigh.", "bullet"))
st.append(P("4. <b>A fix and its cost.</b> A prompt instruction to count origins works but causes over-caution on independent sources; merging by owner in the harness does not.", "bullet"))
st.extend(figure(os.path.join(ROOT, "results", "fig_outcomes.png"), "Figure 1. Main results. Five outlets back the planted answer; each bar is one model's answers to 40 questions. Top block: one outlet disagrees. Bottom block: two independent outlets disagree, so with one owner behind the five the other side has more independent origins. Signed and verified-publisher rows look like the no-provenance row on every model.", 6.5))
st.append(table([["Term", "Meaning in this paper"],
                 ["Origin", "one controlling owner, however many outlets it runs"],
                 ["Planted answer", "the answer the five supporting outlets report"],
                 ["Other side", "the answer the dissenting outlet or outlets report"],
                 ["One owner / five owners", "who controls the five supporting outlets; the article text is the same in both cases"],
                 ["Origin tool", "tool output listing which numbered sources belong to each owner, or saying ownership is unknown"],
                 ["Instruction", "a line in the system prompt: count origins, not documents; \"undetermined\" is allowed"],
                 ["Harness merge", "the harness keeps one document per owner before the model reads anything"],
                 ["Over-caution", "answering \"undetermined\" when the five supporting outlets really are independent"]],
                "Terms used throughout.", colw=[1.6 * inch, 4.9 * inch], bold_first_col=True))

st.append(P("2. Related Work", "h1"))
st.append(P("<b>Copies counted as confirmation.</b> Evidence Laundering (Zhou et al. 2026) shows deep research agents credit a paraphrased cluster like independent sources, and proposes a content-based gate that collapses near-copies; the gate rarely collapses pages written independently. Copies Are Not Confirmations (Metales et al. 2026) measures the same for LLM judges on news, with an entity-novelty detector, and lists ownership, timing and shared errors as signals for future work. Gao et al. (2026) measure how much weight LLM aggregators give a restated observation. SearchGEO (Chen et al. 2026) includes a synthetic-consensus attack on search agents, and Lu and Zhang (2026) poison a news corpus read by LLM forecasters. All of these need shared text, or measure the attack without a provenance variable."))
st.append(P("<b>Dependence and provenance.</b> Bara (2026) formalises why report-only aggregation cannot recover dependence and argues for tracking ancestry; source dependence is an old idea in data fusion (Dong et al. 2009). Operators behind site networks have been found through shared infrastructure, not text (Bengani 2019; Anthropic 2026). C2PA 2.4 and the CAWG identity assertion are the current standards, and for people, C2PA labels raise trust in a news source (Trattner et al. 2026). The Forethought design sketches (Cotton-Barratt et al. 2025) describe provenance tracing and reliability tracking, and the sprint brief asks whether a provenance tool changes agent behaviour."))
st.append(P("<b>What is new here.</b> The outlets never share text, so content detectors do not apply. The variable is what the agent is told about provenance and ownership, and the outcome is the agent's conclusion. A related Apart project studies redundancy between personas inside one model (Gallego and Habana 2026); ours is between sources."))

st.append(P("3. Methods", "h1"))
st.append(P("<b>3.1 Claims and outlets.</b> 40 invented questions about fictional people, places and companies, each with a planted answer and a different answer for the other side. No model can know either. Five supporting outlets have different voices (regional daily, business newsletter, long-form weekly, trade blog, wire bulletin). Each article is written from the bare claim by GPT-5.4 mini, 97 to 135 words, with its own invented details; mean pairwise 3-gram overlap is 0.02 (maximum 0.09), so there is nothing for a copy detector to find. One or two further outlets report the other side."))
st.append(P("<b>3.2 Conditions.</b> Four factors. Who is behind the five: one owner or five separate owners (the article text is identical). What the agent is given: nothing; a valid signature per article; a verified publisher per article; the controlling owner per article; or the origin tool. Opposition: none, one outlet, or two independent outlets. Prompt: neutral, or neutral plus the instruction. The provenance text is simulated and follows the real layers (C2PA manifest, CAWG identity) plus an ownership attestation that current standards do not have. Both origin-tool outputs, known and unknown, end with the same sentence. With one owner and two dissenting outlets it is one origin against two, so the other side has more independent origins."))
st.append(P("<b>3.3 Harness merge.</b> The harness keeps the first-listed document of each attested owner and adds one line saying how many documents were merged. Neutral prompt, no tool, no instruction."))
st.append(P("<b>3.4 Agents and scoring.</b> GPT-5.4 mini on all 49 conditions; GPT-5.4, GPT-5.5, Claude Haiku 5.5 and Claude Sonnet 5.5 on the core conditions. One call per question per condition, source order fixed per question. The agent returns an answer, a confidence from 0 to 100, and the number of independent sources it believes support the answer. An answer is scored planted, other side, or undetermined (including answers that name both sides or say the sources conflict). Intervals are Wilson 95% for counts and a paired bootstrap over questions for confidence."))
st.append(P("<b>3.5 Checks.</b> Repeat: the core conditions were asked a second time on Haiku 5.5 (600 pairs, same outcome in 88.2%) and on GPT-5.4 mini (760 pairs, 93.2%). Position: the plain contradicted condition was run with three source orders. Hypotheses were written in the repository README before the first run; Table A1 gives their status."))
st.append(P("<b>3.6 Reproducibility.</b> Every model call is cached in the repository, so every table and figure can be regenerated without an API key. Tables 1, 2 and A2 in this PDF are computed from the results file when the PDF is built."))

st.append(P("4. Results", "h1"))
st.append(table(results_rows(T1), "Table 1. Planted / undetermined / other side, out of 40 questions. Five outlets back the planted answer. \"1 outlet\" and \"2 outlets\" are the dissenting outlets.", colw=W))
st.append(P("<b>4.1 Signatures and verified identity change nothing (Table 1, Table A3).</b> With one outlet disagreeing, every model gave the planted answer in 34 to 40 of 40 questions whether the articles carried no provenance, a valid signature, or a verified publisher. The paired change in confidence is within 2 points on every model and every interval includes zero. The hypothesis that a signature raises trust was not supported either."))
st.append(P("<b>4.2 Without ownership information every model follows the five outlets,</b> also against two independent outlets (34 to 40 of 40)."))
st.append(P("<b>4.3 Ownership information: ignore, abstain, or re-weigh.</b> With the origin tool reporting one owner and two outlets disagreeing, GPT-5.4 mini and GPT-5.4 kept the planted answer in 35 and 34 of 40 questions. Haiku 5.5 answered undetermined in 34 and Sonnet 5.5 in 15, with 21 planted. GPT-5.5 gave the other side's answer in 38. Showing the owner as a provenance line, with no tool, lowered confidence by 4 to 29 points on four models and by nothing on GPT-5.4 mini (Table A3)."))
st.append(P("<b>4.4 They state the count and follow the documents.</b> When a model kept the planted answer after the tool reported one owner, it usually said that one independent source supported it: 36 of 36 answers for GPT-5.4, 28 of 28 for GPT-5.5, 25 of 26 for Haiku 5.5. In the two-outlet case its reasoning named the single owner in 33 of 34 answers for GPT-5.4 and 21 of 21 for Sonnet 5.5, against 17 of 35 for GPT-5.4 mini. One Sonnet 5.5 answer says the five outlets \"count as one independent origin\" and continues: \"I chose Marrenkamp because far more documents support her\". Confidence at an origin tie, which warrants about 50, averaged 98 for GPT-5.4 mini and 83 for GPT-5.4, against 63 for GPT-5.5 and 57 for Haiku 5.5."))
st.append(P("<b>4.5 The instruction works on four models and has a cost.</b> With the instruction, four of five models stop giving the planted answer in one-owner cases (0 to 6 of 40); GPT-5.4 mini still gives it in 32 and 22. Only GPT-5.5 re-weighs (37 of 40 other side); the others abstain. With five separate owners the instruction makes GPT-5.4 answer undetermined in 17 of 40 questions against one dissenting outlet and 34 against two, and Haiku 5.5 in 12 and 31. Sonnet 5.5 (3 and 6) and GPT-5.5 (0 and 1) are barely affected."))
st.append(table(results_rows(T2, conf=True), "Table 2. Harness merge: planted / undetermined / other side (mean confidence). Neutral prompt, no tool, no instruction.", colw=W))
st.append(P("<b>4.6 Merging by owner in the harness gives re-weighing without over-caution (Table 2).</b> With one owner against two outlets, the merge gives the other side's answer in 34 of 40 questions on GPT-5.4, 26 on Haiku 5.5, 27 on Sonnet 5.5 and 39 on GPT-5.5. Given the same information as tool output, the first three chose the other side in 3, 2 and 4. With five separate owners nothing is merged and every model stays with the five outlets (32 to 40 of 40), where the instruction had cost GPT-5.4 and Haiku 5.5 up to 34 and 31 answers. GPT-5.4 mini is only partly fixed: it moves to the other side in 22 questions and keeps the planted answer in 17, and when the merge leaves one origin against one it still picks the planted answer in 28 at a mean confidence of 91, where the other models answer undetermined in 32 to 39."))
st.append(P("<b>4.7 Other checks.</b> Marking ownership unknown, with the instruction, produces abstention on most models whether or not the sources are independent (Table A2). The position of the dissenting outlet had no meaningful effect (2 of 29 first-position runs on GPT-5.4 mini, 0 of 10 on GPT-5.4). In the two-outlet tool condition, 39 of the 40 questions had at least one model leave the planted answer, so the effect is not carried by a few questions."))

st.append(P("5. Discussion and Limitations", "h1"))
st.append(P("<b>For provenance standards.</b> The two things a manifest can attest today did not help any model. The thing it cannot attest, common control, helped every model that used it. A common-control assertion backed by an ownership register is the missing layer. It is only as good as the register: an operator with five shell owners makes the tool report five owners, which is the five-owners row of Table 1."))
st.append(P("<b>For agent builders.</b> Giving an agent the signal is not the same as the agent using it. Four of five models did not re-weigh by origin when told who owned what, and two of them said the right count and still followed the documents. A prompt instruction buys abstention and costs decisiveness on honest independent reporting. Doing the merge in the harness moved four of five models to the better-supported answer and kept decisiveness on independent sources on all five; the smallest model still did not express doubt at a tie."))
st.append(P("<b>For evaluation.</b> Three numbers should be reported together: acceptance of the planted claim, re-weighing to the better-supported answer, and over-caution on independent sources. A defence that only produces doubt scores well on the first and fails the third."))
st.append(P("Limitations (ethics in Appendix A)", "h2"))
st.append(P("Five models from two vendors, one sample per cell, with a repeat check on two of the five. Four models ran the 19 core conditions only. The outlets are fictional and have no reputation, so the test says nothing about a trusted outlet outweighing unknown ones. Provenance output is simulated text, not real signed manifests. Independence is by our labels, and both answers are invented, so \"better supported\" means supported by more independent origins, not true. The agents read a fixed set of retrieved documents; full research products with live search were not tested. The harness merge assumes a truthful ownership register. Claude was used to help build the experiment and two Claude models are among the agents tested."))
st.append(P("Future Work", "h2"))
st.append(P("Real ownership data (company registers, ads.txt) in place of attested labels; real signed manifests; full research agents with live search; the harness merge on more models and under shell-owner attacks."))

st.append(P("6. Conclusion", "h1"))
st.append(P("A signature shows that an article is authentic and a verified identity shows who published it. Neither tells a research agent whether five agreeing outlets are five sources or one, and on five models neither changed the answer. Ownership information did, but most models needed the counting done for them. The practical steps are an ownership layer in provenance and an origin merge in the agent harness."))

st.append(P("Code and Data", "h1"))
st.append(P("<b>Code repository:</b> https://github.com/SahuNarendra/signed-not-independent. All claims, articles, prompts, cached model answers and analysis scripts are included."))
st.append(P("<b>Data:</b> all data are generated in the sprint and fictional. No external dataset is used."))
st.append(P("<b>Prior work.</b> No code was written before the sprint. Before 13 November the author did a literature search and wrote a plan for a related idea (a score for independent origins). That plan was dropped on 13 November after a second search showed it was already published. Everything in the repository was produced from 13 November 2026."))

st.append(P("Author Contributions", "h1"))
st.append(P("Narendra Sahu: sole author."))

st.append(P("References", "h1"))
for ref in [
    "Anthropic (2026). Detecting and countering misuse of AI: September 2026. https://www.anthropic.com/threat-intelligence-report-september-2026",
    "Bara, M. (2026). Epistemic Sybil Resistance: Multiplying AI Agents Without Multiplying Evidence. arXiv:2609.01873",
    "Bengani, P. (2019). Hundreds of \"pink slime\" local news outlets are distributing algorithmic stories and conservative talking points. Tow Center, Columbia Journalism Review.",
    "C2PA (2025). C2PA Technical Specification 2.4. https://spec.c2pa.org/",
    "Chen, Y. et al. (2026). How Much Can We Trust LLM Search Agents? Measuring Endorsement Vulnerability to Web Content Manipulation. EMNLP 2026. arXiv:2606.16821",
    "Cotton-Barratt, O., Vaintrob, L., Sourbut, O. (2025). Design Sketches: Collective Epistemics. Forethought.",
    "Creator Assertions Working Group (2026). CAWG Identity Assertion. https://cawg.io/",
    "Dong, X. L., Berti-Equille, L., Srivastava, D. (2009). Integrating Conflicting Data: The Role of Source Dependence. Proceedings of the VLDB Endowment 2(1), 550-561.",
    "Gallego, S., Habana, A. (2026). False Epistemic Redundancy: Do AI Ensembles Share a Blind Spot? Apart Research, Digital Minds Research Sprint.",
    "Gao, J. et al. (2026). Copies or Sources? Measuring How LLM Aggregators Count Restated Evidence in Multi-Agent Systems. arXiv:2610.06192",
    "Lu, Y., Zhang, Y. (2026). The Corroboration Illusion: When More News Makes LLM Forecasts Less True. arXiv:2609.22246",
    "Metales, A., Grabenheinrich, M., Metales, A. (2026). Copies Are Not Confirmations: How News Duplication Fools LLM Judges and Continual Learners. arXiv:2611.09203",
    "Navaie, K. (2026). Epistemic norms for AI safety and alignment research. Artificial Intelligence Review. doi:10.1007/s10462-026-11666-8",
    "Trattner, C., Forstner, S. L., Starke, A. D., Knudsen, E. (2026). C2PA Provenance Labels Increase Trust in Digital News Platforms Across Western Countries. ICWSM 2026. doi:10.1609/icwsm.v20i1.42749",
    "Zhou, R. et al. (2026). Evidence Laundering: Deep Research Agents Mistake Correlated Sources for Independent Evidence. EMNLP 2026. https://aclanthology.org/2026.emnlp-main.509/",
]:
    st.append(P(ref, "ref"))

st.append(P("Appendix A. Limitations and Dual-Use / Ethical Considerations", "h1"))
st.append(P("<b>What the result establishes.</b> In a closed lab with fictional outlets, on five models from two vendors, provenance and ownership information had the effects in Tables 1 and 2. <b>What it does not establish.</b> The behaviour of other models or of research products with live search; behaviour when outlets have a real reputation; that any real outlet is or is not independent."))
st.append(P("<b>Dual use.</b> Showing that agreeing outlets written from scratch pass as independent could inform an influence operation. This is already documented in the wild and in the papers cited. The repository contains the lab harness only and no tooling to run outlets. All outlets, people and claims are fictional and nothing was published to the web."))
st.append(P("<b>Conflict to disclose.</b> Claude (Anthropic) was used to help build the experiment and draft this report, and two Claude models are among the agents tested. All numbers come from scripts and cached answers in the repository. <b>Personal data.</b> None."))

st.append(P("Appendix B. Supplementary results", "h1"))
st.append(table([["Claim", "Evidence", "Status"],
                 ["H1. A valid signature does not reduce acceptance of the planted answer", "4.1", "confirmed on five models"],
                 ["H2. A signature or verified publisher raises acceptance", "4.1, Table A3", "not supported; every interval includes zero"],
                 ["H3. Showing the controlling owner reduces acceptance under one owner", "4.3, Table A3", "confirmed on four models, not on GPT-5.4 mini"],
                 ["H4. The origin tool reduces acceptance further", "4.3 to 4.5", "model dependent: re-weigh (1), abstain (2), ignore (2)"],
                 ["Models that keep the planted answer do not register the single owner", "4.4", "refuted for GPT-5.4, GPT-5.5, Haiku 5.5, Sonnet 5.5"],
                 ["An instruction to count origins has no cost", "4.5", "refuted on GPT-5.4 and Haiku 5.5"],
                 ["A harness merge gives re-weighing without over-caution", "4.6", "confirmed on four models; partly on GPT-5.4 mini"],
                 ["Results are stable on a second ask", "3.5", "same outcome in 88 to 92% of pairs"]],
                "Table A1. Claim status.", colw=[3.3 * inch, 1.0 * inch, 2.2 * inch]))
st.append(table(results_rows(TA, conf=True), "Table A2. Further conditions: planted / undetermined / other side (mean confidence).", colw=W))
st.append(table([["Model", "Signature", "Verified publisher", "Owner shown, one owner"],
                 ["GPT-5.4 mini", "+1.6 [-0.2, +4.0]", "+1.6 [-0.8, +4.3]", "+1.4 [-0.7, +4.0]"],
                 ["GPT-5.4", "+0.5 [-1.2, +2.2]", "-1.3 [-2.6, +0.1]", "-4.2 [-7.0, -1.7]"],
                 ["GPT-5.5", "0.0 [-0.8, +0.8]", "-0.1 [-0.8, +0.6]", "-25.9 [-29.4, -22.9]"],
                 ["Haiku 5.5", "0.0 [-2.7, +2.5]", "-0.1 [-2.1, +1.8]", "-12.9 [-16.6, -9.4]"],
                 ["Sonnet 5.5", "+1.2 [-1.1, +3.3]", "+1.0 [-1.0, +3.0]", "-28.6 [-30.9, -26.2]"]],
                "Table A3. Change in mean confidence against no provenance, one outlet disagreeing, paired by question. Brackets: 95% bootstrap interval.",
                colw=[1.4 * inch, 1.7 * inch, 1.7 * inch, 1.7 * inch], bold_first_col=True))
st.append(P("<b>Models.</b> gpt-5.4-mini-2026-03-17, gpt-5.4-2026-03-05, gpt-5.5-2026-04-23 (OpenAI API); claude-haiku-5-5, claude-sonnet-5-5 (Anthropic API, OpenAI-compatible endpoint). Articles were written by gpt-5.4-mini-2026-03-17."))

st.append(KeepTogether([P("LLM Usage Statement", "h1"), P("Claude (Anthropic) was used as a research tool: to locate and summarise related work, to help write and debug the experiment and analysis scripts, and to assist with drafting, editing and checking the consistency of the report. OpenAI and Anthropic models were the systems under test, and an OpenAI model wrote the fictional articles. All reported numbers are produced by scripts in the repository.")]))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Serif", 10)
    canvas.drawCentredString(letter[0] / 2, 0.6 * inch, str(doc.page))
    canvas.restoreState()


doc.build(st, onFirstPage=footer, onLaterPages=footer)
print("saved", OUT)
