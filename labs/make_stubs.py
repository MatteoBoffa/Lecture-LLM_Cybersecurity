#!/usr/bin/env python3
"""Derive the students' notebooks from the solutions.

The solution notebooks are the source of truth.  A cell marks the part the
student is meant to write like this:

    ### TODO: keep the label of the first token of each word
    ### BEGIN SOLUTION
    pairs = ...
    ### END SOLUTION

Here we strip the answer, keep the hints, and leave a `raise NotImplementedError`
at the same indentation, so the stub still parses and fails loudly when run.
Outputs are cleared too - a student should see their own.

    uv run python labs/make_stubs.py
"""

import json
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parent
BEGIN, END = "### BEGIN SOLUTION", "### END SOLUTION"


def strip(source: str) -> str:
    out, skipping = [], False
    for line in source.splitlines():
        stripped = line.strip()
        if stripped == BEGIN:
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f'{indent}raise NotImplementedError("your turn")')
            skipping = True
        elif stripped == END:
            skipping = False
        elif skipping:
            continue
        elif stripped.startswith("###"):          # a hint, or its continuation lines
            out.append(line.replace("###", "#", 1))
        else:
            out.append(line)
    return "\n".join(out)


def main() -> int:
    written = 0
    for solution in sorted(LABS.glob("*/solutions/*.ipynb")):
        nb = json.loads(solution.read_text())
        for cell in nb["cells"]:
            cell["metadata"].pop("execution", None)  # when the solution was last run
            if cell["cell_type"] != "code":
                continue
            cell["outputs"], cell["execution_count"] = [], None
            cell["source"] = strip("".join(cell["source"])).splitlines(keepends=True)
        target = solution.parent.parent / solution.name
        target.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
        print(f"{solution.relative_to(LABS)} -> {target.relative_to(LABS)}")
        written += 1
    if not written:
        print("no solution notebooks found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
