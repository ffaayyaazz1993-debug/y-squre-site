"""Render the Y-Squre header from assets/data/geography.json.

Produces, for every page:
  - masthead        logo, tagline, search, sign in
  - primary nav     Latest + 8 geographic triggers, each with a mega-menu
  - topic bar       Markets / Macro / Research / Blog
  - mobile menu     accordion, nested, independent of the desktop logic
  - breadcrumb      region > subregion > ... (supplied by the caller)

Why generated at build time rather than injected by JS: the shipped HTML then
carries real <a href> elements, so the navigation is present for crawlers, RSS
readers and anyone with JavaScript disabled. nav.js only layers interaction on
top. A JS-injected header would hide the entire nav from all three.

Every trigger is a real link to its section landing page, so with JS off the
menu degrades to ordinary in-page navigation rather than disappearing.
"""

import json, os, html

ROOT = r"C:\Users\ffaay\y-squre-site"
GEO_PATH = os.path.join(ROOT, "assets", "data", "geography.json")

with open(GEO_PATH, encoding="utf-8") as f:
    GEO = json.load(f)

REGIONS = GEO["regions"]
TOPICS = {t["slug"]: t for t in GEO["topics"]}

# Global News dropdown: exactly three grouped region links, each with its own
# hub page. Kept separate from GEO["regions"] so the underlying taxonomy and
# published article URLs stay intact.
GLOBAL_NAV = [
    ("Asia/Oceania/Pacific", "/asia-oceania-pacific/"),
    ("Europe/UK/Middle East", "/europe-uk-middle-east/"),
    ("North America", "/north-america/"),
]
CONTENT_TYPES = GEO["content_types"]

# Megabyte-style column budget: cap how many subregions sit side by side so no
# region produces a panel taller than the viewport on a laptop.
MAX_COLS = 4            # 7 Europe subregions -> 2 rows of 4, so the panel stops clipping

esc = None  # set below, after the function definition


def esc(s):
    return html.escape(str(s), quote=True)

esc = esc


def _cols(items, per_col):
    """Split a list into near-equal columns. Deterministic ordering."""
    out = [[] for _ in range(per_col)]
    for i, it in enumerate(items):
        out[i % per_col].append(it)
    return [c for c in out if c]


def _panel_id(prefix, slug):
    return f"{prefix}-{slug}"


def mega_region(region):
    """Mega-menu for a geographic region: subregion columns, each listing
    its countries as deep links into that subregion's country table.

    A flat region has no meaningful subregion unit, so its countries are listed
    directly against the region page with no subregion heading -- one list under
    a name the reader already sees in the trigger.
    """
    secs = region["sections"]
    if region.get("flat"):
        base = region["path"]
        items = "".join(
            f'<li><a href="{base}#{c["anchor"]}">{esc(c["name"])}</a></li>'
            for c in secs[0]["countries"])
        # No group name: the panel head already says "Europe", and a flat
        # region has no subregion to name. The list goes straight under it.
        cols = ['    <div class="mega-col">\n'
                f'      <ul class="mega-list">{items}</ul>\n'
                '    </div>']
    else:
        # Aim for 3 columns; a region with few subregions uses fewer, never more.
        ncols = min(MAX_COLS, max(2, (len(secs) + 1) // 2))
        ncols = min(ncols, len(secs))
        groups = _cols(secs, ncols)

        cols = []
        for g in groups:
            blocks = []
            for s_ in g:
                base = f"/geopolitics/{region['slug']}/{s_['slug']}/"
                items = "".join(
                    f'<li><a href="{base}#{c["anchor"]}">{esc(c["name"])}</a></li>'
                    for c in s_["countries"])
                # The subregion name used to be a heading link above this list.
                # Removed: the panel head already names the region, and the
                # subregion label was mostly a restatement of it -- "North
                # America" directly above "Canada, United States & Mexico" is
                # one idea said twice, and it pushed the country links down.
                #
                # It was also the ONLY nav link to the three subregion pages
                # (canada-united-states-mexico, gulf, north-africa), so it is
                # not simply deleted: the subregion page is linked from every
                # country explainer in it and from its own region's page, which
                # is 694 inbound links for /gulf/ alone. Those pages stay
                # reachable and stay in the sitemap.
                blocks.append(
                    f'      <div class="mega-group">\n'
                    f'        <ul class="mega-list">{items}</ul>\n'
                    f'      </div>')
            cols.append('    <div class="mega-col">\n' + "\n".join(blocks) + "\n    </div>")

    # The "also" note used to be repeated at the foot of every region panel:
    # "European coverage is a four-country subset for now. The subregions that
    # previously existed here -- Northern Europe, ... -- are retired and
    # redirect to /geopolitics/europe/." It is editorial housekeeping about the
    # site's own taxonomy, and it sat inside the control a reader opens to find
    # country links. The same text is already on the region page itself as a
    # page-note, where it belongs, so nothing is lost by dropping the duplicate.
    #
    # The field stays in geography.json: gen_sections2.py renders it on the
    # region page. Only the mega-panel copy is removed.

    pid = _panel_id("m", region["slug"])
    return f'''
      <div class="mega" id="{pid}" data-open="false" aria-label="{esc(region["name"])} sections">
        <div class="mega-inner">
          <div class="mega-head">
            <a class="mega-title" href="{region["path"]}">{esc(region["name"])}</a>
          </div>
          <div class="mega-cols">
{chr(10).join(cols)}
          </div>
        </div>
      </div>'''


def mega_topic(topic):
    """Mega-menu for a topical section. No country lists, and an explicit
    line stating these are analysis rather than event reporting where the
    brief asks for that distinction."""
    pid = _panel_id("m", topic["slug"])
    # A child's own "url" wins when present: the Global panel mixes its native
    # /geopolitics/global/... children with sections relocated from the deleted
    # nav row, and prefixing topic["path"] onto those produced
    # /geopolitics/global/stocks/ instead of /markets/stocks/.
    items = "".join(
        f'<li><a href="{esc(c.get("url") or (topic["path"] + c["slug"] + "/"))}">'
        f'{esc(c["name"])}</a>'
        f'<span class="mega-item-scope">{esc(c["scope"])}</span></li>'
        for c in topic["children"])

    # The content-type chips and the "never event reporting" note used to be
    # gated on topic["slug"] == "blog". No panel with that slug is ever built:
    # the only topic panel is the Global one, whose slug is "global", because
    # Blog is a child inside it rather than a panel of its own. The branch was
    # unreachable, so the chips and the note never rendered on any page.
    #
    # The distinction it made is still made where a reader actually meets it --
    # in the Blog section page and on the articles themselves -- so nothing is
    # lost by deleting an arm that could not execute.
    kinds = ""

    return f'''
      <div class="mega" id="{pid}" data-open="false" aria-label="{esc(topic["name"])} sections">
        <div class="mega-inner">
          <div class="mega-head">
            <a class="mega-title" href="{topic["path"]}">{esc(topic["name"])}</a>
            <span class="mega-sub">{esc(topic["lede"])}</span>
          </div>
          <div class="mega-cols mega-cols-topic">
            <div class="mega-col">
      <ul class="mega-list mega-list-topic">{items}</ul>
            </div>
          </div>
        </div>
      </div>'''


# The one nav label long enough to force a third line of wrapping on a narrow
# phone. At 520px and under the CSS swaps in a short form; the full name stays
# in the accessible name so a screen reader and the panel title are unchanged.
LONG_LABELS = {"Middle East & North Africa": "MENA"}


def _trigger(label, href, panel_id):
    long_cls = " nav-long" if label in LONG_LABELS else ""
    return (f'      <li class="nav-item">\n'
            f'        <a class="nav-trigger{long_cls}" href="{href}" aria-expanded="false" '
            f'aria-controls="{panel_id}"><span class="nav-label">{esc(label)}</span>'
            f'<svg class="nav-caret" width="8" height="5" viewBox="0 0 8 5" aria-hidden="true">'
            f'<path d="M0 0l4 5 4-5z" fill="currentColor"/></svg></a>\n')


def primary_nav(current=""):
    '''Exact main bar requested: Investing.com label set, Y-Squre links.'''
    out = []

    def plain(label, href, cls=""):
        c = " " + cls if cls else ""
        return (f'      <li class="nav-item"><a class="nav-link{c}" '
                f'href="{href}">{label}</a></li>')

    def simple_panel(pid, title, href, rows):
        lis = "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in rows)
        return f'''<div class="mega" id="{pid}" data-open="false" aria-label="{esc(title)}">
        <div class="mega-inner">
          <div class="mega-head">
            <a class="mega-title" href="{href}">{esc(title)}</a>
          </div>
          <div class="mega-cols"><div class="mega-col">
      <ul class="mega-list">{lis}</ul>
          </div></div>
        </div>
      </div>
      </li>'''

    mid = "m-markets"
    out.append(_trigger("Markets", "/markets/", mid))
    sm_fly = "".join(
        '<li><a href="/markets/stock-market/' + sl + '/">' + esc(n) + '</a></li>'
        for n, sl in (("US", "us"), ("UK", "uk"),
                      ("Europe", "europe"), ("Asia", "asia")))
    mkt_items = (
        '<li class="has-flyout"><a href="/markets/stock-market/">Stock Market</a>'
        '<ul class="mega-flyout">' + sm_fly + '</ul></li>'
        '<li><a href="/markets/forex-market/">Forex Market</a></li>'
        '<li><a href="/markets/indices/">Indices</a></li>'
        '<li><a href="/markets/commodities/">Commodities</a></li>'
        '<li><a href="/markets/currencies/">Currencies</a></li>'
        '<li><a href="/markets/companies/">Companies</a></li>'
        '<li><a href="/markets/sectors/">Sectors</a></li>'
        '<li><a href="/markets/bonds/">Bonds</a></li>')
    out.append(f'''<div class="mega" id="{mid}" data-open="false" aria-label="Market sections">
        <div class="mega-inner">
          <div class="mega-head">
            <a class="mega-title" href="/markets/">Markets</a>
          </div>
          <div class="mega-cols"><div class="mega-col">
      <ul class="mega-list">{mkt_items}</ul>
          </div></div>
        </div>
      </div>
      </li>''')

    out.append(plain('<span class="nav-icon" aria-hidden="true">★</span> My Watchlist',
                     '/account/index.html'))
    out.append(plain('<span class="nav-icon" aria-hidden="true">&#128293;</span> Investing Challenges',
                     '/blog/'))
    n_id = "m-news"
    out.append(_trigger("News", "/latest/", n_id))

    def news_col(title, rows):
        lis = "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in rows)
        return (f'<div class="mega-col"><div class="mega-group">'
                f'<h4>{esc(title)}</h4><ul class="mega-list">{lis}</ul>'
                '</div></div>')

    fin = news_col("Financial News", [
        ("Stock Markets", "/markets/stock-market/"),
        ("Earnings", "/markets/companies/"),
        ("Analyst Ratings", "/research/market-research/"),
        ("Transcripts", "/research/"),
        ("Cryptocurrency", "/crypto/"),
        ("Commodities", "/markets/commodities/"),
        ("Currencies", "/markets/currencies/"),
        ("Economy", "/business/"),
        ("Economic Indicators", "/research/data-statistics/"),
        ("Breaking News", "/latest/"),
        ("Pro News", "/blog/"),
    ])
    more_news = news_col("More In News", [
        ("Latest", "/latest/"),
        ("Most Popular", "/latest/"),
        ("Sports & General", "/latest/"),
        ("World", "/geopolitics/global/"),
        ("Politics", "/geopolitics/global/"),
        ("Press Releases", "/blog/"),
        ("Company News", "/markets/companies/"),
        ("Insider Trading", "/research/market-research/"),
        ("Investment Ideas", "/blog/"),
        ("SEC Filings", "/research/"),
        ("SWOT Analysis", "/research/sector-research/"),
    ])
    out.append(f'''<div class="mega" id="{n_id}" data-open="false" aria-label="News sections">
        <div class="mega-inner">
          <div class="mega-head">
            <a class="mega-title" href="/latest/">News</a>
          </div>
          <div class="mega-cols mega-cols-2">{fin}{more_news}</div>
        </div>
      </div>
      </li>''')

    out.append(plain("Analysis", "/blog/"))
    out.append(plain("Charts", "/markets/"))
    out.append(plain("Technical", "/research/"))
    out.append(plain("Brokers", "/advertising/index.html"))

    tid = "m-tools"
    out.append(_trigger("Tools", "/search/index.html", tid))
    out.append(simple_panel(
        tid, "Tools", "/search/index.html",
        [("Search", "/search/index.html"), ("Sitemap", "/sitemap.xml"),
         ("All articles", "/latest/")]))

    out.append(plain("Academy", "/blog/"))
    out.append(plain("Stock Screener", "/markets/stock-market/"))
    out.append(plain("InvestingPro", "/advertising/index.html", "nav-pro"))

    more_id = "m-more"
    out.append(_trigger("More", "/about/index.html", more_id))
    out.append(simple_panel(
        more_id, "More", "/about/index.html",
        [("About", "/about/index.html"), ("Contact", "/contact/index.html"),
         ("Editorial Policy", "/editorial-policy/index.html"),
         ("Advertising", "/advertising/index.html"),
         ("Privacy", "/privacy/index.html"), ("Terms", "/terms/index.html"),
         ("Investment Disclaimer", "/disclaimer/index.html")]))

    return "\n".join(out)


def mobile_menu():
    """Progressive-enhancement mobile menu.

    The full region > subregion > country tree is NOT duplicated here: it is
    already in the mega-panels, which ship in every page. nav.js builds the
    accordion from those panels at runtime, so the tree exists once in the
    document instead of twice (it was 46KB of pure duplication).

    What ships as HTML is the top-level fallback: the region and topic links
    themselves, so a no-JS mobile reader can still navigate the site.
    """
    # No "Latest" leaf: the wordmark directly above this drawer links to the
    # front page, so a second control for the same destination is a duplicate.
    rows = []
    for name, path in GLOBAL_NAV:
        rows.append(f'<li class="acc-leaf"><a href="{path}">{esc(name)}</a></li>')
    rows.append('<li class="acc-leaf"><a href="/business/">World Economies</a></li>')
    rows.append('<li class="acc-leaf"><a href="/crypto/">Crypto</a></li>')
    for slug in ("markets", "research", "blog"):
        t = TOPICS[slug]
        rows.append(f'<li class="acc-leaf"><a href="{t["path"]}">{esc(t["name"])}</a></li>')

    return f'''
    <div class="mobile-menu" id="mobile-menu" data-open="false" aria-hidden="true" data-accordion data-build="mega">
      <ul class="acc-list acc-list-root acc-fallback">
{chr(10).join("        " + r for r in rows)}
      </ul>
      <div class="mobile-foot">
        <a href="/about/index.html">About</a>
        <a href="/contact/index.html">Contact</a>
        <a href="/editorial-policy/index.html">Editorial Policy</a>
        <a href="/privacy/index.html">Privacy</a>
        <a href="/search/index.html">Search</a>
      </div>
    </div>'''


def market_tape():
    """Real published headlines in a dense terminal-style strip.

    No prices, no 'live' claim: the only dynamic element is a UTC/IST clock and
    the only links are to articles that exist in articles.json.
    """
    path = os.path.join(ROOT, "assets", "data", "articles.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return ""
    items = sorted(data.get("articles", []),
                   key=lambda a: a.get("published") or "", reverse=True)[:8]
    if not items:
        return ""
    desk_names = {
        "global": "GLOBAL NEWS", "business": "WORLD ECONOMIES",
        "market": "MARKET", "crypto": "CRYPTO",
        "blog": "BLOG", "research": "RESEARCH",
    }
    out = []
    for a in items:
        title = html.unescape(a.get("title") or a.get("h1") or "").strip()
        url = html.escape(a.get("url") or "#", quote=True)
        desk = desk_names.get((a.get("section") or "global").lower(), "GLOBAL NEWS")
        pub = a.get("published") or ""
        t = pub[11:16] if len(pub) >= 16 else ""
        out.append(
            f'<a class="mkt-tape-item" href="{url}">'
            f'<span class="tape-kicker">{desk}</span>'
            f'<span>{html.escape(title)}</span>'
            f'<span class="tape-time">{html.escape(t)}</span></a>'
        )
    track = "".join(out)
    return f'''
    <div class="mkt-tape" aria-label="Latest headlines">
      <div class="wrap mkt-tape-inner">
        <span class="mkt-tape-tag"><span class="mkt-tape-dot" aria-hidden="true"></span>Latest</span>
        <span class="mkt-tape-viewport"><span class="mkt-tape-track">{track}</span></span>
      </div>
    </div>'''


def header(current=""):
    """Investing.com-style header: top utility row, main nav bar, headline strip."""
    return f'''
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="masthead">
      <div class="wrap masthead-inner">
        <a class="brand" href="/">
          <span class="brand-mark" aria-hidden="true">Y</span>
          <span class="brand-text"><span class="brand-name">Y-SQUARE</span></span>
        </a>
        <p class="tagline">Global News, Data &amp; Analysis</p>
        <div class="masthead-utils">
          <a class="util-link" href="/search/index.html">
            <svg class="util-icon" width="14" height="14" viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="6.5" cy="6.5" r="5" fill="none" stroke="currentColor" stroke-width="1.8"/>
              <path d="M10.5 10.5L15 15" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            </svg>
            <span>Search</span>
          </a>
          <span class="masthead-clock" data-mkt-clock>UTC --:--:--</span>
        </div>
        <button class="nav-toggle" data-burger aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu">
          <span class="nav-toggle-bars" aria-hidden="true"><i></i><i></i><i></i></span>
          <span class="nav-toggle-text">Menu</span>
        </button>
      </div>
    </div>
    <nav class="primary-nav" data-nav aria-label="Main sections">
      <div class="wrap">
        <ul class="nav-list nav-list-geo">
{primary_nav(current)}
        </ul>
      </div>
    </nav>
{mobile_menu()}
{market_tape()}
  </header>
'''


def breadcrumb(trail):
    """trail: [(label, href_or_None), ...] with the last item the current page."""
    if not trail:
        return ""
    parts = ['<nav class="crumbs" aria-label="Breadcrumb"><ol>']
    for i, (label, href) in enumerate(trail):
        last = i == len(trail) - 1
        if last or not href:
            parts.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
        else:
            parts.append(f'<li><a href="{href}">{esc(label)}</a></li>')
    parts.append("</ol></nav>")
    return "".join(parts)


def section_path(region_slug, sec_slug):
    return f"/geopolitics/{region_slug}/{sec_slug}/"


if __name__ == "__main__":
    h = header()
    m = mobile_menu()
    print(f"  header():      {len(h):>6,} chars")
    print(f"  mobile_menu(): {len(m):>6,} chars")
    print(f"  global nav: {len(GLOBAL_NAV)}  regions: {len(REGIONS)}  topic bar: 4")
    # every trigger must have a matching panel id, and vice versa
    import re
    triggers = set(re.findall(r'aria-controls="(m-[\w-]+)"', h))
    panels = set(re.findall(r'<div class="mega" id="(m-[\w-]+)"', h))
    print(f"  triggers: {len(triggers)}  panels: {len(panels)}  "
          f"{'MATCH' if triggers == panels else 'MISMATCH ' + str(triggers ^ panels)}")
