"""Long-form content for 01_intro.py.

The viewer only swaps the *first* line of a call for its rendering, so every
continuation line of a multi-line call is printed as raw code underneath it.
Anything too long to fit on one lecture line therefore lives here, and the
lecture keeps a single readable call.
"""

# The 2024 -> 2026 threat-landscape table, kept in the order the slide reads it:
# what changed, then why the change matters for the rest of the lecture.
THREAT_LANDSCAPE = {
    "headers": ["Signal", "2024", "2026", "Why it matters"],
    "rows": [
        [
            "⚡ Attackers are faster",
            "Breakout time: **62 min** on average, **2m 07s** at best",
            "**29 min** on average, **27 s** at best",
            "Human-only response does not match attacker speed",
        ],
        [
            "🚨 The exfiltration window is collapsing",
            "Compromise → exfiltration: **2 days** median, **285 min** for the fastest 25%",
            "Median still 2 days, but **72 min** for the fastest 25%; **22%** under one hour",
            "The fastest attacks got **~4x faster**",
        ],
        [
            "📈 Defence is a data-scale problem",
            "**78T** security signals processed per day",
            "**100T+** signals/day, plus 38M identity-risk detections and ~5B emails/day",
            "Human analysts cannot keep up with telemetry",
        ],
        [
            "🕸️ One attack, many fronts",
            "Cloud intrusions **+75%** in one year; attackers who *specifically* go after the cloud **+110%**",
            "**87%** of attacks hit more than one front — endpoint, cloud, identity, email — up to **10** at the same time",
            "No single tool sees the whole attack: the clues must be joined across domains",
        ],
        [
            "👥 Skills do not scale",
            "**90%** report a skills gap; **44%** critical or significant",
            "**95%** report at least one skill need; **59%** critical or significant; **88%** already paid for it",
            "More technology, not enough expertise to operate it",
        ],
        [
            "🤖 AI in the attacker's hands",
            "Nation-state actors and hacktivists *experimenting* with GenAI",
            "AI-enabled adversary activity **+89%** YoY: recon, credential theft, evasion, personas",
            "From *future risk* to routine",
        ],
        [
            "🛡️ AI in the defender's hands",
            "Companies using AI & automation heavily paid **$2.2M less** per breach than those that did not",
            "Still **$1.93M less** per breach - and IBM's own AI-run SOC handles ~**95%** of daily investigations, saving **850+ analyst-hours a month** and **37%** of the time per investigation",
            "The gain is measured, not promised: it is already running in production",
        ],
        [
            "💰 Failure stays expensive",
            "**$4.88M** average breach cost (+10% YoY)",
            "**$4.99M**, an all-time record (+12%)",
            "Around **$5M** per breach, at record levels",
        ],
    ],
    "widths": ["22%", "24%", "28%", "26%"],
    "caption": (
        "Sources: CrowdStrike Global Threat Report "
        "[2024](https://www.crowdstrike.com/en-us/press-releases/2024-crowdstrike-global-threat-report-release/) · "
        "[2026](https://www.crowdstrike.com/en-us/press-releases/2026-crowdstrike-global-threat-report/) - "
        "Unit 42 Incident Response Report "
        "[2024](https://www.paloaltonetworks.com/blog/2024/02/unit-42-incident-response-report/) · "
        "[2026](https://www.paloaltonetworks.com/resources/research/unit-42-incident-response-report) - "
        "Microsoft Digital Defense Report "
        "[2024](https://www.microsoft.com/en-ie/security/security-insider/intelligence-reports/microsoft-digital-defense-report-2024) · "
        "[2025](https://www.microsoft.com/en-us/corporate-responsibility/topics/cybersecurity/reports/microsoft-digital-defense-report-2025/) — "
        "ISC2 Workforce Study "
        "[2024](https://www.isc2.org/Insights/2024/10/ISC2-Workforce-Study-AI-Growth-Opportunity) · "
        "[2025](https://www.isc2.org/insights/2025/12/2025-ISC2-Cybersecurity-Workforce-Study) - "
        "IBM Cost of a Data Breach "
        "[2024](https://www.ibm.com/downloads/documents/us-en/107a02e94948f4ec) · "
        "[2026](https://www.ibm.com/reports/data-breach) - "
        "[WEF, Empowering Defenders 2026](https://www.weforum.org/publications/empowering-defenders-ai-for-cybersecurity/)"
    ),
}
# Caption for the Huawei use-case animation: the deployment the lecture walks
# through, from firewall to human validation.
HUAWEI_USECASE = (
    "**The struggle, in one picture.** In a commercial deployment, what the firewall does not block still raises "
    "**12M events**: an IDS ranks them by level of risk - critical, medium, false alarm - and a security expert has to "
    "validate the verdicts, one by one. The Sisyphus icons mark the struggling steps. "
    "Source: [Bui et al., *A Systematic Comparison of Large Language Models Performance for Intrusion Detection*, "
    "ACM CoNEXT 2024](https://dl.acm.org/doi/abs/10.1145/3696379)"
)

# Kahneman's two systems, mapped onto the SOC pipeline of the previous slide:
# the last row is the bridge to the two halves of the lecture (fast / slow).
FAST_SLOW_THINKING = {
    "headers": ["", "⚡ System 1 - fast", "🐢 System 2 - slow"],
    "rows": [
        [
            "🧠 How it works",
            "Automatic, associative, effortless: **pattern matching** against what it has already seen",
            "Deliberate, step-by-step, effortful: **reasoning** about something new",
        ],
        [
            "⏱️ Cost per item",
            "Milliseconds, essentially free - it runs whether you want it or not",
            "Minutes to hours, and it **competes** with everything else you are doing",
        ],
        [
            "📦 Volume it can face",
            "The **whole stream**: every packet, every log line, every event",
            "Only the **few** items that survived the triage",
        ],
        [
            "❓ Question it answers",
            "*Is this like something I have seen before?*",
            "*What actually happened here, and what do we do about it?*",
        ],
        [
            "🖥️ In the SOC",
            "Firewall rules, IDS scoring, traffic/log clustering, anomaly detection. **And the upkeep that keeps them working**: writing the signature for an attack first seen yesterday, retuning a threshold that now fires on everything, redefining what 'normal traffic' means after the network changed",
            "Alert validation, root-cause analysis, threat hunting, incident response, pentesting",
        ],
        [
            "💥 Failure mode",
            "Confidently blind to the **never-seen-before** attack - and it buries you in false positives",
            "Correct but **too slow**: it does not run 12M times a day",
        ],
        [
            "🤖 AI that fits",
            "Small, cheap, high-throughput models: embeddings and encoders - [DarkVec](https://dl.acm.org/doi/10.1145/3485983.3494863), [LogPrecis](https://www.sciencedirect.com/science/article/pii/S0167404824001068)",
            "Agentic LLMs that plan, call tools and iterate - [AutoPenBench](https://aclanthology.org/2025.emnlp-industry.114/), [CyberSleuth](https://arxiv.org/abs/2508.20643)",
        ],
    ],
    "widths": ["16%", "42%", "42%"],
    "caption": ("The two systems follow Daniel Kahneman, " "[*Thinking, Fast and Slow*](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow) (2011) - " "Nobel Memorial Prize in Economic Sciences, " "[2002](https://www.nobelprize.org/prizes/economic-sciences/2002/kahneman/facts/). " "<br>The last two rows are where the rest of this lecture lives."),
}


# The card that introduces Kahneman's book, just before the two-systems list.
# It carries one job only - "this is a book, not a paper" - because the Nobel
# and the year are already in the FAST_SLOW_THINKING caption a few lines later.
KAHNEMAN_BOOK = "📖 **A book, not a paper.** What we borrow from it is not a result to cite, but a **vocabulary**: *System 1* (fast) and *System 2* (slow)."

KAHNEMAN_SOURCE = "Cover: [Wikipedia](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow), reproduced to identify the work under discussion."
