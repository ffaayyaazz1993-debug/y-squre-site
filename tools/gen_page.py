"""Shared page assembly for the Y-Square generators.

One place that stitches head() + header() + body + footer() so a new page type
cannot forget a piece. Every generator builds a dict and calls render().
"""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import head, header, footer, write, SITE, esc  # noqa: E402


def render(p):
    """p: {path, url, title, desc, body, section, ctype, published, tags, extra_css}"""
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
        + p["body"]
        + footer()
    )


def emit(pages):
    """Write a list of page dicts. Returns total bytes."""
    total = 0
    for p in pages:
        total += write(p["path"], render(p))
    return total
