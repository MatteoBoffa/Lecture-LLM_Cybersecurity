"""Reusable slide furniture.

Kept out of the lecture files because edtrace shows the traced module's source
in the viewer, and this markup would drown the lecture itself.
"""

import inspect
import os
import re
import textwrap

from edtrace import image, text, video

# Figures: capped width so a tall diagram does not dominate the slide, centred
# with a soft frame so it reads as a figure rather than an inline screenshot.
FIGURE = {
    "display": "block",
    "width": "620px",
    "maxWidth": "100%",
    "margin": "18px auto 4px auto",
    "borderRadius": "12px",
    "border": "1px solid #dbe4ee",
    "boxShadow": "0 2px 12px rgba(15, 40, 80, 0.10)",
}

CAPTION = {
    "display": "block",
    "textAlign": "center",
    "fontSize": "13px",
    "color": "#5b6b7f",
    "margin": "0 auto 18px auto",
    "maxWidth": "620px",
    "lineHeight": "1.45",
}

# Callout box for the take-away line: light blue panel with an accent rail,
# matching the blue used by the plots.
CALLOUT = {
    "display": "block",
    "background": "#eaf2fb",
    "borderLeft": "5px solid #2563eb",
    "borderRadius": "10px",
    "padding": "16px 20px",
    "margin": "18px 0 6px 0",
    "lineHeight": "1.6",
    "boxShadow": "0 1px 3px rgba(15, 40, 80, 0.08)",
}

# Extensions figure() hands to edtrace's video() instead of image().  The
# viewer renders those with `controls`, which is the whole point: an animation
# you can stop on the frame you are talking about.
MOVIE_SUFFIXES = (".mp4", ".webm", ".mov", ".m4v")

SUBLIST = {"display": "block", "marginLeft": "2em"}
SUBSUBLIST = {"display": "block", "marginLeft": "4em"}

INSTRUCTORS = [
    {
        "name": "Danilo Giordano",
        "affiliation": "Politecnico di Torino",
        "image": "images/DaniloGiordano.png",
        "focus": "50% 50%",
        "url": "https://www.polito.it/personale?p=danilo.giordano",
        "is_instructor": False,
    },
    {
        "name": "Matteo Boffa",
        "affiliation": "Politecnico di Torino",
        "image": "images/MatteoBoffa.jpeg",
        "focus": "50% 50%",
        "url": "https://www.polito.it/personale?p=051974",
        "is_instructor": True,
    },
    {
        "name": "Idilio Drago",
        "affiliation": "Università di Torino",
        "image": "images/IdilioDrago.jpg",
        # The portrait is a full shot, so pull the crop up to the face.
        "focus": "50% 22%",
        "url": "https://www.cs.unito.it/persone/idilio.drago",
        "is_instructor": False,
    },
]


def figure(path: str, caption: str | None = None, width: str = "620px", caption_width: str | None = None) -> None:
    """Show a centred, framed figure, with an optional caption underneath.

    `width` is any CSS length ("440px", "60%", ...).  edtrace's own
    image(..., width=...) writes the width into the style dict it is handed, so
    a copy is passed here to keep FIGURE from being mutated between calls.

    The caption is as wide as the image unless `caption_width` says otherwise:
    a near-square figure has to stay narrow to keep its *height* in line with
    the rest of the deck, which would otherwise squeeze a long caption into a
    tall, thin column.

    A video path (see MOVIE_SUFFIXES) is rendered by edtrace as a <video> tag
    with the browser's native controls, so an animation can be **paused,
    resumed and scrubbed** while commenting it - which a GIF cannot do. Frame,
    width and caption are identical either way, so switching an animation from
    .gif to .mp4 needs no other change on the lecture line.
    """
    show = video if path.lower().endswith(MOVIE_SUFFIXES) else image
    show(path, style={**FIGURE, "width": width})
    if caption:
        text(caption, style={**CAPTION, "maxWidth": caption_width or width})


# Section dividers.  Numbering restarts on its own whenever a different lecture
# function starts calling them, so reordering sections never needs a renumber.
_SECTION_COUNTERS: dict[str, int] = {}

SECTION_ACCENT = "#8494a8"  # reading
DEMO_ACCENT = "#2563eb"  # running code


def section(label: str) -> None:
    """A numbered divider: grey chip, label, hairline rule."""
    _divider(label, SECTION_ACCENT)


def demo(label: str) -> None:
    """Same divider in accent blue: the audience should watch the code panel."""
    _divider(label, DEMO_ACCENT)


def _divider(label: str, accent: str) -> None:
    caller = inspect.stack()[2].function
    number = _SECTION_COUNTERS.get(caller, 0) + 1
    _SECTION_COUNTERS[caller] = number
    chip = f'<span style="background:{accent}; color:#fff; font-size:12px; font-weight:700; border-radius:999px; padding:2px 9px;">{number}</span>'
    name = f'<span style="font-size:15px; font-weight:600; color:#1f3550;">{label}</span>'
    rule = '<span style="flex:1; height:1px; background:#dbe4ee;"></span>'
    text(f'<div style="display:flex; align-items:center; gap:10px; margin:30px 0 12px 0;">{chip}{name}{rule}</div>')


def ask(chat, question: str, max_new_tokens: int = 60) -> str:
    """One answer from an instruction-tuned model, greedily decoded so the
    lecture reproduces the same text on every run."""
    reply = chat([{"role": "user", "content": question}], max_new_tokens=max_new_tokens, do_sample=False)
    return reply[0]["generated_text"][-1]["content"].strip()


def word_vector(embeddings, word: str):
    """The (unit-norm) embedding of a word that the tokenizer keeps in one piece."""
    tokenizer, matrix = embeddings
    token_ids = tokenizer.encode(word, add_special_tokens=False)
    if len(token_ids) != 1:  # "botnet" is split into pieces, and has no vector of its own
        raise ValueError(f"{word!r} is not a single token: {tokenizer.convert_ids_to_tokens(token_ids)}")
    return matrix[token_ids[0]]


def closest_words(embeddings, vector, exclude: set[str], k: int) -> list[str]:
    """The k vocabulary entries closest to `vector`, with their cosine similarity."""
    import numpy as np

    tokenizer, matrix = embeddings
    similarity = matrix @ (vector / np.linalg.norm(vector))

    found = []
    for index in np.argsort(-similarity):
        token = tokenizer.convert_ids_to_tokens(int(index))
        if token in exclude or not token.isalpha():  # skip the inputs and the sub-word debris
            continue
        found.append(f"{token} ({similarity[index]:.2f})")
        if len(found) == k:
            return found
    return found


def analogy(embeddings, word: str, minus: str, plus: str, k: int = 4) -> list[str]:
    """The classic vector arithmetic: word - minus + plus = ?"""
    vector = word_vector(embeddings, word) - word_vector(embeddings, minus) + word_vector(embeddings, plus)
    return closest_words(embeddings, vector, exclude={word, minus, plus}, k=k)


def similar_words(embeddings, word: str, k: int = 4) -> list[str]:
    """The k nearest neighbours of a word in the embedding space."""
    return closest_words(embeddings, word_vector(embeddings, word), exclude={word}, k=k)


def figure_row(paths: list[str], caption: str | None = None, width: str = "340px", gap: str = "14px") -> None:
    """Several figures side by side, centred, under one shared caption.

    Emitted as one raw-HTML flex row rather than as separate image() renderings:
    those are laid out inline inside a fixed-width container, so any leftover
    space piles up on the right instead of splitting evenly.
    """
    for path in paths:
        if not os.path.exists(path):  # image() checks this for us; raw HTML does not
            raise ValueError(f"Image not found: {path}")

    img_style = css(dict(FIGURE, display="block", width=width, margin="0"))
    imgs = "".join(f'<img src="{path}" style="{img_style}">' for path in paths)
    text(f'<div style="display:flex; justify-content:center; align-items:flex-start; gap:{gap}; margin:18px 0 4px 0;">{imgs}</div>')
    if caption:
        text(caption, style={**CAPTION, "maxWidth": "100%"})


# Tables: no table styling ships with the viewer's markdown CSS, so the whole
# thing is emitted as inline-styled HTML, in the same palette as the figures
# and callouts above.
TABLE = {
    "display": "table",
    "width": "100%",
    "borderCollapse": "collapse",
    "tableLayout": "fixed",
    "fontSize": "13px",
    "lineHeight": "1.45",
    "margin": "16px 0 4px 0",
}

TABLE_HEAD = {
    "textAlign": "left",
    "padding": "7px 10px",
    "fontSize": "11px",
    "fontWeight": "700",
    "letterSpacing": "0.05em",
    "textTransform": "uppercase",
    "color": "#5b6b7f",
    "borderBottom": "2px solid #2563eb",
}

TABLE_CELL = {
    "padding": "9px 10px",
    "verticalAlign": "top",
    "borderBottom": "1px solid #dbe4ee",
    "color": "#1f3550",
}

# First column names the trend, last column carries the punchline: both get a
# little weight so the eye lands on them before reading the numbers.
TABLE_FIRST = {"fontWeight": "600"}
TABLE_LAST = {"color": "#1b4b91", "fontWeight": "600"}

TABLE_STRIPE = "#f5f9fd"


def table(headers: list[str], rows: list[list[str]], widths: list[str] | None = None, caption: str | None = None) -> None:
    """A comparison table, zebra-striped, with the last column as the take-away.

    Cells take the same inline markup as text() (`**bold**`, `[text](url)`):
    markdown is not parsed inside a raw-HTML block, so it is converted here.
    `widths` is one CSS length per column ("26%", "180px", ...).
    """
    for row in rows:
        if len(row) != len(headers):
            raise ValueError(f"Row has {len(row)} cells but there are {len(headers)} headers: {row}")

    cols = "".join(f'<col style="width:{width}">' for width in widths) if widths else ""
    head = "".join(f'<th style="{css(TABLE_HEAD)}">{inline(header)}</th>' for header in headers)

    body = ""
    for index, row in enumerate(rows):
        cells = ""
        for column, cell in enumerate(row):
            style = dict(TABLE_CELL)
            if column == 0:
                style.update(TABLE_FIRST)
            if column == len(row) - 1:
                style.update(TABLE_LAST)
            cells += f'<td style="{css(style)}">{inline(cell)}</td>'
        background = TABLE_STRIPE if index % 2 else "transparent"
        body += f'<tr style="background:{background};">{cells}</tr>'

    text(
        f'<table style="{css(TABLE)}">{cols}' f"<thead><tr>{head}</tr></thead>" f"<tbody>{body}</tbody></table>",
        style={"display": "block"},
    )
    if caption:
        text(caption, style={**CAPTION, "maxWidth": "100%", "textAlign": "left", "fontSize": "12px"})


# Revealed tables: same look as table(), but emitted one fragment per *source
# line*, because the viewer keeps a single set of renderings per line (a loop
# would overwrite itself) and highlights the current line.  One row per line
# therefore means one highlighted row at a time.  Every fragment is a table of
# its own with the same <col> widths, so the columns stay aligned; the row
# background is left transparent so the viewer's yellow cursor shows through.
TABLE_FRAGMENT = {**TABLE, "margin": "0"}


def table_head(spec: dict) -> None:
    """Open a revealed table: the header row, nothing else."""
    cols = "".join(f'<col style="width:{width}">' for width in spec.get("widths") or [])
    cells = "".join(f'<th style="{css(TABLE_HEAD)}">{inline(header)}</th>' for header in spec["headers"])
    text(f'<table style="{css(TABLE_FRAGMENT)}">{cols}<thead><tr>{cells}</tr></thead></table>', style={"display": "block"})


def table_row(spec: dict, key: str) -> None:
    """One row of a revealed table, found by the text of its first cell."""
    # Prefix first, so "A **word**" picks its own row rather than also matching
    # "**Embedding** of a **word**"; substring second, so a key can skip a leading emoji.
    matches = [row for row in spec["rows"] if row[0].lower().startswith(key.lower())]
    matches = matches or [row for row in spec["rows"] if key.lower() in row[0].lower()]
    if len(matches) != 1:  # fail while tracing, not in front of the class
        raise ValueError(f"{key!r} matches {len(matches)} rows: {[row[0] for row in matches]}")
    row = matches[0]

    cols = "".join(f'<col style="width:{width}">' for width in spec.get("widths") or [])
    cells = ""
    for column, cell in enumerate(row):
        style = dict(TABLE_CELL)
        if column == 0:
            style.update(TABLE_FIRST)
        if column == len(row) - 1:
            style.update(TABLE_LAST)
        cells += f'<td style="{css(style)}">{inline(cell)}</td>'
    text(f'<table style="{css(TABLE_FRAGMENT)}">{cols}<tbody><tr>{cells}</tr></tbody></table>', style={"display": "block"})


def table_caption(spec: dict) -> None:
    """Close a revealed table with its caption."""
    text(spec["caption"], style={**CAPTION, "maxWidth": "100%", "textAlign": "left", "fontSize": "12px"})


# A cited *book*: cover on the left, bibliographic line and a note on the right.
# Same idea as instructor_card() one row down - a portrait cover centred with
# figure() would push the bullets that follow it off the screen, and a book is
# not a figure anyway: it is a citation the audience should recognise on sight.
BOOK_CARD = {
    "display": "flex",
    "alignItems": "center",
    "gap": "22px",
    "background": TABLE_STRIPE,
    "border": "1px solid #dbe4ee",
    "borderRadius": "12px",
    "padding": "16px 22px",
    "margin": "18px 0 6px 0",
    "maxWidth": "700px",
    "boxShadow": "0 1px 3px rgba(15, 40, 80, 0.08)",
}

BOOK_COVER = {
    "display": "block",
    "width": "118px",
    "flexShrink": "0",
    "borderRadius": "5px",
    "boxShadow": "0 3px 12px rgba(15, 40, 80, 0.22)",
}


def book_card(cover: str, title: str, byline: str, note: str, source: str | None = None) -> None:
    """Cite a book the way the deck cites a person: with its face.

    `note` takes the same inline markup as text() and carries the reason the
    book is on the slide; `source` is the small print underneath.
    """
    if not os.path.exists(cover):  # image() checks this for us; raw HTML does not
        raise ValueError(f"Cover not found: {cover}")

    small = f'<div style="font-size:11.5px; color:#5b6b7f; margin-top:9px;">{inline(source)}</div>' if source else ""
    # Dedent before interpolating, and join without blank lines: a blank line
    # would close the raw-HTML block and let markdown wrap the rest in <p>.
    card = textwrap.dedent("""
    <div style="{card}">
        <img src="{cover}" style="{image}">
        <div>
            <div style="font-size:17px; font-weight:700; color:#1f3550;">{title}</div>
            <div style="font-size:13px; color:#5b6b7f; margin:3px 0 11px 0;">{byline}</div>
            <div style="font-size:14px; color:#1f3550; line-height:1.5; border-left:3px solid #2563eb; padding-left:12px;">{note}</div>
            {small}
        </div>
    </div>
    """)
    text(card.format(card=css(BOOK_CARD), cover=cover, image=css(BOOK_COVER), title=inline(title), byline=inline(byline), note=inline(note), small=small).strip())


def inline(markup: str) -> str:
    """`**bold**`, `*italic*` and `[text](url)` to HTML; anything else passes through."""
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', markup)
    html = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", html)
    html = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", html)
    return html


def css(style: dict) -> str:
    """Turn a React-style dict into an inline CSS string."""

    def dashed(key: str) -> str:
        return "".join("-" + c.lower() if c.isupper() else c for c in key)

    return ";".join(f"{dashed(key)}:{value}" for key, value in style.items())


def instructor_card():
    # Join without blank lines: a blank line would end the raw-HTML block and
    # let the markdown renderer wrap the rest in <p> tags.
    cards = "\n".join(person_card(person).strip() for person in INSTRUCTORS)
    # Dedent the template *before* interpolating, otherwise the flush-left card
    # HTML makes the common indent 0 and the wrapper stays indented (which
    # markdown reads as a code block).
    row = textwrap.dedent("""
    <div style="
        display:flex;
        justify-content:center;
        align-items:flex-start;
        gap:48px;
    ">
    {cards}
    </div>
    """)
    text(row.format(cards=cards))


def person_card(person: dict) -> str:
    return textwrap.dedent(f"""
    <div style="width:150px; text-align:center; font-size:14px;">
        <a href="{person["url"]}" target="_blank">
            <img
                src="{person["image"]}"
                style="
                    width:120px;
                    height:120px;
                    object-fit:cover;
                    object-position:{person["focus"]};
                    border-radius:100px;
                    margin-bottom:10px;
                "
            >
            <div>{person["name"]}</div>
        </a>
        <div style="font-size:12px; opacity:0.75;">{person["affiliation"]}</div>
        <div>{"<b>Instructor</b>" if person["is_instructor"] else "Instructor"}</div>
    </div>
    """)


def complete(fill_mask, sentence: str, k: int = 3) -> list[str]:
    """Top-k guesses for the [MASK], with the model's confidence."""
    return [f"{p['token_str']} ({p['score']:.0%})" for p in fill_mask(sentence, top_k=k)]
