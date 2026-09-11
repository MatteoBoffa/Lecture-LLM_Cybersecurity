"""Build the static bundle of a lecture: the edtrace viewer plus its trace.

The result is a plain directory of files (``site/`` by default) that can be
served by any static host - GitHub Pages, or the little ``serve.py`` that ships
inside the bundle for students who work offline.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from prepare_lecture import publish
from setup_viewer import main as setup_viewer

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "edtrace" / "frontend"
TRACES = "var/traces"
# The viewer resolves image paths relative to the page, so only the files the
# trace actually mentions need to travel with it.
IMAGE_PATTERN = re.compile(r"images/[A-Za-z0-9_./-]+")


def record(lectures: list[str]) -> None:
    """Re-execute the lectures so the bundled trace matches the sources."""
    subprocess.run([sys.executable, "-m", "edtrace.execute", "-m", *lectures], check=True)


def npm(*args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(["npm", f"--prefix={FRONTEND}", *args], check=True, env=env)


def build(out: Path, base: str) -> None:
    """Run the Vite production build straight into ``out``."""
    setup_viewer()

    env = os.environ | {
        "VITE_EDTRACE_BASE_DIR": base,
        "VITE_EDTRACE_DIST_DIR": str(out),
    }
    # outDir sits outside the frontend project, so Vite needs permission to clear it.
    npm("run", "build", "--", "--emptyOutDir", env=env)


def keep_only_requested_traces(out: Path, lectures: list[str]) -> None:
    """Drop scratch traces that the public bundle has no reason to ship."""
    wanted = {f"{lecture}.json" for lecture in lectures}
    for trace in (out / TRACES).glob("*.json"):
        if trace.name not in wanted:
            trace.unlink()


def keep_only_referenced_images(out: Path) -> None:
    """Drop images no bundled trace mentions (the 23 MB unused GIF, mostly)."""
    referenced = set()
    for trace in (out / TRACES).glob("*.json"):
        referenced |= set(IMAGE_PATTERN.findall(trace.read_text()))

    images = out / "images"
    if not images.is_dir():
        return
    for path in images.rglob("*"):
        if path.is_file() and f"images/{path.relative_to(images)}" not in referenced:
            path.unlink()

    # A trace that points at a file we did not ship renders as a broken image.
    missing = sorted(name for name in referenced if not (out / name).is_file())
    if missing:
        raise SystemExit("Trace references images that are not in the bundle: " + ", ".join(missing))
    print(f"Images kept: {len(referenced)}")


def add_landing_redirect(out: Path, primary: str) -> None:
    """Opening the bundle should land on the lecture, not on the trace prompt."""
    index = out / "index.html"
    html = index.read_text()
    redirect = (
        "<script>"
        "if (!new URLSearchParams(location.search).get('trace')) "
        f"location.replace(location.pathname + '?trace={primary}');"
        "</script>"
    )
    index.write_text(html.replace("</head>", f"  {redirect}\n  </head>", 1))


def add_offline_launcher(out: Path, primary: str) -> None:
    """The viewer fetches its trace, so file:// is not enough - ship a server."""
    shutil.copy(Path(__file__).parent / "offline_serve.py", out / "serve.py")
    (out / "README.txt").write_text(
        "LLMs and Cybersecurity - offline copy of the lecture\n"
        "===================================================\n\n"
        "Opening index.html directly does not work: the viewer fetches the trace\n"
        "over HTTP, which a file:// page is not allowed to do. Instead run\n\n"
        "    python3 serve.py\n\n"
        "from this folder. It starts a local web server and opens the lecture in\n"
        f"your browser (http://localhost:8000/?trace={primary}).\n\n"
        "Navigation: right/left arrow step forward/back, shift+arrows step over a\n"
        "call, 'u' steps out, 'N' toggles the instructor notes, 'E' the variable\n"
        "panel, 'A' the reveal animation, 'g' loads another trace.\n\n"
        f"{primary}.pdf, next to this file, is the same lecture as a printable\n"
        "handout (if it was built).\n"
    )


@contextlib.contextmanager
def serving(directory: Path, port: int):
    """Serve `directory` with the same server the offline bundle ships with.

    Using one implementation everywhere means a bundle that passes the check
    here behaves the same on a student's laptop - Range requests for the
    embedded video included.
    """
    server = subprocess.Popen(
        [sys.executable, str(Path(__file__).parent / "offline_serve.py"),
         "--directory", str(directory), "--port", str(port), "--no-browser"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.5)  # give the socket time to come up
        yield
    finally:
        server.terminate()
        server.wait()


@contextlib.contextmanager
def mounted_at_base(out: Path, base: str):
    """Expose the bundle at the URL path it was built for.

    A site built with `--base /Lectures/` asks for `/Lectures/assets/...`, so
    serving `out` at the server root would 404 on every asset.
    """
    prefix = base.strip("/")
    if not prefix:
        yield out, ""
        return
    with tempfile.TemporaryDirectory() as tmp:
        mount = Path(tmp) / prefix
        mount.parent.mkdir(parents=True, exist_ok=True)
        mount.symlink_to(out, target_is_directory=True)
        yield Path(tmp), f"{prefix}/"


def export_pdf(out: Path, base: str, lectures: list[str], port: int) -> None:
    """Render each lecture to a printable handout, served from the built site."""
    with mounted_at_base(out, base) as (root, prefix), serving(root, port):
        for lecture in lectures:
            subprocess.run(
                ["node", "tools/export-pdf.mjs", lecture, f"http://127.0.0.1:{port}/{prefix}"],
                check=True,
                cwd=ROOT,
            )


def check(out: Path, base: str, port: int) -> None:
    """Load the bundle in a real browser and fail on anything a student would see."""
    # Playwright is a publishing dependency (`npm ci` at the repo root), not
    # something a student needs, so its absence skips the check rather than
    # breaking the build.
    if not (ROOT / "node_modules" / "playwright").is_dir():
        print("Skipping browser check: Playwright is not installed (npm ci).")
        return

    with mounted_at_base(out, base) as (root, prefix), serving(root, port):
        subprocess.run(
            ["node", "tools/check-site.mjs", f"http://127.0.0.1:{port}/{prefix}"],
            check=True,
            cwd=ROOT,
        )


def directory_size(path: Path) -> str:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return f"{total / 1e6:.1f} MB"


def assemble(out: Path, base: str, lectures: list[str]) -> None:
    """Produce a complete, self-contained bundle in `out`."""
    build(out, base)
    keep_only_requested_traces(out, lectures)
    keep_only_referenced_images(out)
    add_landing_redirect(out, lectures[0])
    add_offline_launcher(out, lectures[0])


def make_offline_archive(out: Path, lectures: list[str], base: str, port: int, verify: bool) -> Path:
    """Pack a copy that works when served from a server root.

    The hosted site may be built for a subpath (`/Lectures/`), and its absolute
    asset URLs would 404 under the bundle's own `serve.py`. So the archive gets
    its own root-based build rather than a copy of the hosted one.
    """
    if base.strip("/") == "":
        source = out
    else:
        staging = Path(tempfile.mkdtemp()) / "offline"
        assemble(staging, "/", lectures)
        for lecture in lectures:
            handout = out / f"{lecture}.pdf"
            if handout.is_file():
                shutil.copy(handout, staging / handout.name)
        if verify:
            check(staging, "/", port)
        source = staging

    archive = Path(shutil.make_archive(str(out), "zip", root_dir=source))
    shutil.copy(archive, out / f"{lectures[0]}-offline.zip")
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lectures", nargs="*", default=["01_intro"], help="lecture modules to bundle")
    parser.add_argument("--out", default="site", help="output directory (default: site)")
    parser.add_argument("--base", default="/", help="URL path the site is served from, e.g. /Lectures/")
    parser.add_argument("--skip-trace", action="store_true", help="reuse var/traces/*.json instead of re-running the lectures")
    parser.add_argument("--pdf", action="store_true", help="also render a PDF handout per lecture")
    parser.add_argument("--zip", action="store_true", help="also pack the bundle as <out>.zip")
    parser.add_argument("--no-check", action="store_true", help="skip the browser smoke-test of the built bundle")
    parser.add_argument("--port", type=int, default=8123, help="port used while serving the bundle locally")
    args = parser.parse_args()

    os.chdir(ROOT)
    lectures = args.lectures or ["01_intro"]
    out = Path(args.out).resolve()

    if not args.skip_trace:
        record(lectures)
    for lecture in lectures:
        if not Path(TRACES, f"{lecture}.json").is_file():
            raise SystemExit(f"Missing {TRACES}/{lecture}.json - run without --skip-trace to record it.")

    for name in ("var", "images"):
        publish(name)

    assemble(out, args.base, lectures)

    # The handout and the offline archive travel inside the site, so a student
    # who lands on the published URL can download either one.
    if not args.no_check:
        check(out, args.base, args.port)
    if args.pdf:
        export_pdf(out, args.base, lectures, args.port)
        for lecture in lectures:
            shutil.copy(Path("pdf", f"{lecture}.pdf"), out / f"{lecture}.pdf")
    if args.zip:
        archive = make_offline_archive(out, lectures, args.base, args.port, verify=not args.no_check)
        print(f"Offline bundle: {archive.name} ({archive.stat().st_size / 1e6:.1f} MB)")

    print(f"Site: {out}/ ({directory_size(out)}), base={args.base}, lectures={', '.join(lectures)}")


if __name__ == "__main__":
    main()
