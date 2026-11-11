#!/usr/bin/env python3
"""Optional helper: run generated input files and report crashes."""
from pathlib import Path
import subprocess
import sys

INPUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("inputs")
TARGET = [sys.executable, "calc_buggy.py"]

crashes = []
for path in sorted(INPUT_DIR.glob("*.txt")):
    proc = subprocess.run(TARGET + [str(path)], capture_output=True, text=True)
    if proc.returncode != 0:
        crashes.append((path.name, path.read_text().strip(), proc.stderr.strip().splitlines()[-1]))

print(f"Tested {len(list(INPUT_DIR.glob('*.txt')))} inputs")
print(f"Crashes found: {len(crashes)}")
for name, data, error in crashes[:10]:
    print(f"- {name}: {data!r} -> {error}")
