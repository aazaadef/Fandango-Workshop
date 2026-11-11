# Fandango classroom fuzzing demo

## 1) Install and verify

```bash
python -m pip install fandango-fuzzer
fandango --help
```

## 2) Generate sample inputs

```bash
fandango fuzz -f calc.fan -n 20
```

## 3) Execute the target through Fandango

Default mode: Fandango writes each generated input to a temporary file and passes the file name as the last command-line argument.

```bash
fandango fuzz -f calc.fan -n 100 python calc_buggy.py
```

Alternative stdin mode:

```bash
fandango fuzz -f calc.fan -n 100 --input-method=stdin python calc_buggy.py
```

## 4) Very reliable classroom fallback

Generate individual input files, then run them through the helper script.

```bash
fandango fuzz -f calc.fan -n 100 -d inputs
python run_fuzz_directory.py inputs
```

Expected result: at least some generated inputs look like `DIV 7 0`, causing a `ZeroDivisionError` in `calc_buggy.py`.
