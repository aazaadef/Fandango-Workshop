# Fandango Workshop — Research Artifact

**Paper:** *From Passing Tests to Finding Failures: Teaching Exploratory and Robustness-Oriented Testing with Fuzzing*

Submitted to **IEEE TALE 2026**, Pattaya, Thailand.

## Contents

| File/Folder | Description |
|---|---|
| `Main. Fandango.tex` | Full LaTeX source of the paper (final version) |
| `main.human.tex` | Humanized prose version of the paper |
| `analysis.py` | Python replication script (statistics + figures) |
| `data_pre_questionnaire.csv` | Pre-session self-assessment responses (N=22) |
| `data_post_questionnaire.csv` | Post-session questionnaire responses (N=21) |
| `figures/` | PDF figures used in the paper |

## Reproducing Results

```bash
pip install matplotlib numpy
python analysis.py
```

Outputs Wilcoxon signed-rank test results, effect sizes ($r = |Z|/\sqrt{N}$),
and regenerates the pre/post and perception figures.

## Participants

- N = 22 students enrolled (pre-session)
- N = 21 post-session responses
- N = 20 matched pre/post pairs used in all paired analyses

## Research Questions

- **RQ1:** To what extent does the workshop improve students' self-assessed knowledge and confidence in grammar-based fuzzing and robustness-oriented testing?
- **RQ2:** How do students perceive the workshop in terms of perceived learning, engagement, usability, and cognitive load?
- **RQ3:** What conceptual and practical difficulties do students encounter, and what do they reveal about the challenges of introducing fuzzing in educational contexts?

## Key Results

| Item | Pre | Post | Δ | p | r |
|---|---|---|---|---|---|
| Grammar-fuzz familiarity | 1.60 | 3.65 | +2.05 | < .001 | .877 |
| Random vs. grammar | 1.65 | 3.75 | +2.10 | < .001 | .877 |
| Fuzz familiarity | 1.80 | 3.55 | +1.75 | < .001 | .855 |

## Tool

[Fandango](https://github.com/fandango-fuzzer/fandango) — open-source Python grammar-based fuzzing tool used in the workshop.

## Institution

Universidade da Beira Interior, Covilhã, Portugal  
Supported by FCT project UIDB/50008/2020 and doctoral grant PRT/BD/155023/2023.
