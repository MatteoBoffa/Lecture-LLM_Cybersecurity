#!/usr/bin/env python3
"""Show the lecture. Nothing to install.

    python3 display.py

Opens the lecture in your browser, served from the prebuilt viewer in `site/`.
This needs no uv, no Node, no virtual environment and no network - only a
Python 3 interpreter, which macOS and Linux already have.

Use the lecture with the arrow keys: see README.md, or press Shift+N in the
page for the instructor notes.
"""

import argparse
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
LECTURE = "01_intro"

sys.path.insert(0, str(ROOT / "tools"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Show the lecture in a browser.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--lecture", default=LECTURE, help="trace to open (default: %(default)s)")
    args = parser.parse_args()

    if not (SITE / "index.html").is_file():
        raise SystemExit(
            f"The prebuilt lecture is missing from {SITE}/.\n"
            "It ships with the repository, so this usually means the clone was\n"
            "incomplete. Re-clone it, or rebuild the viewer with:\n"
            "    uv run python tools/build_site.py 01_intro --skip-trace"
        )

    import socketserver

    from offline_serve import Handler  # the server the offline bundle ships with

    Handler.directory_override = SITE
    socketserver.TCPServer.allow_reuse_address = True
    try:
        server = socketserver.ThreadingTCPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        raise SystemExit(
            f"Could not open port {args.port}: {error}.\n"
            f"Something else is using it - try: python3 display.py --port {args.port + 1}"
        )

    url = f"http://localhost:{args.port}/?trace={args.lecture}"
    print(f"\n  The lecture is at {url}")
    print("  Arrow keys step through it. Press Ctrl+C here to stop.\n")
    if not args.no_browser:
        webbrowser.open(url)
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Stopped.")


if __name__ == "__main__":
    main()
