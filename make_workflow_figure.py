#!/usr/bin/env python3
"""Draws figures/fig_fandango_workflow.pdf (Fig. 1, the four workshop phases).

Follows the IEEE conference template: 8-point Times New Roman, drawn at the
3.5-inch column width so LaTeX does not rescale the text. TrueType (Type 42)
fonts, because IEEE PDF eXpress rejects Type 3 fonts.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams.update({
    "pdf.fonttype": 42,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "font.size": 8,
})
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import to_rgba  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

PHASES = [
    ("Phase 1\n20 min", "Conceptual\nIntroduction",
     "Random vs.\ngrammar-based\nfuzzing;\nFandango\nsyntax", "#4472C4"),
    ("Phase 2\n15 min", "Live Demo\n& Setup",
     "Instructor\nfuzzes a buggy\ncalculator;\nstudents install\nvia Drive", "#ED7D31"),
    ("Phase 3\n45 min", "Guided\nReplication",
     "Students run\nthe code, .fan\ngrammar and\n.md guide;\nobserve crashes", "#70AD47"),
    ("Phase 4\n20 min", "Extension\n& Reflection",
     "Add bugs or\nwrite a new\nprogram;\npost-\nquestionnaire", "#7030A0"),
]

W, H = 252.0, 104.0  # figure size in points (3.5 in wide)
BOX_GAP, PAD = 11.0, 3.0
BOX_W = (W - 3 * BOX_GAP) / 4
LINE = 8 * 1.12  # line height in points

fig = plt.figure(figsize=(W / 72, H / 72))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

texts = []
for i, (phase, title, desc, color) in enumerate(PHASES):
    x = i * (BOX_W + BOX_GAP)
    ax.add_patch(FancyBboxPatch((x, 0.5), BOX_W, H - 1, boxstyle="round,pad=0,rounding_size=3",
                                facecolor=to_rgba(color, 0.15), edgecolor="none"))
    # One text object per line on a fixed baseline, so lines align across boxes.
    cx, baseline = x + BOX_W / 2, H - PAD - 1 - 6.5
    for block, weight, shade, space_after in ((phase, "bold", color, 3),
                                               (title, "bold", "#222222", 4),
                                               (desc, "normal", "#333333", 0)):
        for line in block.split("\n"):
            texts.append((x, ax.text(cx, baseline, line, ha="center", va="baseline",
                                     fontweight=weight, color=shade)))
            baseline -= LINE
        baseline -= space_after
    if i < len(PHASES) - 1:
        ax.annotate("", xy=(x + BOX_W + BOX_GAP - 1, H / 2), xytext=(x + BOX_W + 1, H / 2),
                    arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.0,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))

# Every line of text must fit inside its box.
renderer = fig.canvas.get_renderer()
to_points = ax.transData.inverted()
for x, text in texts:
    (x0, y0), (x1, y1) = to_points.transform(text.get_window_extent(renderer).get_points())
    assert x0 >= x + 1 and x1 <= x + BOX_W - 1 and y0 >= 1.5, (text.get_text(), x0, x1, y0)

out = Path(__file__).resolve().parent / "figures" / "fig_fandango_workflow.pdf"
out.parent.mkdir(exist_ok=True)
fig.savefig(out)
print(f"wrote {out}")
