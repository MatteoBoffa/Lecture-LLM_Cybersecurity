"""Fail if a document links to a file that is not in the repository.

Written after three links at the top of the README turned out to be 404s: a
reader's first click is the first thing that has to work.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", *(str(p.relative_to(ROOT)) for p in (*(ROOT / "docs").glob("*.md"), *(ROOT / "labs").rglob("*.md")))]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def main() -> None:
    problems = []
    for name in DOCS:
        document = ROOT / name
        if not document.is_file():
            continue
        for target in LINK.findall(document.read_text()):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = (document.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                problems.append(f"{name} links to {target}, which does not exist")

    if problems:
        raise SystemExit("Dead links:\n  - " + "\n  - ".join(problems))
    print(f"All relative links in {len(DOCS)} document(s) resolve.")


if __name__ == "__main__":
    main()
