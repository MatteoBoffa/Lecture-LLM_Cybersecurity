"""Shared plumbing for the hands-on labs.

The rule here is the same one that governs `logprecis_lab.py`: nothing is
re-implemented that the authors already published.  This module only does the
two unglamorous jobs that stand between a student and the data —

  * **fetching** it (the LogPrécis repository is the source of truth, and it is
    large, so we pull the four files a lab actually needs and cache them);
  * **aligning** it (the released labels are one tactic per *statement*, run-length
    encoded as cumulative indices, and getting that wrong silently corrupts
    every accuracy you compute afterwards).

Everything the lab is actually *about* — word alignment, context chunking,
majority voting, fingerprints — is left for the notebooks to build.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path
from typing import NamedTuple

LABS_DIR = Path(__file__).resolve().parent
ROOT = LABS_DIR.parent
DATA_DIR = LABS_DIR / "data"

# The labs reuse the lecture's own case-study module, which lives one level up.
# Putting the repository root on the path here means a notebook - or this file
# run as a script - works from whatever directory it happens to be started in.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logprecis_lab import TACTICS  # noqa: E402,F401  (re-exported for the notebooks)

# Everything comes from the paper's own repository, so a student can check any
# number in this lab against the artefact the authors released.
_BASE = "https://raw.githubusercontent.com/SmartData-Polito/logprecis/main/"

FILES = {
    # 360 sessions labelled under expert supervision, split 287/72 by the
    # authors' own `split_partitions.py`.  The 72 are what we evaluate on.
    "train": "1.Dataset/Training/Supervised/sample_train_corpus.parquet",
    "test": "1.Dataset/Training/Supervised/sample_test_corpus.parquet",
    # The first chunk of the CyberLab honeynet collection: 9 999 real sessions
    # with the metadata the characterisation needs (sensor, timestamp, date).
    "sessions": "1.Dataset/Inference/Chunks/cyberlab_chunk_aa",
    # LogPrécis's own word-level predictions for all 233 035 sessions of that
    # collection.  This is what makes a paper-scale characterisation fit in a
    # lab: the students run the model on hundreds of sessions, and analyse
    # hundreds of thousands.
    "predictions": "1.Dataset/Inference_with_predictions/logprecis_predictions.parquet",
}


def fetch(key: str) -> Path:
    """Download one of `FILES` into `data/`, or return the cached copy."""
    if key not in FILES:
        raise KeyError(f"unknown file {key!r}; choose from {sorted(FILES)}")
    DATA_DIR.mkdir(exist_ok=True)
    target = DATA_DIR / f"{key}{Path(FILES[key]).suffix}"
    if not target.exists():
        print(f"downloading {key} ...", end=" ", flush=True)
        urllib.request.urlretrieve(_BASE + FILES[key], target)
        print(f"{target.stat().st_size / 1e6:.1f} MB")
    return target


def divide_statements(session: str) -> list[str]:
    """Cut a session into statements, exactly as LogPrécis's authors do.

    Verbatim from `2.Training/core/functions/preprocessing_functions.py` in the
    LogPrécis repository, and it has to be: the released labels are one per
    statement, so any other splitting rule — including the friendlier one in
    `logprecis_lab.statements` — misaligns the ground truth.  Note that a bare
    `|` separates statements too, which is why `cut … | grep …` is two of them.
    """
    parts = re.split(r"(; |\|\|? |&& )", session + " ")
    if len(parts) == 1:  # a session with no separator at all
        return [parts[0].strip() + " ;"]
    return ["".join(parts[i : i + 2]).strip() for i in range(0, len(parts) - 1, 2)]


def expand_labels(labels: str, n_statements: int) -> list[str]:
    """Turn `"Impact - 3 -- Execution - 10"` into one tactic per statement.

    The numbers are *cumulative, inclusive* indices of the last statement each
    tactic covers — not run lengths.  So the example above means statements 0-3
    are Impact and statements 4-10 are Execution: eleven labels, not thirteen.
    """
    out: list[str] = []
    for block in labels.split(" -- "):
        tactic, _, end = block.rpartition(" - ")
        out += [tactic] * (int(end) + 1 - len(out))
    if len(out) != n_statements:
        raise ValueError(f"{len(out)} labels for {n_statements} statements")
    return out


def ground_truth(split: str = "test"):
    """The labelled corpus, one row per session, ready to score against.

    Columns: `session`, `statements` (list[str]) and `tactics` (list[str]), one
    tactic per statement.  `split="test"` gives the 72 sessions held out of
    LogPrécis's training set — the only honest ones to measure on.
    """
    import pandas as pd

    df = pd.read_parquet(fetch(split))
    df["statements"] = df["session"].map(divide_statements)
    df["tactics"] = [expand_labels(row.labels, len(row.statements)) for row in df.itertuples()]
    return df.drop(columns="labels")


def honeypot_sessions():
    """9 999 real CyberLab sessions with their sensor and timestamp.

    `session_id` is the row number in the full collection, which is exactly the
    key LogPrécis's published predictions are indexed by.
    """
    import pandas as pd

    df = pd.read_csv(fetch("sessions"), parse_dates=["first_timestamp", "date"])
    return df.assign(session_id=range(len(df)))


def published_predictions():
    """LogPrécis's own word-level predictions, joined to those sessions.

    Columns: `session_id`, `sequence_words`, `sequence_predictions`, plus the
    metadata.  The join is an inner one on purpose — eleven sessions of the
    collection have no published prediction, and silently shifting the rest by
    one row would corrupt every count in the notebook.
    """
    import pandas as pd

    preds = pd.read_parquet(fetch("predictions"))
    meta = honeypot_sessions()
    joined = preds.merge(meta, on="session_id", how="inner")
    if len(joined) != len(meta):
        print(f"note: {len(meta) - len(joined)} of {len(meta)} sessions carry no published prediction")
    return joined


# ------------------------------------------------------------- CyberSleuth --
# Lab 2 drives a real agent harness (OpenCode) from Python.  Two jobs live here:
# handing the agent its evidence without handing it the answer, and turning a
# run into something you can score.
SLEUTH_DIR = LABS_DIR / "cybersleuth"
EVIDENCE_DIR = SLEUTH_DIR / "evidence"
RUNS_DIR = DATA_DIR / "runs"

_SLEUTH = "https://raw.githubusercontent.com/SmartData-Polito/Cybersleuth_Forensic_Agent/main/data/"

# Four traces from the CyberSleuth repository, two pairs.  In each pair the same
# exploit is fired at a vulnerable and at a patched service.  The Vite pair is
# from the 2025 test set: its CVE was disclosed after the models were trained.
# Neutral names on purpose - the upstream files are named after their CVE, and
# an agent that can read a filename does not need to read the trace.
INCIDENTS = {
    "incident-1": ("CFA-benchmark", 2, "CVE-2021-41773.pcap"),
    "incident-2": ("CFA-benchmark", 3, "CVE-2021-42013.pcap"),
    "incident-3": ("TestSet_benchmark", 2, "cve-2025-30208_success.pcap"),
    "incident-4": ("TestSet_benchmark", 3, "cve-2025-30208_fail.pcap"),
}

# The paper's task prompt (Sec. 4.2), plus the one thing a toy grader needs: a
# machine-readable verdict at the end.  The real benchmark is graded by a human
# reading the prose.
TASK = """Analyse the PCAP file {pcap} to accomplish the following tasks:
1. Identify the name of the service or application involved.
2. Determine the relevant CVE based on the captured data.
3. Gather evidence of malicious activities associated with the identified CVE.
4. Assess whether the service or application is vulnerable to the identified attack.
5. Evaluate whether the attack was successful.

Write a short report. End it with exactly one fenced JSON block:
```json
{{"service": "<name and version>", "cve": "CVE-YYYY-NNNNN", "success": true or false}}
```"""


def fetch_incidents() -> dict[str, dict]:
    """Download the four traces into `cybersleuth/evidence/` and return the answers.

    The answers stay in Python.  Only the PCAPs go where the agent can see them.
    """
    import json

    EVIDENCE_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    truth = {}
    for name, (bench, event, filename) in INCIDENTS.items():
        pcap = EVIDENCE_DIR / f"{name}.pcap"
        if not pcap.exists():
            urllib.request.urlretrieve(f"{_SLEUTH}{bench}/raw/eventID_{event}/{filename}", pcap)
        answers = DATA_DIR / f"{bench}.json"
        if not answers.exists():
            urllib.request.urlretrieve(f"{_SLEUTH}{bench}/tasks/data.json", answers)
        row = next(t for t in json.loads(answers.read_text())["tasks"] if t["event"] == str(event))
        truth[name] = {"service": row["service"], "cve": row["cve"], "success": row["success"]}
    return truth


class Call(NamedTuple):
    """One tool call: what the model asked the harness for, and what came back."""

    tool: str  # a sub-agent's calls are prefixed with its name: "tshark-expert:bash"
    request: str  # the command, the search query, or "<sub-agent>: <question>"
    result: str
    steps: list[Step]  # for a `task` call, the sub-agent's own loop; empty otherwise


class Step(NamedTuple):
    """One call to the LLM. It reads the whole conversation, then writes."""

    read: int  # tokens read: agent prompt, task, and every earlier step
    wrote: int  # tokens written, hidden reasoning included
    cost: float
    calls: list[Call]  # the tools it asked for ...
    text: str  # ... or, on the last step, its answer


class Run(NamedTuple):
    """One agent run: what it concluded, and what it did to get there."""

    agent: str
    incident: str
    report: str
    tools: list[str]  # every tool call, in order, sub-agents included
    tokens: int  # everything the models read and wrote, sub-agents included
    cost: float  # USD at list price, as opencode estimates it; 1 Copilot AI Credit = $0.01
    steps: list[Step]  # the agent loop, one LLM call per step


def investigate(agent: str, incident: str, model: str, rerun: bool = False, timeout: int = 900) -> Run:
    """Run one OpenCode agent on one incident, headless, and parse what it did.

    Runs are cached in `data/runs/`: every run costs you Copilot quota, and a
    notebook you re-execute should not pay twice.  Pass `rerun=True` to pay.
    """
    import json

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    log = RUNS_DIR / f"{agent}__{incident}__{model.replace('/', '_')}.jsonl"
    if rerun or not log.exists():
        prompt = TASK.format(pcap=f"evidence/{incident}.pcap")
        code = _opencode(["run", "--agent", agent, "--model", model, "--format", "json", prompt], log, timeout)
        if code != 0 or '"type":"error"' in log.read_text():
            failure = log.read_text()[-2000:]
            log.unlink()
            raise RuntimeError(f"opencode failed ({code}):\n{failure}")
        _export_subagents(log)
    events = [json.loads(line) for line in log.read_text().splitlines() if line.startswith("{")]
    return _parse(agent, incident, events)


def _opencode(args: list[str], out: Path, timeout: int = 120) -> int:
    """Run the opencode CLI in the lab folder, with its output going to `out`.

    Three details, each of which cost an afternoon: output goes to a file,
    because opencode truncates a pipe at 64 KB; stdin is closed, because it
    reads a piped stdin as part of the prompt; and PWD must match the working
    directory, because opencode trusts the variable.  OPENCODE_ENABLE_EXA
    switches on the keyless `websearch` tool.
    """
    import os
    import subprocess

    env = {**os.environ, "PWD": str(SLEUTH_DIR), "OPENCODE_ENABLE_EXA": "1", "OPENCODE_DISABLE_AUTOUPDATE": "1"}
    with open(out, "w") as sink:
        done = subprocess.run(
            ["opencode", *args], cwd=SLEUTH_DIR, env=env, timeout=timeout,
            stdin=subprocess.DEVNULL, stdout=sink, stderr=subprocess.DEVNULL,
        )
    return done.returncode


def _export_subagents(log: Path) -> None:
    """Append each sub-agent's session to the run log.

    A sub-agent runs in a session of its own, and `opencode run` only streams
    the parent's: the tshark expert's commands and tokens would go uncounted.
    """
    import json
    import tempfile

    events = [json.loads(line) for line in log.read_text().splitlines() if line.startswith("{")]
    for event in events:
        part = event.get("part", {})
        if part.get("tool") != "task":
            continue
        child = re.search(r'task id="(ses_\w+)"', str(part.get("state", {}).get("output", "")))
        if not child:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "session.json"
            _opencode(["export", child[1]], dump)
            session = json.loads(dump.read_text())
        with open(log, "a") as sink:
            sink.write(json.dumps({"type": "subagent", "callID": part.get("callID"), "session": session}) + "\n")


def _parse(agent: str, incident: str, events: list[dict]) -> Run:
    subagents = {e["callID"]: e["session"] for e in events if e.get("type") == "subagent"}
    steps, calls, texts = [], [], []
    for event in events:
        part = event.get("part", {})
        if event.get("type") == "step_start":
            calls, texts = [], []
        elif event.get("type") == "text":
            texts.append(part.get("text", ""))
        elif event.get("type") == "tool_use":
            session = subagents.get(part.get("callID"))
            calls.append(_call(part, _session_steps(session) if session else []))
        elif event.get("type") == "step_finish":
            steps.append(_step(part.get("tokens", {}), part.get("cost", 0.0), calls, texts))
    every = list(_walk(steps))
    return Run(
        agent, incident,
        report=next((s.text for s in reversed(steps) if s.text), ""),
        tools=[call.tool for step in every for call in step.calls],
        tokens=sum(s.read + s.wrote for s in every),
        cost=sum(s.cost for s in every),
        steps=steps,
    )


def _session_steps(session: dict) -> list[Step]:
    """A sub-agent's exported session, as steps: one per assistant message."""
    name = session["info"].get("agent", "subagent")
    steps = []
    for message in session["messages"]:
        info, parts = message["info"], message["parts"]
        if info.get("role") == "assistant":
            calls = [_call(p, [], prefix=f"{name}:") for p in parts if p["type"] == "tool"]
            texts = [p.get("text", "") for p in parts if p["type"] == "text"]
            steps.append(_step(info.get("tokens", {}), info.get("cost", 0.0), calls, texts))
    return steps


def _call(part: dict, steps: list[Step], prefix: str = "") -> Call:
    state = part.get("state", {})
    args = state.get("input", {})
    if "prompt" in args:  # a question for a sub-agent
        request = f"{args.get('subagent_type', 'subagent')}: {args['prompt']}"
    else:
        request = next((str(args[k]) for k in ("command", "query", "url") if k in args), str(args))
    return Call(prefix + part.get("tool", "?"), request, str(state.get("output", "")), steps)


def _step(tokens: dict, cost: float, calls: list[Call], texts: list[str]) -> Step:
    read = tokens.get("input", 0) + tokens.get("cache", {}).get("read", 0)
    wrote = tokens.get("output", 0) + tokens.get("reasoning", 0)
    return Step(read, wrote, cost, calls, "\n\n".join(t for t in texts if t))


def _walk(steps: list[Step]):
    """Every step, each followed by the steps of the sub-agents it started."""
    for step in steps:
        yield step
        for call in step.calls:
            yield from _walk(call.steps)


def show_steps(run: Run, lines: int = 2, width: int = 100) -> None:
    """Print a run the way the agent loop saw it: one LLM call per step.

    `read` is what the model re-read at that step, `wrote` what it produced,
    hidden reasoning included.  Under each tool call, the first `lines` lines
    of what came back.  A sub-agent's steps are indented under the `task` call
    that started them, and its answer is what the main agent reads next.
    """
    print(f"{run.agent} on {run.incident}: {len(run.steps)} steps, "
          f"{len(run.tools)} tool calls, {run.tokens:,} tokens\n")
    print(f"{'step':>4} {'read':>7} {'wrote':>6}")
    _show(run.steps, lines, width, indent="")


def _show(steps: list[Step], lines: int, width: int, indent: str) -> None:
    for n, step in enumerate(steps, 1):
        head = f"{indent}{n:>4} {step.read:>7,} {step.wrote:>6,}  "
        pad = " " * len(head)
        if not step.calls:
            _lines(head + "answer    ", pad + " " * 10, step.text, lines + 1, width)
        for i, call in enumerate(step.calls):
            tool = call.tool.split(":")[-1]
            first = (head if i == 0 else pad) + f"{tool:<10}"
            if call.steps:
                print(_clip(f"{first}-> {call.request}", width))
                _show(call.steps, lines, width, indent + " " * 8)
                print(f"{pad}{' ' * 10}<- its answer is this call's result")
            else:
                print(_clip(first + call.request.splitlines()[0].replace("\t", " ") if call.request else first, width))
                _lines(pad + " " * 10 + "| ", pad + " " * 10 + "| ", call.result, lines, width)


def plot_context(*runs: Run, label_above: int = 1_000):
    """What each step of the main agent reads: the part it already read, and the new part.

    One bar per LLM call.  Dark: what the previous step already read.  Light:
    what was added since - the model's last request and whatever the tool sent
    back.  Jumps over `label_above` tokens are labelled with their cause.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator, StrMethodFormatter

    style()
    fig, axes = plt.subplots(1, len(runs), figsize=(4.6 * len(runs), 3.8), sharey=True, squeeze=False)
    top = max(s.read for run in runs for s in run.steps)
    for ax, run in zip(axes[0], runs):
        read = [s.read for s in run.steps]
        before = [0, *read[:-1]]
        x = range(1, len(read) + 1)
        slot_px = ax.get_window_extent().width / len(read)
        width = min(0.6, 24 / slot_px)  # bars no thicker than 24px
        ax.bar(x, before, width, color=SEQUENTIAL[5], edgecolor="white", linewidth=1, label="already read at the previous step")
        ax.bar(x, [r - b for r, b in zip(read, before)], width, bottom=before,
               color=SEQUENTIAL[2], edgecolor="white", linewidth=1, label="new since the previous step")
        for n, (r, b) in enumerate(zip(read, before), 1):
            if n == 1:
                cause = "prompt\n+ task"
            elif r - b > label_above:
                call = run.steps[n - 2].calls[0]
                cause = f"{call.tool.split(':')[-1]} output\n{len(call.result) / 1000:.0f}k chars"
            else:
                continue
            ax.annotate(cause, (n, r), xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, color=INK_MUTED)
        ax.set_title(f"{run.agent} on {run.incident}")
        ax.set_xlabel("step (one LLM call)")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis="x", visible=False)
        ax.set_ylim(0, top * 1.25)
    axes[0][0].set_ylabel("tokens read")
    axes[0][0].yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    fig.legend(*axes[0][0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    plt.show()


def _lines(first: str, rest: str, text: str, limit: int, width: int) -> None:
    # Rulers like "=====" say nothing, so only lines with a letter or digit count.
    shown = [line.replace("\t", "  ") for line in text.splitlines() if re.search(r"\w", line)]
    if not shown:
        print(first + "(no output)")
    for i, line in enumerate(shown[:limit]):
        print(_clip((first if i == 0 else rest) + line, width))
    if len(shown) > limit:
        more = len(shown) - limit
        print(f"{rest}... {more} more line{'s' if more > 1 else ''}")


def _clip(line: str, width: int) -> str:
    return line if len(line) <= width else line[: width - 3] + "..."


def verdict(report: str) -> dict:
    """The JSON block at the end of a report, or `{}` if the agent forgot it."""
    import json

    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", report, flags=re.S)
    if not blocks:
        return {}
    for candidate in (blocks[-1], blocks[-1].replace('\\"', '"')):  # some models escape the quotes
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    return {}


# ---------------------------------------------------------------- plotting --
# A small validated palette, so every plot in the labs reads as one system.
# Categorical slots are assigned in this fixed order and never cycled; the
# sequential ramp is one hue, light to dark, for magnitude (the confusion
# matrix).  Three of these hues sit below 3:1 against a white notebook
# background, so plots that use them carry visible labels, not colour alone.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
SEQUENTIAL = ("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b")

INK = "#0b0b0b"
INK_MUTED = "#52514e"


def style():
    """Recessive axes, thin marks, our colour cycle. Call once per notebook."""
    import matplotlib as mpl
    from matplotlib.colors import LinearSegmentedColormap

    if "logprecis" not in mpl.colormaps:  # style() may run more than once
        mpl.colormaps.register(LinearSegmentedColormap.from_list("logprecis", SEQUENTIAL))
    mpl.rcParams.update(
        {
            "axes.prop_cycle": mpl.cycler(color=list(SERIES)),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": INK_MUTED,
            "axes.labelcolor": INK_MUTED,
            "axes.titlecolor": INK,
            "axes.titlelocation": "left",
            "axes.titleweight": "bold",
            "axes.grid": True,
            "grid.color": "#e6e5e2",
            "grid.linewidth": 0.8,
            "axes.axisbelow": True,
            "figure.dpi": 110,
            "figure.figsize": (8, 4),
            "lines.linewidth": 2,
            "text.color": INK,
            "xtick.color": INK_MUTED,
            "ytick.color": INK_MUTED,
            "font.size": 10,
        }
    )


if __name__ == "__main__":  # `python labs/labs_lib.py` warms the cache before a class
    for key in FILES:
        print(f"{key:<12} {fetch(key)}")
    for name, answer in fetch_incidents().items():
        print(f"{name:<12} {EVIDENCE_DIR / name}.pcap  ->  {answer}")
