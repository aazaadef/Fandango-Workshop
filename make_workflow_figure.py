#!/usr/bin/env python3
"""Draws figures/fig_fandango_workflow.pdf (Fig. 1, the four workshop phases)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42  # IEEE PDF eXpress rejects Type 3 fonts
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import to_rgba  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

PHASES = [
    ("Phase 1\n(20 min)", "Conceptual\nIntroduction",
     "Random vs.\ngrammar fuzzing;\nFandango syntax", "#4472C4"),
    ("Phase 2\n(15 min)", "Live Demo\n& Setup",
     "Instructor runs buggy\ncalc + grammar;\nstudents install via Drive", "#ED7D31"),
    ("Phase 3\n(45 min)", "Guided\nReplication",
     "Students run provided\ncode, .fan file, .md\n→ observe crashes", "#70AD47"),
    ("Phase 4\n(20 min)", "Extension\n& Reflection",
     "Add bugs or write\nnew program;\npost-questionnaire", "#7030A0"),
]

fig = plt.figure(figsize=(6.6, 2.6))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

width, gap, left = 0.215, 0.032, 0.0185
bottom, height = 0.06, 0.88
for i, (phase, title, desc, color) in enumerate(PHASES):
    x = left + i * (width + gap)
    ax.add_patch(FancyBboxPatch((x, bottom), width, height,
                                boxstyle="round,pad=0,rounding_size=0.012",
                                facecolor=to_rgba(color, 0.15), edgecolor="none"))
    cx = x + width / 2
    ax.text(cx, bottom + height - 0.08, phase, ha="center", va="top",
            fontsize=7, fontweight="bold", color=color, linespacing=1.1)
    ax.text(cx, bottom + height - 0.30, title, ha="center", va="top",
            fontsize=8, fontweight="bold", color="#222222", linespacing=1.1)
    ax.text(cx, bottom + 0.33, desc, ha="center", va="center",
            fontsize=6.8, color="#444444", linespacing=1.3)
    if i < len(PHASES) - 1:
        ax.annotate("", xy=(x + width + gap - 0.004, 0.5), xytext=(x + width + 0.004, 0.5),
                    arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.6,
                                    shrinkA=0, shrinkB=0, mutation_scale=9))

out = Path(__file__).resolve().parent / "figures" / "fig_fandango_workflow.pdf"
out.parent.mkdir(exist_ok=True)
fig.savefig(out)
print(f"wrote {out}")
