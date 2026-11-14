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
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
    return KeepTogether([P(caption, "cap"), t, Spacer(1, 8)])


# ---------- numbers read from the results file ----------
sys.path.insert(0, os.path.join(ROOT, "src"))
import scoring
ALLROWS = scoring.load_mapped()
rows = [r for r in ALLROWS if r["rep"] == 1]
idx = defaultdict(list)
for r in rows:
    idx[(r["model"], r["opposition"], r["level"], r["structure"], r["tool"], r.get("policy", False),
         r.get("toolv", 1 if r["tool"] else 0), r.get("seed", 0), r.get("collapse", False))].append(r)
ORDER = [("gpt-5.4-mini", "GPT-5.4<br/>mini"), ("gpt-5.4-2", "GPT-5.4"), ("gpt-5.5", "GPT-5.5"), ("haiku", "Haiku<br/>5.5"), ("sonnet", "Sonnet<br/>5.5"), ("opus", "Opus<br/>5.5")]
MODELS = [(next(m for m in {r["model"] for r in rows} if k in m), name) for k, name in ORDER if any(k in r["model"] for r in rows)]


def cellstr(model, opp, level, structure, tool, policy, toolv, collapse=False, conf=False):
    g = idx.get((model, opp, level, structure, tool, policy, toolv, 0, collapse), [])
    if not g:
        return "not run"
    c = Counter(r["outcome"] for r in g)
    s = f"{c['planted']}/{c['undetermined'] + c['other']}/{c['trusted']}"
    if conf:
        v = [r["confidence"] for r in g if isinstance(r["confidence"], (int, float))]
        s += f" ({sum(v) / len(v):.0f})"
    return s


def results_rows(conds, conf=False):
    out = [["Against", "What the model is given"] + [n for _, n in MODELS]]
    for opp_label, label, key in conds:
        out.append([opp_label, label] + [cellstr(m, *key, conf=conf) for m, _ in MODELS])
    return out


T1 = [("1 outlet", "No provenance", ("trusted", "none", "na", False, False, 0)),
      ("1 outlet", "Signed", ("trusted", "signature", "na", False, False, 0)),
      ("1 outlet", "Verified publisher", ("trusted", "org", "na", False, False, 0)),
      ("1 outlet", "Owner shown: one owner", ("trusted", "controller", "collusion", False, False, 0)),
      ("1 outlet", "Tool: one owner", ("trusted", "controller", "collusion", True, False, 2)),
      ("1 outlet", "Tool: one owner + instruction", ("trusted", "controller", "collusion", True, True, 2)),
      ("1 outlet", "Tool: five owners + instruction", ("trusted", "controller", "independent", True, True, 2)),
      ("2 outlets", "No provenance", ("two", "none", "na", False, False, 0)),
      ("2 outlets", "Tool: one owner", ("two", "controller", "collusion", True, False, 2)),
      ("2 outlets", "Tool: one owner + instruction", ("two", "controller", "collusion", True, True, 2)),
      ("2 outlets", "Tool: five owners + instruction", ("two", "controller", "independent", True, True, 2))]
T2 = [("1 outlet", "Merge, one owner (model sees 1 v 1)", ("trusted", "controller", "collusion", False, False, 0, True)),
      ("1 outlet", "Merge, five owners (5 v 1)", ("trusted", "controller", "independent", False, False, 0, True)),
      ("2 outlets", "Merge, one owner (1 v 2)", ("two", "controller", "collusion", False, False, 0, True)),
      ("2 outlets", "Merge, five owners (5 v 2)", ("two", "controller", "independent", False, False, 0, True))]
TA = [("1 outlet", "Tool: unknown + instruction", ("trusted", "org", "na", True, True, 2)),
      ("2 outlets", "Tool: unknown + instruction", ("two", "org", "na", True, True, 2)),
      ("none", "No provenance", ("silence", "none", "na", False, False, 0)),
      ("none", "Tool: one owner + instruction", ("silence", "controller", "collusion", True, True, 2))]
# Controls added on 14 November. key = (opposition, level, structure, tool, policy, toolv, collapse, seed)
TC = [("1 outlet", "Five verified, dissenter unsigned", ("trusted", "org_support", "na", False, False, 0, False, 0)),
      ("1 outlet", "Five unsigned, dissenter verified", ("trusted", "org_dissent", "na", False, False, 0, False, 0)),
      ("1 outlet", "Tool: five owners, no instruction", ("trusted", "controller", "independent", True, False, 2, False, 0)),
      ("2 outlets", "Tool: five owners, no instruction", ("two", "controller", "independent", True, False, 2, False, 0)),
      ("1 outlet", "Tool: one owner + instruction B", ("trusted", "controller", "collusion", True, 2, 2, False, 0)),
      ("1 outlet", "Tool: five owners + instruction B", ("trusted", "controller", "independent", True, 2, 2, False, 0)),
      ("2 outlets", "Tool: one owner + instruction B", ("two", "controller", "collusion", True, 2, 2, False, 0)),
      ("2 outlets", "Tool: five owners + instruction B", ("two", "controller", "independent", True, 2, 2, False, 0)),
      ("1 outlet", "Merge, one owner, order 2", ("trusted", "controller", "collusion", False, False, 0, True, 1)),
      ("1 outlet", "Merge, one owner, order 3", ("trusted", "controller", "collusion", False, False, 0, True, 2)),
      ("2 outlets", "Merge, one owner, order 2", ("two", "controller", "collusion", False, False, 0, True, 1)),
      ("2 outlets", "Merge, one owner, order 3", ("two", "controller", "collusion", False, False, 0, True, 2)),
      ("1 outlet", "Same documents as merge, no note, no provenance", ("trusted", "bare", "collusion", False, False, 0, "plain", 0)),
      ("2 outlets", "Same documents as merge, no note, no provenance", ("two", "bare", "collusion", False, False, 0, "plain", 0))]


TC2 = [("1 outlet", "Dissenter verified, five shown \"no manifest found\"", ("trusted", "org_dissent", "na", False, False, 0, False, 0)),
       ("1 outlet", "Dissenter verified, five left blank", ("trusted", "org_dissent_blank", "na", False, False, 0, False, 0)),
       ("1 outlet", "Dissenter signed only, five left blank", ("trusted", "sig_dissent_blank", "na", False, False, 0, False, 0)),
       ("1 outlet", "Five verified, dissenter left blank", ("trusted", "org_support_blank", "na", False, False, 0, False, 0)),
       ("1 outlet", "No provenance + permission to abstain", ("trusted", "none", "na", False, 3, 0, False, 0)),
       ("1 outlet", "Tool: one owner + permission to abstain", ("trusted", "controller", "collusion", True, 3, 2, False, 0)),
       ("2 outlets", "No provenance + permission to abstain", ("two", "none", "na", False, 3, 0, False, 0)),
       ("2 outlets", "Tool: one owner + permission to abstain", ("two", "controller", "collusion", True, 3, 2, False, 0)),
       ("1 outlet", "Owner shown: one owner, names swapped", ("trusted", "controller", "collusion_swap", False, False, 0, False, 0)),
       ("2 outlets", "Tool: one owner, names swapped", ("two", "controller", "collusion_swap", True, False, 2, False, 0))]


def control_rows(conds=None, models=None):
    models = models or MODELS
    out = [["Against", "What the model is given"] + [n for _, n in models]]
    for opp_label, label, (opp, level, structure, tool, policy, toolv, collapse, seed) in (conds or TC):
        line = []
        for m, _ in models:
            g = idx.get((m, opp, level, structure, tool, policy, toolv, seed, collapse), [])
            c = Counter(r["outcome"] for r in g)
            line.append(f"{c['planted']}/{c['undetermined'] + c['other']}/{c['trusted']}" if len(g) == 40 else "not run")
        out.append([opp_label, label] + line)
    return out


def _count(m, key, what):
    g = idx.get((m,) + key, [])
    if len(g) != 40:
        return None
    c = Counter(r["outcome"] for r in g)
    return {"planted": c["planted"], "other": c["trusted"], "und": c["undetermined"] + c["other"]}[what]


def summary_rows():
    """The fixes side by side on three numbers, two dissenting outlets. One value per model, in table order."""
    base = ("two", "none", "na", False, False, 0, 0, False)
    fixes = [("Tool", ("two", "controller", "collusion", True, False, 2, 0, False), ("two", "controller", "independent", True, False, 2, 0, False)),
             ("Tool + instruction", ("two", "controller", "collusion", True, True, 2, 0, False), ("two", "controller", "independent", True, True, 2, 0, False)),
             ("Tool + instruction B", ("two", "controller", "collusion", True, 2, 2, 0, False), ("two", "controller", "independent", True, 2, 2, 0, False)),
             ("Harness merge", ("two", "controller", "collusion", False, False, 0, 0, True), ("two", "controller", "independent", False, False, 0, 0, True))]
    fmt = lambda v: ", ".join("n/r" if x is None else (f"+{x}" if isinstance(x, str) else str(x)) for x in v)
    out = [["Fix", "(1) Planted, one owner (lower is better)", "(2) Other side, one owner (higher is better)", "(3) Added undetermined, five owners (lower is better)"]]
    for name, one, five in fixes:
        pl = [_count(m, one, "planted") for m, _ in MODELS]
        ot = [_count(m, one, "other") for m, _ in MODELS]
        ex = []
        for m, _ in MODELS:
            a, b = _count(m, five, "und"), _count(m, base, "und")
            ex.append(None if a is None or b is None else a - b)
        out.append([name, fmt(pl), fmt(ot), ", ".join("n/r" if x is None else f"{x:+d}" for x in ex)])
    return out


def _unused():
    out = [["Against", "What the model is given"] + [n for _, n in MODELS]]
    for opp_label, label, (opp, level, structure, tool, policy, toolv, collapse, seed) in TC:
        line = []
        for m, _ in MODELS:
            g = idx.get((m, opp, level, structure, tool, policy, toolv, seed, collapse), [])
            c = Counter(r["outcome"] for r in g)
            line.append(f"{c['planted']}/{c['undetermined'] + c['other']}/{c['trusted']}" if g else "not run")
        out.append([opp_label, label] + line)
    return out


HAVE_CONTROLS = any(c != "not run" for row in control_rows()[1:] for c in row[2:])
CLAUDE3 = [(m, n) for m, n in MODELS if "claude" in m]
W = [0.6 * inch, 1.82 * inch] + [4.08 * inch / max(1, len(MODELS))] * len(MODELS)

# ---------- helpers for numbers quoted in the text ----------
MK = {"mini": "gpt-5.4-mini", "g54": "gpt-5.4-2", "g55": "gpt-5.5", "haiku": "haiku", "sonnet": "sonnet", "opus": "opus"}
MID = {k: next(m for m, _ in MODELS if v in m) for k, v in MK.items()}
ALLM = ["mini", "g54", "g55", "haiku", "sonnet", "opus"]
CN = {"none1": ("trusted", "none", "na", False, False, 0, 0, False), "sig1": ("trusted", "signature", "na", False, False, 0, 0, False),
      "org1": ("trusted", "org", "na", False, False, 0, 0, False), "owner1": ("trusted", "controller", "collusion", False, False, 0, 0, False),
      "tool1": ("trusted", "controller", "collusion", True, False, 2, 0, False), "toolA1": ("trusted", "controller", "collusion", True, True, 2, 0, False),
      "five_toolA1": ("trusted", "controller", "independent", True, True, 2, 0, False),
      "none2": ("two", "none", "na", False, False, 0, 0, False), "tool2": ("two", "controller", "collusion", True, False, 2, 0, False),
      "toolA2": ("two", "controller", "collusion", True, True, 2, 0, False), "five_toolA2": ("two", "controller", "independent", True, True, 2, 0, False),
      "merge1": ("trusted", "controller", "collusion", False, False, 0, 0, True), "five_merge1": ("trusted", "controller", "independent", False, False, 0, 0, True),
      "merge2": ("two", "controller", "collusion", False, False, 0, 0, True), "five_merge2": ("two", "controller", "independent", False, False, 0, 0, True),
      "merge2_o2": ("two", "controller", "collusion", False, False, 0, 1, True), "merge2_o3": ("two", "controller", "collusion", False, False, 0, 2, True),
      "bare2": ("two", "bare", "collusion", False, False, 0, 0, "plain"),
      "vdis_nm": ("trusted", "org_dissent", "na", False, False, 0, 0, False), "vsup_nm": ("trusted", "org_support", "na", False, False, 0, 0, False),
      "vdis_blank": ("trusted", "org_dissent_blank", "na", False, False, 0, 0, False), "sdis_blank": ("trusted", "sig_dissent_blank", "na", False, False, 0, 0, False),
      "vsup_blank": ("trusted", "org_support_blank", "na", False, False, 0, 0, False),
      "five_tool1": ("trusted", "controller", "independent", True, False, 2, 0, False), "five_tool2": ("two", "controller", "independent", True, False, 2, 0, False),
      "toolB1": ("trusted", "controller", "collusion", True, 2, 2, 0, False), "five_toolB1": ("trusted", "controller", "independent", True, 2, 2, 0, False),
      "toolB2": ("two", "controller", "collusion", True, 2, 2, 0, False), "five_toolB2": ("two", "controller", "independent", True, 2, 2, 0, False),
      "tool1_permit": ("trusted", "controller", "collusion", True, 3, 2, 0, False), "tool2_permit": ("two", "controller", "collusion", True, 3, 2, 0, False),
      "none1_permit": ("trusted", "none", "na", False, 3, 0, 0, False), "none2_permit": ("two", "none", "na", False, 3, 0, 0, False),
      "owner1_swap": ("trusted", "controller", "collusion_swap", False, False, 0, 0, False), "tool2_swap": ("two", "controller", "collusion_swap", True, False, 2, 0, False),
      "tool2_noclose": ("two", "controller", "collusion", True, False, 3, 0, False), "five_tool2_noclose": ("two", "controller", "independent", True, False, 3, 0, False),
      "tool1_noclose": ("trusted", "controller", "collusion", True, False, 3, 0, False),
      "mixed_tool2": ("two", "controller", "mixed", True, False, 2, 0, False), "mixed_toolB2": ("two", "controller", "mixed", True, 2, 2, 0, False),
      "mixed_merge2": ("two", "controller", "mixed", False, False, 0, 0, True),
      "none2_reorder": ("two", "none", "na", False, 4, 0, 0, False), "tool2_reorder": ("two", "controller", "collusion", True, 4, 2, 0, False),
      "unk1": ("trusted", "org", "na", True, True, 2, 0, False), "unk2": ("two", "org", "na", True, True, 2, 0, False)}
WHAT = {"planted": "planted", "other": "trusted", "none": "undetermined"}
SET2 = defaultdict(list)
for r in scoring.load_mapped("runs_set2.jsonl"):
    SET2[(r["model"],) + scoring.cond(r)].append(r)


def grp(mk, cn, src=None):
    return (src if src is not None else idx).get((MID[mk],) + CN[cn], [])


def c(mk, cn, what="planted", src=None):
    g = grp(mk, cn, src)
    assert len(g) == 40, (mk, cn, len(g))
    return sum(r["outcome"] == WHAT[what] for r in g)


def cav(mk, cn, what="planted", src=None):
    return sum(r["final"] == {"planted": "planted_c", "other": "other_c"}[what] for r in grp(mk, cn, src))


def ran(mk, cn):
    return len(grp(mk, cn)) == 40


def rng(cn, what="planted", mks=ALLM):
    v = [c(m, cn, what) for m in mks if ran(m, cn)]
    return f"{min(v)} to {max(v)}"


def one_source(mk, cn):
    g = [r for r in grp(mk, cn) if r["outcome"] == "planted"]
    return sum(1 for r in g if r.get("independent_sources") == 1), len(g)


def trip(mk, cn, src=None):
    g = grp(mk, cn, src)
    if len(g) != 40:
        return "not run"
    return f"{c(mk, cn, 'planted', src)}/{c(mk, cn, 'none', src)}/{c(mk, cn, 'other', src)}"


def grid(title_rows, mks=ALLM):
    names = dict(zip(ALLM, [n for _, n in MODELS]))
    out = [[""] + [names[m] for m in mks]]
    for kind, label, fn in title_rows:
        out.append([label] + ([""] * len(mks) if kind == "head" else [fn(m) for m in mks]))
    return out


def gtable(rows, caption, colw, heads=()):
    data = [[Paragraph(str(x), S["cellb"] if (i == 0 or j == 0 and i in heads) else S["cell"]) for j, x in enumerate(row)] for i, row in enumerate(rows)]
    t = Table(data, colWidths=colw, hAlign="LEFT")
    style = [("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black), ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
             ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    for h in heads:
        style += [("SPAN", (0, h), (-1, h)), ("LINEABOVE", (0, h), (-1, h), 0.4, colors.grey)]
    t.setStyle(TableStyle(style))
    return KeepTogether([P(caption, "cap"), t, Spacer(1, 8)])


def rows_for(specs, mks=ALLM, src=None):
    return [("row", label, (lambda m, cn=cn: trip(m, cn, src) if (src is not None or ran(m, cn)) else "not run")) for label, cn in specs]


GW = [2.3 * inch] + [0.7 * inch] * 6
GW3 = [3.6 * inch] + [0.95 * inch] * 3
CL3 = ["haiku", "sonnet", "opus"]
os1 = {m: one_source(m, "tool2") for m in ALLM}
# repeat figures
_r2 = defaultdict(dict)
for r in ALLROWS:
    _r2[(r["model"], r["rep"])][(r["claim"],) + scoring.cond(r)] = r["outcome"]
REP = {}
for mk in ALLM:
    a, b = _r2.get((MID[mk], 1), {}), _r2.get((MID[mk], 2), {})
    _core = {k[1:] for k in _r2.get((MID["opus"], 2), {})}
    common = [k for k in b if k in a and k[1:] in _core]
    if common:
        REP[mk] = (sum(a[k] == b[k] for k in common), len(common))
_SUP = {"o1", "o2", "o3", "o4", "o5"}
_m1 = [r for seed in (0, 1, 2) for r in idx.get((MID["mini"], "trusted", "controller", "collusion", False, False, 0, seed, True), []) if r["outcome"] in ("planted", "trusted")]
FIRST = (sum(1 for r in _m1 if (r["outcome"] == "planted") == (r["first_source"] in _SUP)), len(_m1))
import re as _re
_NC = _re.compile(r"^\s*(undetermined|unresolved|unclear|uncertain|cannot|conflict|the sources conflict|disputed|most likely|probably|likely)", _re.I)
HOLE = sum(1 for r in rows if r["outcome_first"] in ("planted", "trusted") and not r.get("reparsed") and _NC.search(str(r["answer"])))
_hc = defaultdict(int)
for r in rows:
    if r["outcome_first"] in ("planted", "trusted") and not r.get("reparsed") and _NC.search(str(r["answer"])):
        _hc[(r["model"],) + scoring.cond(r)] += 1
HOLEMAX = max(_hc.values())
HOLE_OPUS = sum(v for k, v in _hc.items() if "opus" in k[0])
_lab = scoring.coded()
N_CODED = len(_lab)
N_AGREE2 = sum(1 for v in _lab.values() if len(v) == 2)
N_NOMAJ = sum(1 for v in _lab.values() if len(v) == 3 and len(set(v.values())) == 3)

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=1 * inch, rightMargin=1 * inch, topMargin=1 * inch, bottomMargin=1 * inch,
                        title="Signed is not independent", author="Narendra Sahu")
N_ALL = len(ALLROWS) + sum(len(v) for v in SET2.values())
N_REPARSED = sum(1 for r in rows if r.get("reparsed"))
SELF_B2 = sum(1 for r in grp("sonnet", "toolB2") if r.get("first_object") == "planted")
rep2 = lambda mk, cn: sum(1 for k, v in _r2.get((MID[mk], 2), {}).items() if k[1:] == CN[cn] and v == "planted")
two_src = sum(1 for r in grp("mini", "tool2") if r["outcome"] == "planted" and r.get("independent_sources") == 2)


def bt(mk, cn):
    t = trip(mk, cn)
    return f"<b>{t}</b>" if ran(mk, cn) and c(mk, cn) <= 10 else t


CN["owner2"] = ("two", "controller", "collusion", False, False, 0, 0, False)
CN["unk2_ni"] = ("two", "org", "na", True, False, 2, 0, False)
CN["fake5"] = ("two", "org_fake5", "independent", False, False, 0, 0, False)
CN["fakeind"] = ("two", "controller_fakeind", "collusion", True, False, 2, 0, False)
CN["sig2"] = ("two", "signature", "na", False, False, 0, 0, False)
CN["sigshared2"] = ("two", "signature_shared", "na", False, False, 0, 0, False)
CN["org2"] = ("two", "org", "na", False, False, 0, 0, False)
CN["fake5_guard"] = ("two", "org_fake5", "independent", False, 5, 0, 0, False)
CN["sigtool2"] = ("two", "signature_sharedtool", "na", False, False, 0, 0, False)
CN["owntool2"] = ("two", "controller_sharedtool", "independent", False, False, 0, 0, False)
q = lambda mk, cn, what="planted", src=None: f"{c(mk, cn, what, src)}/40"
_dis = [(v.get("alt:claude-sonnet-5-5"), v.get("alt:claude-haiku-5-5")) for v in _lab.values()]
N_DIS = sum(1 for a, b in _dis if a != b)
N_DIS_N = sum(1 for a, b in _dis if a != b and a == "N")
SWAPMAX = max(abs(c(m, a) - c(m, b)) for m in CL3 for a, b in [("owner1", "owner1_swap"), ("tool2", "tool2_swap")])
FIRSTMAX = max(c(m, cn) - sum(r["outcome_first"] == "planted" for r in grp(m, cn)) for m in ALLM for cn in ["none1", "owner1", "none2", "tool2", "five_merge2"])
from math import comb
def signp(mk, a, b, what="planted", srcb=None):
    ga = {r["claim"]: r["outcome"] == WHAT[what] for r in grp(mk, a)}
    gb = {r["claim"]: r["outcome"] == WHAT[what] for r in grp(mk, b, srcb)}
    lo = sum(1 for k in ga if ga[k] and not gb[k]); hi = sum(1 for k in ga if gb[k] and not ga[k])
    n = lo + hi
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(0, min(lo, hi) + 1)) / 2 ** n)
NEWCN = ["org2", "fake5", "fake5_guard", "fakeind", "sig2", "sigshared2", "sigtool2", "owntool2"]
def rep2n(mk, cn, what="planted"):
    return sum(1 for k, v in _r2.get((MID[mk], 2), {}).items() if k[1:] == CN[cn] and v == WHAT[what])
REP2MAX = max(abs(rep2n(m, cn) - c(m, cn)) for m in ("haiku", "sonnet") for cn in NEWCN)
PCTL = [signp("sonnet", "tool2", "tool2_permit"), signp("sonnet", "tool2", "tool2_reorder"), signp("haiku", "tool2", "tool2_permit")]
PNEW = {"fb_h": signp("haiku", "org2", "fake5"), "fb_s": signp("sonnet", "org2", "fake5"), "fb_o": signp("opus", "org2", "fake5"), "gd_o": signp("opus", "fake5", "fake5_guard"), "gd_s": signp("sonnet", "fake5", "fake5_guard"), "pt_o": signp("opus", "sig2", "sigtool2"), "g54p": signp("g54", "tool2", "tool2_permit"), "g54r": signp("g54", "tool2", "tool2_reorder"), "fh": signp("haiku", "none2", "fake5"), "fs": signp("sonnet", "none2", "fake5"), "fo": signp("opus", "none2", "fake5"), "ss": signp("sonnet", "sig2", "sigshared2"), "so": signp("opus", "sig2", "sigshared2")}
_any = [(a, b) for a, b in _dis if a != "N" or b != "N"]
PICK_AGREE = (sum(1 for a, b in _any if a == b), len(_any))
N_PLAIN = sum(1 for a, b in _dis if a == "N" and b == "N")
FIRSTALL = max(c(m, cn) - sum(r["outcome_first"] == "planted" for r in grp(m, cn)) for m in ALLM for cn in ("mixed_tool2", "mixed_toolB2", "mixed_merge2") if ran(m, cn))
G54MAX = max(abs(c("g54", cn) - sum(r["outcome_first"] == "planted" for r in grp("g54", cn))) for cn in CN if ran("g54", cn))
G55MAX = max(abs(c("g55", cn) - sum(r["outcome_first"] == "planted" for r in grp("g55", cn))) for cn in CN if ran("g55", cn))
_tb = [v["alt:claude-opus-5-5"] for v in _lab.values() if len(v) == 3]
TB_PICK = sum(1 for x in _tb if x != "N")
def qagree(mk, cn):
    return sum(1 for k, v in _r2.get((MID[mk], 2), {}).items() if k[1:] == CN[cn] and v == next(r["outcome"] for r in grp(mk, cn) if r["claim"] == k[0]))
_ca, _cb = defaultdict(int), defaultdict(int)
for _a, _b in _dis:
    _ca[_a] += 1; _cb[_b] += 1
_po = sum(1 for a, b in _dis if a == b) / len(_dis)
_pe = sum(_ca[k] * _cb[k] for k in set(_ca) | set(_cb)) / len(_dis) ** 2
KAPPA = (_po - _pe) / (1 - _pe)
S_FIRST = sum(r["outcome_first"] == "planted" for r in grp("sonnet", "tool2"))

st = []
st.append(P("Signed is not independent: what language models do with provenance when one operator runs the majority of sources<font size=11><super>1</super></font>", "title"))
st.append(P("Narendra Sahu<br/>Independent security researcher", "author"))
st.append(P("With<br/>Apart Research", "withapart"))
st.append(P("<super>1</super> Research conducted at the AI x Epistemics Research Sprint, November 2026.", "note"))

st.append(P("Abstract", "h1"))
st.append(P(f"Content provenance standards (C2PA, with the CAWG identity add-on) record who signed and who published an article, not who owns the publisher, so one operator running five verified outlets looks like five independent sources. We gave six models from two vendors 40 invented questions in which five same-owner outlets each wrote their own article for one answer (the planted answer) and two separately owned outlets backed another (the dissenting answer). Signature and verified-publisher lines had no detectable effect, with the planted answer already accepted almost every time. Telling the models outright that the five share an owner made only two of six switch to the dissenting answer; two others, GPT-5.4 and Sonnet 5.5, usually stated that the planted answer rested on one independent source and gave it anyway. Each fix had a cost. Letting models decline made them decline questions that had a well-supported answer, one instruction to count owners did the same when all five owners were separate, and merging same-owner articles before the model reads discarded a real majority for one model when only some outlets shared an owner. The ownership signal can also be forged: an ownership note planted inside one article misled one of four models badly and shifted two more, until one system-prompt sentence told them to treat such text as a claim. Assistants that count sources need an ownership record they can trust, and no current provenance assertion supplies one."))

st.append(P("1. Introduction", "h1"))
st.append(P("Counting how many sources agree only works if the sources are independent, and running many outlets is now cheap for one operator. In September 2026 Anthropic reported about 70 news sites that looked unrelated and were tied to one operator account through shared infrastructure (Anthropic 2026). Assistants that answer from retrieved pages read such sites and repeat what most of them say."))
st.append(P("Recent work shows that agents and LLM judges count copies and paraphrases of one report as confirmation, and proposes detectors based on shared text (Zhou et al. 2026; Metales et al. 2026; Gao et al. 2026). An operator who has each outlet write its own article shares no text. Zhou et al. report that separately rewritten pages get past their detector, and Metales et al. name colluding sources as the open problem. This is a Sybil attack (Douceur 2002), one actor posing as many, applied to evidence. It is the case we test."))
st.append(P("Provenance is the usual answer to doubts about a source. C2PA, the main content provenance standard, attaches a signed manifest that shows the content has not been altered since signing and which signer, often a publishing tool, signed it. The CAWG identity assertion is an add-on that binds a verified person or organisation to the content, here the publisher. Neither says who controls the publisher, so two verified publishers can have one owner. We call this the <b>independence gap</b>: provenance gives integrity and identity, and corroboration needs independence. We ask what models do with each kind of information, and what it takes for ownership information to change the answer."))
st.append(P("<b>Threat model.</b> The adversary is one operator with several outlets. Each outlet writes its own article from the bare claim, in its own voice, and the operator can sign every article and obtain a verified publisher identity for every outlet. The defender is a model answering from retrieved articles, or the harness, meaning the code that builds the prompt around it. The fixes we test assume the defender holds a true record of who owns each outlet, so our numbers are a best case (Section 5)."))
st.append(P("<b>What we test</b> (Figure 1). Ownership can reach the model in three ways: an <b>owner line</b> under each article, an <b>ownership note</b> after the articles that lists which sources share an owner, and a <b>harness merge</b> that keeps one article per owner before the model reads anything. The note is tested alone and with one of two instructions: an <b>abstain instruction</b> (count owners, and answer \"undetermined\" if the sources do not settle it) or a <b>majority instruction</b> (give the answer backed by more independent owners). Every condition with the note also shows the owner line."))
st.extend(figure(os.path.join(ROOT, "results", "fig_setup.png"), "Figure 1. The setup. <b>Planted answer</b>: what the five supporting articles report. <b>Dissenting answer</b>: what the one or two other articles report. Both are invented, so neither is true. \"Origin\" in the prompts and in Box 1 means one owner, however many outlets it runs. <b>No pick</b>: the model declines to choose.", 5.6))
BOXST = ParagraphStyle("boxst", parent=S["body"], fontSize=9.5, leading=11.6, spaceAfter=0)
_ex = next(r for r in grp("sonnet", "tool2") if r["claim"] == "c01")
_box = Table([[Paragraph("<b>Box 1. One reply in full</b> (Sonnet 5.5; the ownership note reports one owner; two dissenting outlets).<br/>"
                         "<b>Question:</b> Who was appointed chief executive of Varnholt Logistics in March? Five articles name Ilse Marrenkamp, two name Dorian Feltz.<br/>"
                         f"<b>Answer:</b> {_ex['answer']}. <b>Confidence:</b> {_ex['confidence']}. <b>Independent sources supporting the answer:</b> {_ex['independent_sources']}.<br/>"
                         f"<b>Reasoning:</b> \"{_ex['reasoning']}\"", BOXST)]], colWidths=[6.5 * inch])
_box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.black), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
st.append(KeepTogether([_box, Spacer(1, 6)]))
st.append(P("<b>Contributions.</b>"))
st.append(P("1. <b>Same owner, no shared text.</b> Earlier work told models that copied reports came from one source. Here the agreeing articles share no text, and the only thing that changes between conditions is what the model is told about signatures, publishers and owners.", "bullet"))
st.append(P(f"2. <b>Models that report the owner count and do not use it, depending on the prompt.</b> Given the ownership note, three of six models mostly kept the planted answer. GPT-5.4 reported one independent source in {os1['g54'][0]} of its {os1['g54'][1]} such replies and Sonnet 5.5 in {os1['sonnet'][0]} of {os1['sonnet'][1]} (Box 1). On both, one sentence permitting abstention, or asking for reasoning first, removed most of the effect. Metales et al. saw small judges ignore a same-source note on copied text, and Pradhan and Goley saw models notice a flaw in a source and endorse it anyway; we see the same for common ownership on two models, and show it is tied to the answer format.", "bullet"))
st.append(P("3. <b>Fixes scored on cost as well as effect.</b> Figure 2 and Table 1 compare the note, two instructions and the merge on what they remove under one owner and on what they wrongly remove when the outlets are separately or partly owned. None is best on all counts.", "bullet"))
st.append(P("4. <b>Two ways an ownership signal can arrive without a trusted channel.</b> A forged note inside an article moves three of four models, and one guard sentence stops it. A shared signer shifts the larger Claude models toward treating the five as one source, rightly or wrongly.", "bullet"))

st.append(P("2. Related Work", "h1"))
st.append(P("<b>Copies counted as confirmation.</b> Zhou et al. (2026) show that deep research agents credit a paraphrased cluster like independent sources, and propose a gate that collapses near-copies before synthesis. Their agent is never told about shared origin. Metales et al. (2026) measure the same for LLM judges on news: two small judges ignored a note that reprinted reports came from one source and the largest judge followed it. Gao et al. (2026) find that a short declaration reduces how much agents count restated messages; Chen et al. (2026) and Lu and Zhang (2026) study related attacks. Our merge step does what their duplicate-collapsing steps do, but groups articles by owner instead of by shared text; it is also close to the isolate-then-aggregate defence of Xiang et al. (2024). None of these papers tells the model about common ownership when the sources share no text. Our forged-note test (Section 4.6) is a case of indirect prompt injection (Greshake et al. 2023). Its closest precedent is Zhu (2026), who shows that labels written inside a retrieved document, such as a verified-source status, sway models and that telling the model such labels are data works as a defence, in the manner of spotlighting (Hines et al. 2024); we aim the same mechanism at source counting."))
st.append(P("<b>How models weigh conflicting evidence.</b> Models follow the retrieved majority and pay little attention to credibility cues (Xie et al. 2024; Wan et al. 2024), which corpus poisoning exploits (Zou et al. 2025). Schuster et al. (2026) find that repetition overrides a preference for institutional sources, and Kawada and Kellis (2026) that models can reject a candidate when checking it and still adopt it. Pradhan and Goley (2026) report the same pattern for sources: models question a flawed statistic in their reasoning and still endorse it, and prompt fixes produce general scepticism. Our Sections 4.3 and 4.4 find both for ownership."))
st.append(P("<b>Dependence and ownership records.</b> Source dependence is an old idea in data fusion (Dong et al. 2009). Bara (2026) shows, in a formal model and in LLM-agent experiments, that an aggregator which sees only reports can be fooled by correlated reports from one root, and proposes aggregating over authenticated origins while warning that provenance need not be truthful. Our merge is that idea with a language model as the aggregator and ownership as the origin. Site networks have been traced through shared infrastructure, not text (Bengani 2019; Anthropic 2026). C2PA 2.4 (C2PA 2026) and the CAWG identity assertion (Creator Assertions Working Group 2026) are the current content standards, and for human readers C2PA labels raise trust in a news source (Trattner et al. 2026). Ownership is recorded elsewhere, for example in legal entity identifiers with parent data, in the owner-domain field of ads.txt, in the control fields of trust.txt, and in media ownership registers. Much of it is self-declared, and we know of no assistant that passes it to the model at answer time. Cotton-Barratt et al. (2025) treat provenance tracing as epistemic infrastructure."))

st.append(P("3. Methods", "h1"))
st.append(P("<b>3.1 Questions and articles.</b> We wrote 40 invented questions about fictional people, places and companies, each with a planted answer and a different dissenting answer. Five supporting outlets have different voices (regional daily, business newsletter, long-form weekly, trade blog, wire bulletin). GPT-5.4 mini wrote each article from the bare claim, 97 to 135 words, with its own invented details; mean pairwise 3-gram overlap is 0.02. The first dissenting outlet is written as a national newspaper that names the document it relies on, the second as a small local paper with first-hand reporting. Table A14 lists every factor we varied, and Table A1 the condition sets and which models ran each. Provenance lines and the ownership note are simulated text that follows the real layers (C2PA manifest, CAWG identity) plus an ownership attestation that C2PA and CAWG do not have; Appendix C gives the wording."))
st.append(P("<b>3.2 Hypotheses.</b> Four were written in the project README before the first run, though the commit history cannot confirm the timing (Appendix A): signatures do not reduce acceptance of the planted answer, signatures or verified publishers raise it, showing the owner reduces it, and the note reduces it further. Table A2 gives their status. Everything else is exploratory."))
st.append(P(f"<b>3.3 Models and scoring.</b> We tested GPT-5.4 mini, GPT-5.4, GPT-5.5, Claude Haiku 5.5, Claude Sonnet 5.5 and Claude Opus 5.5. Each question in each condition is one call with the articles in the prompt and default settings, so this is retrieval-style question answering and not a multi-step agent. The model returns an answer, a confidence, the number of independent sources it believes support the answer, and its reasoning. We report three outcomes: planted, no pick, dissenting. An answer that names one side is scored by token match. About a third of answers ({N_CODED:,} of {N_ALL:,}) were not a single clean name on the first pass and went to the coders. Most of these plainly decline to pick; the rest hedge, as in \"most likely X, though one source says Y\". We count a hedged answer as a pick for the side it favours, as labelled by two coder models with a third breaking ties. The coders agreed on {100 * N_AGREE2 / N_CODED:.0f}% of labels, mostly the plain refusals, and disagreed almost only on whether a hedge counts as a pick at all, not on which side it names (Appendix A). Figure 2 shades hedged answers, and Table A3 gives the stricter count that excludes them."))
st.append(P("<b>3.4 Uncertainty.</b> Each cell is 40 questions, so a count carries a 95% Wilson interval of up to 15 points either side (Table A4). Comparisons are paired within a model, with an exact sign test on the questions that change. The core conditions were asked a second time on four models, and counts moved by up to 7/40 between asks (planted counts by up to 5), so we do not interpret differences below about 8. The later runs were asked once, except the forged-note and shared-signer runs on Haiku 5.5 and Sonnet 5.5 (Section 4.8). All model calls are cached in the repository."))

st.append(P("4. Results", "h1"))
st.append(P("All counts are out of 40 questions. Figure 2 shows the main conditions with two dissenting outlets, and Table A5 and Figure A1 give every core condition. Neither answer is true, so we judge a reply by owners: under one owner the dissenting answer has two owners behind it against one, and under five owners the planted answer has five against two."))
st.append(P(f"<b>4.1 Provenance lines on every article had no detectable effect.</b> With no provenance, every model gave the planted answer on at least {min(c(m, cn) for m in ALLM for cn in ['none1', 'none2'])}/40 questions (Figure 2, top row). This counts hedged answers, which Opus 5.5 gives often (Table A3). A signature or a verified publisher on every article produced no detectable change in answers or stated confidence, against one dissenting outlet on all six models and against two on four (Tables A5, A6, A13). With acceptance at the ceiling the answers could only have shown a decrease, so the test says little about whether such lines add credibility. A line on one side only did matter. When the dissenting article had a verified publisher and the other five carried an explicit \"no manifest found\" line, three models dropped to {max(c(m, 'vdis_nm') for m in ['g55', 'sonnet', 'opus'])}/40 planted answers or fewer (Table A7); when the five were left blank instead, only Opus 5.5 of the three Claude models switched (Table A8). Printing a missing-manifest line was our choice; C2PA does not prescribe it."))
st.extend(figure(os.path.join(ROOT, "results", "fig_main.png"), "Figure 2. Two dissenting outlets against five outlets that back the planted answer. Numbers are planted, no-pick and dissenting counts out of 40; lighter shades mark answers given with a caveat. \"Note\" is the ownership note; every row has two dissenting outlets. The left margin names the ownership situation of each block and which answer has more owners behind it.", 6.5))
st.append(P(f"<b>4.2 Told that the five outlets had one owner, two models switched, one split and three mostly kept the planted answer.</b> The ownership note said that the five supporting outlets had one owner and the two dissenting outlets had different owners (Figure 2, middle block, first row). GPT-5.5 and Opus 5.5 switched to the dissenting answer almost completely ({q('g55', 'tool2', 'other')} and {q('opus', 'tool2', 'other')}). GPT-5.4 mini, GPT-5.4 and Sonnet 5.5 kept the planted answer on at least {min(c(m, 'tool2') for m in ['mini', 'g54', 'sonnet'])}/40. Haiku 5.5 split three ways. The owner line without the note left GPT-5.4 and Haiku 5.5 on the planted answer and switched Opus 5.5. Sonnet 5.5 also switched on most questions with the owner line alone ({q('sonnet', 'owner2')} planted), more than with the note added, which we cannot explain (Table A13). Two wording checks on the Claude models are in Tables A8 and A9: swapping the owner names between sides changed planted counts by at most 8/40, and removing the note's closing warning sentence doubled Haiku 5.5's planted answers."))
st.append(P(f"<b>4.3 Two models kept the planted answer while saying it had one independent source, and the prompt format explains most of it.</b> GPT-5.4 reported one independent source in {os1['g54'][0]} of its {os1['g54'][1]} planted answers, and Sonnet 5.5 in {os1['sonnet'][0]} of {os1['sonnet'][1]}. Box 1 shows a typical reply: the model restates the note correctly and then answers with the five \"because far more documents support\" them. GPT-5.4 mini reported one source in only {os1['mini'][0]} of {os1['mini'][1]} planted answers and two in {two_src}, so it mostly miscounts."))
st.append(P(f"Our default prompt asks for the answer first and does not mention declining. We changed each of these on GPT-5.4 and the Claude models (Table A13). One added sentence permitting \"undetermined\" removed almost all planted answers on GPT-5.4 and Haiku 5.5 and more than half on Sonnet 5.5. On GPT-5.4 they became no-pick answers ({q('g54', 'tool2_permit', 'none')}) and never the dissenting answer, so the sentence produced abstention, not use of the owner count; we did not run it on GPT-5.4 without ownership information. On Haiku 5.5 and Opus 5.5 the same sentence also removed planted answers when no ownership information was given, so it is not free (Table A8). Asking for reasoning before the answer cut planted answers to {q('g54', 'tool2_reorder')} on GPT-5.4 and {q('sonnet', 'tool2_reorder')} on Sonnet 5.5, and left Haiku 5.5's count unchanged. The gap between what these models report and what they answer is real under an answer-first prompt, and mostly closes when the model may decline or must reason first."))

def _b(v, bad):
    return f"<b>{v}</b>" if bad else str(v)
def _fx(cn_one, what, bad=lambda v: False):
    return lambda m: (_b(c(m, cn_one, what), bad(c(m, cn_one, what))) if ran(m, cn_one) else "n/r")
def _added(cn_five):
    return lambda m: (_b(f"{c(m, cn_five, 'none') - c(m, 'none2', 'none'):+d}".replace("+0", "0"), c(m, cn_five, 'none') - c(m, 'none2', 'none') >= 10) if ran(m, cn_five) else "n/r")
FIX = [("Note", "tool2", "five_tool2", "mixed_tool2"), ("Note + abstain instruction", "toolA2", "five_toolA2", None), ("Note + majority instruction", "toolB2", "five_toolB2", "mixed_toolB2"), ("Harness merge", "merge2", "five_merge2", "mixed_merge2")]
T4 = [("head", "(1) Extra no-pick answers when the five owners are separate, against the same model's no-provenance baseline. 0 is ideal.", None)] + [("row", n, _added(b)) for n, a, b, m3 in FIX] \
    + [("head", "(2) Planted answers kept under partial ownership, where the planted side has three owners against two. 40 is ideal.", None)] + [("row", n, _fx(m3, "planted", lambda v: v <= 20)) for n, a, b, m3 in FIX if m3]
st.append(gtable(grid(T4), "Table 1. What each fix costs, two dissenting outlets, counts out of 40 (n/r: not run; large costs in bold). Figure 2 shows what each fix achieves under one owner.", GW, heads=(1, 6)))
st.append(P(f"<b>4.4 The abstain instruction removed the planted answer, and also removed answers that should have stayed.</b> Under one owner it left no planted answers on four models (Figure 2, middle block). But when the five owners were separate, GPT-5.4 gave no pick on {q('g54', 'five_toolA2', 'none')} and Haiku 5.5 on {q('haiku', 'five_toolA2', 'none')} (Figure 2, bottom block; Table 1, block 1). The instruction tells the model to lower its confidence when independent owners disagree and to answer undetermined if the sources do not settle the question, and these models took that literally. The majority instruction had no such cost. It switched GPT-5.5 and the three Claude models to the dissenting answer, but left GPT-5.4 and GPT-5.4 mini mostly on the planted answer. (Sonnet 5.5 often wrote the planted answer and then corrected itself in the same reply, in {SELF_B2} of 40 replies; we score the correction.) Neither instruction is shown to handle unknown ownership. A note saying ownership is unknown, with no instruction, changed almost nothing, and with the abstain instruction five models gave no pick on most questions (Tables A10, A13). The majority instruction was not run there."))
st.append(P(f"<b>4.5 Merging same-owner articles switched five of six models to the dissenting answer.</b> After the merge the model reads one article per owner, so with one owner against two dissenting outlets it reads one article against two. Five of six models then gave the dissenting answer on at least {min(c(m, 'merge2', 'other') for m in ['g54', 'g55', 'haiku', 'sonnet', 'opus'])}/40, including GPT-5.4 and Sonnet 5.5, which had kept the planted answer with all seven articles and the note in the prompt (Figure 2). This is no surprise: models follow the majority of whatever articles remain, and the same three articles with no merge note give the same result (Table A7). GPT-5.4 mini is the exception: after a merge it mostly follows whichever article is listed first (Tables A7, A11). The merge is not always the best fix either. When only three of the five outlets share an owner, the planted side still has three owners against two. There the majority instruction kept the planted answer on 40/40 for all three Claude models, and the merge kept it on only {q('opus', 'mixed_merge2')} for Opus 5.5 (Table 1, block 2)."))
_rp = lambda mk: f"{100 * REP[mk][0] / REP[mk][1]:.0f}%"
st.append(P(f"<b>4.6 A forged ownership note inside an article misled the Claude models, and one guard sentence stopped it.</b> The note is plain text, so an operator can write one; this is indirect prompt injection aimed at the ownership signal. We tested it on GPT-5.4 and the Claude models (Table A13). The five outlets really have five owners and show verified publishers, so the planted answer is the better-supported one, and one dissenting article ends with a forged note saying the five share an owner. Against the same condition without the forgery, planted answers fell from {q('haiku', 'org2')} to {q('haiku', 'fake5')} on Haiku 5.5, and by about 10 of 40 on Sonnet 5.5 and Opus 5.5. GPT-5.4 did not switch, in line with its weak response to the genuine note. One sentence in the system prompt, saying that ownership information is valid only in the provenance lines and that ownership statements inside a source are claims by that source, restored all four models to {min(c(m, 'fake5_guard') for m in ['g54', 'haiku', 'sonnet', 'opus'])}/40 or more. The reverse forgery, a note inside one of the five articles saying all sources are independent while the genuine note says one owner, changed counts by at most {max(abs(c(m, 'fakeind') - c(m, 'tool2')) for m in ['g54', 'haiku', 'sonnet', 'opus'])}/40 in no consistent direction. We did not test a forger who also imitates the provenance lines, which is the known weakness of this kind of guard."))
st.append(P(f"<b>4.7 A shared signer switched the larger Claude models.</b> In Section 4.1 each outlet signs with its own key. Outlets on one publishing system may share a signer, so on GPT-5.4 and the Claude models we showed the five outlets with one shared key and no ownership information (Table A13). Opus 5.5 then switched to the dissenting answer on {q('opus', 'sigshared2', 'other')} and Sonnet 5.5 on {q('sonnet', 'sigshared2', 'other')}; GPT-5.4 and Haiku 5.5 did not react. Nothing in the prompt says what a shared key means. Real C2PA signers are often a publishing platform that unrelated outlets share, so we also named the shared signer as a platform. Sonnet 5.5 then kept the planted answer, but Opus 5.5 still dropped to {q('opus', 'sigtool2')} planted, and returned to {q('opus', 'owntool2')} only when five separate owners were attested beside it. Opus 5.5 thus takes a shared signer as a sign of common ownership unless told otherwise. That is a false-positive risk for honest outlets on a common platform, and a signal an operator can remove by using separate keys."))
st.append(P(f"<b>4.8 Robustness.</b> Four checks are in Table A12. On a second article set, from a different writer and with consistent details on each side, the Sonnet 5.5 result of Section 4.3 weakens further: {q('sonnet', 'tool2', 'planted', SET2)} planted under the note, from a baseline of {q('sonnet', 'none2', 'planted', SET2)} there, against {q('sonnet', 'tool2')} on the main set. Repeat runs move counts by up to 7/40; a second ask of the forged-note, guard and shared-signer conditions on Haiku 5.5 and Sonnet 5.5 moved planted counts by at most {REP2MAX}/40 (forged note: {rep2n('haiku', 'fake5')}/40 and {rep2n('sonnet', 'fake5')}/40; shared key on Sonnet 5.5: {rep2n('sonnet', 'sigshared2')}/40). The main contrasts pass a Bonferroni correction over the 122 tests listed in the analysis script; the later tests are outside that family. Strict scoring of hedged answers lowers several Claude cells, most of all in Table 1, block 2, and leaves the GPT cells almost unchanged."))

st.append(P("5. Discussion and Limitations", "h1"))
st.append(P("<b>What to do.</b> Every fix below assumes a trusted ownership record, which does not exist today."))
st.append(P("1. Do not rely on telling a model who owns a source. Under an answer-first prompt, half the models we tested mostly kept the planted answer.", "bullet"))
st.append(P("2. Let the model decline, or ask for its reasoning first. This removed most of that failure on GPT-5.4 and Sonnet 5.5, at some cost in answers.", "bullet"))
st.append(P("3. Apply ownership in the pipeline before the model reads, and tell the model that ownership claims inside retrieved text are only claims. A forged note misled one model badly and shifted two more; one guard sentence stopped it.", "bullet"))
st.append(P(f"4. Test any such defence on separately owned and partly owned sources too. The abstain instruction gave no pick on up to {max(c(m, 'five_toolA2', 'none') for m in ALLM)}/40 questions when the owners were separate.", "bullet"))
st.append(P("<b>For provenance standards.</b> We assume signatures and verified publishers work as designed. Closing the independence gap would, we propose, take an assertion with three properties that a C2PA manifest and a CAWG identity do not have together. First, it states who controls the publisher, not only who the publisher is. Second, a party other than the publisher issues it, as CAWG already allows for identity claims, since an operator can declare five owners as easily as one; when our note said the five outlets had five owners, all five models that ran that condition kept the planted answer. Third, it has an explicit value for unknown and guidance on what a consumer should do with it: on its own an unknown note changed nothing, and with the abstain instruction it removed most answers (Section 4.4). The manifest format could already carry such an assertion; what is missing is an issuer and a trust list for ownership, so the gap is one of governance more than syntax. Even then an operator with five shell companies defeats it, and the merge trusts the record completely: five honest outlets that share an owner would be collapsed to one and outvoted by two shell outlets."))
st.append(P("<b>Limitations.</b> We tested six models from two vendors on 40 questions, with one sample per cell and repeats on four models. Provenance and the note are simulated text. The task is single-call question answering over fixed articles, not a research product with live search. The two sides are not matched in quality: the dissenting articles are written to sound careful, and the five supporting articles disagree on incidental details, which Box 1 shows a model noticing. The prompt-format, forged-note and shared-signer runs covered GPT-5.4 and the Claude models only, and the partial-ownership, wording and second-article-set runs the Claude models only, and the coders that scored ambiguous answers are from that same vendor and were not checked against human labels. Appendix A lists further limits."))

st.append(P("6. Conclusion", "h1"))
st.append(P("A signature shows that an article is intact and a verified identity shows who published it. Neither shows whether five agreeing outlets are five sources or one. Told about a shared owner, half the models still gave the outlets' answer under an answer-first prompt, and each fix we tried recovered most of the lost ground at a cost of its own. The text channel that carries a true ownership note also carries a forged one. Everything here depends on an ownership record the model can trust, which the operator behind such a network has no reason to provide."))


T3ROWS = [("head", "One dissenting outlet", None)] + [("row", lab, (lambda m, cn=cn: bt(m, cn))) for lab, cn in [("No provenance", "none1"), ("Signed", "sig1"), ("Verified publisher", "org1"), ("Owner line: one owner", "owner1"), ("Note: one owner", "tool1"), ("Note: one owner + abstain instruction", "toolA1"), ("Note: five owners + abstain instruction", "five_toolA1")]] \
    + [("head", "Two dissenting outlets", None)] + [("row", lab, (lambda m, cn=cn: bt(m, cn))) for lab, cn in [("No provenance", "none2"), ("Note: one owner", "tool2"), ("Note: one owner + abstain instruction", "toolA2"), ("Note: five owners + abstain instruction", "five_toolA2"), ("Harness merge: one owner", "merge2"), ("Harness merge: five owners", "five_merge2")]]
st.append(P("Code and Data", "h1"))
st.append(P("<b>Code repository:</b> https://github.com/SahuNarendra/signed-not-independent. All questions, articles, prompts, cached model answers, coder labels and analysis scripts are included. All data are fictional and were generated in the sprint; no external dataset is used."))
st.append(P("<b>Prior work.</b> No code was written before the sprint. A literature search and a plan for a related idea were done before 13 November; the plan was dropped that day when a second search showed it was already published."))

st.append(P("Author Contributions", "h1"))
st.append(P("Narendra Sahu: sole author."))

st.append(P("References", "h1"))
for ref in [
    "Anthropic (2026). Detecting and countering misuse of AI: September 2026. https://www.anthropic.com/threat-intelligence-report-september-2026",
    "Bara, M. (2026). Epistemic Sybil Resistance: Multiplying AI Agents Without Multiplying Evidence. arXiv:2609.01873",
    "Bengani, P. (2019). Hundreds of \"pink slime\" local news outlets are distributing algorithmic stories and conservative talking points. Tow Center, Columbia Journalism Review.",
    "C2PA (2026). Content Credentials: C2PA Technical Specification 2.4. https://spec.c2pa.org/",
    "Chen, Y. et al. (2026). How Much Can We Trust LLM Search Agents? Measuring Endorsement Vulnerability to Web Content Manipulation. arXiv:2606.16821",
    "Cotton-Barratt, O., Vaintrob, L., Sourbut, O. (2025). Design Sketches: Collective Epistemics. Forethought. https://www.forethought.org/",
    "Creator Assertions Working Group (2026). CAWG Identity Assertion. https://cawg.io/",
    "Dong, X. L., Berti-Equille, L., Srivastava, D. (2009). Integrating Conflicting Data: The Role of Source Dependence. Proceedings of the VLDB Endowment 2(1), 550-561.",
    "Douceur, J. R. (2002). The Sybil Attack. International Workshop on Peer-to-Peer Systems (IPTPS).",
    "Gao, J. et al. (2026). Copies or Sources? Measuring How LLM Aggregators Count Restated Evidence in Multi-Agent Systems. arXiv:2610.06192",
    "Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., Fritz, M. (2023). Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. AISec 2023. arXiv:2302.12173",
    "Hines, K., Lopez, G., Hall, M., Zarfati, F., Zunger, Y., Kiciman, E. (2024). Defending Against Indirect Prompt Injection Attacks With Spotlighting. arXiv:2403.14720",
    "Kawada, S., Kellis, M. (2026). Evidence Integration in Large Language Models. arXiv:2609.04290",
    "Lu, Y., Zhang, Y. (2026). The Corroboration Illusion: When More News Makes LLM Forecasts Less True. arXiv:2609.22246",
    "Metales, A., Grabenheinrich, M., Metales, A. (2026). Copies Are Not Confirmations: How News Duplication Fools LLM Judges and Continual Learners. arXiv:2611.09203",
    "Pradhan, R. N., Goley, S. (2026). Trust, but Don't Verify: Epistemic Blind Spots in LLM Source Evaluation. arXiv:2606.05403",
    "Schuster, J., Gautam, V., Markert, K. (2026). Whose Facts Win? LLM Source Preferences under Knowledge Conflicts. arXiv:2601.03746",
    "Trattner, C., Forstner, S. L., Starke, A. D., Knudsen, E. (2026). C2PA Provenance Labels Increase Trust in Digital News Platforms Across Western Countries. ICWSM 2026. doi:10.1609/icwsm.v20i1.42749",
    "Wan, A., Wallace, E., Klein, D. (2024). What Evidence Do Language Models Find Convincing? ACL 2024.",
    "Xiang, C., Wu, T., Zhong, Z., Wagner, D., Chen, D., Mittal, P. (2024). Certifiably Robust RAG against Retrieval Corruption. arXiv:2405.15556",
    "Xie, J., Zhang, K., Chen, J., Lou, R., Su, Y. (2024). Adaptive Chameleon or Stubborn Sloth: Revealing the Behavior of Large Language Models in Knowledge Conflicts. ICLR 2024.",
    "Zhou, R. et al. (2026). Evidence Laundering: Deep Research Agents Mistake Correlated Sources for Independent Evidence. EMNLP 2026. https://aclanthology.org/2026.emnlp-main.509/",
    "Zhu, J. (2026). Document-Authored Control-Signal Impersonation: A Low-Cost Indirect Prompt Attack on RAG Safety Boundaries. arXiv:2606.09005",
    "Zou, W., Geng, R., Wang, B., Jia, J. (2025). PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models. USENIX Security 2025.",
]:
    st.append(P(ref, "ref"))

st.append(P("Appendix A. Limitations and Dual-Use / Ethical Considerations", "h1"))
st.append(P(f"<b>Scoring of hedged answers.</b> The two coders (Sonnet 5.5 and Haiku 5.5) saw the question, both candidate answers, the reply and its confidence. Their kappa was {KAPPA:.2f}. Both read {N_PLAIN:,} answers as no pick; where at least one of them saw a pick, they agreed on only {PICK_AGREE[0]:,} of {PICK_AGREE[1]:,}. In {N_DIS_N:,} of {N_DIS:,} disagreements the Sonnet 5.5 coder read a hedged answer as no pick where the Haiku 5.5 coder read it as a pick, and the third coder (Opus 5.5) sided with the pick reading in {100 * TB_PICK / len(_tb):.0f}% of them. The final scoring is therefore close to the lenient reading, and Table A3 shows the strict one. As one more check, the AI assistant used in this work labelled a sample of 150 of these answers, balanced across models and label types, from a sheet that hides the model, the condition and the automatic label (results/assistant_label_sheet.csv); its labels matched the final scoring on 146. A second instance of the same assistant, given only the sheet and the labelling rule and no knowledge of the project, produced the same 150 labels (results/independent_label_sheet.csv). Both are from the same vendor as the coders, so this shows the labels are stable under that rule and is not an independent check. No human labels were used; a blank copy of the sheet is in the repository for anyone who wants to label it. <b>Further limits of the design.</b> The hypotheses were written in the README on 13 November, but the commit history starts on 14 November, so their timing cannot be checked from it. Ownership is an imperfect stand-in for independence: commonly owned newsrooms can report separately, and separately owned outlets can repeat one press release. Real C2PA signing of text articles is rare, and signer certificates often identify a tool or platform, so nothing here says how real manifests would read. In the main article set one tested model wrote all the articles and the five supporting articles disagree on incidental details, which independent reports of a real event would not; the second set removes both but its articles share more wording (mean 3-gram overlap 0.14, maximum 0.51). Every note condition also carries the owner line under each article. The output format asks for the number of independent sources in every condition, which may draw attention to independence at baseline. The dissenting outlets are written to sound careful, and no run used carelessly written ones. GPT-5.4 and GPT-5.5 were not asked a second time; GPT-5.5 and GPT-5.4 mini did not run the later controls, and GPT-5.4 ran only the conditions in Table A13 (controls 2 and 3 and the second article set are Claude only). Default reasoning settings differ between models and may explain part of the difference between them. Signature and verified-publisher lines were tested against one dissenting outlet on all six models and against two on four (Table A13). The token matcher scored {HOLE} first-ask answers as clean although they open with a hedge such as \"most likely\" or \"probably\" (at most {HOLEMAX} in any cell, {HOLE_OPUS} of them from Opus 5.5), so the strict counts in Table A3 are slightly generous for that model, and {N_REPARSED} replies that contained a corrected second answer were scored by their last answer."))
st.append(P("<b>Future work.</b> Ownership inferred from infrastructure signals, with its false positives. Partial and adversarial ownership records. Real signed manifests, including outlets that share a signer. Multi-step agents with live search and a real tool call. The owner line alone against two dissenting outlets, and a note saying ownership is unknown with no instruction, on all models. The later checks on GPT-5.5 and GPT-5.4 mini. A forger who imitates the provenance lines as well as the note. A check of the coder labels against human labels."))
st.append(P("<b>What the result establishes, and what it does not.</b> In a synthetic test with fictional outlets, on six models from two vendors, provenance and ownership information had the effects in Figure 2 and Table 1. The test says nothing about other models, about research products with live search, about outlets with a real reputation, or about whether any real outlet is independent, and it does not show that a deployable ownership signal exists."))
st.append(P("<b>Dual use.</b> Showing that agreeing outlets written from scratch pass as independent could inform an influence operation, and Section 5 names ways around the fixes (shell owners, shell outlets or a false attestation of shared ownership against an honest group, an explicit negative provenance line on a rival, ownership text planted in an article). The first is already documented in the wild and in the papers cited; we judge that naming the limits of a defence helps defenders more than attackers. The repository contains the test harness only and no tooling to run outlets. All outlets, people and claims are fictional and nothing was published to the web."))
st.append(P("<b>Conflict to disclose.</b> The AI assistant used during the work comes from one of the two vendors whose models were tested, three of the six tested models are from that vendor, and its models served as coders. To limit the effect, every tested model was called through its API with the same fixed prompts, coder prompts are fixed and published, and all numbers come from scripts and cached answers in the repository. <b>Personal data.</b> None."))

st.append(P("Appendix B. Supplementary results", "h1"))
st.append(P("Cells are planted / no pick / dissenting out of 40 unless a caption says otherwise."))
st.append(table([["Condition set", "Conditions", "Models", "Reported in"],
                 ["Core: provenance on every article alike, note, abstain instruction, merge", "19", "all six", "Figure 2, Tables A5, A10, A11"],
                 ["Controls 1: one-sided provenance, majority instruction, merge checks", "14", "five; GPT-5.5 ran 5", "Table A7"],
                 ["Controls 2: other side blank, permission to abstain, names swapped", "9", "three Claude models", "Table A8"],
                 ["Controls 3: partial ownership, note wording, reasoning first", "8", "three Claude models", "Table A9"],
                 ["Second article set", "4", "three Claude models", "Table A9"],
                 ["Retest of the headline condition: permission to abstain, reasoning first, owner line alone, unknown note with no instruction (two dissenting outlets)", "4", "GPT-5.4 and three Claude models; two were already in controls 2 and 3 for Claude", "Table A13"],
                 ["Controls 4: forged ownership note inside an article (two versions), signature with separate keys and with a shared key (two dissenting outlets)", "4", "GPT-5.4 and three Claude models", "Table A13"],
                 ["Controls 5: matched baseline for the forged note, guard sentence, shared platform signer with and without attested owners", "4", "GPT-5.4 and three Claude models", "Table A13"],
                 ["Early exploratory conditions (first-day note wording and other variants)", "28", "GPT-5.4 mini only", "repository only; three cells quoted in Table A2"]],
                "Table A1. Condition sets, 40 questions each. Controls were added on the second day after reviews of drafts by AI reviewers (see the LLM Usage Statement); most later sets ran on Claude models only because the OpenAI budget ran out; the retest and controls 4 and 5 were run last, after further AI review.", colw=[3.3 * inch, 0.75 * inch, 1.2 * inch, 1.25 * inch]))
st.append(table([["Claim", "Evidence", "Status"],
                 ["H1. A valid signature on each article does not reduce acceptance of the planted claim.", "4.1", "no reduction detected on six models"],
                 ["H2. A valid signature or verified publisher raises acceptance compared with no provenance.", "4.1, Table A6", "not testable on answers (baseline at ceiling); no change in stated confidence"],
                 ["H3. Showing the controlling owner reduces acceptance when one owner is behind all five outlets, and does not reduce it when five owners are.", "4.2", "first half held on Opus 5.5, in part on GPT-5.5 and Sonnet 5.5 (10 fewer planted answers each, p = 0.002, which does not pass the corrected threshold), not on the other three; second half run on GPT-5.4 mini only (38 of 40 planted, as at baseline)"],
                 ["H4. The origin count tool (the ownership note) reduces acceptance further, and its \"unknown\" output reduces acceptance even when ownership is not attested.", "4.2, 4.4", "first half not supported; second half confounded with the abstain instruction, with which five of six models mostly declined to pick (Table A10); without the instruction the unknown note produced no reduction on the five models that ran it (Table A13)"],
                 ["Exploratory. Models that keep the planted answer report the single origin.", "4.3", "GPT-5.4 and Sonnet 5.5 mostly, under the answer-first prompt; on both it mostly goes away with permission to abstain or reasoning first, and on Sonnet 5.5 also on the second article set; GPT-5.4 mini in a minority of answers"],
                 ["Exploratory. An instruction to count origins costs answers on separately owned sources.", "4.4", "abstain instruction: GPT-5.4, Haiku 5.5, GPT-5.4 mini; majority instruction: no model, with attested ownership"],
                 ["Exploratory. A provenance line on one side only changes the answer.", "4.1", "with \"no manifest found\" on the five: three models strongly; with the five blank: Opus 5.5 only"],
                 ["Exploratory. The harness merge moves models to the dissenting answer at no cost on separately owned sources.", "4.5", "five models (three source orders on four of them); costs Opus 5.5 answers under partial ownership; GPT-5.4 mini follows the first-listed article"],
                 ["Exploratory. Outcomes repeat on a second ask.", "4.8", "92% to 93% of pairs on four models"]],
                "Table A2. Status of the hypotheses written before the first run (wording as in the README) and of the exploratory claims.", colw=[3.0 * inch, 0.9 * inch, 2.6 * inch]))


def passes(mk, cn):
    g = grp(mk, cn)
    return f"{sum(r['outcome_first'] == 'planted' for r in g)} to {c(mk, cn)}" if sum(r['outcome_first'] == 'planted' for r in g) != c(mk, cn) else str(c(mk, cn))


st.append(gtable(grid([("row", lab, (lambda m, cn=cn: passes(m, cn))) for lab, cn in [("1 outlet. No provenance", "none1"), ("1 outlet. Owner line: one owner", "owner1"), ("2 outlets. No provenance", "none2"), ("2 outlets. Note: one owner", "tool2"), ("2 outlets. Harness merge: five owners", "five_merge2")]]), "Table A3. Planted answers out of 40: first scoring pass alone (clean answers only) to final scoring (plus answers the coders read as planted with a caveat). A single number means both agree.", GW))


def wil(mk, cn):
    k, n, z = c(mk, cn), 40, 1.96
    p = k / n
    d = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return f"{k} [{max(0, round(100 * (ctr - h)))},{min(100, round(100 * (ctr + h)))}]"


st.append(gtable(grid([("row", lab, (lambda m, cn=cn: wil(m, cn))) for lab, cn in [("1 outlet. No provenance", "none1"), ("1 outlet. Owner line: one owner", "owner1"), ("1 outlet. Note: one owner", "tool1"), ("2 outlets. No provenance", "none2"), ("2 outlets. Note: one owner", "tool2"), ("2 outlets. Note: one owner + abstain instr.", "toolA2"), ("2 outlets. Note: five owners + abstain instr.", "five_toolA2"), ("2 outlets. Harness merge: one owner", "merge2"), ("2 outlets. Harness merge: five owners", "five_merge2")]]), "Table A4. Planted answers out of 40 with the 95% Wilson interval in percent.", [2.0 * inch] + [0.75 * inch] * 6))
st.append(gtable(grid(T3ROWS), "Table A5. Core conditions: planted / no pick / dissenting, out of 40. Five outlets back the planted answer. Cells with 10 or fewer planted answers are in bold.", GW, heads=(1, 9)))
st.append(table([["Model", "Signature", "Verified publisher", "Owner line, one owner"],
                 ["GPT-5.4 mini", "+1.6 [-0.2, +4.0]", "+1.6 [-0.8, +4.3]", "+1.4 [-0.7, +4.0]"],
                 ["GPT-5.4", "+0.5 [-1.2, +2.2]", "-1.3 [-2.6, +0.1]", "-4.2 [-7.0, -1.7]"],
                 ["GPT-5.5", "0.0 [-0.8, +0.8]", "-0.1 [-0.8, +0.6]", "-25.9 [-29.4, -22.9]"],
                 ["Haiku 5.5", "0.0 [-2.7, +2.5]", "-0.1 [-2.1, +1.8]", "-12.9 [-16.6, -9.4]"],
                 ["Sonnet 5.5", "+1.2 [-1.1, +3.3]", "+1.0 [-1.0, +3.0]", "-28.6 [-30.9, -26.2]"],
                 ["Opus 5.5", "-1.0 [-3.5, +1.2]", "-0.7 [-3.3, +1.8]", "-17.7 [-21.8, -13.5]"]],
                "Table A6. Change in mean stated confidence against no provenance, one dissenting outlet, paired by question. Brackets: 95% bootstrap interval.",
                colw=[1.4 * inch, 1.7 * inch, 1.7 * inch, 1.7 * inch], bold_first_col=True))
CN["merge1_o2"] = ("trusted", "controller", "collusion", False, False, 0, 1, True)
CN["merge1_o3"] = ("trusted", "controller", "collusion", False, False, 0, 2, True)
CN["bare1"] = ("trusted", "bare", "collusion", False, False, 0, 0, "plain")
CN["none0"] = ("silence", "none", "na", False, False, 0, 0, False)
CN["toolA0"] = ("silence", "controller", "collusion", True, True, 2, 0, False)
A5 = [("head", "One dissenting outlet", None)] + rows_for([("Five verified, dissenting article \"no manifest found\"", "vsup_nm"), ("Dissenting article verified, five \"no manifest found\"", "vdis_nm"), ("Note: five owners, no instruction", "five_tool1"), ("Note: one owner + majority instruction", "toolB1"), ("Note: five owners + majority instruction", "five_toolB1"), ("Harness merge: one owner, source order 2", "merge1_o2"), ("Harness merge: one owner, source order 3", "merge1_o3"), ("Same articles as the merge, no note, no provenance", "bare1")]) \
    + [("head", "Two dissenting outlets", None)] + rows_for([("Note: five owners, no instruction", "five_tool2"), ("Note: one owner + majority instruction", "toolB2"), ("Note: five owners + majority instruction", "five_toolB2"), ("Harness merge: one owner, source order 2", "merge2_o2"), ("Harness merge: one owner, source order 3", "merge2_o3"), ("Same articles as the merge, no note, no provenance", "bare2")])
st.append(gtable(grid(A5), "Table A7. Controls 1 (14 conditions). GPT-5.5 ran five of these.", GW, heads=(1, 10)))
A6 = [("head", "One dissenting outlet", None)] + rows_for([("Dissenting article verified, five left blank", "vdis_blank"), ("Dissenting article signed only, five left blank", "sdis_blank"), ("Five verified, dissenting article left blank", "vsup_blank"), ("No provenance + permission to abstain", "none1_permit"), ("Note: one owner + permission to abstain", "tool1_permit"), ("Owner line: one owner, owner names swapped", "owner1_swap")], CL3) \
    + [("head", "Two dissenting outlets", None)] + rows_for([("No provenance + permission to abstain", "none2_permit"), ("Note: one owner + permission to abstain", "tool2_permit"), ("Note: one owner, owner names swapped", "tool2_swap")], CL3)
st.append(gtable(grid(A6, CL3), "Table A8. Controls 2 (9 conditions), Claude models. Permission to abstain is one sentence added to the neutral system prompt (Appendix C).", GW3, heads=(1, 8)))
A7 = [("head", "Controls 3, main article set, two dissenting outlets unless stated", None)] + rows_for([("Note: one owner, closing sentence removed (one dissenting outlet)", "tool1_noclose"), ("Note: one owner, closing sentence removed", "tool2_noclose"), ("Note: five owners, closing sentence removed", "five_tool2_noclose"), ("No provenance, reasoning before answer", "none2_reorder"), ("Note: one owner, reasoning before answer", "tool2_reorder"), ("Partial ownership (3 + 1 + 1). Note", "mixed_tool2"), ("Partial ownership. Note + majority instruction", "mixed_toolB2"), ("Partial ownership. Harness merge (model reads 3 v 2)", "mixed_merge2")], CL3) \
    + [("head", "Second article set", None)] + rows_for([("No provenance, one dissenting outlet", "none1"), ("No provenance, two dissenting outlets", "none2"), ("Note: one owner, two dissenting outlets", "tool2"), ("Harness merge: one owner, two dissenting outlets", "merge2")], CL3, SET2)
st.append(gtable(grid(A7, CL3), "Table A9. Controls 3 (8 conditions) and the second article set (4 conditions), Claude models.", GW3, heads=(1, 10)))
st.append(gtable(grid(rows_for([("One dissenting outlet. Note: ownership unknown + abstain instruction", "unk1"), ("Two dissenting outlets. Note: ownership unknown + abstain instruction", "unk2"), ("No dissenting outlet. No provenance", "none0"), ("No dissenting outlet. Note: one owner + abstain instruction", "toolA0")])), "Table A10. The four core conditions not in Table A5 or A11.", GW))
st.append(gtable(grid(rows_for([("One dissenting outlet, one owner (model reads 1 v 1)", "merge1"), ("One dissenting outlet, five owners (5 v 1)", "five_merge1"), ("Two dissenting outlets, one owner (1 v 2)", "merge2"), ("Two dissenting outlets, five owners (5 v 2)", "five_merge2")])), "Table A11. Harness merge, all four core conditions. Neutral prompt, no note, no instruction.", GW))
st.append(table([["Check", "What changed", "Consequence"],
                 ["Second article set (Claude models; different writer, consistent details on each side; Table A9)", f"under the note, planted answers fell to {max(c(m, 'tool2', 'planted', SET2) for m in CL3)}/40 or fewer on all three, including Sonnet 5.5 ({q('sonnet', 'tool2')} on the main set); the merge again moved all three", f"the Sonnet 5.5 result depends on the article set; the baseline is also lower there ({q('opus', 'none2', 'planted', SET2)} planted on Opus 5.5 with no provenance)"],
                 ["Second ask (four models)", f"same outcome on {min(100 * REP[m][0] / REP[m][1] for m in ['mini', 'haiku', 'sonnet', 'opus']):.0f}% to {max(100 * REP[m][0] / REP[m][1] for m in ['mini', 'haiku', 'sonnet', 'opus']):.0f}% of question-condition pairs overall, but only {qagree('haiku', 'tool2')}/40 (Haiku 5.5) and {qagree('sonnet', 'tool2')}/40 (Sonnet 5.5) under the note; Sonnet 5.5 planted count {rep2('sonnet', 'tool2')}/40", "counts are stable to about 7/40; single questions less so"],
                 ["Paired exact tests", f"p below 0.0001 for the note on GPT-5.5, Haiku 5.5 and Opus 5.5, for the cost of the abstain instruction on GPT-5.4 and Haiku 5.5, and for merge against note on four models; the Section 4.3 checks have p = {PCTL[0]:.5f} (Sonnet 5.5, permission), {PCTL[1]:.5f} (Sonnet 5.5, reasoning first) and {PCTL[2]:.4f} (Haiku 5.5, permission)", f"the first group passes a Bonferroni threshold of 0.0004 over the 122 tests in the analysis script (which also reports a Holm correction per model), as do other tests there; the Section 4.3 checks were added later, and the Haiku 5.5 one would not pass. Also added later: GPT-5.4 permission and reasoning first (p below 0.0001 each); forged note against its matched baseline, p below 0.0001 (Haiku 5.5), {PNEW['fb_s']:.4f} (Sonnet 5.5), {PNEW['fb_o']:.4f} (Opus 5.5; the last two would not pass a correction); guard sentence against forged note, p below 0.0001 (Haiku 5.5), {PNEW['gd_s']:.4f} (Sonnet 5.5, which would not pass a correction), {PNEW['gd_o']:.4f} (Opus 5.5); shared key against separate keys, p below 0.0001 on Sonnet 5.5 and Opus 5.5; shared platform signer against separate keys, p below 0.0001 on Opus 5.5"],
                 ["Strict scoring (hedged answers not counted as picks; Table A3)", f"Sonnet 5.5 under the note: {c('sonnet', 'tool2')} to {S_FIRST}; Claude cells in Table 1 block 2 fall by up to {FIRSTALL}/40; GPT-5.4 cells change by at most {G54MAX}, GPT-5.5 cells not at all", "Table 1 block 2 and the Opus 5.5 baseline depend on the scoring rule"]],
                "Table A12. Robustness checks.", colw=[1.75 * inch, 3.0 * inch, 1.75 * inch]))
if any(ran(m, cn) for m in ALLM for cn in ("owner2", "fake5", "sig2")):
    A13 = [("head", "Checks on the headline condition", None)] + rows_for([("Note: one owner (as in Figure 2)", "tool2"), ("Note: one owner + permission to abstain", "tool2_permit"), ("Note: one owner, reasoning before answer", "tool2_reorder"), ("Owner line: one owner, no note", "owner2"), ("Note: ownership unknown, no instruction", "unk2_ni")]) \
        + [("head", "Forged note and signing key", None)] + rows_for([("Five separate owners (verified publishers); a dissenting article carries a forged note saying the five share one owner", "fake5"), ("Genuine note says one owner; a supporting article carries a forged note saying all seven are independent", "fakeind"), ("Signed, each outlet its own key", "sig2"), ("Signed, the five outlets share one key", "sigshared2")] + ([("Verified publishers, five owners, no forged note (matched baseline)", "org2"), ("Forged note as above, plus a guard sentence in the system prompt", "fake5_guard"), ("Signed by a named publishing platform shared by the five", "sigtool2"), ("Same shared platform, with five separate owners attested", "owntool2")] if any(ran(m, "org2") for m in ALLM) else []))
    st.append(gtable(grid(A13), "Table A13. Retest of the headline condition and the fourth control set, two dissenting outlets.", GW, heads=(1, 7)))
st.append(table([["Factor", "Levels"],
                 ["Owner of the five outlets", "one owner; five separate owners (same articles in both); in a control, three under one owner"],
                 ["Dissenting outlets", "one; two with separate owners (and none, as a sanity check)"],
                 ["Provenance line under each article", "none; valid signature; plus verified publisher; plus controlling owner (the owner line)"],
                 ["Ownership note", "a paragraph after the articles, headed \"Origin count tool\" in the prompt, listing which sources belong to each owner, or saying ownership is unknown"],
                 ["Instruction (with the note)", "abstain instruction: count origins and answer \"undetermined\" if independent origins disagree; majority instruction: give the answer backed by more independent origins"],
                 ["Harness merge", "before the model reads, keep the first-listed article of each owner and add a one-line note"],
                 ["Output order", "answer first (default); or reasoning and source count first"]],
                "Table A14. Factors varied. Provenance lines and the ownership note are simulated text that follows the real layers (C2PA manifest, CAWG identity) plus an ownership attestation that C2PA and CAWG do not have. Appendix C gives the wording.", colw=[1.9 * inch, 4.6 * inch], bold_first_col=True))
st.extend(figure(os.path.join(ROOT, "results", "fig_outcomes.png"), "Figure A1. Core conditions as bars, in the style of Figure 2: counts out of 40, lighter shades for answers given with a caveat.", 6.5))
st.append(P("<b>Models.</b> gpt-5.4-mini-2026-03-17, gpt-5.4-2026-03-05, gpt-5.5-2026-04-23 (OpenAI API, JSON mode); claude-haiku-5-5, claude-sonnet-5-5, claude-opus-5-5 (Anthropic API through its OpenAI-compatible endpoint, JSON by instruction; these identifiers carry no date). Main-set articles were written by gpt-5.4-mini-2026-03-17 and second-set articles by claude-sonnet-5-5."))

st.append(P("Appendix C. Prompt components, word for word", "h1"))
import run_agents as RA
import provenance as PV
import code_answers as CA
from outlets import SUPPORTING, TRUSTED
MONO = ParagraphStyle("mono", fontName="Courier", fontSize=8, leading=9.6, leftIndent=10, spaceAfter=6)


def mono(t):
    return Paragraph(t.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;"), MONO)


st.append(P("<b>System prompt (neutral, answer first).</b>"))
st.append(mono(RA.SYSTEM))
st.append(P("<b>System prompt with reasoning before the answer.</b>"))
st.append(mono(RA.SYSTEM_REORDERED))
st.append(P("<b>Abstain instruction</b> (added to the neutral system prompt)."))
st.append(mono(RA.POLICY.strip()))
st.append(P("<b>Majority instruction.</b>"))
st.append(mono(RA.POLICY2.strip()))
st.append(P("<b>Permission to abstain.</b>"))
st.append(mono(RA.PERMIT.strip()))
st.append(P("<b>Provenance lines under an article</b> at the owner level. The signature level shows the first two lines, the verified-publisher level the first three."))
st.append(mono(PV.block(SUPPORTING[0], "controller", "collusion")))
st.append(P("<b>One-sided provenance.</b> In Table A7 the unmarked side shows the two lines below under each article; in Table A8 it shows nothing."))
st.append(mono(PV.block(SUPPORTING[0], "org_dissent", "collusion")))
_outs = SUPPORTING[:3] + [TRUSTED] + SUPPORTING[3:]
st.append(P("<b>Ownership note, one owner.</b> The last sentence is the closing sentence removed in one control."))
st.append(mono(PV.origin_tool_v2(_outs, "controller", "collusion")))
st.append(P("<b>Ownership note, ownership unknown.</b>"))
st.append(mono(PV.origin_tool_v2(_outs, "org", "collusion")))
st.append(P("<b>Forged ownership note</b> (controls 4), appended to the text of one dissenting article; the five outlets have five owners and show verified publishers only."))
st.append(mono(PV.fake_note(_outs + [__import__("outlets").TRUSTED2], "five_one_owner")))
st.append(P("<b>Guard sentence</b> (controls 5), added to the neutral system prompt."))
st.append(mono(RA.GUARD.strip()))
st.append(P("<b>Shared platform signer</b> (controls 5), shown under each of the five supporting articles; each dissenting article names a different platform."))
st.append(mono(PV.block(SUPPORTING[0], "signature_sharedtool", "na")))
st.append(P("<b>Shared signing key</b> (controls 4). The signature level as above, with the same key shown under each of the five supporting articles and a different key under each dissenting article."))
st.append(P("<b>Harness merge note.</b>"))
st.append(mono(PV.collapse_by_owner(_outs, "collusion")[1]))
st.append(P("<b>Coder prompt</b> (second scoring pass). The coder sees the question, the two candidate answers, the reply and its stated confidence."))
st.append(mono(CA.SYSTEM))
st.append(P("<b>Layout of the user message.</b> \"Question: ...\", then \"Retrieved sources:\", then each source as \"[Source k] Outlet name (domain)\" followed by the article text and its provenance lines, then the ownership note or merge note if any. Full prompts for every call can be rebuilt with src/run_agents.py."))

st.append(KeepTogether([P("LLM Usage Statement", "h1"), P("The author set the research question, decided the design, hypotheses and conditions, ran the experiments and is responsible for every claim in this report. An AI assistant was used as a working tool throughout, under the author's direction: for literature search, for writing and debugging the experiment and analysis code, for reviewing drafts in the role of independent judges, and for drafting and editing the text. Models from OpenAI and Anthropic were the systems under test, wrote the fictional articles, and labelled ambiguous answers in the second scoring pass. All reported numbers are produced by scripts in the repository and can be regenerated from the cached model answers.")]))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Serif", 10)
    canvas.drawCentredString(letter[0] / 2, 0.6 * inch, str(doc.page))
    canvas.restoreState()


doc.build(st, onFirstPage=footer, onLaterPages=footer)
print("saved", OUT)
