# Executable lectures, end to end

How to run a course whose lectures are Python programs, from an empty directory
to a URL you hand to students. Written for an instructor adopting the approach,
with the reasoning behind each step rather than only the commands.

This guide is self-contained. The reference implementation is the repository it
lives in: <https://github.com/MatteoBoffa/L-LLM_-_Cybersecurity>.

---

## 0. The mental model

```
01_intro.py  ──edtrace.execute──▶  var/traces/01_intro.json  ──viewer──▶  browser
  the program          records            the recording         replays
```

Three things follow from that arrow, and most confusion comes from missing one:

1. **The recording is the artifact.** Once a lecture has run, everything the
   class sees — values, figures, model output — is frozen in one JSON file. The
   viewer is a React app that replays it. No Python runs while you present.
2. **Publishing means shipping that JSON plus a static build of the viewer.**
   There is no server to deploy, no notebook kernel, nothing to keep alive.
3. **A recording cannot answer a question it was not asked.** Changing an input
   means re-executing the program and recording again. Tell students this
   explicitly, or they will assume the page is live.

You end up maintaining two deliverables: the **live viewer** you drive in class,
and the **published recording** students keep.

---

## 1. One-time course setup

Prerequisites: **Git**, **[uv](https://docs.astral.sh/uv/getting-started/installation/)**,
**Node.js LTS**. One setup per *course*, not per lecture.

```bash
uv init && git init
uv add edtrace                                  # pulls PyTorch: large first download

git submodule add https://github.com/percyliang/edtrace.git edtrace
git config -f .gitmodules submodule.edtrace.ignore dirty
npm ci --prefix edtrace/frontend

npm init -y && npm install -D playwright        # for the PDF handout
npx playwright install chromium                 # Linux: --with-deps chromium
```

The viewer lives in a submodule so the course repository stays small and the
viewer version is explicit. `ignore = dirty` exists because publishing writes
symlinks into the submodule's `public/`; without it every `git status` is noise.

Layout that the tooling assumes:

```text
course/
├── 01_intro.py           # the lecture: the only file whose source is traced
├── slides.py             # house style: figure(), section(), table(), callouts
├── *_content.py          # long prose and table specs, kept off the lecture file
├── *_lab.py              # the computation each case study runs on
├── images/
├── patches/              # local viewer changes (§6)
├── tools/                # the build chain (§3, §4)
├── var/traces/           # recordings
├── edtrace/              # submodule: the viewer
└── .github/workflows/    # publish on push (§5)
```

### What to commit, and one deviation worth making

Commit `pyproject.toml`, `uv.lock`, `.gitmodules`, the submodule reference,
`package.json`, `package-lock.json`.

The usual advice is to gitignore `var/` entirely as generated output. **Commit
the lecture traces anyway:**

```gitignore
var/*
!var/traces
var/traces/*
!var/traces/[0-9][0-9]_*.json
```

Two reasons. Continuous integration can then build the published site without
installing PyTorch or downloading models — it only needs Node. And a student who
clones the repository can read the lecture immediately, paying the model
download only if they want to change an input. The cost is ~1 MB of JSON churn
per re-recording, which is a fair trade for a lecture that otherwise takes
minutes and gigabytes to reconstitute.

---

## 2. Writing a lecture

edtrace imports the module and calls `main()`. Top-level statements run but are
not traced, so a flat script produces an empty trace.

```python
from edtrace import text, note
from slides import CALLOUT, SUBLIST, figure, section


def main() -> None:
    opening()


def opening():
    text("# Lecture 1")
    section("Where we left off")

    x = 3                  # @inspect x
    x = square(x)          # @inspect x

    figure("images/pipeline.png", caption="**The pipeline.**")   # @stepover
    note("Ask them to predict the output before stepping forward.")
    text("**That is the whole idea.**", style=CALLOUT)


def square(value: int) -> int:      # defined here, so the class can step into it
    return value * value            # @inspect value
```

| Directive | Effect |
| --- | --- |
| `@inspect x` | show `x` in the variable panel, keep it updated (follows `a.b.c`) |
| `@clear x` | stop showing `x` |
| `@stepover` | run the line without tracing into it |
| `@hide` | do not display the line at all (it still runs) |

Five rules that save time later:

1. **Everything hangs off `main()`.**
2. **One source line is one unit of display.** Set `line-length = 400` under
   `[tool.black]` and keep long strings in `*_content.py`. A wrapped call leaks
   its continuation lines onto the screen as raw source.
3. **The lecture file decides what is steppable.** edtrace traces the lecture
   module and nothing else: a function defined in the lecture is walked line by
   line; a function imported from another module is one step, in and out. That
   is the real purpose of the `*_lab.py` split — and it means `@stepover` only
   matters for helpers kept in the lecture file.
4. **Only rendering calls reach the audience** — `text`, `image`, `video`,
   `plot`, `link`, `note`. A `print()` dies in your terminal.
5. **A trace is real program state.** Never execute a secret in a lecture; treat
   `var/traces/*.json` as publishable material.

⚠️ A directive is **any `@word` after a `#`**, including inside a string. A
`text("...")` containing both a hash and an at-word is parsed as a directive.
Rephrase, or drop the hash.

---

## 3. Recording and presenting

```bash
uv run python tools/prepare_lecture.py 01_intro     # execute + publish assets
npm run --prefix edtrace/frontend dev -- --port 5173 --strictPort
# http://localhost:5173/?trace=01_intro
```

`prepare_lecture.py` does two things a manual copy of the JSON does not: it
symlinks `var/` and `images/` into the viewer's static root (`image()` records
paths relative to the course root, so without this every figure is broken), and
it accepts several lecture modules at once, which makes re-recording a whole
course after an upgrade one command.

| Key | |
| --- | --- |
| `→` / `l`, `←` / `h` | step forward / back |
| `Shift+→` / `j`, `Shift+←` / `k` | step *over* a call |
| `u` | step *out* |
| `Shift+A` | gradual reveal on/off (**on** by default) |
| `Shift+R` | rendered ⇄ raw code |
| `Shift+E` | variable panel · `Shift+N` notes |
| `g` | load a different trace |
| click a line number | jump there |

One server serves every lecture; change only the `trace` parameter. The URL
encodes your position, so you can bookmark or share an exact step.

---

## 4. Publishing: the part the dev server does not give you

A running `npm run dev` is not something students can keep. The build chain turns
one recording into three artifacts:

| Artifact | For |
| --- | --- |
| `site/` | a static site: the viewer + the trace, for GitHub Pages |
| `site/<lecture>.pdf` | printable handout with your `note()` content included |
| `site/<lecture>-offline.zip` | the same site plus a tiny server, for offline use |

Four tools produce them (copy `tools/` from the reference repository):

| Tool | |
| --- | --- |
| `setup_viewer.py` | fetch the submodule, apply `patches/`, `npm install` |
| `build_site.py` | the build chain below |
| `offline_serve.py` | the static server — used by the build, shipped in the ZIP |
| `check-site.mjs` | load the built bundle in a real browser and assert it works |

plus `export-pdf.mjs`, extended to accept a base URL so the handout is rendered
from the built site rather than from a dev server.

```bash
uv run python tools/build_site.py 01_intro --pdf --zip
uv run python tools/build_site.py 01_intro --skip-trace --pdf --zip   # reuse the trace
```

What `build_site.py` does, in order, and why each step exists:

1. **Record** the lecture (skip with `--skip-trace` when the trace is current).
2. **Publish assets** into the viewer's `public/`, as `prepare_lecture` does.
3. **Vite production build** with `VITE_EDTRACE_BASE_DIR` and
   `VITE_EDTRACE_DIST_DIR`. The output directory sits outside the frontend
   project, so Vite needs `--emptyOutDir` to clear it.
4. **Prune traces** — scratch recordings have no business in a public bundle.
5. **Prune images.** Vite copies all of `images/`; keep only the files the trace
   actually mentions, and *fail the build* if the trace mentions a file that is
   not there. This is worth the twenty lines: it caught a 23 MB GIF that had been
   superseded by an MP4 months earlier, and it turns a broken figure into a build
   error instead of a surprise in class.
6. **Inject a landing redirect**, so opening the site lands on the lecture rather
   than on the viewer's "type a trace name" prompt.
7. **Add `serve.py` and a README** for the offline bundle.
8. **Check it in a browser** (§7) before anything is packaged.
9. **Render the PDF**, then copy it into the site so it is downloadable.
10. **Zip the bundle** and copy the archive into the site too.

### The base-path trap

A site served from `https://user.github.io/<repo>/` must be built with
`--base "/<repo>/"`, or every asset URL 404s. But the offline ZIP is served from
the *root* of a local server, where `/<repo>/assets/…` resolves to nothing.

The two cannot share one build. `build_site.py` therefore gives the archive its
own root-based build rather than zipping the hosted one. If you take one thing
from this section, take that: **an offline bundle built for a subpath is broken,
and it is broken silently.**

### What students actually receive

The interactive page, plus a ZIP whose `README.txt` says, in full:

> Opening `index.html` directly does not work: the viewer fetches the trace over
> HTTP, which a `file://` page is not allowed to do. Instead run
> `python3 serve.py` from this folder.

Any Python 3 works — verified on macOS's stock 3.9. No uv, no Node, no virtual
environment. That constraint is the whole point of the offline bundle: a student
who cannot install anything can still follow the lecture.

---

## 5. Continuous publishing

`.github/workflows/pages.yml`, which builds on push and needs no models because
the trace is committed (§1):

```yaml
name: Publish lecture
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: >
          python tools/build_site.py 01_intro --skip-trace --pdf --zip
          --base "/${{ github.event.repository.name }}/"
      - uses: actions/upload-pages-artifact@v3
        with: { path: site }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Enable it once under **Settings → Pages → Source: GitHub Actions**.

Two things to know before you promise students a URL. Publishing Pages from a
**private** repository requires a paid plan, so on a free account the repository
must be public — plan for the ZIP as the interim channel. And until Pages is
enabled, the `deploy` job fails on every push while `build` passes; that red X is
expected, not a broken build.

---

## 6. Keeping local viewer changes

You will end up changing the viewer — a style, a default, a bug. Do not leave
those edits sitting uncommitted in the submodule: they are invisible to Git
(especially with `ignore = dirty`), and anyone who clones the course gets a
different viewer than the one you presented with.

Keep them as a patch instead of forking, so the submodule still tracks upstream:

```bash
git -C edtrace diff > patches/edtrace-viewer.patch     # after editing the viewer
uv run python tools/setup_viewer.py                    # applies it, idempotently
```

`setup_viewer.py` checks with `git apply --check --reverse` before applying, so
running it twice is safe, and it fails loudly with recovery instructions if the
patch has gone stale against a newer submodule pin.

**One patch you almost certainly need.** The viewer's `index.html` defines
`window.MathJax` as a configuration object, then loads MathJax itself with
`async`. `TraceViewer.jsx` checks only that `window.MathJax` exists before
calling `window.MathJax.typeset()`:

```js
if (renderedContent && typeof window.MathJax?.typeset === 'function') {
```

Without that guard the call throws. In development the many module requests
usually hide the race; in a production bundle it loses reliably, React unmounts,
and **the published page is blank** — while the build reports success. If you
publish a static build at all, patch this first.

---

## 7. Verifying before you publish

"The build succeeded" says nothing: the blank page above compiled perfectly.
`check-site.mjs` loads the finished bundle in headless Chromium and asserts what
a student would notice:

- the landing redirect reaches a trace, and the viewer container renders
- source lines are present (a crashed React tree renders none)
- **no broken images** — `naturalWidth === 0` on any `<img>`
- **the video reached `readyState >= 1`**, which is what proves the server
  answers Range requests
- pressing `→` actually advances the step

`build_site.py` runs it automatically on both bundles and refuses to package a
failure. It skips itself when Playwright is absent, so a student running the
build is not blocked by a publishing dependency.

The Range-request detail is the kind of thing only a browser catches:
`python -m http.server` ignores `Range`, Chromium aborts the request, and an
embedded MP4 simply never plays. `offline_serve.py` implements `206 Partial
Content` for exactly this reason — and the build checks against the same server
students will run, so a passing check means something.

---

## 8. Gotchas, collected

| Symptom | Cause |
| --- | --- |
| Empty trace, or `module has no attribute 'main'` | the lecture has no `main()` |
| Broken images; gaps in the PDF | trace copied by hand instead of via `prepare_lecture.py` |
| Published page blank, build green | the MathJax race (§6) |
| Video never plays offline | server does not answer Range requests (§7) |
| Offline ZIP 404s on every asset | built for a subpath instead of root (§4) |
| Handout nearly blank | missing `animate=0`; cloaked lines render at 20% opacity |
| Handout clipped at the right edge | `.lines-panel` reserves 1000px and scrolls; override it in the print CSS so content reflows |
| `npm warn allow-scripts` on npm 11+ | postinstall scripts are blocked by default; Vite still builds, because esbuild ships per-platform packages |
| A student's `file://` page shows nothing | the viewer fetches its trace over HTTP; they need `serve.py` |

---

## 9. The cycle

Per lecture:

```bash
uv run python tools/prepare_lecture.py 07_agents      # after editing
npm run --prefix edtrace/frontend dev -- --port 5173 --strictPort
```

Per release:

```bash
uv run python tools/build_site.py 07_agents --pdf --zip   # build, verify, package
git add var/traces/07_agents.json && git commit && git push   # CI publishes
```

After upgrading edtrace, upgrade both halves together — they share the trace
format — then re-record one lecture end to end before class:

```bash
uv add --upgrade edtrace
git -C edtrace pull origin main && npm ci --prefix edtrace/frontend
uv run python tools/setup_viewer.py        # re-apply your patches onto the new pin
```

---

Built on [edtrace](https://github.com/percyliang/edtrace) by Percy Liang, the
tool behind Stanford's [CS221](https://github.com/stanford-cs221/autumn2025-lectures).
