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
def latest():
    b = head("Latest | Y-Squre Research",
             "Every article, explainer and research note published by Y-Squre, newest first, with publication times, content labels and reading times.", "/latest/")
    b += header("/latest/")
    # The topic bar that used to sit here -- Geopolitics, Macro, Markets,
    # Analysis, Research -- duplicated items already present in the two nav rows
    # above it (Markets, Macro, Research and Blog are top-level; Geopolitics is
    # reachable from every region panel). A third row restating them was noise,
    # and on the Latest page it read as a section header for content that was
    # never sectioned. Removed rather than restyled.
    b += crumbs([("/", "Home"), ("/latest/", "Latest")])
    b += '  <main id="main">\n' + ad("Advertisement", "ad-top")
    # The "Latest" title block that sat here duplicated the breadcrumb directly
    # above it and pushed the first story 145px down the page. It was also the
    # only thing between the header and the lead story, so the ad slot had no
    # room to be seen. Removed: the breadcrumb and the lead headline both say
    # where you are. The <h1> is kept for structure and screen readers, so the
    # page is not left without a top-level heading.
    b += '  <h1 class="visually-hidden">Latest</h1>\n'
    _grid, _n, _sec, _rest = GL.latest_body(ARTICLES, GL.load_manifest())
    b += f'''    <div class="wrap" style="padding-top:26px">
{_grid}
      <section class="sect" style="margin-top:34px">
        <div class="sect-head"><h2>Reporting sections</h2></div>
        <div class="empty-state">
          <strong>No event reports published yet</strong>
          Geopolitics, macro and markets reporting will appear here in reverse chronological
          order. Sections exist and are linked below; they are empty because nothing has been
          published, not because anything is hidden.
        </div>
        <ul class="chips" style="margin-top:14px">
          <li><a class="chip" href="/geopolitics/">Geopolitics</a></li>
          <li><a class="chip" href="/macro/">Macro</a></li>
          <li><a class="chip" href="/markets/">Markets</a></li>
        </ul>
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
    b += crumbs([("/", "Home"), (f"/{slug}/", title)])
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
        ("index.html", homepage()),
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
