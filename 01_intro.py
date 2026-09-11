from autopenbench_lab import ACTION_SPACE, ASSISTED, AUTONOMOUS, TASK, compare, dead_ends, loop, replay, score, stages
from cybersleuth_lab import APISIX_GPT4O, APISIX_GPT5, APISIX_RUNS, TEA_BAD, TEA_GOOD, TSHARK, allocate, summaries, track
from darkvec_lab import HOUR, PORT_TO_SERVICE, corpus_of, corpus_summary, darkvec, neighbours, preview, recall_by_group, scatter, synthetic_darknet
from edtrace import link, note, plot, text
from intro_content import FAST_SLOW_THINKING, HUAWEI_USECASE, KAHNEMAN_BOOK, KAHNEMAN_SOURCE, THREAT_LANDSCAPE
from logprecis_lab import CAMPAIGN, SESSION, fingerprint, fingerprints_of, labelled, rm_in_context, statements, tactics_of
from research_content import (
    AUTOPENBENCH_INFRA,
    AUTOPENBENCH_LLMS,
    AUTOPENBENCH_MAPPING,
    AUTOPENBENCH_RESULTS,
    AUTOPENBENCH_SOLUTION,
    AUTOPENBENCH_TARGETS,
    CONTRIBUTIONS,
    CYBERSLEUTH_ARCH_FIG,
    CYBERSLEUTH_ARCHITECTURES,
    CYBERSLEUTH_HUMAN,
    CYBERSLEUTH_INCIDENTS,
    CYBERSLEUTH_SPREAD,
    CYBERSLEUTH_LLMS,
    CYBERSLEUTH_MAPPING,
    CYBERSLEUTH_TESTSET,
    CYBERSLEUTH_WEBSEARCH,
    DARKVEC_MAPPING,
    DARKVEC_RESULTS,
    DARKVEC_SCENARIOS,
    DARKVEC_SCHEMA,
    DARKVEC_SETUP,
    LOGPRECIS_FINGERPRINTS,
    LOGPRECIS_MAPPING,
    LOGPRECIS_MODELS,
    LOGPRECIS_RESULTS,
)
from slides import CALLOUT, SUBLIST, SUBSUBLIST, analogy, ask, book_card, complete, demo, figure, figure_row, instructor_card, section, similar_words, table, table_caption, table_head, table_row


def main() -> None:
    welcome()
    recent_news()
    from_models_to_llms()
    why_cybersecurity()
    ai_and_cybersecurity()
    closing()


def welcome():
    # ---------- Title ----------  @hide
    text("# LLMs and Cybersecurity - Modelli per l'IA")

    instructor_card()  # @stepover

    # ---------- Agenda ----------  @hide
    text("<ins>**Plan for the next four hours:**</ins>")
    # ---------- Part 0: News ----------  @hide
    text("- **The last year in four headlines**: some news that makes this lecture timely.")
    # ---------- Part 1: Reminder on LLMs ----------  @hide
    text("- **The promise of LLMs**: recap on how LLMs differ from traditional models.")
    text("- Pre-trained knowledge: LLMs are pre-trained on vast amounts of text data.", style=SUBLIST)
    text("- Adaptability: LLMs can be used *off-the-shelf* or *fine-tuned* for specific tasks.", style=SUBLIST)
    text("- Strong performance on recent benchmarks: the promise of LLMs is real.", style=SUBLIST)
    # ---------- Part 2: LLMs for cybersecurity ----------  @hide
    text("- **Why LLMs for cybersecurity?**: The Sisyphean struggle of security experts.")
    text("- The threat landscape is evolving faster than experts can keep up.", style=SUBLIST)
    text("- A use-case: Network Security in a big tech company.", style=SUBLIST)
    text("- Fast vs. slow thinking: the two lanes of cybersecurity tasks.", style=SUBLIST)
    # ---------- Part 3: fast vs. slow ----------  @hide
    text("- **Fast vs. slow thinking in cybersecurity**: how to use LLMs/NLP for each lane.")
    text("- ⚡ Fast Thinking: [DarkVec](https://dl.acm.org/doi/10.1145/3485983.3494863), [LogPrecis](https://www.sciencedirect.com/science/article/pii/S0167404824001068)", style=SUBLIST)
    text("- 🐢 Slow Thinking: [AutoPenBench](https://aclanthology.org/2025.emnlp-industry.114/), [Cybersleuth](https://arxiv.org/abs/2508.20643)", style=SUBLIST)

    # ---------- Rationale ----------  @hide
    text("**Rationale of this lecture:** You developed a toolkit of AI tools 🧰.<br>Now, learn **when and how to use them** for real problems.", style=CALLOUT)


def recent_news():
    text("# 📰 Why now? The last year in four headlines")
    text("Before the theory, the news. From the labs' **own incident reports**:")

    # ---------- 1. Offence is already agentic ----------  @hide
    text("- 🥷 **The attacker is already an agent.** ([Anthropic, Nov 2025](https://www.anthropic.com/news/disrupting-AI-espionage))")
    text("- A state-sponsored group drove *Claude Code* through an espionage campaign on **~30 organizations**.", style=SUBLIST)
    text("- The model ran **80-90%** of the operation; humans stepped in at only **4-6 decision points**.", style=SUBLIST)
    # ---------- 2. Capability, and the decision not to ship it ----------  @hide
    text("- 🔓 **The model out-hacks nearly every human.** ([Anthropic Frontier Red Team, Apr 2026](https://www.anthropic.com/research/mythos-preview))")
    text("- *Claude Mythos Preview* autonomously found **and exploited** 0-days in **every major OS and browser**", style=SUBLIST)
    text('- Anthropic\'s call: *"we do not plan to make Mythos Preview generally available"*.', style=SUBLIST)
    figure("images/mythos_firefox_exploit.png", caption="**The jump, measured.** Share of trials that produced a *working* exploit for crashes found in the Firefox JS shell: **&lt;1%** for Opus 4.6, **72.4%** for Mythos Preview - ~100x more often. Source: [Anthropic Frontier Red Team, Apr 2026](https://www.anthropic.com/research/mythos-preview)", width="620px")  # @stepover
    # ---------- 3. The agent does not stay in the box ----------  @hide
    text("- 🧪 **And it does not always stay in the sandbox.** ([OpenAI, Aug 2026](https://openai.com/index/hugging-face-incident-and-the-road-ahead/))")
    text("- In OpenAI's *own* evaluations, agents chained 0-days in a package proxy to escape the sandbox.", style=SUBLIST)
    text("- They then ran code on **41 Hugging Face production servers** (**reward hacking**).", style=SUBLIST)
    # ---------- 4. The same capability, defending ----------  @hide
    text("- 🛡️ **Same capability, other side of the fence.** ([Google, Jul 2025](https://blog.google/innovation-and-ai/technology/safety-security/cybersecurity-updates-summer-2025/))")
    text("- Google's *Big Sleep* found the SQLite 0-day [CVE-2025-6965](https://nvd.nist.gov/vuln/detail/CVE-2025-6965) that attackers were about to use.", style=SUBLIST)
    text("- **The first time an AI agent foiled an exploit in the wild.**", style=SUBLIST)

    text("**In one year AI went from *assistant* to *operator* - on both sides of the fence.**<br>The question is no longer *whether*, but **which AI, for which task**: that map is what we build today.", style=CALLOUT)


def from_models_to_llms():
    text("# From traditional ML to LLMs - The promise of LLMs")
    section("The premise")
    text("**Why this hype in LLMs?** At the end of the day, LLMs are just another neural network!")
    figure("images/transformer_vs_llm.gif", caption="**Transformer vs. Mixture of Experts.** The dense feed-forward block is replaced by a router that activates only a few experts per token. **Most of the backbone architecture remains the same!** Source: [Daily Dose of Data Science](https://www.dailydoseofds.com/p/transformer-vs-mixture-of-experts-in-llms/)", width="440px")  # @stepover
    text("The main difference lies in the **training procedure**!")

    section("Traditional ML")
    text("**Traditional ML models**: learn from labeled data for a specific task.")
    text("1) You collect a dataset of input-output pairs.", style=SUBLIST)
    text("2) You train a (randomly initialized) model on this dataset.", style=SUBLIST)
    text("3) The model learns to map inputs to outputs ([Pattern Recognition](https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf)).", style=SUBLIST)
    text("4) You evaluate the model's performance on a test set.", style=SUBLIST)
    section("Pre-trained models — first wave")
    text("**Pre-trained models ([First Wave](https://proceedings.mlr.press/v202/longpre23a/longpre23a.pdf))**: 1) learn from a large corpus of text data, 2) fine-tuned on a specific task.")
    text("1) You collect a large **unlabelled** dataset of text (e.g., [English Wikipedia](https://arxiv.org/abs/1810.04805)).", style=SUBLIST)
    text("2) You *pre-train* a model on this dataset to predict the next/masked word in a sentence.", style=SUBLIST)
    text("3) The model learns general language patterns and knowledge.", style=SUBLIST)
    text("4) You *fine-tune* the model on a smaller dataset for a specific task.", style=SUBLIST)

    demo("What pre-training alone buys you")
    text("Step 3 is easy to state and easy to underestimate, so **let us look at it directly**.")
    text("Let's put [distilbert-base-uncased](https://huggingface.co/distilbert/distilbert-base-uncased)(67M parameters) to the test!")

    fill_mask = load_fill_mask()  # @stepover
    MASKED_SENTENCES = [
        "Paris is the capital of [MASK].",  # world knowledge
        "She went to the store because she [MASK] out of milk.",  # grammar and idiom
        "A [MASK] is a program that replicates itself and infects computers.",  # security vocabulary
        "The attacker gained [MASK] to the server.",  # security semantics
    ]
    for sentence in MASKED_SENTENCES:
        completions = complete(fill_mask, sentence)  # @inspect sentence completions

    text("Word order, world knowledge, and security vocabulary all fall out of **reading text**, not out of labels.")  # @clear sentence completions fill_mask MASKED_SENTENCES
    text("This is the pre-trained knowledge **we get for free**, and what we can later fine-tune!")

    section("Pre-trained models — second wave")
    text("🙋🏻‍♂️ **Question**: is this what GPT/Claude looks like?")
    text("**Not quite**. Current LLMs are **general-purpose** models!", style=SUBLIST)
    text("- You ask them a question, they give you an answer")
    text("- You use them 'off-the-shelf' for any task (no fine-tuning)")
    text("This happens because of: *post-training* phase (instructions tuning) and *scale* (billions of parameters).")

    # ---------- Figures: instruction tuning (FLAN) ----------  @hide
    figure("images/schema_instruction_tuning.png", caption="**Instruction tuning.** The model is fine-tuned on many tasks *phrased as instructions*, then asked to solve a task type it never saw during tuning. Source: [Finetuned Language Models Are Zero-Shot Learners](https://openreview.net/pdf?id=gEZrGCozdqR)", width="680px")  # @stepover
    figure_row(
        ["images/held_out_vs_held_in.png", "images/held_out_vs_size.png"],  # @hide
        caption="**Two ingredients.** *Left:* held-out performance keeps climbing as more task clusters are folded into instruction tuning. *Right:* the gain only appears with scale — below ~8B parameters, instruction tuning actually **hurts** zero-shot accuracy. Source: [Finetuned Language Models Are Zero-Shot Learners](https://openreview.net/pdf?id=gEZrGCozdqR)",  # @hide
        width="340px",  # @hide
    )  # @stepover @hide

    demo("The same recipe, one model later")
    text("Let us put that to the test. [Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) is pre-trained **and** instruction-tuned (0.5B parameters)")

    chat = load_chat_model()  # @stepover
    QUESTIONS = [
        # DistilBERT needed a [MASK] slot for this
        "What is the capital of France?",
        # a task nobody fine-tuned it for
        "In one sentence, what does a firewall do?",
        # zero-shot classification
        "Is this email suspicious?\n" '"Dear user, your account will be closed. Click here to verify your password."\n' "Answer yes or no.",
        # too specific for 0.5B
        "Which software is affected by CVE-2021-44228? Answer in one word.",
    ]
    for question in QUESTIONS:
        answer = ask(chat, question)  # @inspect question answer

    text("No `[MASK]`, no fine-tuning, no task-specific head: we simply **asked**, in plain English.")  # @clear question answer chat QUESTIONS
    text("⚠️ The last answer is **confidently wrong** - CVE-2021-44228 is *Log4Shell*, in **Log4j**, not Tomcat.")
    text("**This is the scale axis of the plot above.** The recipe is right, but 0.5B parameters are not enough.", style=CALLOUT)

    section("Why this matters")
    text("**So what?** These properties are what turn an LLM into a **reasoning backbone**.")
    text("- Pre-trained knowledge: it already speaks the domain's vocabulary.", style=SUBLIST)
    text("- Instruction following: we program it in **plain English**, not with labels.", style=SUBLIST)
    text("- Generalization: one model, many tasks, no fine-tuning per task.", style=SUBLIST)
    text("And the capability keeps **growing fast**!")
    figure("images/metr_time_horizon.png", caption="**The promise, measured.** The length of a task a model can finish *on its own* (50% success rate) has been doubling every ~4 months, over 228 software engineering, **cybersecurity**, general reasoning and ML tasks. Source: [METR](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)", width="620px")  # @stepover
    text("Also, this is what makes **agentic architectures** possible!")
    text("- An LLM-based agent can *Plan*, *Call tools*, and *React to what it observes*.")

    section("Wrapping up")
    text("1) Same architecture - the difference is **how we train it**.", style=SUBLIST)
    text("2) Pre-training buys knowledge, instruction tuning buys **usability**, scale buys **reliability**.", style=SUBLIST)
    text("3) A 0.5B model already answers in plain English - and already **makes things up**.", style=SUBLIST)
    text('**<p align="center">Next:** How do we apply this to cybersecurity?</p>', style=CALLOUT)


def why_cybersecurity():
    text("# Why cybersecurity? The Sisyphean struggle")
    section("The challenge")
    text("Cybersecurity experts face an **ever-evolving landscape of threats**, making it difficult to keep up.")
    text(
        "In 2024, [Palo Alto Networks](https://start.paloaltonetworks.com/2024-unit42-ir-report-ondemand-webcast?utm_source=google-jg-amer-unit42-unrc-unpr&utm_medium=paid_search&utm_campaign=google-unit42-more_prepared-amer-multi-lead_gen-en-brand-broad&utm_content=7014u0000017pdSAAQ&utm_term=unit%2042%20threat%20intelligence&cq_plac=&cq_net=g&gad_source=1&gclid=Cj0KCQjwsc24BhDPARIsAFXqAB2HDuqDdCc2iZLx7ef3jha7olIjvJROdVOVOx2sjh7Uteg1BZcQRigaAqo3EALw_wcB) compared the experts' struggle with that of Sisyphus:"  # @hide
    )  # @hide

    figure(
        "images/sisyphus_struggle.jpg",  # @hide
        caption="**Sisyphean task**: A Sisyphean task is a job that can never be completed. "  # @hide
        "The term comes from Sisyphus, a figure in Greek mythology condemned by the gods to roll a huge boulder up a hill, only for it to roll back down each time he neared the top. His punishment was eternal repetition of a futile labor. "  # @hide
        "Image source: [Jerry Nixon on X](https://x.com/jerrynixon/status/1976854991261647029)",  # @hide
        width="440px",  # @hide
    )  # @stepover @hide

    text("> **The landscape of threats is evolving faster than the experts can keep up.**")
    text("A nice metaphor - but is the boulder *really* rolling back faster? Let us **check the numbers**.")

    section("The evidence")
    text("📈 **Two years of telemetry**, side by side:")
    table_head(THREAT_LANDSCAPE)  # @stepover
    table_row(THREAT_LANDSCAPE, "Attackers are faster")  # @stepover
    table_row(THREAT_LANDSCAPE, "exfiltration")  # @stepover
    table_row(THREAT_LANDSCAPE, "data-scale")  # @stepover
    table_row(THREAT_LANDSCAPE, "many fronts")  # @stepover
    table_row(THREAT_LANDSCAPE, "Skills do not scale")  # @stepover
    table_row(THREAT_LANDSCAPE, "attacker's hands")  # @stepover
    table_row(THREAT_LANDSCAPE, "defender's hands")  # @stepover
    table_row(THREAT_LANDSCAPE, "Failure stays")  # @stepover
    table_caption(THREAT_LANDSCAPE)  # @stepover

    text("**Read the last column top to bottom**: every row tells the same story from a different angle.")
    text("- ⚡ The attacker's clock now runs in **minutes**; the defenders' still runs in shifts and tickets.", style=SUBLIST)
    text("- 📈 The evidence hides in **100T+ signals a day**, scattered over up to 10 fronts at once.", style=SUBLIST)
    text("- 👥 The expertise to read it **does not grow**: more tools, same (missing) people.", style=SUBLIST)
    text("- 🤖 Both sides now bring AI to the table - the open question is **who uses it better**.", style=SUBLIST)
    text("Aggregate numbers, though, are easy to nod at. **What does this look like in a single company?**")

    section("The struggle, up close")
    text("**The struggle of Network Security Experts**: A [real-world](https://dl.acm.org/doi/abs/10.1145/3696379) use case.")
    figure("images/Huawei_usecase.mp4", caption=HUAWEI_USECASE, width="680px")  # @stepover

    text("Note *where* the Sisyphus icons sit:")
    text("- The firewall only stops what is already known - **who is in charge of the unknown?**", style=SUBLIST)
    text("- Some attacks are eventually detected by rule-based IDS. **What about the rest?**", style=SUBLIST)
    text("- Post-mortem analysis needs context and expertise. **Which signals to prioritize?**", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: Do these tasks actually require the same data throughput and latency?")

    section("Fast vs. slow thinking")
    text("**They do not** - and psychology gave us the vocabulary for this long before cybersecurity needed it.")
    book_card("images/thinking_fast_and_slow.jpg", "Thinking, Fast and Slow", "Daniel Kahneman · Farrar, Straus and Giroux · **2011**", KAHNEMAN_BOOK, source=KAHNEMAN_SOURCE)  # @stepover
    text("In [*Thinking, Fast and Slow*](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow), Daniel Kahneman argues we do not think with one mind, but with **two systems**:")
    text("- ⚡ **System 1** *(fast)*: automatic, effortless, involuntary.", style=SUBLIST)
    text("- Recognising a face, reading a word in your own language.", style=SUBSUBLIST)
    text("- Feeling that *this scan looks like the other 10M*.", style=SUBSUBLIST)
    text("- 🐢 **System 2** *(slow)*: deliberate, effortful, one step at a time.", style=SUBLIST)
    text("- Computing 17 × 24 in your head.", style=SUBSUBLIST)
    text("- Reconstructing **how** an attacker went from a phished mailbox to the domain controller.", style=SUBSUBLIST)
    text("The catch: System 1 is **always on** and cheap, System 2 is **lazy** and expensive.")
    text("🕵🏻 **The same split runs through the pipeline you just saw**:")
    table_head(FAST_SLOW_THINKING)  # @stepover
    table_row(FAST_SLOW_THINKING, "How it works")  # @stepover
    table_row(FAST_SLOW_THINKING, "Cost per item")  # @stepover
    table_row(FAST_SLOW_THINKING, "Volume")  # @stepover
    table_row(FAST_SLOW_THINKING, "Question it answers")  # @stepover
    table_row(FAST_SLOW_THINKING, "In the SOC")  # @stepover
    table_row(FAST_SLOW_THINKING, "Failure mode")  # @stepover
    table_row(FAST_SLOW_THINKING, "AI that fits")  # @stepover
    table_caption(FAST_SLOW_THINKING)  # @stepover

    text("Map it back onto the animation: firewall and IDS are the ⚡ lane, the analyst's verdict is the 🐢 lane.")
    text('⚠️ **Careful**: this is *not* "the fast lane is solved, the slow one is not". **Both** need help, just of a different kind.')
    text("- ⚡ Rules go stale, thresholds are guesswork, priorities are set by hand.", style=SUBLIST)
    text("- Automation: **keeping up with what is new**, and unlocking analyses nobody can run manually.", style=SUBSUBLIST)
    text("- 🐢 Verdicts, root causes, reports: automation here means **expert reasoning through one case**.", style=SUBLIST)
    text("What separates the lanes is the **budget per item** - and it is a budget in *data* as much as in *time*.")

    text("🧮 **Do the arithmetic**: 12M events a day. **1 second** on each → **139 days** of compute for a *single* day of traffic.")
    text("- An LLM call takes seconds; an agent takes minutes. In the ⚡ lane it is **arithmetically impossible**.", style=SUBLIST)
    text("- The ⚡ lane needs models that cost **milliseconds**, and look at the whole stream at once.</strong>", style=SUBLIST)
    text("- The 🐢 lane sees only what survived triage: few items, high stakes - there you <strong>can afford to think</strong>**.", style=SUBLIST)
    text("So the question is not *AI or no AI*: it is **which AI** (how much compute you may spend per item).")
    text('<p align="center">⚡ Fast: the whole stream, milliseconds per item - <strong>scale is the constraint</strong>.<br>🐢 Slow: one case at a time, minutes per item - <strong>depth is the point</strong>.<br><p align="center"><strong>This is the map for the rest of the lecture.</strong></p>', style=CALLOUT)

    section("Wrapping up")
    text("1) The threat landscape scales with **machines**; the response scales with **people**.", style=SUBLIST)
    text("2) Filtering, ranking and judgement are **all understaffed** - but cannot be helped by the same model.", style=SUBLIST)
    text("3) That judgement needs **domain knowledge, context, and plain-English instructions**.", style=SUBLIST)
    text("4) And it comes in **two flavours**: ⚡ System 1 for the stream, 🐢 System 2 for the case that survives it.", style=SUBLIST)
    text('<p align="center"><strong>The gap is structural</strong>: attacks compress, telemetry explodes, expertise does not follow.<br><strong>This is where AI (and LLMs) earns its place.</strong></p>', style=CALLOUT)


def ai_and_cybersecurity():
    text("# Time to get our hands dirty 😈")
    text("Four contributions, same rule for each:")
    text("- The **security problem**, the **NLP idea**, one **result**. Then a bit of code.", style=SUBLIST)
    table_head(CONTRIBUTIONS)  # @stepover
    table_row(CONTRIBUTIONS, "DarkVec")  # @stepover
    table_row(CONTRIBUTIONS, "LogPrécis")  # @stepover
    table_row(CONTRIBUTIONS, "AutoPenBench")  # @stepover
    table_row(CONTRIBUTIONS, "CyberSleuth")  # @stepover
    table_caption(CONTRIBUTIONS)  # @stepover

    text("Read the **NLP idea** column top to bottom:")
    text("- ⚡ In the fast lane there is **no LLM in the loop at all**: co-occurrence counts, a fine-tuned encoder.", style=SUBLIST)
    text("- 🐢 In the slow lane the LLM **is** the analyst: it plans, runs commands, reads output, and reports.", style=SUBLIST)
    text("What stays constant is the **trick**: security data that *is not* text, read **as if** it were text.")
    text('<p align="center">⚡ <strong>DarkVec</strong> · <strong>LogPrécis</strong> - milliseconds per item, the whole stream.<br>🐢 <strong>AutoPenBench</strong> · <strong>CyberSleuth</strong> - minutes per case, one case at a time.', style=CALLOUT)

    darkvec_section()
    logprecis_section()
    autopenbench_section()
    cybersleuth_section()


def darkvec_section():
    text("# ⚡ DarkVec: who is scanning **together**?")

    section("The setting: a Darknet 🌐")
    text("A **darknet** is a range of routable IP addresses that hosts **nothing**: no service, no client, no user.")
    figure("images/darvec_setup.png", caption=DARKVEC_SETUP, width="440px", caption_width="820px")  # @stepover
    text("- Every incoming packet is, by construction, **unsolicited** - nobody could legitimately want to talk to it.", style=SUBLIST)
    text("- 🔭 **Free observatory**: scanners, botnets, misconfigurations, and *backscatter* from spoofed victims.", style=SUBLIST)
    text("- 🧾 **Noise-free by design**: no need to separate attacks from legitimate traffic - **no legitimate traffic**.", style=SUBLIST)
    text("**The catch is the volume.** A single **/24** (256 addresses) in a campus network, over 30 days:")
    text("- **543 900** distinct sender IP addresses, **63.5M** packets, spread over **all 65 537** ports.", style=SUBLIST)
    text("- **36%** of senders are seen exactly *once* in a month", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: and now what? **Who** is going to look at 543 900 senders?")

    section("The task")
    text("Nobody looks at senders one by one. The useful question is about **groups**:")
    text("- 👥 Which senders are running the **same operation**?", style=SUBLIST)
    text("- A botnet, a scan project, a research crawler", style=SUBSUBLIST)
    text("- 🏷️ And when a **new** IP address shows up: does it belong to a group **we already know**?", style=SUBLIST)
    text("**Why groups?** Because coordination is *not* an accident - it is the **signature of an operation**:")
    text("- A *botnet* receives one order from its Command & Control, so its members act **at the same time**.", style=SUBLIST)
    text("- A *scan project* (Censys, Shodan) **splits** the port space across its fleet and sweeps on a **schedule**.", style=SUBLIST)
    text("One sender tells you almost nothing. **A group tells you the campaign.**")

    text("🙋🏻‍♂️ **Question**: what features would you use?")
    text("- *Which ports a sender hits* is the obvious answer - and it is **not enough**!", style=SUBLIST)
    text("- Ports are shared (Censys alone sweeps **11 000+** of them, everybody knocks on 445).", style=SUBSUBLIST)
    text("- See the paper for more details.", style=SUBSUBLIST)

    section("The NLP idea")
    text("The distributional hypothesis, [Firth 1957](https://en.wikipedia.org/wiki/Distributional_semantics): *“You shall know a word by the company it keeps.”*")
    text("- Translated into [Word2Vec](https://arxiv.org/abs/1301.3781): words from the same context land **close** in the embedding space.", style=SUBLIST)
    text("Well known example: 🤴🏻 king vs 👸🏻 queen")
    text("- Using [distilbert-base-uncased](https://huggingface.co/distilbert/distilbert-base-uncased) as a proxy for Word2Vec and measuring *cosine similarity*.", style=SUBLIST)

    embeddings = load_word_embeddings()  # @stepover
    queen = analogy(embeddings, "king", minus="man", plus="woman")  # @inspect queen

    text("**king - man + woman ≈ queen.** Nobody taught it royalty, or gender: it learned from **co-occurrences**.")

    like_attacker = similar_words(embeddings, "attacker")  # @inspect like_attacker

    text("And it holds in **our** vocabulary too - *adversary*, *intruder*: synonyms **nobody wrote down anywhere**.")  # @clear embeddings queen like_attacker

    section("DarkVec's adaptation")
    text("👀 *You shall know a scanner by the company it scans with.*")
    table_head(DARKVEC_MAPPING)  # @stepover
    table_row(DARKVEC_MAPPING, "A **word**")  # @stepover
    table_row(DARKVEC_MAPPING, "A **sentence**")  # @stepover
    table_row(DARKVEC_MAPPING, "A **document")  # @stepover
    table_row(DARKVEC_MAPPING, "The **corpus**")  # @stepover
    table_row(DARKVEC_MAPPING, "**Context window")  # @stepover
    table_row(DARKVEC_MAPPING, "**Embedding")  # @stepover
    table_caption(DARKVEC_MAPPING)  # @stepover

    figure("images/darkvec_schema.png", caption=DARKVEC_SCHEMA, width="880px")  # @stepover

    text("Then: **off-the-shelf Word2Vec** (skip-gram) on that corpus. Nothing else changes.")
    text("- Each sender IP becomes a **50-dimensional vector**; senders that arrive together land **close together**.", style=SUBLIST)
    text("- Cost of comparing two senders afterwards: **one dot product**. That is what makes it a ⚡ fast-lane tool.", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: does that actually work, or does it just sound good? **Let us build it.**")

    demo("A pocket-sized DarkVec")
    text("A **toy darknet**: 24 hours, ~40 senders, three (unknown) coordinated groups hiding in a crowd.")

    packets = synthetic_darknet()  # @stepover
    example_packets = preview(packets)  # @inspect example_packets

    text("- 🔴 `bot-*`: 8 hosts hammering **Telnet**, every hour, all together (our Mirai-like botnet).", style=SUBLIST)
    text("- 🔵 `scan-*`: 6 hosts of a scan project. Each takes **its own slice** of 10 ports, coming in the **same 6 hours**.", style=SUBLIST)
    text("- 🟢 `smb-*`: 5 hosts on **SMB**, on a regular hourly beat.", style=SUBLIST)
    text("- ⚪ `noise-*`: 20 unrelated senders, at the **same port pool** of the scan project, at random times.", style=SUBLIST)
    text("Notice: `scan-*` and `noise-*` are **indistinguishable by port**, and are separable **only** by timing.")

    text("**The corpus**: one sentence per (service, hour), senders in **order of arrival**.")
    text("- Let us build it **by hand**, on the very first four packets above 👆", style=SUBLIST)

    first_sentences = build_sentences(packets[:4])  # @inspect first_sentences

    text("Two services, so **two sentences**: `bot-4` joins the one `bot-2`, `scan-2` the one `noise-7`.")
    text("⚠️ Note `scan-2` shares a sentence with a *noise* sender (but they are unrelated)!")
    text("- **Hypothesis:** One co-occurrence means nothing - only a **repeated** one does.", style=SUBLIST)
    text("- In other terms, the network has to be robust **to noise** and sensitive **to patterns**.", style=SUBLIST)

    text("`corpus_of` applies the same logic of `build_sentences`, over all **1 253** packets:")

    corpus = corpus_of(packets)  # @stepover
    corpus_shape = corpus_summary(corpus)  # @inspect corpus_shape
    telnet_sentence = corpus_of(packets, service="telnet")[0]  # @inspect telnet_sentence

    text("And here is a full Telnet sentence: the **same 8 words**, over and over.")  # @clear first_sentences telnet_sentence

    text("**Now embed**: we use pre-trained DarkVec model from the paper with 8 dimensions.")

    embedding = darkvec(corpus, dim=8)  # @stepover
    darkvec_neighbours = neighbours(embedding, "scan-2")  # @inspect darkvec_neighbours

    text("`scan-2`'s nearest neighbours are its **five colleagues** - hosts it shares **no port** with, only a **clock**.")

    darkvec_recall = recall_by_group(embedding)  # @inspect darkvec_recall

    text("Every coordinated group recovered - and **we never told the model that groups exist**.")

    plot(scatter(embedding, "DarkVec: senders that scan together, land together"))  # @stepover

    text("Three tight coordinated clusters, one diffuse grey cloud. **This is what gets handed to the analyst.**")  # @clear packets example_packets corpus corpus_shape embedding darkvec_neighbours darkvec_recall

    section("The results, on the real darknet")
    text("Same experiment at scale: 30 days, ~100 000 active senders, **9 labelled groups**, leave-one-out 7-NN.")
    table_head(DARKVEC_RESULTS)  # @stepover
    table_row(DARKVEC_RESULTS, "Mirai")  # @stepover
    table_row(DARKVEC_RESULTS, "Censys")  # @stepover
    table_row(DARKVEC_RESULTS, "Shodan")  # @stepover
    table_row(DARKVEC_RESULTS, "Engin")  # @stepover
    table_row(DARKVEC_RESULTS, "Stretchoid")  # @stepover
    table_row(DARKVEC_RESULTS, "Overall")  # @stepover
    table_caption(DARKVEC_RESULTS)  # @stepover

    text("**96% overall**- but read the *per-group* column: the win is the **small** groups!")
    text("⚠️ When the algorithm fails - **Stretchoid**: few packets, irregular times. **No rhythm → no embedding.**")

    text("**Now drop the labels entirely**: k-NN graph on the embedding + [Louvain](https://arxiv.org/abs/0803.0476) → **46 clusters**:")
    figure("images/results_darkvec.png", caption=DARKVEC_SCENARIOS, width="880px")  # @stepover
    text("**A** - you knew *who* they were: the embedding tells you **how the operation is organised**.")
    text("**B** - you knew nothing at all: the embedding tells you **there is an operation**, where you saw only stray IPs.")

    section("Wrapping up")
    text("1) The data was not text - but *senders in time* behave like *words in sentences* → **reuse the whole toolkit**.", style=SUBLIST)
    text("2) The signal was never in the ports, but in **who shows up with whom**.", style=SUBLIST)
    text("3) ⚡ Fast-lane economics: train once (**486M** skip-grams, **~1.2 h**), then **one dot product** per sender.", style=SUBLIST)
    text("-  No LLM, no labels, no prompt.", style=SUBSUBLIST)
    text("4) ⚠️ The embedding is **not general**. Campaigns keep changing → **retrained per darknet, per period**.", style=SUBLIST)
    text("- The opposite of an off-the-shelf LLM.", style=SUBSUBLIST)
    text("- There can be knowledge transfer, as long as there are enough intersecting senders ([i-DarkVec](https://dl.acm.org/doi/epdf/10.1145/3595378))", style=SUBSUBLIST)


def logprecis_section():
    text("# ⚡ LogPrécis: what was the attacker **trying to do**?")

    section("The setting: a honeypot 🍯")
    text("A **honeypot** is a machine built to be broken into: weak password, **nothing of value** behind it.")
    text("- Every session recorded on it is, by construction, an **attack**: nobody logs in there by mistake.", style=SUBLIST)
    text("- 🎥 And it records the **whole session**: every statement the attacker typed, from login to logout.", style=SUBLIST)
    text("- Same trick as the darknet, one layer up: **there is no legitimate traffic to filter out**.", style=SUBLIST)
    text("**Two collections, two years**: 50+ honeypot nodes across Europe and the US, plus 24 addresses at PoliTO.")
    text("- **393 522** *unique* sessions - and unique is literal: **one character** of difference makes a new one.", style=SUBLIST)
    text("- **~90%** of the words in these logs appear **exactly once**: random file names, random keys, random IPs.", style=SUBLIST)
    text("- Intersect 50 000 of those words with 50 000 English ones: **71** in common. This is **not** English.", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: 400 000 sessions, in a language where almost every word is new. **And now what?**")

    section("The task")
    text("This time the useful question is not *what* was typed, it is **why**:")
    text("- 🎯 Statement by statement, what was the attacker **trying to achieve**?", style=SUBLIST)
    text("[MITRE ATT&CK](https://attack.mitre.org/tactics/enterprise/) already gives us the vocabulary: a **tactic** is the *why* of a step.")
    text("- **Discovery**: *what machine did I land on?* · **Persistence**: *make sure I can come back*.", style=SUBLIST)
    text("- **Execution**: *run my payload* · **Impact**: *break something* · **Defense Evasion**: *erase my traces*.", style=SUBLIST)
    text("**Notice**: the *what* is often pseudo-random, the *why* is not!")
    text("- **DOTA** ([a.k.a. Outlaw](https://www.elastic.co/security-labs/outlaw-linux-malware)), an SSH cryptomining worm: **>30 000** *unique* sessions in our logs...", style=SUBLIST)
    text("- ...and every one of them runs the **same 138 tactics**, in the same order.", style=SUBLIST)
    text("👀 One of them, abridged - a **real** session, off the [model card](https://huggingface.co/SmartDataPolito/logprecis):")
    text("- `cat /proc/cpuinfo | grep name | wc -l ;` → *what machine did I land on?*", style=SUBLIST)
    text("- `echo -e pcnv81k7W9cAOnon... | passwd | bash ;` → *lock the owner out, with a **random** password*", style=SUBLIST)
    text("- `crontab -l ; w ; uname -a ; echo admin pc > /tmp/up.txt ;` → *keep looking around, note the credentials down*", style=SUBLIST)
    text("- `rm -rf /var/tmp/dota* ;` → *wipe the previous run - and this is where the family got its name*", style=SUBLIST)
    text("- Another session of the family sets `xue7wsmGreOb` instead, and writes `root diablo` into `/tmp/up.txt`.", style=SUBLIST)
    text("- The payload name, the drop server and the root password change at every run. **The intent does not.**", style=SUBLIST)

    section("The NLP idea")
    text("Putting a label on every word of a sentence is a task NLP has had a name for since the 1990s:")
    text("- [Named Entity Recognition](https://en.wikipedia.org/wiki/Named-entity_recognition): given a sentence, tag each word as *person*, *place*, *company*, ...", style=SUBLIST)
    text("- Here: given a **session**, tag each word with the **tactic** it serves. Same task, different vocabulary.", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: Is the same command always assigned the same tactic?")
    text("**No**! The very same command serves **different intents** provided the context it is used in:")
    text('- 1️⃣ `echo "321" > /var/tmp/.var03522123; rm -rf /var/tmp/.var03522123; cat /var/tmp/.var03522123;`', style=SUBLIST)
    text("- **Discovery**: write a file, delete it, read it back - *can I even write on this machine?*", style=SUBSUBLIST)
    text('- 2️⃣ `cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa SSHKEY== user" >> .ssh/authorized_keys;`', style=SUBLIST)
    text("- **Persistence**: delete the owner's keys, install mine - *I want to be able to come back.*", style=SUBSUBLIST)
    text("Same `rm -rf`, same flags, same target shape. **Only the neighbours differ** - and they decide the tactic.")

    section("LogPrécis's adaptation")
    text("👀 *You shall know a command by the company it keeps* - and here that is meant literally.")
    table_head(LOGPRECIS_MAPPING)  # @stepover
    table_row(LOGPRECIS_MAPPING, "A **word**")  # @stepover
    table_row(LOGPRECIS_MAPPING, "A **sentence**")  # @stepover
    table_row(LOGPRECIS_MAPPING, "The **labels**")  # @stepover
    table_row(LOGPRECIS_MAPPING, "The **task**")  # @stepover
    table_row(LOGPRECIS_MAPPING, "The **model**")  # @stepover
    table_row(LOGPRECIS_MAPPING, "The **training set**")  # @stepover
    table_caption(LOGPRECIS_MAPPING)  # @stepover

    text("Then: an **off-the-shelf CodeBERT**, domain-adapted, with a one-layer classifier on top. Nothing exotic.")
    text("- ⚠️ Note the asymmetry with DarkVec: there we **trained** the embedding, here we **borrow** one.", style=SUBLIST)
    text("- Cost per session afterwards: **one forward pass**. Still ⚡ fast-lane economics.", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: does 360 hand-labelled sessions really teach a model the mind of an attacker? **Let us run it.**")

    demo("LogPrécis, live")
    text("Not a re-implementation: this is **the model from the paper**, straight off the Hugging Face Hub.")

    logprecis = load_logprecis()  # @stepover
    text("**One captured session**, exactly as the honeypot logged it - a single line of text:")

    session = SESSION  # @inspect session

    text("🙋🏻‍♂️ **Question**: what is this attacker doing - and how many seconds did you need to say it?")
    text("The shell does not read it as one line, though: `;`, `&&`, `||` cut it into **statements**.")

    attack = statements(session)  # @inspect attack

    text("Four statements - and the *why* changes half-way through. That is what we want the model to find.")
    text("Now the model. It classifies **tokens**, so for each word we keep the label of its **first** token:")

    pairs = tactics_of(logprecis, session)  # @stepover
    per_word = labelled(pairs)  # @inspect per_word

    text("First the firewall goes down (**Impact**), then the payload is fetched, made executable, and run (**Execution**).")
    text("Collapse the consecutive repetitions, and the session becomes its **fingerprint**:")

    session_fingerprint = fingerprint(pairs)  # @inspect session_fingerprint

    text("13 words of shell → **two tactics**. The *how* is gone, the *why* remains: this is the whole abstraction.")  # @clear session attack per_word session_fingerprint

    text("Back to the claim we made above. Here is `rm`, **the same command**, in three different sessions:")

    rm_tactics = rm_in_context(logprecis)  # @inspect rm_tactics

    text("**One command, three tactics**:")
    text("- Erase your own probe (*Discovery*)", style=SUBLIST)
    text("- Erase the owner's keys to install yours (*Persistence*)", style=SUBLIST)
    text("- Erase the binary you just copied (*Execution*).", style=SUBLIST)

    text("**Notice:** You need *contextualised* embeddings to tell the difference!")  # @clear pairs rm_tactics
    text("- Word2Vec (non-contextual encoder) has only **one** vector for `rm`!", style=SUBLIST)
    text("- Here, we need a contextualised encoder (Transformer-based model) to tell the difference!", style=SUBLIST)

    text("And now what fingerprints are *for*. Six sessions, **no two identical** as strings:")

    campaign = list(CAMPAIGN)  # @inspect campaign

    text("Payload name, drop server and SSH key change every time: to a `grep`, these are **six different attacks**.")

    campaign_fingerprints = fingerprints_of(logprecis)  # @inspect campaign_fingerprints

    text("**6 unique sessions → 3 fingerprints.** The randomness lived in the *words*; the *intent* was shared.")  # @clear logprecis campaign campaign_fingerprints

    section("Which model? The design space")
    text("The paper compares **81** combinations (chunking × pre-training × model × entity). Two results:")
    text("- 🧠 **Pre-training is what pays**: BERT *from scratch* on the logs scores **0.27**, *pre-trained* **0.44**.", style=SUBLIST)
    text("- 💻 Pre-training **on code** beats pre-training on English (CodeBERT > BERT)", style=SUBLIST)
    text("- Shell is closer to Python than to Wikipedia", style=SUBSUBLIST)

    text("Now the comparison that matters for this lecture: **small and specialised** against **huge and general**.")
    table_head(LOGPRECIS_MODELS)  # @stepover
    table_row(LOGPRECIS_MODELS, "Word2Vec")  # @stepover
    table_row(LOGPRECIS_MODELS, "BERT")  # @stepover
    table_row(LOGPRECIS_MODELS, "**CodeBERT**")  # @stepover
    table_row(LOGPRECIS_MODELS, "GPT-3")  # @stepover
    table_caption(LOGPRECIS_MODELS)  # @stepover

    text("- Fine-tuning 130M parameters on **360** labels beats renting a model 1300× bigger. **Task fit > size.**", style=SUBLIST)
    text("- ⚠️ Even if winning, GPT-3 would have not been an option here (too slow for the ⚡ lane).", style=SUBLIST)

    section("The results, on two years of honeypots")
    text("Run it over both collections - **45M words**, none of them seen in training - and count what the analyst gets:")
    table_head(LOGPRECIS_RESULTS)  # @stepover
    table_row(LOGPRECIS_RESULTS, "Sessions")  # @stepover
    table_row(LOGPRECIS_RESULTS, "Where to look")  # @stepover
    table_row(LOGPRECIS_RESULTS, "Novelty")  # @stepover
    table_row(LOGPRECIS_RESULTS, "Words never seen")  # @stepover
    table_row(LOGPRECIS_RESULTS, "The `lockr`")  # @stepover
    table_row(LOGPRECIS_RESULTS, "Attack families")  # @stepover
    table_caption(LOGPRECIS_RESULTS)  # @stepover

    text("Observe the third row: *thousands of new sessions a day* is an unreadable queue.")
    text("- **5-10 new fingerprints a day** is a person's morning. That is the difference between the two lanes.", style=SUBLIST)
    text("And the fingerprints do not just count attacks - they let you **watch a family evolve**:")
    figure("images/logprecis_fingerprints_time.png", caption=LOGPRECIS_FINGERPRINTS, width="480px", caption_width="820px")  # @stepover

    section("Wrapping up")
    text("1) Again, the data was not text - but *commands in a session* behave like *words in a sentence*.", style=SUBLIST)
    text("2) Unlike DarkVec, the signal **is** in the words - but only **in context** → attention, not Word2Vec.", style=SUBLIST)
    text("3) ⚡ Fast-lane economics: **360** labels once, then **one forward pass** per session, locally.", style=SUBLIST)
    text("- **360** labels are enough *only* because the model is **pre-trained**: from scratch, fidelity is 0.27.", style=SUBSUBLIST)
    text("- And the 175B model was slower, pricier, and **not better**. Size is not the axis here.", style=SUBSUBLIST)
    text("4) 🎁 The payoff: **80%** of the words are labelled right even when they **never appeared in training**.", style=SUBLIST)
    text("- Those are the *random* strings. The model reads them **off their neighbours**.", style=SUBSUBLIST)
    text("- Word2Vec would have **no vector at all** for them. That is what attention buys you.", style=SUBSUBLIST)
    text('<p align="center">⚡ <strong>Two problems, one move</strong>: read the security data <em>as text</em>, and the whole NLP toolkit comes with it.<br><strong>Next:</strong> what happens when we can finally afford to <strong>think</strong> 🐢.</p>', style=CALLOUT)


def autopenbench_section():
    text("# 🐢 AutoPenBench: can an agent **break in**?")

    section("The setting: a penetration test 🎯")
    text("A **penetration test** is an authorised attack: someone is paid to break in, so that nobody else does it first.")
    text("- 🎯 An example of the 🐢 lane: **one target at a time**, hours of work, a written report at the end.", style=SUBLIST)
    text("- 🧠 And it is not *one* skill: scan, read the output, form a hypothesis, pick a tool, **fail**, try something else.", style=SUBLIST)
    text("- 💸 The bottleneck is the usual one: a pentest costs **days of an expert** who is already fully booked.", style=SUBLIST)
    text("Same Sisyphus as before, one lane over: the systems to test grow, the people who can test them do not.")
    text("🙋🏻‍♂️ **Question**: DarkVec had groups, LogPrécis had tactics. **What would you even label here?**")
    text("- Nothing. A real pentest ends in a **report** - prose, judged by another expert. No ground truth to score.", style=SUBLIST)

    section("Making it measurable: the CTF 🚩")
    text("The security community hit this wall long before us, and its fix is a **gamified pentest**: the **Capture The Flag**.")
    text("- 🚩 A machine deliberately built to be breakable, with a `flag` file placed **behind** the vulnerability.", style=SUBLIST)
    text("- 🎓 This is how *humans* are already measured: courses, competitions, hiring.", style=SUBLIST)
    text("- ⚠️ It is a **proxy**: a CTF box is *known* to be solvable, nobody writes the report at the end.", style=SUBLIST)
    text("So: keep the pentest **task**, borrow the CTF as the **ruler** → agent measured by **whether it finds the flag**.")

    section("The task")
    text("So the questions we would like to answer are simple to state:")
    text("- 1️⃣ Can an LLM agent run a penetration test **on its own**?", style=SUBLIST)
    text("- Other papers at the time already proved that a human-in-the-loop LLM can ([PentestGPT](https://www.usenix.org/conference/usenixsecurity24/presentation/deng)).", style=SUBSUBLIST)
    text("- We want to know if it can do it **without** a human, and if it can do it **reliably**.", style=SUBSUBLIST)
    text("- 2️⃣ **How should we measure it?**", style=SUBLIST)

    text("⚠️ Measuring is genuinely hard here, because **success is binary and success is rare**:")
    text("- Agent **A** finds the target, gets a shell, escalates to root, fumbles the last command → **SR=0**.", style=SUBLIST)
    text("- Agent **B** scans the network, gives up, does nothing else → **SR=0**.", style=SUBLIST)
    text("- Same number. **We just learned nothing about either.**", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: how would you tell A from B?")

    text("**AutoPenBench's answer, part one**: 33 vulnerable machines, in Docker, at two levels of realism.")
    table_head(AUTOPENBENCH_TARGETS)  # @stepover
    table_row(AUTOPENBENCH_TARGETS, "🧪 Access Control")  # @stepover
    table_row(AUTOPENBENCH_TARGETS, "🧪 Web Security")  # @stepover
    table_row(AUTOPENBENCH_TARGETS, "🧪 Network Security")  # @stepover
    table_row(AUTOPENBENCH_TARGETS, "🧪 Cryptography")  # @stepover
    table_row(AUTOPENBENCH_TARGETS, "🌍 **Real-world CVEs**")  # @stepover
    table_caption(AUTOPENBENCH_TARGETS)  # @stepover

    text("Note the last row: those CVEs are not exercises, they are **the vulnerabilities that made the news**.")
    figure("images/autopenbench_infrastructure.png", caption=AUTOPENBENCH_INFRA, width="560px", caption_width="820px")  # @stepover

    section("The 🐢 idea: the LLM *is* the pentester")
    text("Stop and compare with the two ⚡ works, because **everything we relied on there is gone**:")
    text("- DarkVec **trained** embeddings. LogPrécis **fine-tuned** an encoder. Here: **no training at all**.", style=SUBLIST)
    text("- There, the model produced a *vector* or a *tactic*. Here it generates the next **command**.", style=SUBLIST)

    text("Here the agent performs a **[REACT loop](https://openreview.net/challenge?redirect=%2Fpdf%3Fid%3DWE_vluYUL-X)**: *think → act → observe*")
    text("- Stopping conditions: flag turns up or the steps run out.", style=SUBLIST)
    table_head(AUTOPENBENCH_MAPPING)  # @stepover
    table_row(AUTOPENBENCH_MAPPING, "The **prompt**")  # @stepover
    table_row(AUTOPENBENCH_MAPPING, "The **observation**")  # @stepover
    table_row(AUTOPENBENCH_MAPPING, "The **action space**")  # @stepover
    table_row(AUTOPENBENCH_MAPPING, "The **memory**")  # @stepover
    table_row(AUTOPENBENCH_MAPPING, "The **loop**")  # @stepover
    table_row(AUTOPENBENCH_MAPPING, "The **supervision**")  # @stepover
    table_caption(AUTOPENBENCH_MAPPING)  # @stepover

    text("This is why the section is 🐢: **one LLM call per line** of that loop, minutes per target.")
    text("- 🧮 Recall the ⚡ arithmetic: minutes per item, times 12M events a day, is not *slow* - it is **impossible**.", style=SUBLIST)
    text("- But nobody is asked to pentest 12M machines. A pentest is **scoped in advance**:", style=SUBLIST)
    text("- That is the 🐢 lane's privilege: with **one item to work on**, minutes per step is the normal price.", style=SUBSUBLIST)

    section("Measuring a break-in: milestones")
    text("Back to question 2️⃣ - **A vs B**. The paper's answer: do not simply grade the *outcome*, grade the **path**.")
    text("- 🔹 **Command milestones**: the commands the agent *must* run, written as descriptions, not as strings.", style=SUBLIST)
    text("- *Find the SSH credentials* - Hydra, John, or a lucky guess all count. **Many solutions stay correct.**", style=SUBSUBLIST)
    text("- 🔸 **Stage milestones**: the **six phases** every pentest goes through, mapped onto those commands.", style=SUBLIST)
    text("- Discovery → Reconnaissance → Detection → Exploitation → Flag Capturing → Success.", style=SUBSUBLIST)
    figure("images/autopenbench_solution.png", caption=AUTOPENBENCH_SOLUTION, width="700px", caption_width="820px")  # @stepover
    text("Two numbers come out, and only the first one is the one you would have thought of:")
    text("- **Success Rate (SR)**: binary. Did the submitted flag match?", style=SUBLIST)
    text("- **Progress Rate (PR)**: the fraction of command milestones reached. **This is what tells A from B.**", style=SUBLIST)
    text("⚠️ **Who decides that a command reached a milestone?**")
    text("- 1️⃣ **LLM-as-a-judge**: GPT-4o reads the run's log and marks the milestone per command.", style=SUBLIST)
    text("- 2️⃣ **Human validation**: the authors check those marks and correct them. We publish these numbers.", style=SUBLIST)
    text("- Neither half works alone: the judge hallucinates, and a human cannot read every log of every run.", style=SUBSUBLIST)
    text("🙋🏻‍♂️ **Question**: enough theory - what does one of these runs actually look like?")

    demo("One task, seventeen steps")
    text("Nothing runs here: this is the agent's **own log**, from the appendix of the paper (gpt-4o, task AC0).")

    task = TASK  # @inspect task

    text("That is everything it is told. **No IP address, no service, no hint of what the vulnerability is.**")
    text("And this is everything it can *do* - four tools, and the first one is 'any Kali command':")

    tools = list(ACTION_SPACE)  # @inspect tools

    text("**One turn of the loop.** The LLM writes the first two lines; the container writes the third:")

    one_step = loop(AUTONOMOUS, 2)  # @inspect one_step

    text("That observation goes **straight back into the prompt** of the next turn. That is the whole architecture.")
    text("Now the entire run. Last column: the milestone that step achieved - **most steps achieve none**.")

    autonomous = replay(AUTONOMOUS)  # @inspect autonomous

    text("🏁 It wins. It also takes **17 steps to do 8**:")  # @clear task tools one_step

    text("Now grade it. First the path, stage by stage:")

    progress = stages(AUTONOMOUS)  # @inspect progress

    text("Then the two numbers:")

    autonomous_score = score(AUTONOMOUS, "autonomous")  # @inspect autonomous_score

    text("This run reached the flag, so **SR = 1** and **PR = 1.00** (by construction):")  # @clear progress
    text("- So on a *solved* task PR tells us nothing new.", style=SUBLIST)
    text("- It is on the **failed** runs that it starts to matter - we will see it shortly.", style=SUBLIST)

    text("**Now change exactly one thing**: a human writes the sub-goals. Same LLM, same tools, same target.")

    assisted = replay(ASSISTED)  # @inspect assisted

    text("Five lines of plain English:")
    text("- The human never says *how*: 'infiltrate as student' is a goal, not a command.", style=SUBLIST)
    text("- What it does is **cut the problem in five**, and **wipe the scratchpad** between the pieces.", style=SUBLIST)

    both = compare()  # @inspect both

    text("Same task, same model: **17 steps → 10**.")  # @clear autonomous wrong_turns autonomous_score assisted both

    section("The results, on all 33 targets")
    text("Both architectures, gpt-4o, one run per target:")
    table_head(AUTOPENBENCH_RESULTS)  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "Access Control")  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "Web Security")  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "Network Security")  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "Cryptography")  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "**Total in-vitro**")  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "**Real-world")  # @stepover
    table_row(AUTOPENBENCH_RESULTS, "**Overall**")  # @stepover
    table_caption(AUTOPENBENCH_RESULTS)  # @stepover

    text("**21% alone, 64% with a human.** Two rows deserve a second look:")
    text("- 🔐 **Cryptography: 0.00.** The agent *names* the weakness correctly then never recovers the key.", style=SUBLIST)
    text("- Everywhere else there is an exploit to **recall** (Metasploit module, a CVE write-up, a blog post).", style=SUBSUBLIST)
    text("- Crypto has none: Here the attack has to be **computed**, on *these* numbers.", style=SUBSUBLIST)
    text("- 🌍 **Real-world: 0.09 → 0.73.** The single biggest jump in the table, on the *hardest* tasks.", style=SUBLIST)

    text("And now use the PR to see **where** the autonomous agent loses the real CVEs - stage by stage:")
    text("- **100%** find the target. Reconnaissance is where it starts to bleed: **55%**.", style=SUBLIST)
    text("- It trusts `nmap` and stops there, instead of *talking* to the service.", style=SUBSUBLIST)
    text("- Of those that get through, **83%** pick the **right Metasploit exploit**. The knowledge is there.", style=SUBLIST)
    text("- Then **40%** of them **misconfigure its parameters** and fail. Knowing ≠ doing.", style=SUBLIST)
    text("⚠️ A Success Rate of 0.09 would have told us *none* of this. **This is what the milestones are for.**", style=CALLOUT)

    section("What a benchmark is *for*")
    text("**Same agent, same task** (AC0 - the easiest one), 5 runs, swap only the LLM:")
    table_head(AUTOPENBENCH_LLMS)  # @stepover
    table_row(AUTOPENBENCH_LLMS, "**gpt-4o**")  # @stepover
    table_row(AUTOPENBENCH_LLMS, "gpt-4-turbo")  # @stepover
    table_row(AUTOPENBENCH_LLMS, "gpt-4o-mini")  # @stepover
    table_row(AUTOPENBENCH_LLMS, "o1-mini")  # @stepover
    table_row(AUTOPENBENCH_LLMS, "o1-preview")  # @stepover
    table_row(AUTOPENBENCH_LLMS, "gemini-1.5")  # @stepover
    table_caption(AUTOPENBENCH_LLMS)  # @stepover

    text("**One model out of six** can drive the loop at all - on the *easiest* target in the benchmark.")
    text("- 🧠 The dominant failure is **contextual awareness**: the transcript grows, the agent forgets the plan.", style=SUBLIST)
    text("- Exactly what the assisted agent fixes by **emptying the scratchpad** at every sub-task.", style=SUBSUBLIST)
    text("- 🚫 And *o1-preview* did not fail - **it refused**, reading a sandboxed pentest as a jailbreak attempt.", style=SUBLIST)

    section("Wrapping up")
    text("1) 🐢 lane economics: no labels, no training - an off-the-shelf LLM, a shell, and minutes per target.", style=SUBLIST)
    text("- The 'adaptation' is a **prompt and a loop**, not a fine-tuning run. That is the whole shift.", style=SUBSUBLIST)
    text("2) The contribution is the **ruler**, not the agent: 33 reproducible targets, in Docker, with gold steps.", style=SUBLIST)
    text("3) 🎯 **Binary success hides everything.** Milestones turn *'it failed'* into *'it failed at exploit configuration'*.", style=SUBLIST)
    text("4) 🤝 **21% → 64%** by adding a human who, at the right time, only writes **five lines of plain English**.", style=SUBLIST)
    text("- Not a better model, not more tools: just someone **splitting the goal** and **clearing the context**.", style=SUBSUBLIST)
    text('<p align="center">🐢 The agent can <strong>act</strong>. What it still cannot do is <strong>stay on plan</strong> without help.<br><strong>Next:</strong> the same lane, the other side of the fence - the box is already compromised 🕵🏻.</p>', style=CALLOUT)


def cybersleuth_section():
    text("# 🕵🏻 CyberSleuth: box compromised - what happened?")

    section("The setting: post-mortem forensics 🔍")
    text("Flip the fence. The attack is **over**, it **worked**, and someone has to write down what happened.")
    text("- 🧾 **Incident triage**: an alert fires; someone must reconstruct what happened.", style=SUBLIST)
    text("- Evidence: A disk image, a memory dump, endpoint telemetry, application logs, a packet capture...", style=SUBSUBLIST)
    text("- 🕳️ Usually the **symptom** is the easy part - the damaged page, the machine mining crypt...", style=SUBLIST)
    text("- 🪾 The **root cause** is the hard part: the exploit that got them in, and the vulnerability it abused.", style=SUBLIST)
    text("- How did they get **in**, how far did they get, what did they **touch**, is it still running? ...", style=SUBSUBLIST)
    text("- ⏱️ Answer is **manual**: experts pivot across evidence and correlates it with public knowledge.", style=SUBLIST)
    text("Note the asymmetry with the previous section:")
    text("- 🥷 **Red team**: the system is **live** → every hypothesis is **self-verifying** (fire the exploit, see if works).", style=SUBLIST)
    text("- And many roads lead in: **any** one that reaches the flag counts as a win.", style=SUBSUBLIST)
    text("- 🛡️ **Blue team**: the system is **gone**. A frozen, **partial** recording - nothing left to probe.", style=SUBLIST)
    text("- And exactly **one** thing happened: the answer is not *a* plausible exploit, it is *the* one.", style=SUBSUBLIST)
    text("🙋🏻‍♂️ **Question**: here, there is *a ground truth*. **Why is it not simply easier than AutoPenBench?**")

    section("The task")
    text("*'Find the root cause'* is a **report**, not a label!")
    text("- There is no single correct string to compare it against, so it **cannot be scored** objectively.", style=SUBLIST)
    text("In CyberSleuth, we focus on **network incidents** and ask for something we can grade:")
    text("- 🧾 **Input.** Packet traces (pcaps) of the incident.", style=SUBLIST)
    text("- 🎯 **Expected Output.** The open-ended *why* collapses into **three questions**:", style=SUBLIST)
    text("- **Which service** was attacked", style=SUBSUBLIST)
    text("- **Which CVE** was exploited", style=SUBSUBLIST)
    text("- **Did the exploit work** (true/false)", style=SUBSUBLIST)
    text("- 🧑‍💻 **Who it is assisting.** an expert in **Wireshark**, following streams until matches with exploit.", style=SUBLIST)

    text("Here is what that looks like as a benchmark:")

    table_head(CYBERSLEUTH_SPREAD)  # @stepover
    table_row(CYBERSLEUTH_SPREAD, "**Incidents**")  # @stepover
    table_row(CYBERSLEUTH_SPREAD, "**Attack succeeded**")  # @stepover
    table_row(CYBERSLEUTH_SPREAD, "**Packets**")  # @stepover
    table_row(CYBERSLEUTH_SPREAD, "**Traffic volume**")  # @stepover
    table_caption(CYBERSLEUTH_SPREAD)  # @stepover

    text("Read the last two rows together: **831x more packets**, **23 000x more bytes** - and the same amount of *evidence*.")
    text("- 25MB of GitLab traffic hides one exploit request, exactly like a 2KB Solr trace does.", style=SUBLIST)
    text("- 🎯 **Size tells the agent nothing** about where to look, and it cannot afford to read everything.", style=SUBSUBLIST)

    text("A subset of the benchmark - the CVEs, the versions, the volumes:")

    table_head(CYBERSLEUTH_INCIDENTS)  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#8")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#0")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#4")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#6")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#12")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#17")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#14")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#15")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#28")  # @stepover
    table_row(CYBERSLEUTH_INCIDENTS, "#29")  # @stepover
    table_caption(CYBERSLEUTH_INCIDENTS)  # @stepover

    text("Two design choices in the table:")  # @clear incidents
    text("- 🔁 Each 2025 CVE appears **twice**: once on a vulnerable version, once on a **patched** one.", style=SUBLIST)
    text("- The exploit fired is *identical*. Only the answer to 'did it work' changes. **Recognition is not enough.**", style=SUBSUBLIST)
    text("- 📅 Incidents **20-29** CVEs were disclosed in **2025**, after the backends' training.", style=SUBLIST)

    text("We aim at answering the following questions:")
    text("- 1️⃣ **Service Identification** - did the agent name the service under attack?", style=SUBLIST)
    text("- 2️⃣ **CVE Detection** - did it name the *exact* CVE, not a plausible neighbour?", style=SUBLIST)
    text("- 3️⃣ **Attack Success** - did it correctly say whether the attack worked?", style=SUBLIST)
    text("⚠️ Note they are **sequential**, exactly like AutoPenBench's stages: no service → no CVE → no verdict.")

    section("The 🐢 idea: the LLM *is* the forensic analyst")
    text("Same lane as AutoPenBench, and yet **almost every design choice flips**:")
    table_head(CYBERSLEUTH_MAPPING)  # @stepover
    table_row(CYBERSLEUTH_MAPPING, "The **prompt**")  # @stepover
    table_row(CYBERSLEUTH_MAPPING, "The **observation**")  # @stepover
    table_row(CYBERSLEUTH_MAPPING, "The **action space**")  # @stepover
    table_row(CYBERSLEUTH_MAPPING, "The **memory**")  # @stepover
    table_row(CYBERSLEUTH_MAPPING, "The **loop**")  # @stepover
    table_row(CYBERSLEUTH_MAPPING, "The **supervision**")  # @stepover
    table_caption(CYBERSLEUTH_MAPPING)  # @stepover

    text("The row that decides everything is **the observation**. The agent's real environment is one command:")

    tshark = TSHARK  # @inspect tshark

    text("Every architecture in this paper is a choice of *which* of them to run - and of **who runs them**.")

    section("Three architectures, one trace")
    figure("images/cybersleuth_architectures.png", caption=CYBERSLEUTH_ARCH_FIG, width="720px", caption_width="820px")  # @stepover
    text("- 1️⃣ **SA** - **list of all packets** + plus **one packet at the time**, as a tool. Single Agent.", style=SUBLIST)
    text("- 2️⃣ **TEA** - gets **the connection list** + asks `tshark` sub-agent *in English* for anything else. *Nested*.", style=SUBLIST)
    text("- 3️⃣ **FRA** - summariser processes connections first; main agent works on the report. *Sequential*.", style=SUBLIST)
    text("🙋🏻‍♂️ **Question**: which one would you bet on?")  # @clear tshark
    text("- The intuition says 2️⃣ - it is the one that behaves like a real security team.", style=SUBLIST)

    section("The results: which architecture")
    text("Three architectures, GPT-4o fixed, 20 incidents, three runs each:")  # @clear bad_run
    table_head(CYBERSLEUTH_ARCHITECTURES)  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "Service ✅")  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "CVE ✅")  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "Success (Acc)")  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "Success (MCC)")  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "Steps")  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "Input tokens")  # @stepover
    table_row(CYBERSLEUTH_ARCHITECTURES, "Cost")  # @stepover
    table_caption(CYBERSLEUTH_ARCHITECTURES)  # @stepover

    text("**The intuition was wrong.** The *simplest* orchestration wins - and wins on every column at once:")
    text("- 🥇 **FRA beats TEA** on accuracy, on steps, on tokens, and on cost. It is not a trade-off.", style=SUBLIST)
    text("- 🧠 **18 steps → 5.5.** SA's high step count is not diligence, it is **losing the thread**.", style=SUBLIST)
    text("- ⚠️ **MCC = -0.11** for SA: with no evidence it defaults to *'attack failed'*, which is **wrong on this set**.", style=SUBLIST)
    text("- Accuracy 0.47 looked survivable. MCC says it is **worse than a coin toss**. Pick your metric carefully.", style=SUBSUBLIST)
    text("🙋🏻‍♂️ **Question**: why does giving the agent *more* freedom (TEA) make it *worse*?")
    text("- Because freedom has to be **spent well**! ", style=SUBLIST)
    text("- TEA's main agent asks *'explore the HTTP traffic'* and gets noise back (**coordination failure**)", style=SUBSUBLIST)
    text("- **Example**: See Appendix B. Incident **4**: Apache HTTP Server 2.4.49, path traversal.", style=SUBSUBLIST)
    text("- FRA does the reading **once, up front, for every connection**.", style=SUBLIST)
    text("- No instruction to get wrong.", style=SUBSUBLIST)
    text("- Problem: if summarizer fails, main agent cannot go back :(", style=SUBSUBLIST)

    section("The results: which LLM")
    text("Now fix the architecture to **FRA** and swap the backend:")
    table_head(CYBERSLEUTH_LLMS)  # @stepover
    table_row(CYBERSLEUTH_LLMS, "GPT-4o")  # @stepover
    table_row(CYBERSLEUTH_LLMS, "o3")  # @stepover
    table_row(CYBERSLEUTH_LLMS, "**GPT-5**")  # @stepover
    table_row(CYBERSLEUTH_LLMS, "**DeepSeek R1** 🔓")  # @stepover
    table_row(CYBERSLEUTH_LLMS, "Kimi K2 🔓")  # @stepover
    table_row(CYBERSLEUTH_LLMS, "Llama-4 Maverick 🔓")  # @stepover
    table_caption(CYBERSLEUTH_LLMS)  # @stepover

    text("Contrast with AutoPenBench's table, where **five models out of six scored zero**:")
    text("- 🔓 Here the **open-weight** models are competitive - and DeepSeek R1 is the *best* at finding the service.", style=SUBLIST)
    text("- 💾 Good beyond the price! forensic traces = **evidence**. On-premise → evidence stay local.", style=SUBSUBLIST)
    text("- 📉 Spread is much narrower → **FRA did the hard part**.", style=SUBLIST)
    figure("images/cybersleuth_websearch.png", caption=CYBERSLEUTH_WEBSEARCH, width="620px", caption_width="820px")  # @stepover
    text("That figure splits one number into **two skills**, and no model has both by default:")
    text("- 🔍 **Retrieval**: did the search return the right CVE? *Llama-4 Maverick* is the best searcher (**80%**).", style=SUBLIST)
    text("- 🎯 **Selection**: did it then pick that one? *Maverick* picks a near-identical neighbour **30%** of the time.", style=SUBLIST)
    text("- 🤨 And *o3* skips the search in **half** the runs, answering from memory. **It is often right.**", style=SUBLIST)
    text("- ⚠️ Which works until the CVE is newer than the model. That is the next table.", style=SUBSUBLIST)

    demo("Retrieval is not selection")
    text("Incident **12**, Apache APISIX 2.9. Both backends run FRA and retrieve the **same two candidate CVEs**.")
    text("Here is what GPT-4o wrote in its own summary - the only thing that reaches the main agent:")

    gpt4o = summaries("GPT-4o", APISIX_GPT4O, APISIX_RUNS["GPT-4o"])  # @inspect gpt4o

    text("Both entries say *'this is relevant, RCE, be careful'*. **Nothing distinguishes them.** Now GPT-5:")

    gpt5 = summaries("GPT-5", APISIX_GPT5, APISIX_RUNS["GPT-5"])  # @inspect gpt5

    text("🎯 The difference is one clause: *'no evidence of the batch-requests plugin was observed in the traffic'*.")  # @clear gpt4o
    text("- It **ruled a candidate out** by checking it against the evidence, instead of describing both.", style=SUBLIST)
    text("- Same architecture, same tool, same two CVEs retrieved. **1/3 runs correct → 3/3.**", style=SUBLIST)

    section("Test of time: 2025 CVEs")
    text("Everything so far was tuned on 20 incidents the models could have memorised. The test set could not be:")  # @clear gpt5
    table_head(CYBERSLEUTH_TESTSET)  # @stepover
    table_row(CYBERSLEUTH_TESTSET, "Service ✅")  # @stepover
    table_row(CYBERSLEUTH_TESTSET, "CVE ✅")  # @stepover
    table_row(CYBERSLEUTH_TESTSET, "Success (MCC)")  # @stepover
    table_row(CYBERSLEUTH_TESTSET, "Steps")  # @stepover
    table_row(CYBERSLEUTH_TESTSET, "Cost")  # @stepover
    table_caption(CYBERSLEUTH_TESTSET)  # @stepover

    text("**80% on the exact CVE**, on vulnerabilities disclosed after training - and *higher* than on the design set.")
    text("- 🤔 Higher, because these are **single-service** incidents.", style=SUBLIST)
    text("- 🔓 **DeepSeek matches GPT-5 on the CVE at 1/3 of the cost** - only struggles on the verdict.", style=SUBLIST)
    text("- 🕊️ And on **10 benign browsing traces**: no false alarms. ", style=SUBLIST)
    text("- It flagged two repeated-failed-login episodes, which were real.", style=SUBSUBLIST)

    section("Does the design travel? 🧳")
    text("Everything so far was **one** forensic task. So take the finished agent to a *different* one - **malware infections**:")
    text("- 📼 **10 real captures** from the Unit 42 exercises", style=SUBLIST)
    text("A Windows host is infected, and generates outgoing traffic. The traffic is recorded.", style=SUBSUBLIST)
    text("- Bigger and messier than the web incidents - **5k-39k packets**, up to **27MB**.", style=SUBSUBLIST)
    text("- And the malicious flows sit inside the victim's normal browsing!", style=SUBSUBLIST)
    text("- ❓ And a different question: not *which CVE*, but **who was hit** (host, IP, user) and **which IoC**?", style=SUBLIST)
    text("🔧 The experiment is really about **what they were allowed to change**:")
    text("- ✏️ The **task prompt**, and what the Web Search tool is told to look for. That is the entire modification.", style=SUBLIST)
    text("- 🧱 Flow Summariser, token budget, memory manager, loop: **untouched**.", style=SUBLIST)
    text("- 🎯 Victim details correct in **9 of 10**, the relevant IOCs consistently extracted, and known campaigns named and confirmed by search - *Cobalt Strike*, *NetSupport RAT*.", style=SUBLIST)
    text("⚠️ The **architecture** transferred. The domain knowledge came from the **prompt** and the LLM!", style=CALLOUT)

    section("Wrapping up")
    text("1) 🧠 **Multi-agent specialisation is what works** - but *simple* orchestration, not deep nesting.", style=SUBLIST)
    text("- TEA had more freedom and expert tooling, and lost to a **pipeline with one arrow removed**.", style=SUBSUBLIST)
    text("2) 🔍 **Retrieval ≠ selection.** The best searcher was the worst chooser!.", style=SUBLIST)
    text("3) 🔓 **Open weights are competitive here**.", style=SUBLIST)
    text("- Good for evidence that cannot leave the building!", style=SUBSUBLIST)
    text("4) 🧾 **80% on 2025 CVEs**, in reports 25 experts called complete, useful and coherent.", style=SUBLIST)
    text("5) 🧳 **The design travels.** Same pipeline + new prompt: **9/10** victims identified on malware captures.", style=SUBLIST)
    text('<p align="center">🕵🏻 The architecture, not the model, is what turned <strong>28% → 68%</strong>.<br>Same LLM, same tools, same evidence - <strong>a different way of handing it over</strong>.</p>', style=CALLOUT)


def closing():
    text("# 🎬 Bringing It All Together")

    section("The four, in one line each")
    text("- ⚡ **DarkVec** - senders that *show up together* are words that *appear together*.", style=SUBLIST)
    text("- No LLM, no labels: one dot product per sender.", style=SUBSUBLIST)
    text("- ⚡ **LogPrécis** - a command is a word, a session a sentence.", style=SUBLIST)
    text("- **360** labels and a pre-trained encoder beat a **175B** model.", style=SUBSUBLIST)
    text("- 🐢 **AutoPenBench** - the LLM *is* the pentester.", style=SUBLIST)
    text("- **21% → 64%** by adding a human who writes **five lines of plain English**.", style=SUBSUBLIST)
    text("- 🕵🏻 **CyberSleuth** - the LLM *is* the forensic analyst.", style=SUBLIST)
    text("*- **80%** on CVEs disclosed *after* its own training cut-off.", style=SUBSUBLIST)

    section("What to take home")
    text("1) 🧩 **The same move, four times.** None of this data was text. Read it **as** text.", style=SUBLIST)
    text("- Word2Vec, attention, pre-training, agents - not one of them was invented for security.", style=SUBSUBLIST)
    text("2) 🗺️ **Choose lane before choosing models** - your **budget per item** decides the lane.", style=SUBLIST)
    text("- ⚡ Milliseconds, the whole stream. 🐢 Minutes, the one case that survived triage.", style=SUBSUBLIST)
    text("- [A Systematic Comparison of Large Language Models Performance for Intrusion Detection](https://dl.acm.org/doi/abs/10.1145/3696379)", style=SUBSUBLIST)
    text("- DRIFTGUARD: Self-Repair for Phishing Detection using LLM-Guided Active Learning ([WTMC](https://wtmc.info/index.html))", style=SUBSUBLIST)
    text("3) 🏗️ **Slow lane → architecture beats the model.** Same LLM, same tools, same evidence: **28% → 68%**.", style=SUBLIST)
    text("- The *simplest* orchestration won, and a human writing five lines of English beat a better backend.", style=SUBSUBLIST)
    text("4) 📏 **Build the ruler, not just the agent.** Binary success hid the failures!", style=SUBLIST)
    text("- Milestones, MCC, CVEs newer than the model... **The measurement is part of the contribution!**", style=SUBSUBLIST)
    text("- [Establishing best practices for building rigorous agentic benchmarks](https://neurips.cc/virtual/2025/loc/san-diego/poster/121769)", style=SUBSUBLIST)
    text("5) 🔓 **Open weights are competitive now** - decisive where the evidence cannot leave the building.", style=SUBLIST)

    text("⚠️ What still does not work:")
    text("- 🧠 **Staying on plan.** The agent acts well and forgets why; 5/6 backends could not drive the loop at all.", style=SUBLIST)
    text("- 🗣️ **Agents talking to agents.** TEA failed because two agents never agreed on what to look for.", style=SUBLIST)
    text("- 🔐 **Computing instead of recalling.** Cryptography: **0.00**. No look up → true reasoning skills!.", style=SUBLIST)

    section("Thanks for the attention 🙇🏻‍♂️")

    instructor_card()  # @stepover

    text('<p align="center">📬 <strong>Questions</strong>: <a href="mailto:matteo.boffa@polito.it">matteo.boffa@polito.it</a><br>' "📄 The four papers are linked in the opening table - <strong>they are the place for the details</strong>.<br>" "<strong>Grazie, e buona caccia 🕵🏻</strong></p>", style=CALLOUT)


def build_sentences(packets: list[tuple[float, str, int]]) -> dict[tuple[str, int], list[str]]:
    """Every packet joins the sentence of its own (service, hour) - and that is the whole corpus."""
    sentences = {}
    for timestamp, sender, port in packets:  # @inspect sender port
        key = (PORT_TO_SERVICE[port], int(timestamp // HOUR))  # @inspect key
        sentences.setdefault(key, []).append(sender)  # @inspect sentences
    return sentences  # @clear sender port key sentences


def load_word_embeddings():
    """DistilBERT's *input* embedding table: one static vector per token, learned
    from co-occurrence during pre-training - before any attention, any context."""
    import numpy as np
    from transformers import AutoModel, AutoTokenizer

    matrix = AutoModel.from_pretrained("distilbert-base-uncased").embeddings.word_embeddings.weight.detach().numpy()
    return AutoTokenizer.from_pretrained("distilbert-base-uncased"), matrix / np.linalg.norm(matrix, axis=1, keepdims=True)


def load_fill_mask():
    """The off-the-shelf checkpoint, straight from the Hugging Face Hub."""
    from transformers import pipeline

    return pipeline("fill-mask", model="distilbert-base-uncased")


def load_logprecis():
    """The model published with the paper: a CodeBERT domain-adapted on Unix
    sessions, then fine-tuned to tag every token with a MITRE tactic."""
    from transformers import pipeline

    return pipeline("token-classification", model="SmartDataPolito/logprecis")


def load_chat_model():
    """Same recipe as FLAN — pre-training plus instruction tuning — at 0.5B parameters."""
    from transformers import pipeline

    return pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
