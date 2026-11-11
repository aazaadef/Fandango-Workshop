#!/usr/bin/env python3
"""
Tiny target program for a classroom fuzzing demo.
Input format: OP X Y, e.g., ADD 4 5 or DIV 10 0
Intentional bug: DIV by zero is not handled.
"""
import sys


def load_input() -> str:
    if len(sys.argv) > 1:
        with open(sys.argv[-1], "r", encoding="utf-8") as f:
            return f.read().strip()
    return sys.stdin.read().strip()


def main() -> None:
    data = load_input()
    parts = data.split()
    if len(parts) != 3:
        raise ValueError(f"Expected: OP X Y, got: {data!r}")

    op, x_raw, y_raw = parts
    x = int(x_raw)
    y = int(y_raw)

    if op == "ADD":
        result = x + y
    elif op == "SUB":
        result = x - y
    elif op == "MUL":
        result = x * y
    elif op == "DIV":
        # Intentional bug: when y == 0, Python raises ZeroDivisionError.
        result = x / y
    else:
        raise ValueError(f"Unknown operator: {op}")

    print(result)


if __name__ == "__main__":
    main()
