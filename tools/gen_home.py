"""Generate the homepage, latest index, and the static/legal pages."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import *  # noqa
import gen_latest as GL

# The three published pieces, newest first. This list is the single source
# for the homepage, /latest/, /blog/, /research/ and the sitemap.
ARTICLES = [
    dict(url="/blog/2026/09/26/understanding-currency-depreciation.html",
         title="Understanding currency depreciation: a mechanics explainer",
         deck="A falling currency is a number, not a mechanism. Three distinct channels produce "
              "it, and the same move means opposite things depending on which one is running.",
         type="Explainer", section="Blog", sect_href="/blog/",
         kicker="kicker-analysis", topics="Currencies, Explainer, Trade",
         published="2026-09-26T16:00:00+05:30", read="7 min read",
         summary="Why a currency falls is rarely one thing. The balance-of-payments mechanism, "
                 "the interest-rate channel and the risk-premium channel are separated, with "
                 "the diagnostic that tells them apart."),
    dict(url="/blog/2026/09/26/reading-central-bank-intent.html",
         title="What a central bank balance sheet tells you that the rate does not",
         deck="The judgement calls on top of the mechanics — and the three situations "
              "where the framework should be abandoned rather than used.",
         type="Analysis", section="Blog", sect_href="/blog/",
         kicker="kicker-analysis", topics="Monetary policy, Analysis",
         published="2026-09-26T14:30:00+05:30", read="6 min read",
         summary="Expansion and contraction are not symmetric signals. A framework that weights "
                 "them equally will systematically over-read tightening."),
    dict(url="/research/2026/09/26/central-bank-balance-sheets.html",
         title="The balance sheet is the policy: reading central banks past the rate decision",
         deck="Markets price the rate decision, then react to what the central bank actually "
              "did to its portfolio.",
         type="Research Note", section="Research", sect_href="/research/",
         kicker="kicker-research", topics="Monetary policy, Central banks",
         published="2026-09-26T11:00:00+05:30", read="8 min read",
         summary="The asset side of a central bank balance sheet expresses intent. It has led "
                 "comparable changes in rate stance by two to three quarters in the episodes "
                 "examined, and it fails in identifiable ways."),
]


def story_row(a, show_summary=True):
    s = f'\n        <p>{a["summary"]}</p>' if show_summary else ""
    return f"""      <a class="story" href="{a['url']}">
        <span class="kicker {a['kicker']}">{a['section']} / {a['type']}</span>
        <h3>{a['title']}</h3>{s}
        <span class="meta">
          <time class="story-time" datetime="{a['published']}" data-ago="{a['published']}">{a['published'][:10]}</time>
          <span class="meta-sep">/</span>{a['read']}
        </span>
      </a>"""


def card(a):
    return f"""        <a class="card" href="{a['url']}">
          <span class="kicker {a['kicker']}">{a['type']}</span>
          <h3>{a['title']}</h3>
          <p>{a['summary'][:150]}{'…' if len(a['summary']) > 150 else ''}</p>
          <span class="meta" data-ago="{a['published']}"></span>
        </a>"""


def index_row(a):
    return f"""        <div class="index-row">
          <div class="index-when">
            <span class="kicker {a['kicker']}">{a['section']}</span>
            <time datetime="{a['published']}" data-ago="{a['published']}">{a['published'][:10]}</time>
          </div>
          <div>
            <h3><a href="{a['url']}">{a['title']}</a></h3>
            <p>{a['summary']}</p>
            <span class="meta">{a['type']}<span class="meta-sep">/</span>{a['read']}<span class="meta-sep">/</span>{a['topics']}</span>
          </div>
        </div>"""


# ================================================================= homepage
def homepage():
    lead = ARTICLES[0]
    b = head("Y-Squre | Macro, Geopolitics & Markets Research",
             "Independent research on macroeconomics, geopolitics and markets. Original "
             "analysis, primary sources, stated assumptions and named limitations.",
             "/")
    b += header("/")
    b += '  <main id="main">\n'
    b += ad("Advertisement", "ad-top")

    # Lead story — the newest published piece, honestly labelled as an explainer.
    b += f"""    <div class="wrap">
      <article class="lead">
        <div>
          <span class="kicker kicker-analysis">Lead / {lead['type']}</span>
          <h1><a href="{lead['url']}">{lead['title']}</a></h1>
          <p class="lede">{lead['deck']}</p>
          <p class="meta">
            <time datetime="{lead['published']}" data-ago="{lead['published']}">{lead['published'][:10]}</time>
            <span class="meta-sep">/</span>{lead['read']}
            <span class="meta-sep">/</span>Y-Squre Research
          </p>
          <p style="margin-top:14px"><a class="btn" href="{lead['url']}">Read more</a></p>
        </div>
        <aside class="lead-brief">
          <h2>In this explainer</h2>
          <ul>
            <li>Three distinct channels produce a falling currency.</li>
            <li>The risk-premium channel has nothing to do with the trade balance.</li>
            <li>Credit spreads moving with the currency is the diagnostic that tells them apart.</li>
          </ul>
          <p class="meta">Opinion / explainer &middot; not reporting</p>
        </aside>
      </article>
    </div>
"""

    # Latest
    b += f"""    <div class="wrap">
      <section class="sect">
        <div class="sect-head">
          <h2>Latest</h2>
          <a class="more" href="/latest/">View all &rarr;</a>
        </div>
        <div class="story-list">
{chr(10).join(story_row(a) for a in ARTICLES[1:])}
        </div>
      </section>
    </div>
"""

    # Reporting sections — explicit empty states, never invented headlines.
    b += """    <div class="wrap">
      <section class="sect">
        <div class="sect-head">
          <h2>Geopolitics</h2>
          <a class="more" href="/geopolitics/">All geopolitics &rarr;</a>
        </div>
        <div class="empty-state">
          <strong>No event reporting published yet</strong>
          Geopolitical reporting goes here, organised by region, with each item carrying a
          publication time, an update time and a named source. Nothing is shown rather than
          placeholder headlines: an unverified story on a research site is worse than an empty
          section. Section structure and coverage scope are live at
          <a href="/geopolitics/">/geopolitics/</a>.
        </div>
      </section>
    </div>
"""

    # Macro / markets cards
    macro_cards = "\n".join(f"""        <a class="card" href="/macro/{c}/">
          <span class="kicker kicker-macro">Macro</span><h3>{t}</h3>
        </a>""" for c, t in [("inflation", "Inflation"), ("gdp", "GDP & Growth"),
                            ("interest-rates", "Interest Rates"),
                            ("monetary-policy", "Monetary Policy")])
    mkt_cards = "\n".join(f"""        <a class="card" href="/markets/{c}/">
          <span class="kicker kicker-markets">Markets</span><h3>{t}</h3>
        </a>""" for c, t in [("stocks", "Stocks"), ("commodities", "Commodities"),
                            ("currencies", "Currencies"), ("crypto", "Crypto")])
    b += f"""    <div class="wrap">
      <div class="cols">
        <div>
          <section class="sect">
            <div class="sect-head"><h2>Macroeconomics</h2>
              <a class="more" href="/macro/">All macro &rarr;</a></div>
            <div class="cards">
{macro_cards}
            </div>
          </section>
          <section class="sect">
            <div class="sect-head"><h2>Markets</h2>
              <a class="more" href="/markets/">All markets &rarr;</a></div>
            <div class="cards">
{mkt_cards}
            </div>
          </section>
        </div>
        <aside class="sidebar">
          <h3>Most read</h3>
          <ul class="side-list">
            <li><span class="num">1</span><a href="/research/2026/09/26/central-bank-balance-sheets.html">The balance sheet is the policy</a></li>
            <li><span class="num">2</span><a href="/blog/2026/09/26/understanding-currency-depreciation.html">Currency depreciation explained</a></li>
            <li><span class="num">3</span><a href="/blog/2026/09/26/reading-central-bank-intent.html">What the asset side adds</a></li>
          </ul>
          <div class="ad-slot ad-sidebar" data-ad-label="Advertisement"></div>
        </aside>
      </div>
    </div>
"""

    # Analysis + research
    b += f"""    <div class="wrap">
      <section class="sect">
        <div class="sect-head">
          <h2>Analysis &amp; opinion</h2>
          <a class="more" href="/blog/">All analysis &rarr;</a>
        </div>
        <p class="meta" style="margin-bottom:12px">Y-Squre's own views. Not reporting.</p>
        <div class="cards">
{card(ARTICLES[1])}
        </div>
      </section>
      <section class="sect">
        <div class="sect-head">
          <h2>Research</h2>
          <a class="more" href="/research/">All research &rarr;</a>
        </div>
        <div class="story-list">
{story_row(ARTICLES[2])}
        </div>
      </section>
    </div>
"""
    b += ad("Advertisement", "ad-bottom")

    # Contact strip
    b += f"""    <div class="wrap">
      <section class="sect">
        <div class="sect-head"><h2>Contact</h2></div>
        <div class="cols">
          <div>
            <p class="lede">Questions, corrections, or a specific research request? Write to us
            directly. We reply within two business days.</p>
            <p style="margin-top:14px"><a class="btn" href="mailto:{EMAIL}">{EMAIL}</a></p>
          </div>
          <aside class="sidebar">
            <h3>Elsewhere</h3>
            <ul class="side-list">
              <li><a href="/about/index.html">About Y-Squre</a></li>
              <li><a href="/editorial-policy/index.html">Editorial policy</a></li>
              <li><a href="/contact/index.html">Contact</a></li>
              <li><a href="/advertising/index.html">Advertising</a></li>
            </ul>
          </aside>
        </div>
      </section>
    </div>
  </main>
"""
    b += footer()
    return b


# ================================================================== latest
DESK_META = {
    "global":   ("Global News", "/", "kicker-geo"),
    "market":   ("Markets", "/markets/", "kicker-markets"),
    "crypto":   ("Crypto", "/crypto/", "kicker-analysis"),
    "business": ("World Economies", "/business/", "kicker-macro"),
    "blog":     ("Blog", "/blog/", "kicker-analysis"),
    "research": ("Research", "/research/", "kicker-research"),
}


def load_live_articles():
    """Read the generated article feed; the front page must never go stale."""
    path = os.path.join(ROOT, "assets", "data", "articles.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    live = []
    for a in data.get("articles", []):
        sec = (a.get("section") or "global").lower()
        label, href, kicker = DESK_META.get(sec, DESK_META["global"])
        title = html.unescape(a.get("title") or a.get("h1") or "").strip()
        if not title or not a.get("url"):
            continue
        live.append({
            "url": a["url"], "title": title,
            "section": label, "sect_href": href, "kicker": kicker,
            "type": (a.get("ctype") or "Analysis").title(),
            "published": a.get("published") or "",
            "read": "Article", "summary": a.get("desc") or a.get("deck") or "",
            "desk": sec, "image": a.get("image") or "",
        })
    return sorted(live, key=lambda x: x["published"], reverse=True)


def mkt_deck_html(live):
    cards = [
        ("Market", "markets", "/markets/", "Stock Market, Forex &amp; Indices"),
        ("World Economies", "business", "/business/", "Developed to non-performing"),
        ("Crypto", "crypto", "/crypto/", "Popular coins, alt-coins, NFTs"),
        ("Global News", "global", "/", "North America, EU/UK, Asia Pacific"),
    ]
    out = []
    used = set()
    for label, key, href, note in cards:
        story = next((a for a in live if a["desk"] == key), None)
        fallback = False
        if story is None and live:
            story = next((a for a in live if a["url"] not in used), live[0])
            fallback = True
        if story:
            used.add(story["url"])
        cls = "is-markets" if key == "markets" else ("is-business" if key == "business" else
               ("is-crypto" if key == "crypto" else "is-global"))
        if story:
            head_html = (f'<h3><a href="{esc(story["url"])}">{esc(story["title"])}</a></h3>'
                         f'<p>{esc(story["summary"][:150])}</p>')
            foot = (f'<span>{"From " + esc(story["section"]) if fallback else esc(story["section"])}</span>'
                    f'<span>{esc(story["published"][:10])}</span>')
        else:
            head_html = f'<h3>{note}</h3><p>Coverage is live. The first story for this desk is pending.</p>'
            foot = '<span>Desk</span><span>Browse &rarr;</span>'
        out.append(f'''      <div class="mkt-card {cls}">
        <div class="mkt-card-head"><a href="{href}"><strong>{label}</strong></a><span>Desk</span></div>
        {head_html}
        <div class="mkt-card-foot">{foot}<a href="{href}">Browse &rarr;</a></div>
      </div>''')
    return '\n'.join(out)


def mkt_quick_html(live):
    rows = []
    for a in live[:14]:
        rows.append(
            f'''      <a class="mkt-row" href="{esc(a["url"])}" data-desk="{esc(a["desk"])}">
        <time datetime="{esc(a["published"])}">{esc(a["published"][:16].replace("T", " "))}</time>
        <span class="mkt-desk">{esc(a["section"])}</span>
        <h3>{esc(a["title"])}</h3>
        <span class="mkt-type">{esc(a["type"])}</span>
      </a>'''
        )
    if not rows:
        rows.append('      <div class="mkt-empty">No published articles yet.</div>')
    return '\n'.join(rows)


# ================================================================== latest
def latest():
    live = load_live_articles()
    img_manifest = {a["url"].lstrip("/"): [{"url": a["image"]}] for a in live if a["image"]}
    b = head("Latest | Y-Squre Research",
             "Every article, explainer and research note published by Y-Squre, newest first, with publication times, content labels and reading times.", "/latest/")
    b += header("/latest/")
    b += '  <main id="main">\n' + ad("Advertisement", "ad-top")
    b += '  <h1 class="visually-hidden">Latest</h1>\n'
    b += f'''    <div class="wrap" style="padding-top:22px">
      <section class="mkt-deck" aria-label="Desks">
{mkt_deck_html(live)}
      </section>
'''
    _grid, _n, _sec, _rest = GL.latest_body(live, img_manifest)
    b += f"{_grid}\n"
    b += f'''      <section class="mkt-quick" aria-label="Latest headlines" data-mkt-quick>
        <div class="mkt-quick-head">
          <h2>All headlines</h2>
          <div class="mkt-filters" data-mkt-filters>
            <button class="mkt-filter" type="button" data-filter="all" aria-pressed="true">All</button>
            <button class="mkt-filter" type="button" data-filter="global" aria-pressed="false">Global News</button>
            <button class="mkt-filter" type="button" data-filter="market" aria-pressed="false">Market</button>
            <button class="mkt-filter" type="button" data-filter="crypto" aria-pressed="false">Crypto</button>
            <button class="mkt-filter" type="button" data-filter="business" aria-pressed="false">World Economies</button>
          </div>
        </div>
{mkt_quick_html(live)}
      </section>
      <section class="mkt-rail" aria-label="Browse desks">
        <div>
          <h3>News desks</h3>
          <ul>
            <li><a href="/asia-oceania-pacific/">Asia / Oceania / Pacific</a></li>
            <li><a href="/europe-uk-middle-east/">Europe / UK / Middle East</a></li>
            <li><a href="/north-america/">North America</a></li>
            <li><a href="/business/">World Economies</a></li>
          </ul>
        </div>
        <div>
          <h3>Research desks</h3>
          <ul>
            <li><a href="/markets/">Market</a></li>
            <li><a href="/crypto/">Crypto</a></li>
            <li><a href="/blog/">Blog &amp; analysis</a></li>
            <li><a href="/research/">Research notes</a></li>
          </ul>
        </div>
      </section>
    </div>
  </main>
'''
    b += footer()
    return b


# ============================================ blog / research index (real lists)
def listing(slug, title, lede, kind_label, note):
    items = [a for a in ARTICLES if a["section"].lower() == slug.rstrip("/")]
    b = head(f"{title} | Y-Squre Research & Analysis", lede, f"/{slug}/", section=title)
    b += header(f"/{slug}/")
    b += crumbs([("/latest/", "Home"), (f"/{slug}/", title)])
    b += '  <main id="main">\n' + ad("Advertisement", "ad-top")
    b += page_head(esc(title), esc(lede))
    rows = "\n".join(index_row(a) for a in items)
    b += f"""    <div class="wrap" style="padding-top:26px">
      <div class="index-list">
{rows}
      </div>
      <div class="notice">
        <p><strong>How to read this section.</strong> {note}</p>
      </div>
    </div>
  </main>
"""
    b += footer()
    return b


if __name__ == "__main__":
    n = 0
    for path, content in [
        # The root page is retired: / 301s to /latest/, which is the
    # canonical front page. See the redirect in .htaccess .
    # ("index.html", homepage()),
        ("latest/index.html", latest()),
        ("blog/index.html", listing(
            "blog", "Blog",
            "Y-Squre analysis, explainers and commentary. Every item is opinion or analysis, "
            "never reported fact, and each is labelled accordingly.",
            "Analysis",
            "Everything on this page is Y-Squre's own analysis. It is not reporting and "
            "should not be cited as a description of events. Where we refer to what others "
            "have said, the source is named and the claim is attributed rather than asserted.")),
        ("research/index.html", listing(
            "research", "Research",
            "Research notes and data notes with stated methodology and named sources.",
            "Research Note",
            "Research notes carry a method note and name their data sources. They are "
            "opinion about evidence, not evidence itself: our reading of a relationship is a "
            "judgement, and the underlying published data is the check on it.")),
    ]:
        print(f"  {path:<26}{write(path, content):>7}B")
        n += 1
    print(f"\npages: {n}")
