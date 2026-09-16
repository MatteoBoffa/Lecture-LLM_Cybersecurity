# Hands-on labs

Two practical labs that follow the lecture, one per lane.

The lecture argued that ⚡ fast thinking and 🐢 slow thinking buy different
things. These labs make you pay for both and check what you got.

|                        |                            |                                       |
| ---------------------- | -------------------------- | ------------------------------------- |
| ⚡ **LogPrécis**, 2h   | [`logprecis/`](logprecis/) | a 130M-parameter model                |
| 🐢 **CyberSleuth**, 2h | [`cybersleuth/`](cybersleuth/) | an agent, and what it costs to ask it |

---

## ⚡ LogPrécis

Nothing is trained. The model is
[`SmartDataPolito/logprecis`](https://huggingface.co/SmartDataPolito/logprecis)
off the Hub, and every dataset comes from the authors'
[own repository](https://github.com/SmartData-Polito/logprecis), so any number you
produce can be checked against what they published.

| Notebook                                                         | ~      | What you come out with                                                                         |
| ---------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| [`1_model_and_labels.ipynb`](logprecis/1_model_and_labels.ipynb) | 60 min | an accuracy you measured on held-out data, and the harness bug that was hiding 15 points of it |
| [`2_characterization.ipynb`](logprecis/2_characterization.ipynb) | 60 min | 10 000 real attacks reduced to a queue you could actually work, and one named campaign         |

[![Open Lab 1 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MatteoBoffa/Lecture-LLM_Cybersecurity/blob/main/labs/logprecis/1_model_and_labels.ipynb)
[![Open Lab 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MatteoBoffa/Lecture-LLM_Cybersecurity/blob/main/labs/logprecis/2_characterization.ipynb)

In Lab 1 you run the model yourself, on a few hundred sessions, which a CPU does in seconds.
In Lab 2 you analyse the authors' published predictions for 233 035 sessions - more intensive hardware-wise.
You get the paper's scale without the paper's compute.

## Running the LogPrécis lab

### On Colab — nothing to install

Click a badge above. The first cell of each notebook installs the packages it
needs and clones this repository for you.

That is the whole procedure, and it is the one to use unless you have a reason not to.

### On your own laptop

You need [**uv**](https://docs.astral.sh/uv/getting-started/installation/) and
**git**. Nothing else — uv fetches the right Python itself.

```sh
# 1. Clone. No --recurse-submodules: the labs do not need the lecture viewer.
git clone https://github.com/MatteoBoffa/Lecture-LLM_Cybersecurity.git
cd Lecture-LLM_Cybersecurity

# 2. Install the lab dependencies (the lecture itself does not use them)
uv sync --group labs

# 3. Open the first notebook
uv run jupyter lab labs/logprecis/1_model_and_labels.ipynb
```

The notebooks work the same either way: the setup cell notices it is not on Colab
and simply uses the clone you are sitting in.

### The data

Each notebook downloads what it needs on first use into `labs/data/` (~41 MB
total) and caches it there, so you pay the cost once. Lab 1 pulls two small
labelled corpora; Lab 2 pulls the honeypot sessions and LogPrécis's published
predictions.

Everything comes from the authors'
[own repository](https://github.com/SmartData-Polito/logprecis), so any number
you produce can be checked against what they published.

If the lecture-room wifi cannot be trusted, warm the cache beforehand:

```sh
uv run python labs/labs_lib.py
```

### The model

Lab 1 downloads `SmartDataPolito/logprecis` from Hugging Face on first use —
about 500 MB, cached by Hugging Face afterwards. No token or account is needed.
Lab 2 does not load the model at all.

## 🐢 CyberSleuth

The paper's agent needs paid APIs, a Google search key and a custom framework.
This lab rebuilds a toy version from parts every student already has:

- [**OpenCode**](https://opencode.ai), an open-source agent harness in the style of Claude Code
- **GitHub Copilot**, for the LLM
- `tshark`, for reading the traces

The incidents are four of the paper's own traces, from the authors'
[repository](https://github.com/SmartData-Polito/Cybersleuth_Forensic_Agent),
in two pairs. Each pair fires the same exploit at a vulnerable and at a patched
service.

| Notebook                                                         | ~       | What you come out with                                                                                     |
| ---------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| [`investigation.ipynb`](cybersleuth/investigation.ipynb)         | 120 min | two agent architectures scored on the paper's checkpoints, what each one costs, and what breaks without the web |

An architecture is a 30-line Markdown file in
[`cybersleuth/.opencode/agents/`](cybersleuth/.opencode/agents/):

| Agent           | Architecture                                                                              |
| --------------- | ----------------------------------------------------------------------------------------- |
| `sleuth`        | single agent: runs `tshark` itself, searches the web                                      |
| `sleuth-tea`    | Tshark Expert: cannot run anything, and delegates every look at the trace to...           |
| `tshark-expert` | ...a sub-agent that can run `tshark` and nothing else                                     |

The tools are set by permissions, not by prompts. `bash` is denied except for
commands that start with `tshark`, and nothing can edit a file.

### Running it

This lab needs a terminal: OpenCode is a command-line program, and logging in
is interactive. Colab is not an option.

**In a GitHub Codespace (recommended).**
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MatteoBoffa/Lecture-LLM_Cybersecurity)
The container installs `tshark`, `opencode` and the lab dependencies by itself.
It takes a few minutes the first time. Codespaces are free up to a monthly quota
on personal accounts.

**On your own laptop.** You need `tshark` and `opencode` as well as uv:

```sh
brew install wireshark sst/tap/opencode                    # macOS
sudo apt install tshark && curl -fsSL https://opencode.ai/install | bash   # Debian/Ubuntu
uv sync --group labs
```

**Either way, log in once**, in a terminal:

```sh
opencode auth login --provider github-copilot
```

It prints a code. Enter it at <https://github.com/login/device>. Then open
`labs/cybersleuth/investigation.ipynb`.

### Copilot: the rules

The LLM is billed to **your** GitHub account, so read this before your first run.

- **You need Copilot on your account.** Check
  <https://github.com/settings/copilot>. Verified students get the Copilot
  Student plan for free through
  [GitHub Education](https://education.github.com/pack). GitHub officially
  supports OpenCode for
  [paid Copilot plans](https://github.blog/changelog/2026-01-16-github-copilot-now-supports-opencode/)
  (Pro, Pro+, Business, Enterprise). The Free and Student plans are not on that
  list: if the login works but runs are refused, that is why.
- **Every run spends AI Credits** (1 credit = $0.01). On the lab's model,
  `gpt-5-mini`, a single-agent run costs about 1 credit and a Tshark Expert run
  about 4. The whole notebook costs about 30. The notebook shows the cost of
  each run, and your real usage is at <https://github.com/settings/billing>.
- **Mind your monthly allowance.** The Copilot Student plan includes
  [about 200 AI Credits a month](https://github.com/orgs/community/discussions/197557),
  and they reset on the 1st (00:00 UTC). The lab needs about 30, but Copilot
  Chat and agent mode in your editor spend the same credits. Check what's left
  at <https://github.com/settings/billing> before you start. Once they run out,
  runs are refused until the next month.
- **Runs are cached** in `labs/data/runs/`. Re-executing the notebook costs
  nothing. `rerun=True` pays again, so use it on purpose.
- **Keep the model.** A larger model can cost many times more per run. Check
  [GitHub's price list](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
  before you change `MODEL`.
- **No loops.** Twelve runs is the lab. Scripting hundreds of them against your
  personal plan is not what it is for, and GitHub's terms say so.
- **Your login is a credential.** It lives in
  `~/.local/share/opencode/auth.json`. Never commit it, and never paste it into
  a notebook. When you are done with a codespace, run `opencode auth logout` or
  delete the codespace.
- **Leave the permissions alone.** The agents can run `tshark` on recorded
  traffic and nothing else. Do not give them a shell, and do not point them at
  a live system.

## For the instructor

If you are a student, you are done - the rest is about how these labs are kept.

Every lab exists twice:

| File                               |                                             |
| ---------------------------------- | ------------------------------------------- |
| `<lab>/solutions/<name>.ipynb` | the worked lab, answers and outputs and all |
| `<lab>/<name>.ipynb`           | what the students open, answers removed     |

The second is generated from the first. **Edit only the solution**, then re-run

```sh
uv run python labs/make_stubs.py
```

to rebuild the students' copies. Never edit those by hand - the next run
overwrites them.

In a solution cell, fence off the part the student is meant to write:

```python
### TODO: keep the label of the first token of each word
### BEGIN SOLUTION
pairs = ...
### END SOLUTION
```

`make_stubs.py` deletes what is between the markers, demotes the `###` hints to
ordinary comments, and leaves a `raise NotImplementedError("your turn")` where the
answer was, so the stub still parses and fails loudly instead of quietly returning
nothing. Outputs are cleared too - a student should see their own.

The answers stay off GitHub: `solutions/` is gitignored, so back them up
yourself. To publish them after the class, delete that line from the root
`.gitignore`. (A separate branch works as well, but `make_stubs.py` reads the
solutions off disk, so you would be switching branches every time you regenerate.)

| File                             |                                                    |
| -------------------------------- | -------------------------------------------------- |
| [`labs_lib.py`](labs_lib.py)     | fetching, ground-truth alignment, the plot palette |
| [`make_stubs.py`](make_stubs.py) | solutions → students' notebooks                    |
| `cybersleuth/.opencode/`         | the agents, and OpenCode's project config         |
| `data/`, `cybersleuth/evidence/` | downloaded on demand, gitignored                   |
| `data/runs/`                     | cached agent runs: delete one to pay for it again  |

### One thing worth knowing before you teach it

The released labels are one tactic per **statement**, run-length encoded as
_cumulative_ indices: `"Impact - 3 -- Execution - 10"` means statements 0-3 are
Impact and 4-10 are Execution — eleven labels, not thirteen. They are aligned to
the authors' own splitter, in which a bare `|` starts a new statement too, so
`cut … | grep …` counts as two. Get either detail wrong and every accuracy in Lab 1
is quietly meaningless. `labs_lib.divide_statements` is that splitter, copied from
upstream; it reproduces the label counts on all 359 sessions.
