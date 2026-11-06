"""Generate editorial front pages for the geopolitics region indexes.

Scans published article files under geopolitics/<region>/, extracts real
metadata, and renders the section-front layout used by North America and the
other geopolitics sections. No story titles, timestamps, summaries or images
are invented.
"""
import os, re, sys, datetime, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import gen_lib as L
import gen_page as P

REGIONS = {
    "north-america": {
        "name": "North America",
        "lede": "Trade and tariff policy, alliance commitments, border and immigration policy, "
                "and fiscal and monetary divergence across the region.",
        "title": "North America Geopolitics & Economic Coverage | Y-Squre",
        "desc": "Geopolitical and economic coverage across North America: trade and tariff policy, "
                "alliances, border and immigration policy, and fiscal and monetary divergence.",
    },
    "europe": {
        "name": "Europe",
        "lede": "Energy security, the sanctions architecture, fiscal fragmentation, and monetary "
                "policy divergence between the euro area and the periphery.",
        "title": "Europe Geopolitics & Economic Coverage | Y-Squre",
        "desc": "Geopolitical and economic coverage across Europe: energy security, the sanctions "
                "architecture, fiscal fragmentation, and monetary policy divergence.",
    },
    "middle-east-north-africa": {
        "name": "Middle East & North Africa",
        "lede": "Energy policy, sovereign economics and trade across the Middle East and North Africa.",
        "title": "Middle East & North Africa Geopolitics & Economic Coverage | Y-Squre",
        "desc": "Geopolitical and economic coverage across the Middle East and North Africa: "
                "energy policy, sovereign economics and trade.",
    },
    "asia": {
        "name": "Asia",
        "lede": "Commodity demand, energy exports and import dependence, sanctions exposure, "
                "manufacturing share, and export policy.",
        "title": "Asia Geopolitics & Economic Coverage | Y-Squre",
        "desc": "Geopolitical and economic coverage across Asia: commodity demand, energy exports, "
                "sanctions exposure, manufacturing share, and export policy.",
    },
    "oceania-pacific": {
        "name": "Oceania & Pacific",
        "lede": "Commodity exports, RBA policy, and Pacific financing arrangements.",
        "title": "Oceania & Pacific Geopolitics & Economic Coverage | Y-Squre",
        "desc": "Geopolitical and economic coverage across Oceania and the Pacific: commodity exports, "
                "RBA policy, and Pacific financing arrangements.",
    },
    "global": {
        "name": "Global",
        "lede": "Stories not primarily associated with one region.",
        "title": "Global | Y-Squre",
        "desc": "Stories not primarily associated with one region.",
    },
}

TARGETS = ["north-america", "europe", "middle-east-north-africa", "asia",
           "oceania-pacific", "global"]

GLOBAL_SECTIONS = [
    ("World", "/geopolitics/global/world/",
     "Cross-border developments with no single national home."),
    ("Global Economy", "/geopolitics/global/global-economy/",
     "Global growth, trade-weighted output, and synchronised cycles."),
    ("Global Trade", "/geopolitics/global/global-trade/",
     "Tariff action, supply chains, and trade agreement negotiation."),
    ("International Organizations", "/geopolitics/global/international-organizations/",
     "WTO, IMF, UN and multilateral institution positions."),
    ("Climate & Energy", "/geopolitics/global/climate-energy/",
     "Energy transition, grid investment, and carbon policy."),
    ("Global Security", "/geopolitics/global/global-security/",
     "Defence posture, alliances, and arms transfers."),
    ("Global Technology", "/geopolitics/global/global-technology/",
     "Export controls, semiconductor capacity, and platform regulation."),
]


def _rx(text, pattern, default=""):
    m = re.search(pattern, text, re.S | re.I)
    return m.group(1).strip() if m else default


def parse_article(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    url = "/" + rel
    text = open(path, encoding="utf-8").read()

    title = html.unescape(_rx(text, r"<title>(.*?)</title>"))
    title = title.replace(" | Y-Squre", "").strip()
    desc = html.unescape(_rx(text, r'<meta name="description" content="(.*?)"'))
    published = _rx(text, r'<meta property="article:published_time" content="(.*?)"')
    section = _rx(text, r'<meta property="article:section" content="(.*?)"', "Geopolitics")
    deck = html.unescape(_rx(text, r'<p class="article-deck">(.*?)</p>'))
    keywords = re.findall(r'<meta name="keywords" content="(.*?)"', text, re.I)
    category = html.unescape(keywords[0].strip()) if keywords else section

    img_candidates = re.findall(r'<img src="([^"]+)" alt="([^"]*)"', text, re.I)
    img_src = ""
    img_alt = title
    for src, alt in img_candidates:
        src = src.strip()
        if src.startswith(("http://", "https://")):
            candidate = src
        elif src.startswith("/"):
            candidate = src
        else:
            candidate = "/" + os.path.join(os.path.dirname(rel), src).replace(os.sep, "/")
        candidate = os.path.normpath(candidate).replace(os.sep, "/")
        if not candidate.startswith("/"):
            candidate = "/" + candidate
        if os.path.exists(os.path.join(ROOT, candidate.lstrip("/"))):
            img_src = src
            img_alt = html.unescape(alt.strip()) or title
            break
    if not img_src and img_candidates:
        img_src = img_candidates[0][0].strip()
        img_alt = html.unescape(img_candidates[0][1].strip()) or title

    if img_src and not img_src.startswith(("http://", "https://")):
        if img_src.startswith("/"):
            img_url = img_src
        else:
            img_url = "/" + os.path.join(os.path.dirname(rel), img_src).replace(os.sep, "/")
    else:
        img_url = img_src
    if img_url:
        img_url = os.path.normpath(img_url).replace(os.sep, "/")
        if not img_url.startswith("/"):
            img_url = "/" + img_url
        if not os.path.exists(os.path.join(ROOT, img_url.lstrip("/"))):
            img_url = None

    excerpt = (deck or desc).strip()

    return {
        "url": url,
        "title": title,
        "desc": desc,
        "published": published,
        "section": section,
        "category": category,
        "excerpt": excerpt,
        "image": img_url,
        "image_alt": img_alt or title,
    }


def load_articles(region_slug):
    art_dir = os.path.join(ROOT, "geopolitics", region_slug)
    out = []
    for root, _, files in os.walk(art_dir):
        for name in files:
            if not name.endswith(".html") or name == "index.html":
                continue
            out.append(parse_article(os.path.join(root, name)))

    def _sort_key(a):
        raw = a["published"] or ""
        try:
            dt = datetime.datetime.fromisoformat(raw)
        except ValueError:
            return (1, datetime.datetime.min.replace(tzinfo=datetime.timezone.utc))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return (0, dt)

    out.sort(key=_sort_key, reverse=True)
    return out


def time_el(pub):
    text = (pub or "")[:10]
    return ('<time datetime="%s" data-ago="%s">%s</time>'
            % (L.esc(pub), L.esc(pub), L.esc(text)))


def img_link(a, loading="lazy", width=1400, height=933, cls=""):
    if not a["image"]:
        return ""
    return ('<a class="%s" href="%s" tabindex="-1" aria-hidden="true">'
            '<img src="%s" alt="%s" loading="%s" width="%d" height="%d"></a>'
            % (cls, a["url"], L.esc(a["image"]), L.esc(a["image_alt"]),
               loading, width, height))


def build_body(region_slug, items):
    cfg = REGIONS[region_slug]
    name = cfg["name"]
    region_links = [
        ("North America", "/geopolitics/north-america/"),
        ("Europe", "/geopolitics/europe/"),
        ("Middle East & North Africa", "/geopolitics/middle-east-north-africa/"),
        ("Asia", "/geopolitics/asia/"),
        ("Oceania & Pacific", "/geopolitics/oceania-pacific/"),
        ("Global", "/geopolitics/global/"),
    ]

    lead = items[0] if items else None
    cursor = 1
    related = items[cursor:cursor + 3]
    cursor += len(related)
    grid = items[cursor:cursor + 4]
    cursor += len(grid)

    pool = items[cursor:]
    extras = []
    feed = []
    for i, a in enumerate(pool):
        if i < len(grid):
            extras.append(a)
        else:
            feed.append(a)

    body = []
    body.append('  <main id="main" class="wrap page na-page">')
    body.append('    <div class="ad-slot ad-top" data-ad-label="Advertisement"></div>')
    body.append("    <h1>%s</h1>" % L.esc(name))
    body.append('    <p class="page-lede">%s</p>' % L.esc(cfg["lede"]))
    if lead:
        related_items = []
        for a in related:
            thumb = img_link(a, loading="lazy", width=72, height=54, cls="na-related-thumb")
            related_body = ('<div class="na-related-body">'
                            '<a class="na-related-link" href="%s">%s</a>'
                            '<span class="na-related-time">%s</span>'
                            "</div>" % (a["url"], L.esc(a["title"]), time_el(a["published"])))
            if thumb:
                related_items.append(
                    '          <li class="na-related-item">%s%s</li>' % (thumb, related_body))
            else:
                related_items.append(
                    '          <li class="na-related-item na-related-item--text">%s</li>' % related_body)
        body.append('    <section class="na-lead" aria-label="Lead story">')
        body.append('      <article class="na-lead-main">')
        body.append('        <p class="na-lead-kicker">%s</p>' % L.esc(lead["category"]))
        body.append('        <h2 class="na-lead-headline"><a href="%s">%s</a></h2>'
                    % (lead["url"], L.esc(lead["title"])))
        if lead["excerpt"]:
            body.append('        <p class="na-lead-dek">%s</p>' % L.esc(lead["excerpt"]))
        body.append('        <p class="na-lead-time">%s</p>' % time_el(lead["published"]))
        lead_image = img_link(lead, loading="eager", cls="na-lead-image")
        if lead_image:
            body.append("        " + lead_image)
        body.append("      </article>")
        if related:
            body.append('      <aside class="na-related" aria-label="Related headlines">')
            body.append('        <h2 class="na-related-label">Related headlines</h2>')
            body.append('        <ul class="na-related-list">')
            body.extend(related_items)
            body.append("        </ul>")
            body.append("      </aside>")
        body.append("    </section>")

    if grid:
        cards = []
        for idx, a in enumerate(grid):
            extra = extras[idx] if idx < len(extras) else None
            parts = ['      <article class="na-card">']
            image = img_link(a, loading="lazy", cls="na-card-image")
            if image:
                parts.append("        " + image)
            parts.append('        <h3 class="na-card-headline"><a href="%s">%s</a></h3>'
                         % (a["url"], L.esc(a["title"])))
            parts.append('        <p class="na-card-time">%s</p>' % time_el(a["published"]))
            if extra:
                parts.append('        <a class="na-card-extra" href="%s">%s</a>'
                             % (extra["url"], L.esc(extra["title"])))
            parts.append("      </article>")
            cards.append("\n".join(parts))
        body.append('    <section class="na-strip" aria-label="Featured stories">')
        body.append('      <div class="na-strip-grid">')
        body.extend(cards)
        body.append("      </div>")
        body.append("    </section>")

    if feed:
        rows = []
        for a in feed:
            parts = ['      <article class="na-feed-row">']
            parts.append('        <div class="na-feed-text">')
            parts.append('          <p class="na-feed-meta"><span class="na-feed-cat">%s</span> '
                         '&middot; %s</p>' % (L.esc(a["category"]), time_el(a["published"])))
            parts.append('          <h3 class="na-feed-headline"><a href="%s">%s</a></h3>'
                         % (a["url"], L.esc(a["title"])))
            if a["excerpt"]:
                parts.append('          <p class="na-feed-summary">%s</p>' % L.esc(a["excerpt"]))
            parts.append("        </div>")
            thumb = img_link(a, loading="lazy", width=280, height=187, cls="na-feed-thumb")
            if thumb:
                parts.append("        " + thumb)
            parts.append("      </article>")
            rows.append("\n".join(parts))
        body.append('    <section class="na-latest" aria-label="Latest %s">'
                    % L.esc(name))
        body.append('      <h2 class="na-latest-h">Latest %s</h2>' % L.esc(name))
        body.append('      <div class="na-feed">')
        body.extend(rows)
        body.append("      </div>")
        body.append("    </section>")

    if region_slug == "global":
        cards = []
        for title, href, scope in GLOBAL_SECTIONS:
            cards.append('        <a class="sec-card" href="%s">'
                         '<h3>%s</h3><p class="sec-card-scope">%s</p></a>'
                         % (href, L.esc(title), L.esc(scope)))
        body.append('    <section class="na-subsections" aria-label="Global sections">')
        body.append('      <h2 class="section-h">Global sections</h2>')
        body.append('      <div class="sec-grid">')
        body.extend(cards)
        body.append("      </div>")
        body.append("    </section>")

    if not items:
        body.append('    <div class="empty-state"><strong>No %s articles published yet</strong>'
                    'Articles will appear here as they are published.</div>' % L.esc(name))

    body.append("  </main>")
    return "\n".join(body) + "\n"


def generate(region_slug):
    items = load_articles(region_slug)
    cfg = REGIONS[region_slug]
    body_text = build_body(region_slug, items)
    page = {
        "path": "/geopolitics/%s/index.html" % region_slug,
        "url": "/geopolitics/%s/" % region_slug,
        "title": cfg["title"],
        "desc": cfg["desc"],
        "body": body_text,
        "section": "geopolitics",
        "tags": [cfg["name"], "Geopolitics"],
        "extra_css": ("/assets/css/section-front.css",),
    }
    L.write(page["path"], P.render(page))
    return len(items)


if __name__ == "__main__":
    for slug in TARGETS:
        n = generate(slug)
        print("wrote /geopolitics/%s/index.html articles: %d" % (slug, n))
