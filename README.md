# Dancing at the Edge Cases — Replication Package

**Paper:** "Dancing at the Edge Cases: Teaching Grammar-Based Fuzz Testing with *Fandango*"

Accepted at **IEEE EDUNINE 2027** (World Engineering Education Conference).

## Contents

| File/Folder | Description |
|---|---|
| `main.tex` | LaTeX source of the paper |
| `analysis.py` | Replication script: every statistic in the paper, and Figs. 2–3 |
| `make_workflow_figure.py` | Draws Fig. 1 (the four workshop phases) |
| `data_pre_questionnaire.csv` | Pre-session responses (21 students) |
| `data_post_questionnaire.csv` | Post-session responses (20 students) |
| `figures/` | Figures used in the paper |
| `workshop/` | The materials students received: the buggy calculator (`calc_buggy.py`), its Fandango grammar (`calc.fan`), the step-by-step guide (`README.md`), and an optional helper that runs saved inputs (`run_fuzz_directory.py`) |

## Reproducing the results

```bash
pip install numpy scipy matplotlib
python analysis.py
python make_workflow_figure.py
```

`analysis.py` reads only the two CSV files in this directory. It prints the
pre/post self-assessment table (exact two-sided Wilcoxon signed-rank tests,
effect size r = |Z|/√N), the multiple-choice knowledge item (exact McNemar
test), and the post-session constructs with Cronbach's α, then regenerates the
figures.

## Running the workshop

See [`workshop/README.md`](workshop/README.md). It needs Python and
`pip install fandango-fuzzer`; the grammar generates inputs such as `DIV 7 0`
that crash the calculator with a `ZeroDivisionError`. The lecture slides are not
included.

## Participants and matching

- 22 students in the class; 21 completed the pre-session questionnaire and 20 the post-session questionnaire.
- Students linked the two questionnaires with a self-generated code (last two digits of phone number + birth month + first letter of the mother's first name).
- 18 codes match exactly. Two post-session codes contain typing errors and are mapped to their pre-session codes in `analysis.py` (`CODE_CORRECTIONS`), giving 20 matched pairs. The script also reports the analysis with the 18 exact matches only; the conclusions are the same.

## Key results (N = 20 matched pairs)

| Item | Pre | Post | Δ | p | r |
|---|---|---|---|---|---|
| Grammar-fuzz familiarity | 1.60 | 3.65 | +2.05 | < .001 | .888 |
| Random vs. grammar | 1.65 | 3.75 | +2.10 | < .001 | .885 |
| Fuzz familiarity | 1.80 | 3.55 | +1.75 | < .001 | .873 |

The multiple-choice knowledge item did not improve: 18 of 20 answered correctly before the workshop and 15 of 20 afterwards (exact McNemar p = 0.375).

## Privacy

The questionnaire files contain no names, student numbers or e-mail addresses. Free-text answers are released verbatim; some are in Portuguese.

## Tool

[Fandango](https://github.com/fandango-fuzzer/fandango): J. A. Zamudio Amaya, M. Smytzek, and A. Zeller, "FANDANGO: Evolving Language-Based Testing," *Proc. ACM Softw. Eng.* 2(ISSTA), 2025.

## Institution

Universidade da Beira Interior, Covilhã, Portugal.
Supported by FCT project UIDB/50008/2020, doctoral grant PRT/BD/155023/2023, and the Promptme4Better project (Erasmus+, grant agreement 2025-1-PT01-KA220-HED-000363565).
