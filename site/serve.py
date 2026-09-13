"""Serve a lecture bundle over HTTP.

Inside a bundle this is `serve.py`: run `python3 serve.py` from the folder that
contains index.html.  The viewer fetches its trace over HTTP, so the files
cannot simply be opened from disk.

The build tooling reuses it (`--directory`, `--port`, `--no-browser`) so that
what gets checked locally, in CI, and by students is the same server.
"""

import argparse
import http.server
import os
import re
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
HERE = Path(__file__).resolve().parent
RANGE_HEADER = re.compile(r"bytes=(\d*)-(\d*)")


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static handler that also understands Range requests.

    The lecture embeds an MP4, and browsers request video in ranges; without
    this the request is refused and the clip never plays.
    """

    directory_override = HERE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(self.directory_override), **kwargs)

    def log_message(self, *args):
        pass

    def send_head(self):
        header = self.headers.get("Range")
        match = RANGE_HEADER.fullmatch(header.strip()) if header else None
        if not match:
            return super().send_head()

        path = self.translate_path(self.path)
        try:
            handle = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        size = os.fstat(handle.fileno()).st_size
        first, last = match.groups()
        if first:
            start = int(first)
            end = int(last) if last else size - 1
        else:  # "bytes=-500" means the last 500 bytes
            start, end = max(size - int(last), 0), size - 1
        end = min(end, size - 1)

        if start > end:
            handle.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return None

        self.send_response(206)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        handle.seek(start)
        return _Window(handle, end - start + 1)


class _Window:
    """A read-only view of `length` bytes, which copyfile() can stream."""

    def __init__(self, handle, length):
        self.handle, self.remaining = handle, length

    def read(self, size=-1):
        if self.remaining <= 0:
            return b""
        size = self.remaining if size < 0 else min(size, self.remaining)
        chunk = self.handle.read(size)
        self.remaining -= len(chunk)
        return chunk

    def close(self):
        self.handle.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a lecture bundle.")
    parser.add_argument("--directory", default=str(HERE))
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    Handler.directory_override = Path(args.directory).resolve()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), Handler) as server:
        url = f"http://localhost:{args.port}/"
        print(f"Serving the lecture at {url} - press Ctrl+C to stop.", flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
