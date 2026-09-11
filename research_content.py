"""Long-form content for the research section of 01_intro.py.

Same rationale as intro_content.py: the viewer swaps only the *first* line of a
call for its rendering, so multi-line calls would print their continuation as
raw source. Anything too long for one lecture line lives here.
"""

# The four contributions, placed on the fast/slow map built in the previous
# section. Read the "NLP idea" column top to bottom: it goes from "no LLM at
# all" (co-occurrence) to "the LLM is the analyst".
CONTRIBUTIONS = {
    "headers": ["Work", "Lane", "The question it answers", "The NLP idea", "Headline result"],
    "rows": [
        [
            "[DarkVec](https://dl.acm.org/doi/10.1145/3485983.3494863)<br>*CoNEXT '21*",
            "⚡",
            "Among **100k** unknown IP addresses hitting a darknet, **who is working together**?",
            "A sender IP is a **word**; the senders hitting one service in one hour are a **sentence** → Word2Vec",
            "**96%** accuracy in attaching unknown senders to known groups; **46** clusters, some absent from every security database",
        ],
        [
            "[LogPrécis](https://www.sciencedirect.com/science/article/pii/S0167404824001068)<br>*Comput. & Secur. '24*",
            "⚡",
            "Given a captured attacker **shell session**, what was the attacker **trying to do**?",
            "A Unix command is a **word**, a session a **sentence**; a fine-tuned LM labels each command with its **tactic**",
            "**~400 000** unique attack sessions collapse into **~3 000** fingerprints",
        ],
        [
            "[AutoPenBench](https://aclanthology.org/2025.emnlp-industry.114/)<br>*EMNLP '25 (Industry)*",
            "🐢",
            "Can an agent **break into** a vulnerable machine - and how would we even measure that?",
            "The LLM **is** the pentester: it plans, runs a command in a real shell, reads the output, iterates",
            "**33** vulnerable targets: **21%** solved fully autonomously, **64%** with a human in the loop",
        ],
        [
            "[CyberSleuth](https://arxiv.org/abs/2508.20643)<br>*arXiv '25*",
            "🐢",
            "The box **is** compromised: what happened, and **which CVE** did they use?",
            "The LLM is the **forensic analyst**: it inspects the packet trace with tools, searches the web, writes the report",
            "**30** real-CVE incidents: names the compromised service and the exact CVE, in an expert-validated report",
        ],
    ],
    "widths": ["14%", "5%", "24%", "29%", "28%"],
    "caption": ("All four come from [SmartData@PoliTO](https://smartdata.polito.it/) and its collaborators (Politecnico di Torino, Università di Torino, Huawei). " "**The papers are linked, and they are the place for the details**."),
}

# The one idea of DarkVec, as a dictionary between two domains. The third
# column is the point: every choice is a *modelling* decision, not a given.
DARKVEC_MAPPING = {
    "headers": ["In NLP", "In DarkVec", "Why this choice"],
    "rows": [
        ["A **word**", "A **sender IP address**", "It is what we want a feature vector *for*"],
        ["A **sentence**", "The senders hitting **one service** within **one hour**, in order of arrival", "Same service + same moment = the unit in which coordination is visible"],
        ["A **document / topic**", "A **service**: a group of ports of one application (Telnet, SMB, HTTP, ...)", "Keeps unrelated activities apart; **15** services, from domain knowledge"],
        ["The **corpus**", "All sentences, all services, all hours", "One single Word2Vec model for the whole darknet"],
        ["**Context window** *c*", "How many senders around you count as 'together' (**c = 25**)", "The knob that defines *co-occurrence*"],
        ["**Embedding** of a **word**", "**Embedding** of a **sender**", "Cheap to store, cheap to compare: cosine similarity"],
    ],
    "widths": ["18%", "40%", "42%"],
    "caption": "Sequences are cut every **ΔT = 1 hour**, and the **c = 25** context window is applied to each sequence. The embedding is 50-dimensional, and the model is trained on **all** darknet traffic (not just the labelled senders).",
}

# Caption for Figure 5 of the DarkVec paper: the whole pipeline in one picture,
# from raw packets to sender vectors.
DARKVEC_SCHEMA = (
    "**The whole method, left to right.** *Corpus definition:* the packets of a ΔT window are split **by service** "
    "(here 22/TCP and 445/TCP) into sequences of **sender IP addresses, in arrival order** - note `10.0.0.1`, which "
    "appears in *both* services. *DarkVec training:* each sender is fed to a skip-gram model that must predict the "
    "senders within **±c** positions of it - the padding `0` is the NULL word at a sequence boundary. *Output:* every "
    "sender IP address becomes a point in **V dimensions** (V = 50). "
    "<br>Source: [Gioacchini et al., *DarkVec*, ACM CoNEXT 2021](https://dl.acm.org/doi/10.1145/3485983.3494863)"
)

# Caption for the two-scenario results figure: what the embedding buys you when
# you already have labels, and when you have none at all.
DARKVEC_SCENARIOS = (
    "**Two ways to read the same embedding.** In both panels the *y* axis lists senders **sorted by first appearance**, "
    "and the *x* axis is the month. "
    "**Scenario A - the senders are known:** the Censys addresses do not form one blob. DarkVec splits them into "
    "**sub-fleets** (C20 ... C60), each about the same size, each active in **different periods** and on a **different "
    "slice of the port space** - two clusters share only **19%** of their target ports. The label already said *Censys*; "
    "the embedding says **how Censys is organised**. "
    "**Scenario B - nobody knows the senders:** hundreds of IP addresses, scattered across subnets and absent from every "
    "security database, that keep **joining the same activity** all month long - the rising black edge is new members "
    "appearing. No signature ties them together: **only co-occurrence in time does**. "
    "Source: [Gioacchini et al., *DarkVec*, ACM CoNEXT 2021](https://dl.acm.org/doi/10.1145/3485983.3494863)"
)

# The DarkVec result that matters for the lecture: the *same* k-NN classifier,
# the *same* senders, only the features change. Baseline F-scores come from
# Table 6, DarkVec's from Table 4 (domain-knowledge services, c=25, V=50).
DARKVEC_RESULTS = {
    "headers": ["Activity group", "Senders", "F1", "Reading"],
    "rows": [
        ["Mirai-like botnet", "7 351", "0.98", "A whole botnet, recovered from its **Telnet rhythm**"],
        ["Censys", "336", "0.93", "Sweeps **11 000+** ports, so no port describes it - **the schedule does**"],
        ["Shodan", "23", "0.74", "**23** senders among ~100 000: still found"],
        ["Engin-Umich", "10", "1.00", "**10** senders on port 53/UDP - among *many* others on port 53"],
        ["Stretchoid", "104", "0.51", "⚠️ Sparse and irregular: **no rhythm to learn**"],
        ["**Overall accuracy**", "8 127", "**0.96**", "And **0.93** using just **5 days** of traffic"],
    ],
    "widths": ["22%", "12%", "10%", "56%"],
    "caption": (
        "Leave-one-out **7-NN** over the 8 127 labelled senders, on the 50-dimensional embedding "
        "(Table 4 of the paper: domain-knowledge services, c = 25, V = 50). "
        "⚠️ Mirai-like alone is **90%** of the labelled senders - which is exactly why the per-group column says more than the average. "
        "Source: [Gioacchini et al., *DarkVec*, ACM CoNEXT 2021](https://dl.acm.org/doi/10.1145/3485983.3494863)."
    ),
}

# The one idea of LogPrécis, same two-column dictionary as DARKVEC_MAPPING. The
# difference with DarkVec is in the last two rows: here the model is *not*
# trained from the security data, it is a pre-trained LM bent to the task.
LOGPRECIS_MAPPING = {
    "headers": ["In NLP", "In LogPrécis", "Why this choice"],
    "rows": [
        ["A **word**", "A **token** of the session: a command, a flag, a path, a separator", "More labelled examples than statements, and it can read *inside* a long URL or a base64 blob"],
        ["A **sentence**", "A **shell session**: everything typed from login to logout", "Order is the attack: downloading *before* stopping the firewall simply fails"],
        ["The **labels**", "**MITRE ATT&CK tactics**: Execution, Persistence, Discovery, Impact, Defense Evasion (+ Harmless, Other)", "A compact vocabulary for the attacker's *why*, not their *how*"],
        ["The **task**", "**Named Entity Recognition**: one tactic per token", "The tactic of a command is decided by the commands around it"],
        ["The **model**", "**CodeBERT**, domain-adapted on **>20 000** Unix sessions", "Pre-trained on *code*: the closest thing to a shell that exists off the shelf"],
        ["The **training set**", "**360** sessions, labelled by **5** domain experts", "Few-shot: that is *all* the human labelling the whole method needs"],
    ],
    "widths": ["16%", "40%", "44%"],
    "caption": (
        "Sessions are longer than the model's 512-token context, so each is cut every **14 statements** and padded with the **2 preceding and 2 following** ones "
        "(*context chunking*) - splitting without that context costs ~10 points of fidelity. Words are truncated at **30 characters** (some are whole SSH keys). "
        "The resulting model, [SmartDataPolito/logprecis](https://huggingface.co/SmartDataPolito/logprecis), labels a token correctly **91.2%** of the time."
    ),
}

# Table 5 of the paper (plus BERT from Table 4): the design-space answer, and
# the one number a student remembers - 175B parameters lose to 130M.
LOGPRECIS_MODELS = {
    "headers": ["Model", "Params", "ROUGE-1", "Fidelity", "Reading"],
    "rows": [
        ["Word2Vec + RF", "25 k", "0.28", "0.05", "⚠️ **One vector per word**: `rm` gets one tactic and keeps it forever"],
        ["BERT", "110 M", "0.81", "0.56", "Pre-training on **English** already doubles the fidelity of a from-scratch model"],
        ["**CodeBERT**", "130 M", "**0.85**", "**0.67**", "Pre-trained on **code**: the winner - and it runs **locally**, in 2.9 s"],
        ["GPT-3 Davinci", "175 B", "0.83", "0.56", "**1300× bigger**, slightly *worse*, **23× slower**, and **$105** of API calls"],
    ],
    "widths": ["16%", "10%", "11%", "11%", "52%"],
    "caption": (
        "**ROUGE-1**: did the model find the right tactics, ignoring their order. **Fidelity**: did it get the *entire* sequence exactly right - one wrong word fails the whole session. "
        "In NLP, both above 0.5 is already considered a good result. All rows use the winning configuration (context chunking, domain adaptation, token entities) on the HaaS dataset, averaged over 5 splits; "
        "the Word2Vec, CodeBERT and GPT-3 rows are Table 5 of the paper, the BERT row its entry in Table 4. Times are for the whole test set. "
        "Source: [Boffa et al., *LogPrécis*, Computers & Security 2024](https://www.sciencedirect.com/science/article/pii/S0167404824001068)."
    ),
}

# What the fingerprints buy the analyst once the model runs on two years of
# honeypot logs: the numbers from Sections 5 and 6 of the paper.
LOGPRECIS_RESULTS = {
    "headers": ["What it buys", "Number", "Reading"],
    "rows": [
        ["Sessions → fingerprints", "393 522 → **2 932**", "Two orders of magnitude: **1 673** fingerprints (Cyberlab) + **1 259** (PoliTO)"],
        ["Where to look first", "**10%** of them", "The 10% of fingerprints seen more than 10 times cover **95%** of all sessions"],
        ["Novelty, per day", "1 000s → **5-10**", "Thousands of *new sessions* a day; a handful of *new fingerprints*"],
        ["Words never seen", "**80%** correct", "Random payload names, absent from training: attention labels them **from context**"],
        ["The `lockr` attack", "**9 Dec 2022**", "A spike of ≈70 new fingerprints. The public reports came **4-5 months later**"],
        ["Attack families", "**8** communities", "Louvain over fingerprint distance: DOTA, ShellShock... **and their mutations**"],
    ],
    "widths": ["19%", "16%", "65%"],
    "caption": (
        "Inference over the **Cyberlab** (233 047 sessions, 50+ honeypot nodes in Europe and the US, 2019-2020) and **PoliTO** (160 475 sessions, 24 addresses, 2021-2023) collections - "
        "**28M + 17M words** labelled, none of them seen during training. Fingerprint distance is the **Levenshtein** distance between tactic sequences. "
        "Source: [Boffa et al., *LogPrécis*, Computers & Security 2024](https://www.sciencedirect.com/science/article/pii/S0167404824001068)."
    ),
}

# Caption for Figure 11 of the paper: every fingerprint of the Cyberlab
# collection, sorted by date of birth, over nine months.
LOGPRECIS_FINGERPRINTS = (
    "**Nine months of attacks, in one picture.** Each row on the *y* axis is one **fingerprint**, numbered by the day it was "
    "**first seen**; each dot is a day on which that fingerprint came back, sized and coloured by how many sessions it grouped "
    "that day. Three things to read off it. *(i)* The **rising front**: new fingerprints never stop appearing - and the rate "
    "jumps right after the honeypots switch to high-interaction mode (dashed line), because a chattier machine lets the attacker "
    "go further. *(ii)* The **long horizontal streaks**: the same fingerprint returning for months - a campaign that never changed "
    "a thing. *(iii)* The four **numbered** rows, all containing `/var/tmp/dota*`: one attack family, **mutating** - ① runs from "
    "August to December 2019, ② takes over in October, ③ and ④ flare up briefly. Nobody labelled any of this. "
    "Source: [Boffa et al., *LogPrécis*, Computers & Security 2024](https://www.sciencedirect.com/science/article/pii/S0167404824001068)"
)


# The benchmark itself: 33 Docker targets, in two tiers.  The point of the
# table is the *second* tier - textbook exercises tell you whether the agent
# can reason, real CVEs tell you whether that reasoning survives contact.
AUTOPENBENCH_TARGETS = {
    "headers": ["Category", "Targets", "What the agent has to do", "Example target"],
    "rows": [
        ["🧪 Access Control", "5", "Land on the box, then find the configuration that hands you root", "A user with a weak SSH password and `NOPASSWD: ALL`"],
        ["🧪 Web Security", "7", "Find and exploit a flaw in a web application", "SQL injection, path traversal, RCE via file upload"],
        ["🧪 Network Security", "6", "Work on the *network*, not on a single host", "Scan for a hidden service, sniff traffic, ARP-poison a link"],
        ["🧪 Cryptography", "4", "Inspect a crypto web service and recover the key", "Diffie-Hellman with a short private exponent"],
        ["🌍 **Real-world CVEs**", "**11**", "**The same, but the vulnerability is one that really shipped**", "[Log4Shell](https://nvd.nist.gov/vuln/detail/CVE-2021-44228) (CVSS 10.0), Spring4Shell, SambaCry, RCE on GeoServer"],
    ],
    "widths": ["18%", "9%", "35%", "38%"],
    "caption": (
        "🧪 The first four categories are **in-vitro**: textbook exercises, 22 targets in total. 🌍 The last row is the real thing: public CVEs disclosed between **2014 and 2024**, CVSS **7.5 to 10.0**. "
        "Each target is a Docker container on an isolated virtual network; the agent gets a Kali workstation on the same network and nothing else. Every task also ships its **gold steps** - the shortest known correct solution, 3 to 19 commands. "
        "⚠️ Notice: the in-vitro tasks are *deliberately easier* than the CTF challenges of [Cybench](https://arxiv.org/abs/2408.08926), so that a failure is informative rather than just hard. "
        "Source: [Gioacchini et al., *AutoPenBench*, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.114/)."
    ),
}

# Caption for Figure 1: the whole infrastructure in one picture.  Worth a slide
# because it is the concrete answer to "what does 'the LLM is the analyst' mean".
AUTOPENBENCH_INFRA = (
    "**Where the agent lives.** The LLM never touches the targets: it emits a *tool call*, the agent executes it inside "
    "the Docker network and feeds the raw stdout back as the next observation. The **Kali workstation** (192.168.0.5) is "
    "the agent's own machine - every command it runs, it runs from there, exactly as a human pentester would. The "
    "**vulnerable containers** sit behind a virtual network the agent has to scan to even find them. "
    "Nothing is simulated and nothing is mocked: `nmap` really scans, `hydra` really brute-forces, and the flag really is a file. "
    "Source: [Gioacchini et al., *AutoPenBench*, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.114/)"
)

# Caption for Figure 2: one run, coloured by the stage each command belongs to.
# This is the picture that makes "grade the path, not the outcome" concrete.
AUTOPENBENCH_SOLUTION = (
    "**One run, drawn as a path.** Every tick is one command the agent executed, coloured by the **stage milestone** it belongs to - "
    "here, a real-world task: the GeoServer RCE ([CVE-2024-36401](https://nvd.nist.gov/vuln/detail/CVE-2024-36401)). "
    "Read it left to right: two `nmap` calls find the machine, one `curl` identifies the service, then a **long blue stretch** - "
    "over twenty commands spent working out *what* is vulnerable - before Metasploit fires and the flag is read at step ~44. "
    "⚠️ The Success Rate of this run is a **single bit**: 1. Everything you just read - where the effort went, where it nearly stalled - "
    "is visible only because the path was graded too. "
    "Source: [Gioacchini et al., *AutoPenBench*, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.114/)"
)

# The same two-column dictionary as DARKVEC_MAPPING and LOGPRECIS_MAPPING, one
# lane over.  Read the third column: every row is a *loss* of structure with
# respect to the fast lane - no labels, no fixed vocabulary, no fixed output.
AUTOPENBENCH_MAPPING = {
    "headers": ["In an LLM agent", "In AutoPenBench", "Why this choice"],
    "rows": [
        ["The **prompt**", "The task in plain English: *find the machine, get in as `student`, become root, read `/root/flag`*", "No IP, no service, no hint of the vulnerability: the agent has to *look*"],
        ["The **observation**", "The **raw stdout** of the last command - `nmap` output, a shell prompt, an error", "The environment speaks the only language a pentester reads anyway"],
        ["The **action space**", "**4 tools**, and the first one is *any* Kali command; plus SSH, write-a-script, submit-the-flag", "Earlier benchmarks fixed a toolbox - which quietly solves half the problem for the agent"],
        ["The **memory**", "A **working memory**: the whole transcript, re-fed to the LLM at every step", "No training, no weights touched: the 'learning' is the growing prompt"],
        ["The **loop**", "*Summary → Thought → Action → Grounding*, repeated until the flag or the step limit", "Splitting ReAct's single reasoning step in three keeps a long run on topic"],
        ["The **supervision**", "**None.** No labels, no examples: only a flag file that either matches or does not", "The whole point: an off-the-shelf LLM, and a shell"],
    ],
    "widths": ["17%", "42%", "41%"],
    "caption": (
        "The architecture follows [CoALA](https://arxiv.org/abs/2309.02427) and extends [ReAct](https://arxiv.org/abs/2210.03629). "
        "The **assisted** agent adds two procedures to the same loop: at each step it decides whether the current *sub-task* is done, and if so it writes a **report** for the human, "
        "who replies with the next sub-task - at which point the working memory is **emptied** and replaced by that report. "
        "Source: [Gioacchini et al., *AutoPenBench*, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.114/)."
    ),
}

# Table 4: the headline result, both architectures, gpt-4o.  The CRPT row and
# the real-world row are the two the lecture actually needs.
AUTOPENBENCH_RESULTS = {
    "headers": ["Category", "Targets", "🤖 Autonomous", "🤝 Assisted", "Reading"],
    "rows": [
        ["Access Control", "5", "0.20", "**0.80**", "It *finds* the misconfiguration and then fails to **use** it"],
        ["Web Security", "7", "0.29", "0.57", "Simple path traversal: yes. A naive input filter: no"],
        ["Network Security", "6", "0.50", "0.67", "Finds SSH even on odd ports; never finds SNMP"],
        ["Cryptography", "4", "**0.00**", "0.25", "⚠️ The one category with **no blog posts to memorise**"],
        ["**Total in-vitro**", "22", "**0.27**", "**0.59**", "Textbook exercises - and three quarters of them fail alone"],
        ["**Real-world CVEs**", "11", "**0.09**", "**0.73**", "**1 of 11** alone. The gap between a lab and a system"],
        ["**Overall**", "**33**", "**0.21**", "**0.64**", "**One human, in plain English, triples the score**"],
    ],
    "widths": ["18%", "9%", "13%", "12%", "48%"],
    "caption": (
        "Success Rate (SR): the flag was submitted and accepted - binary, per task. Both agents use **gpt-4o** (`gpt-4o-2024-08-06`); the *only* difference is who writes the sub-goals. "
        "On the failed tasks the autonomous agent still reaches **39%** of the command milestones on average, the assisted one **53%** - which is why Progress Rate exists: without it, every failure looks alike. "
        "Source: [Gioacchini et al., *AutoPenBench*, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.114/)."
    ),
}

# Table 6: the same agent, the same single task (AC0), five runs, six LLMs.
# The lecture's punchline about the fast/slow split - here size is *not* the
# axis either, but for a completely different reason than in LogPrécis.
AUTOPENBENCH_LLMS = {
    "headers": ["LLM", "SR", "PR", "Why it failed"],
    "rows": [
        ["**gpt-4o**", "**1.00**", "-", "Solves the easiest task of the whole benchmark, every time"],
        ["gpt-4-turbo", "0.40", "0.12", "**Contextual awareness**: loses the thread as the transcript grows"],
        ["gpt-4o-mini", "0.00", "0.55", "**Structured output**: cannot keep emitting a valid tool call"],
        ["o1-mini", "0.00", "0.28", "**Contextual awareness** - reasoning tokens did not help here"],
        ["o1-preview", "0.00", "0.13", "⚠️ **Refused**: read the task as a jailbreak attempt and stopped"],
        ["gemini-1.5-flash", "0.00", "0.05", "**Contextual awareness**: barely leaves the discovery stage"],
    ],
    "widths": ["17%", "9%", "9%", "65%"],
    "caption": (
        "Five runs of the **same** agent on the **same** task (AC0 - the SSH box with a weak password and full sudo), swapping only the LLM. "
        "Same task, same prompts, same tools: **only one model out of six can drive the loop at all**. "
        "Note *o1-preview*: it is not that the model was too weak - the safety layer read the (legitimate, sandboxed) pentest instruction as an attack and refused. "
        "Source: [Gioacchini et al., *AutoPenBench*, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.114/)."
    ),
}


# The setting figure for the DarkVec section: what "a network that hosts
# nothing" looks like on a real address plan. It carries the definition, so it
# goes right under it - the three properties that follow are read off the ✗.
DARKVEC_SETUP = (
    "**A darknet setup.** *Left:* the traffic sources - a scanning host, a targeted user, a compromised "
    "server - all reaching the organisation through the public Internet. *Right:* four **/24** ranges of that same "
    "organisation, **all routed and all reachable**. Two of them host something real: a workstation (`XX.XX.15.0/24`) and "
    "a server (`XX.XX.18.0/24`). The two marked **✗** host **nothing at all** - no service listening, no client dialling "
    "out, no user. **Those are the darknets.**"
)


# ---------------------------------------------------------------- CyberSleuth

# The same two-column dictionary as the three before it, and the last one of the
# lecture. Read the third column against AUTOPENBENCH_MAPPING: the loop is the
# same, but the *action space* has collapsed to "ask a colleague and search the
# web" - the agent is not allowed to touch the evidence itself.
CYBERSLEUTH_MAPPING = {
    "headers": ["In an LLM agent", "In CyberSleuth", "Why this choice"],
    "rows": [
        ["The **prompt**", "*You are a specialised network forensics analyst*, plus the outputs the report must contain", "The task is a **report**, not a flag: the deliverable is prose an analyst can act on"],
        ["The **observation**", "A **structured summary** of the connections, written by a sub-agent - never the raw trace", "A 25MB PCAP does not fit in a context window, and the agent gets lost trying"],
        ["The **action space**", "**Examine Traces** + **Web Search**: a natural-language query, answered with CVE summaries", "Ground the evidence; link and retrieve *knowledge of the CVE*"],
        ["The **memory**", "**MemGPT-style**: system instructions + a working context + a token-budgeted FIFO queue, backed by a vector DB", "A forensic investigation outlives the context window - the agent must decide what to keep"],
        ["The **loop**", "*Summarise → reason → search → cross-check*, until the three checkpoints are answered", "The investigation is **sequential**: no service, no CVE; no CVE, no verdict"],
        ["The **supervision**", "**None at inference.** The ground truth is the CVE that was actually fired", "Same 🐢 economics as AutoPenBench: no labels, no training, an API key and a trace"],
    ],
    "widths": ["17%", "42%", "41%"],
    "caption": (
        "The memory design follows [MemGPT](https://arxiv.org/abs/2310.08560); the agents are built on [LangChain / LangGraph](https://www.langchain.com/), where a node is a reasoning step or a tool call and the LLM decides the next edge. "
        "⚠️ Note the **Web Search** tool is *not* a raw search: it queries Google, fetches the top 10 pages and asks an LLM to compress each one into `CVE-XXXX-YYYY: description` lines. "
        "Handing the agent the full pages instead was, in the prior work, *the* dominant cause of failure. "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}

# Caption for Figure 1: the three architectures side by side. The figure is the
# section's spine - every result afterwards is "which of these three, and why".
CYBERSLEUTH_ARCH_FIG = (
    "**Three ways to read the same trace.** All three share the memory manager, the task prompt and the Web Search tool; "
    "they differ *only* in how the evidence reaches the main agent. **SA** (Single Agent) gets the packet list dumped into its prompt and a "
    "one-packet-at-a-time reader tool. **TEA** (Tshark Expert Agent) delegates to a `tshark` sub-agent it instructs in natural language - "
    "a **nested** design. **FRA** (Flow Reporter Agent) puts a Flow Summariser *before* the main agent: every connection is read once, up "
    "front, and the main agent only ever sees the report - a **sequential** design. "
    "⚠️ The arrow that matters is the one that is **missing** in FRA: the main agent cannot ask the summariser a follow-up question. "
    "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)"
)

# The benchmark in four numbers, shown before the incident-by-incident table.
# Every row is a *range*, because the argument of this slide is the spread:
# one architecture has to survive all of it.
CYBERSLEUTH_SPREAD = {
    "headers": ["", "Across the 30 incidents", "What it forces"],
    "rows": [
        ["**Incidents**", "**30** - 20 design set + 10 test set", "The 10 test incidents carry **2025** CVEs, disclosed after the backends finished training"],
        ["**Attack succeeded**", "19 of 30 - **14 of the 20** design incidents", "⚠️ Always answering *'successful'* already scores **70%** on the design set. Accuracy alone will lie to us"],
        ["**Packets**", "12 → 9 978  (**831x**)", "An architecture that works on twelve packets need not work on ten thousand"],
        ["**Traffic volume**", "1.1KB → 25.5MB  (**23 000x**)", "🧠 25MB does not fit in a context window - and neither does 3MB. **This is the binding constraint**"],
    ],
    "widths": ["16%", "27%", "57%"],
    "caption": (
        "The design set (incidents 0-19) comes from [CFA-bench](https://arxiv.org/abs/2508.20643); the test set (20-29) was collected for this paper. "
        "⚠️ The two range rows are the reason architecture matters at all: the *same* agent has to handle a 12-packet exchange and a 25MB capture, and **volume is not evidence** - the largest trace in the benchmark is one where the attack failed. "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}

# Table 1: the benchmark itself, ten of the thirty incidents. The rows are
# picked, not sampled - every one of them is referred to later in the section,
# or carries one of the two design choices the slide stops on.
CYBERSLEUTH_INCIDENTS = {
    "headers": ["#", "Service / version", "CVE", "Pkts", "Volume", "Attack", "Why this row is here"],
    "rows": [
        ["#8", "Apache ActiveMQ 5.17.3", "CVE-2017-15709", "12", "1.1KB", "failed", "**The smallest incident in the benchmark.** Twelve packets, and the right answer is *'nothing happened'*"],
        ["#0", "Apache Solr 8.11.0", "CVE-2021-44228", "22", "2.9KB", "success", "Log4Shell: **one crafted HTTP header** and the box is gone. The whole investigation fits on a screen"],
        ["#4", "Apache HTTP Server 2.4.49", "CVE-2021-41773", "113", "13.3KB", "success", "🔎 Path traversal - **the incident of the TEA demo later in this section**"],
        ["#6", "Apache HTTP Server 2.4.50", "CVE-2021-42103", "114", "13.1KB", "failed", "⚠️ **One packet larger, opposite answer.** The patched twin: same attack, and it bounces"],
        ["#12", "Apache APISIX 2.9", "CVE-2021-45232", "390", "50.6KB", "success", "🔎 Two candidate CVEs on the same evidence - **the retrieval-vs-selection demo later**"],
        ["#17", "Cacti 1.2.22", "CVE-2022-46169", "2 028", "257.5KB", "success", "Every agent fails here, and *not* because of the volume: **the CVE is barely documented online**"],
        ["#14", "GitLab 13.10.0", "CVE-2021-22205", "6 680", "19.1MB", "success", "**Three containers.** The exploit is an image upload; the other 19MB is the application talking"],
        ["#15", "GitLab 13.10.3", "CVE-2021-22205", "9 978", "**25.5MB**", "failed", "⚠️ **The largest trace in the benchmark - and the attack failed.** Volume is not evidence"],
        ["#28", "Erlang/OTP 27.3.2", "CVE-2025-32433", "20", "3.0KB", "success", "📅 A **2025** CVE: disclosed after every backend finished training. No memorising this one"],
        ["#29", "Erlang/OTP 27.3.3", "CVE-2025-32433", "19", "2.9KB", "failed", "⚠️ **Nineteen packets against twenty**, same exploit, patched target. Recognition is not enough"],
    ],
    "widths": ["4%", "16%", "12%", "6%", "7%", "8%", "47%"],
    "caption": (
        "Ten of the **30 incidents** - the full list is Tab. 7 of the paper. Incidents **0-19** are the design set, from [CFA-bench](https://arxiv.org/abs/2508.20643): containerised services, an external attacker, one CVE each, **14 succeeded and 6 failed**. "
        "Incidents **20-29** are the test set collected for this paper: five services with **2025** CVEs, each deployed **twice** - once vulnerable, once patched - and attacked in both. "
        "⚠️ The paired rows (#4/#6, #14/#15, #28/#29) are the reason the benchmark works: the *same exploit* is fired at both, so an agent that scores by **recognising the attack** gets the third checkpoint wrong half the time. "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}

# Table 2: the architecture comparison, GPT-4o fixed. The row to read out loud
# is MCC - it is the one that says SA is not merely weak but *wrong*.
CYBERSLEUTH_ARCHITECTURES = {
    "headers": ["Metric", "CFA-bench", "SA", "TEA", "FRA", "Reading"],
    "rows": [
        ["Service ✅", "0.42", "0.45", "0.58", "**0.67**", "Every design finds the service more often than the previous one"],
        ["CVE ✅", "0.14", "0.28", "0.35", "**0.45**", "Better memory and a focused web tool already **double** the baseline"],
        ["Success (Acc)", "0.13", "0.47", "0.48", "**0.62**", "⚠️ Accuracy alone is misleading here - 70% comes free"],
        ["Success (MCC)", "-", "**-0.11**", "0.00", "**0.45**", "**Negative**: SA is not guessing, it is guessing *wrongly*"],
        ["Steps", "-", "18.1", "11.3", "**5.5**", "The best agent is also the one that thinks the **least**"],
        ["Input tokens", "-", "5.48M", "4.37M", "**3.86M**", "Reading everything once beats reading the wrong things repeatedly"],
        ["Cost", "-", "$14.48", "$12.15", "**$10.78**", "60 runs. **The most accurate design is the cheapest one.**"],
    ],
    "widths": ["15%", "11%", "9%", "9%", "9%", "47%"],
    "caption": (
        "All three architectures on the **20 design-set incidents**, three runs each, backend fixed to **GPT-4o**, 25 steps maximum. "
        "**MCC** (Matthews Correlation Coefficient) is the honest metric for the success question: the set is 14 successful vs 6 failed attacks, so a classifier that always answers *'successful'* scores **70% accuracy** and **0.00 MCC**. "
        "SA's **-0.11** says it does worse than a coin: when it finds no evidence it answers *'unsuccessful'*, which is the wrong default on this set. "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}

# Table 3: six backends, FRA fixed. Same shape as AUTOPENBENCH_LLMS, opposite
# conclusion - here every model can drive the loop, and they differ in *how*.
CYBERSLEUTH_LLMS = {
    "headers": ["LLM", "Service", "CVE", "MCC", "Steps", "Cost", "How it gets there"],
    "rows": [
        ["GPT-4o", "0.67", "0.45", "0.45", "5.5", "$8.60", "Searches in 95% of runs - and only 54% of results contain the CVE"],
        ["o3", "0.75", "0.48", "**0.65**", "**3.6**", "$9.30", "⚠️ Searches in **50%** of runs: **overconfident**, answers from memory"],
        ["**GPT-5**", "0.80", "**0.68**", "0.63", "3.9", "$8.63", "**Balanced**: searches, then picks the right CVE 90-95% of the time"],
        ["**DeepSeek R1** 🔓", "**0.85**", "0.67", "0.55", "5.4", "**$3.78**", "Matches GPT-5 at **half the price** - and can run on-premise"],
        ["Kimi K2 🔓", "0.82", "0.63", "0.55", "6.7", "$4.63", "Same profile as R1, slightly more steps to get there"],
        ["Llama-4 Maverick 🔓", "0.75", "0.53", "0.35", "17.1", "$2.52", "⚠️ **Best searcher** (80% hit rate), worst at *choosing*: 30% wrong pick"],
    ],
    "widths": ["16%", "9%", "8%", "8%", "8%", "8%", "43%"],
    "caption": (
        "The **FRA** architecture on the 20 design-set incidents, three runs each, swapping only the backend. 🔓 marks open-weight models. "
        "The last column is the interesting one, and it comes from splitting each run in two: *did the web search return the right CVE*, and *did the agent then pick it*. "
        "Those are different skills, and no model is good at both by default: **Llama-4 Maverick** retrieves best and chooses worst, **o3** barely retrieves and leans on priors, **GPT-5** and **DeepSeek R1** do both. "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}

# Caption for Figure 4: the retrieval/selection split, per backend. This is the
# picture that turns "GPT-5 is better" into something a student can act on.
CYBERSLEUTH_WEBSEARCH = (
    "**Two skills, not one.** For each backend, across all 60 runs: how often it **searched** the web (green), how often the last "
    "response actually **contained** the correct CVE (blue), how often it then **selected** that CVE (cream), and how often it got the "
    "CVE right **without** the web, from prior knowledge alone (red). Read blue against cream: that gap is *selection* failure, and it is "
    "where **Llama-4 Maverick** loses - it retrieves the right answer and picks a near-identical neighbour 30% of the time. Read the green "
    "bar for **o3**: it declines to search in half the runs, and the red bar shows it often gets away with it. "
    "⚠️ For a 2025 CVE, 'getting away with it' stops being an option. "
    "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)"
)

# Table 5: the honest test set - ten incidents whose CVEs were disclosed after
# the backends stopped training. This is the number the abstract quotes.
CYBERSLEUTH_TESTSET = {
    "headers": ["Metric", "DeepSeek R1 🔓", "o3", "GPT-5", "Reading"],
    "rows": [
        ["Service ✅", "**0.90**", "0.80", "**0.90**", "Nine incidents out of ten, on services it cannot have seen attacked"],
        ["CVE ✅", "**0.80**", "0.70", "**0.80**", "**The headline number**: the exact CVE, disclosed after training"],
        ["Success (MCC)", "0.41", "**0.82**", "**0.82**", "⚠️ R1 nearly guesses here - 3 wrong verdicts out of 10"],
        ["Steps", "5.5", "**4.3**", "4.4", "A full investigation in four steps, because the summariser did the reading"],
        ["Cost", "**$0.72**", "$1.46", "$2.47", "Ten incidents. **A forensic analyst costs more than that per minute**"],
    ],
    "widths": ["16%", "13%", "10%", "10%", "51%"],
    "caption": (
        "The **10 incidents of the 2025 test set**: five services (4 HTTP, 1 SSH) with vulnerabilities disclosed in **2025**, each deployed twice - once vulnerable, once patched - and attacked in both. "
        "⚠️ That pairing is the point: an agent cannot score by recognising the exploit, because it sees the *same* exploit against a patched target and has to say so. "
        "**GPT-5** is the final CyberSleuth backend. Challenged additionally with **10 benign browsing traces**, it reported no attack in all of them - flagging, in two, the repeated failed logins that were genuinely there. "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}

# Sec. 7.5: the human study. It is the only evidence in the whole lecture that
# the *output* is usable, as opposed to merely correct.
CYBERSLEUTH_HUMAN = {
    "headers": ["What the experts were asked", "Score", "What it means"],
    "rows": [
        ["**Completeness** - does the report contain relevant and accurate information?", "**4.33** / 5", "Nothing important is missing from the reconstruction"],
        ["**Usefulness** - is it helpful to a human analyst?", "**4.23** / 5", "The bar that matters: would a SOC analyst *use* this?"],
        ["**Logical coherence** - is the reasoning clear and consistent?", "**4.31** / 5", "The reasoning trace can be **audited**, not just trusted"],
        ["**Preference**: DeepSeek R1 🔓 vs o3", "**4.39** vs 4.20", "A slight preference for the **open-weight** model"],
    ],
    "widths": ["44%", "14%", "42%"],
    "caption": (
        "**25 volunteers** - students, researchers and professors - graded the reports of four solved 2025 incidents on a 0-5 scale, seeing the reasoning steps, the final report and the PCAP. "
        "12 self-declared low expertise, 8 medium, 5 high. The preference for **DeepSeek R1** is a *qualitative* one and worth repeating: the free-text feedback found o3 more concise but **overconfident** - which Fig. 4 independently confirms - "
        "while R1's longer reasoning track made it easier to check. **Auditability beat brevity.** "
        "Source: [Fumero et al., *CyberSleuth*, arXiv 2025](https://arxiv.org/abs/2508.20643)."
    ),
}
