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
matplotlib.rcParams["pdf.fonttype"] = 42  # IEEE PDF eXpress rejects Type 3 fonts
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt  # noqa: E402

FIG_DIR.mkdir(exist_ok=True)
pre_means = [np.mean([likert(a[c]) for a, _ in pairs]) for c in PRE_ITEMS]
post_means = [np.mean([likert(b[c]) for _, b in pairs]) for c in POST_ITEMS]
short = ["Fuzz\nfamil.", "Grammar\nfamil.", "CLI\nconf.", "Edge\ncase",
         "Auto\ngen.", "Crash\ninterp.", "Rand. vs\ngrammar"]
x = np.arange(len(short))
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.bar(x - 0.2, pre_means, 0.35, label="Pre", color="#4472C4", alpha=0.85)
ax.bar(x + 0.2, post_means, 0.35, label="Post", color="#ED7D31", alpha=0.85)
ax.set_ylabel("Mean Likert (1-5)")
ax.set_ylim(1, 5.5)
ax.set_title(f"Fandango: Pre/Post Self-Assessment (N = {len(pairs)})")
ax.set_xticks(x)
ax.set_xticklabels(short, fontsize=7)
ax.axhline(3, color="gray", linestyle="--", linewidth=0.7, alpha=0.5)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(FIG_DIR / "fig_fandango_prepost.pdf", bbox_inches="tight")
plt.close(fig)

labels = ["Perceived\nlearning", "Engagement", "Usability",
          "CL: mental\neffort", "CL: parts\nconfusing", "CL: difficulty\nappropriate"]
values = [results[k] for k in list(CONSTRUCTS) + list(COGNITIVE_LOAD)]
colors = ["#4472C4", "#ED7D31", "#70AD47", "#A5A5A5", "#A5A5A5", "#A5A5A5"]
fig, ax = plt.subplots(figsize=(6, 3.2))
bars = ax.bar(labels, values, color=colors, alpha=0.85, width=0.6)
for bar, value in zip(bars[3:], values[3:]):
    bar.set_hatch("//")
ax.axhline(3, color="gray", linestyle="--", linewidth=0.8, alpha=0.6, label="Neutral (3)")
ax.set_ylim(1, 5)
ax.set_ylabel("Mean score (1-5)", fontsize=9)
ax.set_title(f"Post-Session Student Perception (N = {len(post_rows)})", fontsize=10, fontweight="bold")
ax.tick_params(axis="x", labelsize=7.5)
for bar, value in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, value + 0.05, f"{value:.2f}",
            ha="center", va="bottom", fontsize=8.5, fontweight="bold")
ax.legend(fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG_DIR / "fig_fandango_perception.pdf", bbox_inches="tight")
plt.close(fig)
print("\nFigures written to figures/")
