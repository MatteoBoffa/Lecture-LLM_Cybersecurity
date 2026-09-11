"""Bring the edtrace viewer to the state this course expects.

The viewer is an upstream submodule, but the lecture relies on a few local
changes to it (see patches/edtrace-viewer.patch).  Keeping them as a patch
rather than a fork means `git submodule update` still tracks upstream.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBMODULE = ROOT / "edtrace"
FRONTEND = SUBMODULE / "frontend"
PATCH = ROOT / "patches" / "edtrace-viewer.patch"


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, **kwargs)


def applies_cleanly(*flags: str) -> bool:
    """Ask git whether the patch could be applied (or reversed) right now."""
    result = subprocess.run(
        ["git", "apply", "--check", *flags, str(PATCH)],
        cwd=SUBMODULE,
        capture_output=True,
    )
    return result.returncode == 0


def ensure_submodule() -> None:
    if not (FRONTEND / "package.json").is_file():
        print("Fetching the edtrace submodule...")
        run(["git", "submodule", "update", "--init", "--recursive"], cwd=ROOT)


def apply_patch() -> None:
    if not PATCH.is_file():
        return
    if applies_cleanly("--reverse"):
        print("Viewer patch already applied.")
        return
    if not applies_cleanly():
        raise SystemExit(
            f"{PATCH.name} does not apply. Reset the submodule with\n"
            "    git submodule update --force --recursive\n"
            "and run this script again."
        )
    run(["git", "apply", str(PATCH)], cwd=SUBMODULE)
    print(f"Applied {PATCH.name}.")


def install_dependencies() -> None:
    if (FRONTEND / "node_modules").is_dir():
        print("Frontend dependencies already installed.")
        return
    print("Installing frontend dependencies (npm install)...")
    run(["npm", f"--prefix={FRONTEND}", "install"])


def main(install_npm: bool = True) -> None:
    os.chdir(ROOT)
    ensure_submodule()
    apply_patch()
    if install_npm:
        install_dependencies()
    print("Viewer ready.")


if __name__ == "__main__":
    main(install_npm="--no-npm" not in sys.argv)
