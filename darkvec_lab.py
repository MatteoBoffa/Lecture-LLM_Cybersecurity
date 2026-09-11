"""A pocket-sized DarkVec, for the live demo in 01_intro.py.

The paper trains gensim's skip-gram Word2Vec on 486M skip-grams (~1.2 hours).
That does not fit in a lecture, so here the embedding is built by factorising
the PPMI matrix of the very same co-occurrence counts: Levy and Goldberg
(NeurIPS 2014, https://papers.nips.cc/paper/5477) show skip-gram with negative
sampling is implicitly doing exactly this factorisation.  It runs in
milliseconds, and - unlike SGD - it gives the same vectors on every run, which
is what a lecture needs.

Everything here works on a *toy* darknet: 24 hours, ~40 senders, built so that
the failure mode of the port-based baseline is visible by eye.
"""

import numpy as np

# Ports grouped as the paper does it: domain knowledge, one service per group
# of ports that a real application would use (Table 7 in the paper).
SERVICES = {
    "telnet": (23, 2323),
    "smb": (445, 139),
    "http": (80, 443, 8080),
    "db": (1433, 3306, 5432, 6379),
    "remote": (22, 3389, 5900),
    "iot": (5555, 37215, 52869),
}
PORT_TO_SERVICE = {port: service for service, ports in SERVICES.items() for port in ports}

HOUR = 3600

# The three coordinated groups of the toy trace, and the crowd they hide in.
# `scan-*` is the interesting one: it spreads over many ports, and every one of
# those ports is *also* used by some `noise-*` sender - which is precisely why
# the port profile cannot tell them apart (cf. Figure 3 and Table 6 of the paper).
BOTNET = [f"bot-{i}" for i in range(8)]
SCANNERS = [f"scan-{i}" for i in range(6)]
SMB_GROUP = [f"smb-{i}" for i in range(5)]
NOISE = [f"noise-{i}" for i in range(20)]

SCAN_PORTS = (80, 443, 8080, 1433, 3306, 5432, 6379, 22, 3389, 5900)

# Colours picked to match the slide palette: the three coordinated groups get
# saturated hues, the crowd stays grey.
GROUP_COLOURS = {"bot": "#d62728", "scan": "#2563eb", "smb": "#2ca02c", "noise": "#b8c4d2"}


def synthetic_darknet(hours: int = 24, seed: int = 0) -> list[tuple[float, str, int]]:
    """One day of toy darknet packets, as (timestamp, sender, destination port).

    Three coordinated groups plus a crowd of unrelated senders:
      * `bot-*`    a Mirai-like botnet: all 8 hosts hammer Telnet, every hour;
      * `scan-*`   a scan project: 6 hosts sweeping 10 ports, but only in
                   bursts, and always the same hours - together;
      * `smb-*`    5 hosts scanning SMB on a regular hourly beat;
      * `noise-*`  everybody else: a couple of ports each, at random times.
    """
    rng = np.random.default_rng(seed)
    packets: list[tuple[float, str, int]] = []

    def send(sender: str, port: int, hour: int) -> None:
        packets.append((hour * HOUR + float(rng.uniform(0, HOUR)), sender, port))

    for hour in range(hours):
        # The botnet: always on, always Telnet, always all together.
        for sender in BOTNET:
            for _ in range(3):
                send(sender, int(rng.choice([23, 23, 23, 2323])), hour)
        # The SMB group: same beat, one service.
        for sender in SMB_GROUP:
            send(sender, int(rng.choice([445, 445, 139])), hour)

    # The scan project: each host gets its *own* slice of the port space - as
    # Censys does with its sub-fleets - so no two members look alike port-wise.
    # What they do share is the clock: the fleet wakes up in the same 6 hours.
    slices = {sender: rng.choice(SCAN_PORTS, size=4, replace=False) for sender in SCANNERS}
    for hour in rng.choice(hours, size=6, replace=False):
        for sender in SCANNERS:
            for port in slices[sender]:
                for _ in range(2):
                    send(sender, int(port), int(hour))

    # The crowd: each sender picks a handful of ports out of the *same* pool the
    # scan project uses, and hits them whenever it feels like it.
    for sender in NOISE:
        for port in rng.choice(SCAN_PORTS, size=int(rng.integers(3, 7)), replace=False):
            for _ in range(int(rng.integers(2, 5))):
                send(sender, int(port), int(rng.integers(hours)))

    return sorted(packets)


def preview(packets: list[tuple[float, str, int]], n: int = 4) -> list[str]:
    """The first n packets, as an analyst would read them off the wire."""
    return [f"{int(t) // 3600:02d}:{int(t) % 3600 // 60:02d}:{int(t) % 60:02d}  {sender:<9} -> port {port:<5} ({PORT_TO_SERVICE[port]})" for t, sender, port in packets[:n]]


def labels_of(senders: list[str]) -> list[str]:
    """The ground truth of the toy trace: the group each sender belongs to."""
    return [sender.split("-")[0] for sender in senders]


def corpus_of(packets: list[tuple[float, str, int]], window: int = HOUR, service: str | None = None) -> list[list[str]]:
    """The DarkVec corpus: one sentence per (service, time window).

    A sentence is the sequence of sender IP addresses that hit the ports of one
    service inside one time window, **in order of arrival** - the darknet
    equivalent of "words in a sentence".  Pass `service` to look at the
    sentences of a single service (handy on a slide).
    """
    sentences: dict[tuple[str, int], list[str]] = {}
    for timestamp, sender, port in packets:  # packets arrive sorted in time
        key = (PORT_TO_SERVICE[port], int(timestamp // window))
        if service is None or key[0] == service:
            sentences.setdefault(key, []).append(sender)
    return [sentence for _, sentence in sorted(sentences.items()) if len(sentence) > 1]


def corpus_summary(corpus: list[list[str]]) -> dict[str, int]:
    """Shape of the corpus - the whole thing is far too big to put on a slide."""
    return {
        "sentences": len(corpus),
        "words (packets)": sum(len(sentence) for sentence in corpus),
        "vocabulary (senders)": len({sender for sentence in corpus for sender in sentence}),
        "longest sentence": max(len(sentence) for sentence in corpus),
    }


def port_profiles(packets: list[tuple[float, str, int]]) -> tuple[list[str], np.ndarray]:
    """The baseline features: *which ports* each sender hits, as shares.

    This is the paper's baseline (Section 4), and it throws away time entirely.
    """
    senders = sorted({sender for _, sender, _ in packets})
    ports = sorted({port for _, _, port in packets})
    counts = np.zeros((len(senders), len(ports)))
    for _, sender, port in packets:
        counts[senders.index(sender), ports.index(port)] += 1
    return senders, normalize(counts / counts.sum(axis=1, keepdims=True))


def darkvec(corpus: list[list[str]], dim: int = 8, context: int = 5) -> tuple[list[str], np.ndarray]:
    """Sender embeddings from co-occurrence alone: PPMI, then a truncated SVD."""
    senders = sorted({sender for sentence in corpus for sender in sentence})
    index = {sender: i for i, sender in enumerate(senders)}

    # Count how often two senders show up within `context` positions of each
    # other - the skip-gram window, exactly as in Figure 5 of the paper.
    counts = np.zeros((len(senders), len(senders)))
    for sentence in corpus:
        for position, sender in enumerate(sentence):
            for other in sentence[position + 1 : position + 1 + context]:
                counts[index[sender], index[other]] += 1
                counts[index[other], index[sender]] += 1

    # PPMI: how much more often than chance do these two senders co-occur?
    # Negative evidence is dropped (a *missing* pair says very little).
    # The 0.75 exponent is word2vec's own trick: without it, rare pairs get
    # implausibly high scores and a busy group like the botnet - which co-occurs
    # with itself constantly - gets pushed out of the embedding altogether.
    total = counts.sum()
    sender_share = counts.sum(axis=1, keepdims=True) / total
    context_share = counts.sum(axis=0) ** 0.75
    context_share = (context_share / context_share.sum())[None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((counts / total) / (sender_share * context_share))
    ppmi = np.nan_to_num(np.maximum(pmi, 0), nan=0.0, neginf=0.0, posinf=0.0)

    # Factorise: each sender becomes a point in `dim` dimensions.
    u, s, _ = np.linalg.svd(ppmi)
    return senders, normalize(u[:, :dim] * np.sqrt(s[:dim]))


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Unit-norm rows, so that a dot product *is* the cosine similarity."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(norms == 0, 1, norms)


def neighbours(space: tuple[list[str], np.ndarray], sender: str, k: int = 5) -> list[str]:
    """The k closest senders in the given space, by cosine similarity."""
    senders, vectors = space
    similarity = vectors @ vectors[senders.index(sender)]
    similarity[senders.index(sender)] = -np.inf  # never return the query itself
    return [f"{senders[i]} ({similarity[i]:.2f})" for i in np.argsort(-similarity)[:k]]


def knn_predict(space: tuple[list[str], np.ndarray], k: int = 7) -> tuple[list[str], list[str]]:
    """Leave-one-out k-NN over the toy ground truth: (truth, prediction) per sender."""
    senders, vectors = space
    truth = labels_of(senders)
    similarity = vectors @ vectors.T
    np.fill_diagonal(similarity, -np.inf)

    predicted = []
    for i in range(len(senders)):
        votes = [truth[j] for j in np.argsort(-similarity[i])[:k]]
        predicted.append(max(set(votes), key=votes.count))
    return truth, predicted


def knn_accuracy(space: tuple[list[str], np.ndarray], k: int = 7) -> str:
    """Overall leave-one-out accuracy - the number the paper reports as 0.96."""
    truth, predicted = knn_predict(space, k)
    return f"{sum(t == p for t, p in zip(truth, predicted)) / len(truth):.0%}"


def recall_by_group(space: tuple[list[str], np.ndarray], k: int = 7) -> dict[str, str]:
    """Per-group recall: the paper's Table 4/6 view, where the small groups show."""
    truth, predicted = knn_predict(space, k)
    return {group: f"{sum(p == group for t, p in zip(truth, predicted) if t == group) / truth.count(group):.0%}" for group in GROUP_COLOURS}


def scatter(space: tuple[list[str], np.ndarray], title: str) -> dict:
    """A Vega-Lite scatter of the space, projected to its two main axes."""
    senders, vectors = space
    projected = np.linalg.svd(vectors - vectors.mean(axis=0))[0][:, :2] if vectors.shape[1] > 2 else vectors
    groups = labels_of(senders)
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
        "title": title,
        "width": 420,
        "height": 300,
        "data": {"values": [{"x": float(x), "y": float(y), "group": group, "sender": sender} for (x, y), group, sender in zip(projected, groups, senders)]},
        "mark": {"type": "point", "filled": True, "size": 90, "opacity": 0.85},
        "encoding": {
            "x": {"field": "x", "type": "quantitative", "axis": {"title": "dimension 1"}},
            "y": {"field": "y", "type": "quantitative", "axis": {"title": "dimension 2"}},
            "color": {"field": "group", "type": "nominal", "scale": {"domain": list(GROUP_COLOURS), "range": list(GROUP_COLOURS.values())}, "legend": {"title": "group"}},
            "tooltip": [{"field": "sender", "type": "nominal"}],
        },
    }
