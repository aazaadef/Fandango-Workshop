#!/usr/bin/env python3
"""
Replication Analysis Script
Paper: From Passing Tests to Finding Failures:
       Teaching Exploratory and Robustness-Oriented Testing with Fuzzing

Usage:
  pip install matplotlib numpy
  python analysis.py
"""

import csv, math
from pathlib import Path

BASE = Path(__file__).resolve().parent
PRE_CSV  = BASE / "data_pre_questionnaire.csv"
POST_CSV = BASE / "data_post_questionnaire.csv"
FIG_DIR  = BASE / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Normalize participant codes (typos)
def normalize(code):
    code = code.strip().upper()
    if code == '6702D': return '6708D'
    if code == '1824A': return '1809A'
    return code

# Likert item columns
PRE_LIKERT  = [8, 11, 14, 17, 20, 23, 26]   # 7 items
POST_LIKERT = [11, 14, 17, 20, 23, 26, 29]  # 7 items

LABELS = ['Fuzz familiarity', 'Grammar-fuzz famil.', 'CLI confidence',
          'Edge-case underst.', 'Auto-test generation',
          'Crash interpretation', 'Random vs. grammar']

def parse_l(v):
    for i in range(1, 6):
        if v.strip().startswith(str(i)): return i
    return None

def mean(v): return sum(v)/len(v) if v else 0

def wilcoxon(diffs):
    nonzero = [(abs(d), 1 if d>0 else -1) for d in diffs if d!=0]
    n = len(nonzero)
    if n < 3: return None, None, None
    nonzero.sort(key=lambda x: x[0])
    ranks = []
    i = 0
    while i < n:
        j = i
        while j < n and nonzero[j][0] == nonzero[i][0]: j += 1
        avg = (i+1+j)/2
        for k in range(i,j): ranks.append((avg, nonzero[k][1]))
        i = j
    W_plus = sum(r for r,s in ranks if s>0)
    mW = n*(n+1)/4
    sW = math.sqrt(n*(n+1)*(2*n+1)/24)
    Z = (W_plus - mW)/sW if sW > 0 else 0
    a1,a2,a3,a4,a5 = 0.254829592,-0.284496736,1.421413741,-1.453152027,1.061405429
    pp = 0.3275911
    t_ = 1.0/(1.0+pp*abs(Z))
    cdf = 1.0-(((((a5*t_+a4)*t_)+a3)*t_+a2)*t_+a1)*t_*math.exp(-Z*Z/2)
    p = 2*(1-cdf)
    N = len(diffs)
    r = abs(Z)/math.sqrt(N)
    return round(Z,3), round(p,4), round(r,3)

# Load data
pre_rows  = list(csv.reader(open(PRE_CSV,  encoding='utf-8')))
post_rows = list(csv.reader(open(POST_CSV, encoding='utf-8')))

pre_data  = {}
for r in pre_rows[1:]:
    code = normalize(r[5])
    if not code: continue
    pre_data[code] = [parse_l(r[c]) for c in PRE_LIKERT]

post_data = {}
for r in post_rows[1:]:
    code = normalize(r[8])
    if not code: continue
    post_data[code] = [parse_l(r[c]) for c in POST_LIKERT]

matched = sorted(set(pre_data) & set(post_data))
N = len(matched)

# ---------------------------------------------------------------------------
print("=" * 60)
print("FANDANGO WORKSHOP — PRE/POST LIKERT ANALYSIS")
print("=" * 60)
print(f"N matched: {N}")
print(f"\n{'Item':<25} {'Pre':>5} {'Post':>5} {'Δ':>6}  {'↑':>3}/{'=':>3}/{'↓':>3}  Z      p      r")
print("-"*78)

for i, label in enumerate(LABELS):
    pv = [pre_data[c][i]  for c in matched if pre_data[c][i] and post_data[c][i]]
    qv = [post_data[c][i] for c in matched if pre_data[c][i] and post_data[c][i]]
    dv = [qv[j]-pv[j] for j in range(len(pv))]
    up, same, down = sum(1 for d in dv if d>0), sum(1 for d in dv if d==0), sum(1 for d in dv if d<0)
    Z, p, r = wilcoxon(dv)
    print(f"{label:<25} {mean(pv):>5.2f} {mean(qv):>5.2f} {mean(dv):>+6.2f}  "
          f"{up:>3}/{same:>3}/{down:>3}  {Z}  {p}  {r}")

# Post-session perception
print("\n" + "=" * 60)
print("POST-SESSION PERCEPTION")
print("=" * 60)
constructs = {
    'Perceived Learning': [43,45,47,49,51],
    'Engagement':         [53,55,57],
    'Usability':          [59,61],
    'Cognitive Load':     [63,65,67],
}
for cname, cols in constructs.items():
    all_vals = []
    for r in post_rows[1:]:
        row_vals = [parse_l(r[c]) for c in cols]
        if all(row_vals): all_vals.append(row_vals)
    flat = [v for row in all_vals for v in row]
    construct_mean = mean([mean([row[j] for row in all_vals]) for j in range(len(cols))])
    pct = sum(1 for v in flat if v >= 4)/len(flat)*100 if flat else 0
    print(f"  {cname:<20}: mean={construct_mean:.2f}  %agree(4+5)={pct:.0f}%")

# Generate figures
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    # Pre/post Likert bar chart
    pre_means  = [mean([pre_data[c][i]  for c in matched if pre_data[c][i]])  for i in range(7)]
    post_means = [mean([post_data[c][i] for c in matched if post_data[c][i]]) for i in range(7)]

    short_labels = ["Fuzz\nfamil.", "Grammar\nfamil.", "CLI\nconf.",
                    "Edge\ncase", "Auto\ngen.", "Crash\ninterp.", "Rand. vs\ngrammar"]
    x = range(7)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar([i-0.2 for i in x], pre_means,  0.35, label="Pre",  color="#4472C4", alpha=0.85)
    ax.bar([i+0.2 for i in x], post_means, 0.35, label="Post", color="#ED7D31", alpha=0.85)
    ax.set_ylabel("Mean Score (1–5)"); ax.set_ylim(1, 5.5)
    ax.set_title("Fandango: Pre/Post Self-Assessment")
    ax.set_xticks(list(x)); ax.set_xticklabels(short_labels, fontsize=7)
    ax.axhline(y=3, color='gray', linestyle='--', linewidth=0.7, alpha=0.5)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig_fandango_prepost.pdf", dpi=300, bbox_inches="tight")
    plt.close()

    # Perception bar chart
    constructs_plot = ['Perceived\nLearning', 'Engagement', 'Usability', 'Cognitive\nLoad']
    means_plot = [3.73, 3.87, 3.90, 3.32]
    colors = ['#4472C4', '#ED7D31', '#70AD47', '#A5A5A5']
    fig, ax = plt.subplots(figsize=(5, 3.2))
    bars = ax.bar(constructs_plot, means_plot, color=colors, alpha=0.85, width=0.55)
    ax.axhline(y=3, color='gray', linestyle='--', linewidth=0.8, alpha=0.6, label='Neutral (3)')
    ax.set_ylim(1, 5); ax.set_ylabel('Mean Score (1–5)', fontsize=9)
    ax.set_title('Post-Session Student Perception', fontsize=10, fontweight='bold')
    for bar, val in zip(bars, means_plot):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.05, f'{val:.2f}',
                ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax.legend(fontsize=8)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fig_fandango_perception.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    print("\nFigures saved to figures/")
except ImportError:
    print("\nmatplotlib not installed — skip figures. Run: pip install matplotlib numpy")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
