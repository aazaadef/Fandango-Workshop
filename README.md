# Fandango Workshop — Research Artifact

**Paper:** *From Passing Tests to Finding Failures: Teaching Exploratory and Robustness-Oriented Testing with Fuzzing*

Submitted to **TALE 2026**.

## Contents

| File/Folder | Description |
|---|---|
| `main.tex` | Full LaTeX source of the paper |
| `analysis.py` | Python replication script (statistics + figures) |
| `data_pre_questionnaire.csv` | Pre-session self-assessment responses (N=21) |
| `data_post_questionnaire.csv` | Post-session questionnaire responses (N=21) |
| `figures/` | PDF figures used in the paper |

## Reproducing Results

```bash
pip install matplotlib numpy
python analysis.py
```

Outputs Wilcoxon signed-rank test results, effect sizes (r = |Z|/√N),
and regenerates the pre/post and perception figures.

## Participant Matching

- N = 20 matched pre/post pairs
- Typo corrections: `6702D` → `6708D`, `1824A` → `1809A`

## Tool

[Fandango](https://fandango-fuzzer.github.io) — grammar-based fuzzing tool used in the workshop.
