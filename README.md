# LLMs and Cybersecurity — Modelli per l'IA

Materials for the four-hour lecture on LLMs and cybersecurity (Politecnico di Torino).

The lecture is not a slide deck: it is a **Python program** you step through.
Every claim in it is a line of code that runs, and the demos are the real
models, not screenshots. The viewer is [edtrace](https://github.com/percyliang/edtrace).

---

## Which one do you need?

The lecture ships in two forms, and they are not the same thing.

**A recording** (§1) — the published page and the ZIP both serve
`var/traces/01_intro.json`: the source of `01_intro.py` plus **802 recorded
steps**, each carrying the variable values and rendered output from the moment
the lecture was run. Stepping through it replays that recording. There is no
Python behind the page, only static files.

**The program** (§2) — the lecture itself, which you execute.

| | recording (§1) | clone (§2) |
| --- | --- | --- |
| Follow the lecture, step by step | ✅ | ✅ (same trace) |
| Print it / read it offline | ✅ | ✅ |
| Read the case-study implementations | ❌ *not included* | ✅ |
| Ask the models something I choose | ❌ | ✅ |
| Import the code into my own notebook | ❌ | ✅ |

Two things are worth spelling out.

*The recording cannot answer a question it was not asked.* When the lecture
calls `ask(chat, question)` or `tactics_of(logprecis, session)`, the page shows
the answer for the input chosen while recording. Your own SSH session, your own
prompt, is a step that does not exist in the file — producing it means loading
the models and running the program.

*The recording does not contain the case studies.* Every lab call is marked
`@stepover`, so the trace carries `01_intro.py` and nothing else. If you want to
see how `fingerprints_of` works, or `from logprecis_lab import fingerprints_of`
in a notebook of your own, you need the repository.

**If you are here to follow the lecture, §1 is enough — and simpler.** §2 is for
poking at it, which is the reason it is code and not slides.

---

## 1. Follow the lecture (nothing to install)

| What | Where |
| --- | --- |
| Interactive lecture | <https://matteoboffa.github.io/Lecture-LLM_Cybersecurity/> |
| Printable handout | <https://matteoboffa.github.io/Lecture-LLM_Cybersecurity/01_intro.pdf> |
| Offline copy (ZIP) | <https://matteoboffa.github.io/Lecture-LLM_Cybersecurity/01_intro-offline.zip> |

**The offline copy** unzips to a folder of plain files. Opening `index.html`
directly will *not* work (the viewer fetches its trace over HTTP, which a
`file://` page may not do). Instead run, from inside the folder:

```sh
python3 serve.py
```

It starts a small local server and opens the lecture in your browser.

### Getting around the viewer

| Key | Action |
| --- | --- |
| `→` / `←` | step forward / back one line |
| `shift`+`→` / `shift`+`←` | step *over* a function call |
| `u` | step out of the current function |
| `N` | show/hide the instructor notes |
| `E` | show/hide the variable panel |
| `A` | turn the progressive reveal off (show everything at once) |
| `R` | raw mode: source instead of rendered output |
| `g` | load a different trace |

Clicking a line number jumps there, and the URL always encodes your position,
so you can bookmark or share an exact step.

---

## 2. Reproduce it on your laptop

You need **Python 3.12+**, [**uv**](https://docs.astral.sh/uv/getting-started/installation/),
**Node 20+**, and **git**.

```sh
# 1. Clone with the viewer submodule
git clone --recurse-submodules https://github.com/MatteoBoffa/Lecture-LLM_Cybersecurity.git
cd Lecture-LLM_Cybersecurity

# 2. Python environment
uv sync

# 3. Viewer: fetch the submodule, apply this course's patches, install npm deps
uv run python tools/setup_viewer.py

# 4. Run the lecture and record its trace
uv run python tools/prepare_lecture.py 01_intro

# 5. Open the viewer
npm --prefix=edtrace/frontend run dev
```

Then go to <http://localhost:5173/?trace=01_intro>.

Steps 1-3 and 6 alone already give you the recorded lecture in the viewer, with
no model downloads: `var/traces/01_intro.json` is in the repository. **Step 4 is
what makes the lecture yours** - it re-executes `01_intro.py` and records a new
trace, so any input you change shows its real output.

**Step 4 downloads models** (`distilbert-base-uncased`,
`SmartDataPolito/logprecis`, `Qwen/Qwen2.5-0.5B-Instruct`) — roughly 2 GB and a
few minutes on the first run, cached by Hugging Face afterwards. If you only
want to *read* the lecture, skip step 4: `var/traces/01_intro.json` is already
in the repo.

If you cloned without `--recurse-submodules`, step 3 fetches the submodule for
you.

---

## 3. What is in here

| Path | |
| --- | --- |
| `01_intro.py` | the lecture itself — read this one |
| `slides.py` | presentation helpers (`section`, `table`, `figure`, …) |
| `*_content.py` | the prose, tables and figures the lecture cites |
| `darkvec_lab.py`, `logprecis_lab.py` | ⚡ fast-thinking case studies |
| `autopenbench_lab.py`, `cybersleuth_lab.py` | 🐢 slow-thinking case studies |
| `edtrace/` | the viewer, as an upstream submodule |
| `patches/edtrace-viewer.patch` | local viewer changes this course depends on |
| `tools/` | build the trace, the static site, the handout |
| `var/traces/` | recorded traces (the lecture, ready to view) |

The case-study modules are ordinary Python: run them, change the inputs, break
them. That is the point of shipping the lecture as code.

---

## 4. Publishing (instructor)

Rendering the handout needs Playwright, once:

```sh
npm ci && npx playwright install chromium
```

Then:

```sh
# Everything at once: trace, static site, handout, offline archive
uv run python tools/build_site.py 01_intro --pdf --zip

# Fast path when the trace is already current (no model downloads)
uv run python tools/build_site.py 01_intro --skip-trace --pdf --zip
```

This writes `site/` (a self-contained static site), `pdf/01_intro.pdf`, and
`site.zip`, and copies the last two into `site/` so they are downloadable from
the published page. Both bundles are loaded in a real browser before the build
succeeds — it fails on a broken image, an unplayable video, or a viewer that
does not step. Pass `--no-check` to skip that.

To preview locally:

```sh
uv run python tools/offline_serve.py --directory site
```

Pushing to `main` rebuilds and deploys to GitHub Pages
(`.github/workflows/pages.yml`), which builds with `--base /<repo>/` so the
asset URLs match the published path. Enable it once under
**Settings → Pages → Source: GitHub Actions**.

The offline archive gets its own root-based build, because the hosted site's
absolute asset URLs (`/<repo>/assets/…`) would not resolve under the bundle's
own `serve.py`.

### Changing the viewer

`edtrace/` tracks upstream, so local viewer changes live in
`patches/edtrace-viewer.patch`. After editing files under `edtrace/frontend/`,
refresh the patch:

```sh
git -C edtrace diff > patches/edtrace-viewer.patch
```

---

## Running a course like this

[`docs/instructor-guide.md`](docs/instructor-guide.md) is the whole workflow in
one file, for another instructor: course setup, writing a lecture, recording it,
presenting it, and publishing the static site, handout and offline bundle —
including the traps that only surface once you publish.

## Credits

Lecture by **Matteo Boffa** (Politecnico di Torino).
Viewer: [edtrace](https://github.com/percyliang/edtrace) by Percy Liang (Apache 2.0).
