"""Shared page assembly for the Y-Squre generators.

One place that stitches head() + header() + body + footer() so a new page type
cannot forget a piece. Every generator builds a dict and calls render().
"""

import re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import head, header, footer, write, SITE, esc, ad  # noqa: E402


def render(p):
    """p: {path, url, title, desc, body, section, ctype, published, tags, extra_css}

    Every page gets an advertising slot directly below the header. It is
    injected here rather than in each generator because the audit found region
    pages, section pages and the /macro/ and /markets/ indexes rendering with
    no slot at all: each generator built its own <main> and none of them
    remembered. One seam, so a new page type cannot forget either.

    A page that already emits its own slot is left alone -- two top slots on
    one page would be a layout bug, not a safety net.
    """
    body = p["body"]
    if 'class="ad-slot ad-top"' not in body:
        # Right after the opening <main ...>: below the header, above the
        # first heading, which is where the slot is meant to sit.
        m = re.search(r"<main\b[^>]*>", body)
        if m:
            body = (body[:m.end()] + "\n" + ad("Advertisement", "ad-top").strip()
                    + body[m.end():])
    return (
        head(
            p["title"], p["desc"], p["url"],
            ctype=p.get("ctype", "website"),
            published=p.get("published", ""),
            updated=p.get("updated", ""),
            section=p.get("section", ""),
            tags=p.get("tags"),
            noindex=p.get("noindex", False),
            extra_css=p.get("extra_css", ()),
        )
        + header(p.get("section", ""))
        + body
        + footer()
    )


def emit(pages):
    """Write a list of page dicts. Returns total bytes."""
    total = 0
    for p in pages:
        total += write(p["path"], render(p))
    return total
