#!/usr/bin/env python3
"""Replication script for "Dancing at the Edge Cases: Teaching Grammar-Based
Fuzz Testing with Fandango" (EDUNINE 2027).

Reads only the two CSV files next to it, prints every number reported in the
paper, and regenerates figures/fig_fandango_prepost.pdf and
figures/fig_fandango_perception.pdf.

    pip install numpy scipy matplotlib
    python analysis.py
"""
import csv
import re
from pathlib import Path

import numpy as np
from scipy import stats

BASE = Path(__file__).resolve().parent
PRE_CSV = BASE / "data_pre_questionnaire.csv"
POST_CSV = BASE / "data_post_questionnaire.csv"
FIG_DIR = BASE / "figures"

# Two post-session codes contain typing errors. 1824A has an impossible birth
# month (24); 6702D differs by one digit from an otherwise unmatched pre code.
# Each is mapped to the only pre-session code it can belong to. The analysis is
# also repeated without these corrections (exact matches only).
CODE_CORRECTIONS = {"1824A": "1809A", "6702D": "6708D"}

PRE_ITEMS = [8, 11, 14, 17, 20, 23, 26]
POST_ITEMS = [11, 14, 17, 20, 23, 26, 29]
ITEM_LABELS = ["Fuzz familiarity", "Grammar-fuzz famil.", "CLI confidence",
               "Edge-case underst.", "Auto-test generation",
               "Crash interpretation", "Random vs. grammar"]
PRE_MCQ, POST_MCQ = 29, 32
MCQ_CORRECT = "It generates structured inputs based on predefined rules"

CONSTRUCTS = {
    "Perceived learning": [43, 45, 47, 49, 51],
    "Engagement": [53, 55, 57],
    "Usability": [59, 61],
}
COGNITIVE_LOAD = {
    "Mental effort": 63,
    "Parts confusing": 65,
    "Difficulty appropriate": 67,
}


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))[1:]


def likert(value):
    match = re.match(r"\s*([1-5])", value)
    return int(match.group(1)) if match else None


def code(value, corrected):
    c = value.strip().upper()
    return CODE_CORRECTIONS.get(c, c) if corrected else c


def wilcoxon(diffs, n_pairs):
    """Two-sided Wilcoxon signed-rank test on paired differences.

    Zero differences are discarded and tied absolute differences get
    mid-ranks. The p-value is exact: it enumerates every sign assignment of the
    observed ranks. Z uses the tie-corrected normal approximation and gives the
    effect size r = |Z| / sqrt(N) with N the number of pairs.
    """
    d = np.array([x for x in diffs if x != 0], dtype=float)
    n = len(d)
    ranks = stats.rankdata(np.abs(d))
    w_plus = ranks[d > 0].sum()
    centre = ranks.sum() / 2
    signs = (np.arange(2 ** n)[:, None] >> np.arange(n)) & 1
    w_all = signs @ ranks
    p = np.mean(np.abs(w_all - centre) >= abs(w_plus - centre) - 1e-9)
    _, ties = np.unique(np.abs(d), return_counts=True)
    var = n * (n + 1) * (2 * n + 1) / 24 - (ties ** 3 - ties).sum() / 48
    z = (w_plus - n * (n + 1) / 4) / np.sqrt(var)
    return p, z, abs(z) / np.sqrt(n_pairs)


def cronbach_alpha(matrix):
    m = np.asarray(matrix, dtype=float)
    k = m.shape[1]
    return k / (k - 1) * (1 - m.var(axis=0, ddof=1).sum() / m.sum(axis=1).var(ddof=1))


def fmt_p(p):
    return "<.001" if p < 0.001 else f"{p:.3f}".lstrip("0")


pre_rows, post_rows = read_rows(PRE_CSV), read_rows(POST_CSV)
print(f"Responses: {len(pre_rows)} pre-session, {len(post_rows)} post-session")


def matched_pairs(corrected):
    pre = {code(r[5], corrected): r for r in pre_rows}
    post = {code(r[8], corrected): r for r in post_rows}
    keys = sorted(set(pre) & set(post))
    return [(pre[k], post[k]) for k in keys], sorted(set(pre) - set(post))


# ---------------------------------------------------------------- RQ1, Table I
for corrected in (True, False):
    pairs, pre_only = matched_pairs(corrected)
    title = "with code corrections" if corrected else "exact code matches only"
    print(f"\nTable I -- pre/post self-assessment, N = {len(pairs)} ({title})")
    print(f"  pre-session only: {pre_only}")
    print(f"  {'Item':22s} {'Pre':>5s} {'Post':>5s} {'Delta':>6s} {'up/=/down':>10s} {'p':>6s} {'Z':>6s} {'r':>5s}")
    for label, pre_col, post_col in zip(ITEM_LABELS, PRE_ITEMS, POST_ITEMS):
        pre_v = np.array([likert(a[pre_col]) for a, _ in pairs])
        post_v = np.array([likert(b[post_col]) for _, b in pairs])
        diffs = post_v - pre_v
        p, z, r = wilcoxon(diffs, len(pairs))
        moves = f"{(diffs > 0).sum()}/{(diffs == 0).sum()}/{(diffs < 0).sum()}"
        print(f"  {label:22s} {pre_v.mean():5.2f} {post_v.mean():5.2f} {diffs.mean():+6.2f} "
              f"{moves:>10s} {fmt_p(p):>6s} {z:6.3f} {r:5.3f}")

# ----------------------------------------------------------------------- MCQ
print("\nKnowledge item (MCQ): 'Which statement best describes grammar-based fuzzing?'")
pre_ok = [r[PRE_MCQ] == MCQ_CORRECT for r in pre_rows]
post_ok = [r[POST_MCQ] == MCQ_CORRECT for r in post_rows]
print(f"  all respondents: pre {sum(pre_ok)}/{len(pre_ok)}, post {sum(post_ok)}/{len(post_ok)} correct")
pairs, _ = matched_pairs(corrected=True)
before = [a[PRE_MCQ] == MCQ_CORRECT for a, _ in pairs]
after = [b[POST_MCQ] == MCQ_CORRECT for _, b in pairs]
lost = [b[POST_MCQ] for (a, b), x, y in zip(pairs, before, after) if x and not y]
gained = sum((not x) and y for x, y in zip(before, after))
mcnemar_p = stats.binomtest(min(len(lost), gained), len(lost) + gained, 0.5).pvalue
print(f"  matched N = {len(pairs)}: pre {sum(before)} -> post {sum(after)} correct; "
      f"right->wrong {len(lost)}, wrong->right {gained}; exact McNemar p = {mcnemar_p:.3f}")
print(f"  answers chosen by those who switched to a wrong answer: {sorted(lost)}")

# ---------------------------------------------------------- RQ2, Table II
print(f"\nTable II -- post-session perception, N = {len(post_rows)}")
results = {}
for name, cols in CONSTRUCTS.items():
    m = np.array([[likert(r[c]) for c in cols] for r in post_rows])
    agree = np.mean([(m[:, j] >= 4).mean() for j in range(m.shape[1])])
    results[name] = m.mean()
    print(f"  {name:24s} ({len(cols)} items) mean {m.mean():.2f}  agree {100*agree:3.0f}%  "
          f"alpha {cronbach_alpha(m):.3f}")
cl = np.array([[likert(r[c]) for c in COGNITIVE_LOAD.values()] for r in post_rows])
print(f"  Cognitive load: alpha {cronbach_alpha(cl):.2f} -> items reported separately")
for j, name in enumerate(COGNITIVE_LOAD):
    results[name] = cl[:, j].mean()
    print(f"    {name:22s} mean {cl[:, j].mean():.2f}  agree {100*(cl[:, j] >= 4).mean():3.0f}%")

# ------------------------------------------------------------------- figures
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

# IEEE conference template: "Use 8 point Times New Roman for Figure labels" and
# words rather than abbreviations in axis labels. Figures are drawn at the
# 3.5-inch column width so LaTeX does not rescale the text. TrueType (Type 42)
# fonts, because IEEE PDF eXpress rejects Type 3 fonts.
matplotlib.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "hatch.linewidth": 0.6,
})
COLUMN_WIDTH = 3.5  # inches
PRE_COLOR, POST_COLOR = "#4472C4", "#ED7D31"

FIG_DIR.mkdir(exist_ok=True)

# Fig. 2: pre/post self-assessment, one row per Likert item.
pre_means = np.array([np.mean([likert(a[c]) for a, _ in pairs]) for c in PRE_ITEMS])
post_means = np.array([np.mean([likert(b[c]) for _, b in pairs]) for c in POST_ITEMS])
item_labels = ["Fuzz testing familiarity", "Grammar-based fuzzing familiarity",
               "Command-line confidence", "Edge-case understanding",
               "Automated test generation", "Crash interpretation",
               "Random versus grammar-based"]
y = np.arange(len(item_labels))
fig, ax = plt.subplots(figsize=(COLUMN_WIDTH, 1.75), layout="constrained")
h = 0.38
ax.barh(y - h / 2, pre_means - 1, h, left=1, color=PRE_COLOR, label="Before the workshop")
ax.barh(y + h / 2, post_means - 1, h, left=1, color=POST_COLOR, label="After the workshop")
ax.set_yticks(y, item_labels)
ax.invert_yaxis()
ax.set_xlim(1, 5)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xlabel("Mean self-rating (1–5)")
ax.tick_params(axis="y", length=0)
ax.spines[["top", "right"]].set_visible(False)
fig.legend(loc="outside upper center", ncol=2, frameon=False, handlelength=1.2, columnspacing=1.5)
fig.savefig(FIG_DIR / "fig_fandango_prepost.pdf")
plt.close(fig)

# Fig. 3: post-session constructs, then the three cognitive-load items.
labels = ["Perceived learning", "Engagement", "Usability",
          "Mental effort", "Parts confusing", "Difficulty appropriate"]
values = np.array([results[k] for k in list(CONSTRUCTS) + list(COGNITIVE_LOAD)])
ypos = np.array([0, 1, 2, 3.35, 4.35, 5.35])
CL_COLOR, CL_HATCH = "#D0D0D0", "#606060"
colors = [PRE_COLOR, POST_COLOR, "#70AD47"] + [CL_COLOR] * 3
fig, ax = plt.subplots(figsize=(COLUMN_WIDTH, 1.75), layout="constrained")
bars = ax.barh(ypos, values - 1, 0.62, left=1, color=colors)
for bar in bars[3:]:
    bar.set_hatch("////")
    bar.set_edgecolor(CL_HATCH)
    bar.set_linewidth(0)
for yy, value in zip(ypos, values):
    ax.text(value + 0.05, yy, f"{value:.2f}", va="center", ha="left")
ax.axvline(3, color="gray", linestyle="--", linewidth=0.6)
ax.set_yticks(ypos, labels)
ax.invert_yaxis()
ax.set_xlim(1, 5)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xlabel("Mean rating (1–5)")
ax.tick_params(axis="y", length=0)
ax.spines[["top", "right"]].set_visible(False)
fig.legend(handles=[Patch(facecolor=CL_COLOR, edgecolor=CL_HATCH, hatch="////", linewidth=0,
                          label="Cognitive-load item"),
                    Line2D([0], [0], color="gray", linestyle="--", linewidth=0.6, label="Neutral (3)")],
           loc="outside upper center", ncol=2, frameon=False, handlelength=1.6, columnspacing=1.5)
fig.savefig(FIG_DIR / "fig_fandango_perception.pdf")
plt.close(fig)
print("\nFigures written to figures/")
