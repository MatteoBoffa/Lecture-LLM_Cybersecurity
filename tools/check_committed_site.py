"""Verify the prebuilt viewer in `site/` still matches the sources.

`site/` is committed so that `python3 display.py` needs no toolchain. That
convenience has one failure mode: re-recording a lecture without rebuilding,
which would silently serve an old lecture. This catches exactly that.
"""

from __future__ import annotations

import filecmp
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
IMAGE_PATTERN = re.compile(r"images/[A-Za-z0-9_./-]+")


def main() -> None:
    problems = []

    if not (SITE / "index.html").is_file():
        raise SystemExit("site/index.html is missing: run tools/build_site.py.")

    traces = sorted((SITE / "var" / "traces").glob("*.json"))
    if not traces:
        problems.append("site/var/traces/ contains no trace at all.")

    for trace in traces:
        source = ROOT / "var" / "traces" / trace.name
        if not source.is_file():
            problems.append(f"{trace.name} is bundled but no longer exists in var/traces/.")
        elif not filecmp.cmp(trace, source, shallow=False):
            problems.append(
                f"{trace.name} in site/ differs from var/traces/{trace.name}: "
                "the lecture was re-recorded without rebuilding the viewer."
            )

        for name in sorted(set(IMAGE_PATTERN.findall(trace.read_text()))):
            if not (SITE / name).is_file():
                problems.append(f"{trace.name} references {name}, which is not in site/.")

    if problems:
        raise SystemExit(
            "The committed viewer is out of date:\n  - "
            + "\n  - ".join(problems)
            + "\n\nRebuild it with: uv run python tools/build_site.py 01_intro --skip-trace"
        )

    print(f"Committed viewer is current ({len(traces)} trace(s), images all present).")


if __name__ == "__main__":
    main()
