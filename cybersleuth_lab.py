"""A pocket-sized CyberSleuth, for the demo in 01_intro.py.

Same rationale as autopenbench_lab.py: nothing is re-run here.  The real thing
is 30 Docker incidents, a Google Custom Search key, a vector database and six
LLM backends (https://github.com/SmartData-Polito/LLM_Agent_Cybersecurity_Forensic),
and one incident takes 5-20 minutes and real money.

What this module holds instead is the *published* evidence.  The incident table
is Table 1 of the paper; the two reasoning tracks are Appendix B verbatim (the
same incident, the same architecture, twice - once where the two agents
understand each other and once where they do not); the two web-search summaries
are Appendix C verbatim.

The one thing that *is* computed here is the Flow Summariser's token budget
(Sec. 5.3): it is four lines of arithmetic, and it is the concrete answer to
"the evidence does not fit in the context window - now what?".
"""

from typing import NamedTuple


class Incident(NamedTuple):
    """One row of Table 1: a service, a CVE, and the trace the agent is handed.

    `success` is the ground truth for the third checkpoint - the same CVE is
    fired at a vulnerable *and* at a patched version of the service, so the
    agent cannot score by recognising the exploit alone.  `packets` and `bytes_`
    are the reason architecture matters at all: they span three orders of
    magnitude, and the big ones are exactly the ones the agents lose.
    """

    id: int
    service: str
    version: str
    cve: str
    containers: int
    success: bool
    packets: int
    bytes_: int


# Table 1.  Incidents 0-19 are CFA-bench, sorted from the ones every agent
# solves to the ones none of them do; 20-29 are the 2025 test set collected for
# this paper - five services, each attacked in a vulnerable *and* a patched
# version.  Those ten are the honest evaluation: the CVEs were disclosed after
# the backends finished training, so no model can have memorised them.
INCIDENTS = (
    Incident(0, "Apache Solr", "8.11.0", "CVE-2021-44228", 1, True, 22, 2_890),
    Incident(1, "Jenkins", "2.441", "CVE-2024-23897", 1, True, 798, 2_950_000),
    Incident(2, "SaltStack", "3002", "CVE-2020-11651", 1, False, 29, 2_660),
    Incident(3, "Grafana", "8.2.6", "CVE-2021-43798", 1, True, 276, 721_730),
    Incident(4, "Apache HTTP Server", "2.4.49", "CVE-2021-41773", 1, True, 113, 13_300),
    Incident(5, "SaltStack", "2019.2.3", "CVE-2020-11651", 1, True, 32, 2_420),
    Incident(6, "Apache HTTP Server", "2.4.50", "CVE-2021-42103", 1, False, 114, 13_060),
    Incident(7, "Apache ActiveMQ", "5.14.2", "CVE-2017-15709", 1, True, 18, 1_540),
    Incident(8, "Apache ActiveMQ", "5.17.3", "CVE-2017-15709", 1, False, 12, 1_080),
    Incident(9, "CouchDB", "3.2.1", "CVE-2022-24706", 1, True, 35, 2_610),
    Incident(10, "phpMyAdmin", "4.4.15.6", "CVE-2016-5734", 1, True, 280, 65_460),
    Incident(11, "phpMyAdmin", "4.8.1", "CVE-2018-12613", 1, True, 327, 80_870),
    Incident(12, "Apache APISIX", "2.9", "CVE-2021-45232", 2, True, 390, 50_620),
    Incident(13, "Joomla", "4.2.7", "CVE-2023-23752", 1, True, 596, 205_090),
    Incident(14, "GitLab", "13.10.0", "CVE-2021-22205", 3, True, 6_680, 19_090_000),
    Incident(15, "GitLab", "13.10.3", "CVE-2021-22205", 3, False, 9_978, 25_500_000),
    Incident(16, "Apache Airflow", "1.10.10", "CVE-2020-11981", 7, True, 793, 174_130),
    Incident(17, "Cacti", "1.2.22", "CVE-2022-46169", 1, True, 2_028, 257_470),
    Incident(18, "Apache Airflow", "1.10.10", "CVE-2020-11981", 7, False, 131, 34_550),
    Incident(19, "Apache APISIX", "2.11", "CVE-2021-45232", 3, False, 500, 74_030),
    Incident(20, "Vite", "6.2.2", "CVE-2025-30208", 1, True, 24, 8_200),
    Incident(21, "Vite", "6.2.3", "CVE-2025-30208", 1, False, 24, 3_480),
    Incident(22, "Next.js", "15.2.2", "CVE-2025-29927", 1, True, 26, 11_540),
    Incident(23, "Next.js", "15.2.3", "CVE-2025-29927", 1, False, 24, 2_460),
    Incident(24, "Langflow", "1.2.0", "CVE-2025-3248", 1, True, 20, 2_180),
    Incident(25, "Langflow", "1.2.0", "CVE-2025-3248", 1, True, 135, 121_010),
    Incident(26, "Langflow", "1.5.0", "CVE-2025-3248", 1, False, 44, 6_230),
    Incident(27, "Tomcat", "9.0.97", "CVE-2025-24813", 1, False, 54, 29_590),
    Incident(28, "Erlang/OTP", "27.3.2", "CVE-2025-32433", 1, True, 20, 2_970),
    Incident(29, "Erlang/OTP", "27.3.3", "CVE-2025-32433", 1, False, 19, 2_880),
)

# The number of the last CFA-bench incident: everything above it was collected
# for this paper, after the backends' training cut-off.
DESIGN_SET = 20

# The task, from the System Instructions block of the prompt (Sec. 4.2).  Read
# the five points: they are the *report*, and checkpoints 1, 2 and 5 are the
# three numbers the benchmark scores.
CONTEXT = (
    "Analyse the provided PCAP (Packet Capture) file to accomplish the following tasks:",
    "1. Identify the name of the service or application involved.",
    "2. Determine the relevant CVE (Common Vulnerabilities and Exposures) based on the captured data.",
    "3. Gather evidence of malicious activities associated with the identified CVE.",
    "4. Assess whether the service or application is vulnerable to the identified attack.",
    "5. Evaluate whether the attack was successful.",
)

# The three checkpoints the report is graded on (Sec. 6.2), inherited from
# CFA-bench.  Each is a true/false test on the *text* of the report - no
# structured output, no parsing tricks: an expert reads it and ticks the box.
CHECKPOINTS = (
    ("Service Identification", "Did the agent name the service under attack?"),
    ("CVE Detection", "Did it name the exact CVE - not a plausible neighbour?"),
    ("Attack Success", "Did it correctly say whether the attack worked?"),
)

# The actual tshark invocations, verbatim from Sec. 5.  This is the whole
# "environment" of a forensic agent: four commands, and the choice of *which*
# ones to run - and of *who* runs them - is what separates the architectures.
# Keyed by what each command returns, deliberately: the architectures have not
# been introduced yet on the slide where this is shown, and naming them here
# would answer the question the slide is asking.
TSHARK = {
    "every packet, as text": 'tshark -r {pcap} -T fields -e frame.number -e frame.time -e frame.protocols -e _ws.col.Info\n    -> one line per packet: the whole trace as text, straight into the prompt',
    "one packet, in full": 'tshark -r {pcap} -Y "frame.number=={n}" -T fields -e data\n    -> the payload of a single packet, on request',
    "the connection list": "tshark -r {pcap} -q -z conv,tcp -z conv,udp\n    -> one line per *conversation*, not per packet",
    "one connection, in full": "tshark -r {pcap} -q -z follow,{tcp|udp},ascii,{stream}\n    -> the full application-layer exchange of one connection, as ASCII",
}


class Turn(NamedTuple):
    """One step of a two-agent reasoning track (Appendix B).

    `actor` is MA (the main agent, which reasons and searches the web) or TE
    (the Tshark Expert sub-agent, which is the only one allowed to touch the
    trace).  `note` marks the steps where the hand-off is what decides the run.
    """

    actor: str
    text: str
    note: str | None = None


# Appendix B, incident 4 - Apache HTTP Server 2.4.49, the path traversal of
# CVE-2021-41773.  Same architecture (TEA), same incident, same LLM: the only
# difference is how precise the main agent's *first* instruction happens to be.
TEA_GOOD = (
    Turn("MA", "Multiple TCP conversations on port 80: HTTP traffic. Ask the Tshark Expert to extract HTTP requests and headers.", note="Specific instruction: 'requests and headers', not 'have a look'."),
    Turn("TE", "Observes directory traversal attempts (GET /icons/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/shadow), a mix of 200 and 403 - and the server banner: Apache/2.4.49.", note="The banner. From here the CVE is one web query away."),
    Turn("MA", "Web query: 'Apache 2.4.49 directory traversal command execution vulnerability'"),
    Turn("MA", "Two candidates come back: CVE-2021-41773 (2.4.49) and CVE-2021-42013 (2.4.50). Asks TE for more evidence anyway."),
    Turn("TE", "Tries three times to filter requests containing ../ by string matching. The filters fail each time.", note="tshark syntax, not forensics: the sub-agent's own tooling is what fails."),
    Turn("MA", "Instructs TE to refine the regular expression and retry."),
    Turn("TE", "The refined filter works - but requests alone do not disambiguate the two CVEs."),
    Turn("MA", "Links the banner Apache/2.4.49 to CVE-2021-41773. Traversals answered with 200 -> attack successful.", note="✅ Service, CVE and success: all three checkpoints."),
)

TEA_BAD = (
    Turn("MA", "Multiple TCP conversations on port 80: HTTP traffic. Requests HTTP requests and headers to identify the service and possible attack patterns."),
    Turn("TE", "Extracts the requests: empty User-Agent, no Referer, no Cookie. Detects the ../ traversal attempts but *fails to identify the service*.", note="⚠️ The banner is in the trace. It just did not come back."),
    Turn("MA", "Notes the traversal, asks for a deeper look at the HTTP URIs to pin the service down."),
    Turn("TE", "Returns /etc/passwd, /etc/shadow, /var/log/syslog. Command syntax errors while correlating streams. Confirms traversal.", note="More evidence of the *attack*, still nothing about the *service*."),
    Turn("MA", "Gives up on the service and searches the web anyway: 'web service directory traversal vulnerability'", note="⚠️ The broad query. This is the step the run is lost at."),
    Turn("MA", "Gets candidates across unrelated products - Cisco ASA, Barracuda, WordPress plugins - and picks CVE-2020-3452 (Cisco ASA)."),
    Turn("MA", "Asks TE for the HTTP responses to the suspicious requests."),
    Turn("TE", "Status 200, leaking /etc/passwd and /etc/hosts. Confirms the traversal succeeded.", note="The evidence is *correct*, and it arrives after the conclusion."),
    Turn("MA", "Final report: Cisco ASA, CVE-2020-3452, attack successful.", note="❌ Service and CVE wrong; 'successful' right, for the wrong system."),
)

# Appendix C, incident 12 - Apache APISIX 2.9.  Both backends run the *same*
# architecture (FRA) and retrieve the *same* two candidate CVEs from the web.
# What differs is only the summary each one writes for itself.
APISIX_GPT4O = (
    "CVE-2021-45232: This vulnerability affects the Apache APISIX Dashboard, enabling unauthorized access "
    "that leads to remote code execution (RCE). It is critical for analyzing systems using Apache APISIX "
    "since unauthorized users could potentially execute arbitrary code [...]",
    "CVE-2022-24112: This CVE pertains to a Remote Code Execution vulnerability in Apache APISIX versions "
    "prior to 2.10.0. It is highly relevant for forensic analysts investigating unauthorized execution "
    "incidents involving APISIX 2.9.0 [...]",
)

APISIX_GPT5 = (
    "CVE-2021-45232: Apache APISIX Dashboard (Manager API) exposed the /apisix/admin/migrate/import endpoint "
    "without proper authentication [...] This directly matches the 'Manager API migrate import' RCE vector "
    "under analysis.",
    "CVE-2022-24112: [...] Often seen in combination with CVE-2021-45232 (e.g., enabling or configuring the "
    "plugin via migrate/import) but NOT APPLICABLE IN THIS CASE, since no evidence of the batch-requests "
    "plugin was observed in the traffic.",
)

# Sec. 7.1 and Appendix C: how often each backend got incident 12 right, out of
# three runs. Same evidence, same candidates - different reading of them.
APISIX_RUNS = {"GPT-4o": 1, "GPT-5": 3}


def benchmark(incidents: tuple[Incident, ...] = INCIDENTS) -> list[str]:
    """The benchmark in one screen: what the agent is handed, per incident.

    Two columns carry the whole difficulty argument - `packets`, which spans
    12 to ~10 000, and `success`, which is False in a third of the cases.
    """
    lines = [f"{'id':>3}  {'service':<20} {'version':<10} {'CVE':<16} {'pkts':>6} {'volume':>9}  attack"]
    for one in incidents:
        volume = f"{one.bytes_ / 1e6:.1f}MB" if one.bytes_ >= 1e6 else f"{one.bytes_ / 1e3:.1f}KB"
        lines.append(f"{one.id:>3}  {one.service:<20} {one.version:<10} {one.cve:<16} {one.packets:>6} {volume:>9}  {'succeeded' if one.success else 'failed'}")
    return lines


def spread(incidents: tuple[Incident, ...] = INCIDENTS) -> list[str]:
    """Why 'read the trace' is not one task but many.

    The point of this table is the ratio between the smallest and the largest
    incident: an architecture that works on 12 packets need not work on 10 000.
    """
    packets = sorted(one.packets for one in incidents)
    volumes = sorted(one.bytes_ for one in incidents)
    succeeded = sum(1 for one in incidents if one.success)
    return [
        f"incidents          {len(incidents)}  ({DESIGN_SET} design set + {len(incidents) - DESIGN_SET} test set, 2025 CVEs)",
        f"attack succeeded   {succeeded} of {len(incidents)}  (design set: 14 of 20 -> always answering 'successful' already scores 70%)",
        f"packets            {packets[0]} to {packets[-1]}  ({packets[-1] // packets[0]}x)",
        f"traffic volume     {volumes[0] / 1e3:.1f}KB to {volumes[-1] / 1e6:.1f}MB  ({volumes[-1] // volumes[0]}x)",
    ]


def allocate(tokens: dict[str, int], budget: int) -> list[str]:
    """The Flow Summariser's square-root token budget (Sec. 5.3).

    The problem: the payloads of all connections do not fit in the context
    window, and a *proportional* split would hand the whole budget to the one
    bulk transfer and nothing to the four-packet exploit.  The fix is to
    allocate on the square root of each connection's size, which is the whole
    of the arithmetic below:

        allocation_i = budget * sqrt(tokens_i) / sum_j sqrt(tokens_j)

    capped so that a small connection never gets more than it needs.  Compare
    the last two columns: this is the design decision that keeps the *evidence*
    in the prompt.
    """
    roots = {name: size**0.5 for name, size in tokens.items()}
    total = sum(roots.values())
    raw = sum(tokens.values())
    lines = [f"{'connection':<30} {'tokens':>8} {'proportional':>13} {'sqrt-based':>11}  kept"]
    for name, size in tokens.items():
        fair = int(budget * size / raw)
        allocation = min(size, int(budget * roots[name] / total))
        lines.append(f"{name:<30} {size:>8} {fair:>13} {allocation:>11}  {allocation / size:>4.0%}")
    return lines


def track(run: tuple[Turn, ...]) -> list[str]:
    """One TEA reasoning track, main agent and sub-agent interleaved.

    Read only the `MA -> TE` hand-offs: in both runs the *evidence* in the trace
    is identical, and what differs is what the sub-agent chose to report back.
    """
    lines = []
    for number, turn in enumerate(run, start=1):
        lines.append(f"{number:>2} [{turn.actor}]  {turn.text}")
        if turn.note:
            lines.append(f"        ^^ {turn.note}")
    return lines


def summaries(name: str, entries: tuple[str, ...], runs: int) -> list[str]:
    """The web-search summaries one backend wrote for itself, on incident 12.

    Both backends saw the same two CVEs.  The summary is the only thing that
    reaches the main agent's context - so the summary *is* the evidence.
    """
    lines = [f"--- {name}: correct CVE in {runs}/3 runs ---"]
    for entry in entries:
        lines.extend(["", entry])
    return lines
