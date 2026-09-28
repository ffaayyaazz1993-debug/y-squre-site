"""The /latest/ editorial grid.

Nothing here is positional. The page sorts ARTICLES by publication time (newest
first) and assigns roles by RANK, not by index: rank 0 is the lead, ranks 1-4 are
secondary, everything after that is the grid. Publishing a new article inserts it
at the top and every other card moves down a rank automatically -- there is no
template to edit and no article is named in the layout code.

The rank -> role mapping degrades honestly. With one article there is a lead and
no grid. With three there is a lead and two secondaries. The grid appears when
there is a fifth article, because that is the first time "everything else" is a
real set rather than an empty container.

Images come from the Commons manifest. An article with no image gets a card
without one, and the lead without an image falls back to a type-set lead panel
rather than showing an empty grey box.
"""
import os, re, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "assets", "img", "manifest.json")

# A lead plus at most four secondaries. Four is the point where a right-hand
# rail stops reading as "a few highlights" and starts competing with the lead.
LEAD = 1
SECONDARY_MAX = 4


def load_manifest():
    if not os.path.exists(MANIFEST):
        return {}
    return json.load(open(MANIFEST, encoding="utf-8"))


def sort_key(a):
    """Newest first. Falls back to a stable secondary key so an article without
    a timestamp cannot jump ahead of one that has one."""
    pub = a.get("published") or a.get("updated") or ""
    return (pub == "", pub)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def when(a, long=False):
    """Timestamp. ISO datetime in the attribute; a readable form in the text."""
    import datetime
    pub = a.get("published") or a.get("updated") or ""
    if not pub:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(pub)
    except ValueError:
        return f'<time>{esc(pub)}</time>'
    if long:
        return dt.strftime("%d %B %Y, %H:%M")
    return dt.strftime("%d %b %Y, %H:%M")


def lead_card(a, img):
    """Rank 0. The image is the point of the lead, so it leads the card."""
    if img:
        figure = (f'      <a class="lg-img" href="{a["url"]}" tabindex="-1" aria-hidden="true">'
                  f'<img src="{esc(img["url"])}" alt="" loading="eager" width="1400" height="900">'
                  f'</a>\n')
    else:
        figure = ""
    updated = ""
    if a.get("updated"):
        updated = (f'<span class="lg-updated">Updated {esc(when(a, True))}</span>')
    return f"""    <article class="lg-lead">
{figure}      <div class="lg-body">
        <div class="lg-kicker">
          <a class="kicker {a['kicker']}" href="{a['sect_href']}">{esc(a['section'])}</a>
          <span class="lg-type">{esc(a['type'])}</span>
        </div>
        <h2 class="lg-headline"><a href="{a['url']}">{esc(a['title'])}</a></h2>
        <p class="lg-summary">{esc(a.get('summary') or a.get('deck') or '')}</p>
        <p class="lg-meta">
          <time datetime="{a['published']}">{esc(when(a))}</time>
          {updated}
          <span class="meta-sep">/</span>{esc(a['read'])}
        </p>
      </div>
    </article>"""


def secondary_card(a, img):
    if img:
        figure = (f'        <a class="sec-img" href="{a["url"]}" tabindex="-1" aria-hidden="true">'
                  f'<img src="{esc(img["url"])}" alt="" loading="lazy" width="1400" height="900">'
                  f'</a>\n')
    else:
        figure = ""
    return f"""      <article class="sec-card-lg">
{figure}        <div class="sec-body-lg">
          <div class="sec-kicker">
            <a class="kicker {a['kicker']}" href="{a['sect_href']}">{esc(a['section'])}</a>
            <span class="sec-type">{esc(a['type'])}</span>
          </div>
          <h3 class="sec-headline"><a href="{a['url']}">{esc(a['title'])}</a></h3>
          <p class="sec-summary">{esc(a.get('summary') or a.get('deck') or '')}</p>
          <p class="sec-meta">
            <time datetime="{a['published']}">{esc(when(a))}</time>
            <span class="meta-sep">/</span>{esc(a['read'])}
          </p>
        </div>
      </article>"""


def grid_card(a, img):
    if img:
        figure = (f'          <a class="gc-img" href="{a["url"]}" tabindex="-1" aria-hidden="true">'
                  f'<img src="{esc(img["url"])}" alt="" loading="lazy" width="1400" height="900">'
                  f'</a>\n')
    else:
        figure = ""
    return f"""      <article class="grid-card">
{figure}        <div class="gc-body">
          <div class="gc-kicker">
            <a class="kicker {a['kicker']}" href="{a['sect_href']}">{esc(a['section'])}</a>
            <span class="gc-type">{esc(a['type'])}</span>
          </div>
          <h3 class="gc-headline"><a href="{a['url']}">{esc(a['title'])}</a></h3>
          <p class="gc-summary">{esc(a.get('summary') or a.get('deck') or '')}</p>
          <p class="gc-meta">
            <time datetime="{a['published']}">{esc(when(a))}</time>
            <span class="meta-sep">/</span>{esc(a['read'])}
          </p>
        </div>
      </article>"""


def latest_body(articles, manifest):
    """Rank-driven layout. This is the whole mechanism: sort, slice by rank,
    render. No article is ever addressed by name or position here."""
    items = sorted(articles, key=sort_key, reverse=True)
    n = len(items)

    lead = items[:LEAD]
    secondary = items[LEAD:LEAD + SECONDARY_MAX]
    rest = items[LEAD + SECONDARY_MAX:]

    def img_for(a):
        g = (manifest.get(a["url"].lstrip("/")) or [None])
        return g[0] if g else None

    out = []
    if lead:
        out.append('    <section class="lg" aria-label="Lead story">')
        out.append(lead_card(lead[0], img_for(lead[0])))
        if secondary:
            out.append('      <div class="sec-rail" aria-label="More from Y-Square">')
            for a in secondary:
                out.append(secondary_card(a, img_for(a)))
            out.append("      </div>")
        out.append("    </section>")

    if rest:
        out.append('    <section class="gc-section" aria-label="All articles">')
        out.append('      <h2 class="gc-h">Earlier</h2>')
        out.append('      <div class="grid-cards">')
        for a in rest:
            out.append(grid_card(a, img_for(a)))
        out.append("      </div>")
        out.append("    </section>")

    if n == 0:
        out.append('    <div class="empty-state"><strong>Nothing published yet</strong>'
                   'Articles will appear here newest first, with images, summaries and '
                   'timestamps.</div>')
    return "\n".join(out), n, len(secondary), len(rest)
