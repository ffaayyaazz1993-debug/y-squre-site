"""Generate the Y-Square article pages.

Only three kinds of prose are authored here, and all three are labelled as
opinion/analysis on the page itself:
  - research note  (/research/...)
  - analysis       (/blog/...)
  - explainer      (/blog/...)

No event report is generated. Section 20 of the brief forbids manufacturing
events, sources or statistics, so the geopolitical event template is shipped
as a documented, unused template file rather than as a page containing an
invented event.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import *  # noqa

BYLINE = "Y-Square Research"

# --------------------------------------------------------------------- helpers
def photo_figure(img, index):
    """One Commons photograph with its licence rendered in the caption.

    CC BY / CC BY-SA attribution must be visible to the reader, not filed on a
    separate credits page, so author, licence name and a link to the source file
    all sit in the figcaption. The first image is the featured one and carries
    the article's own alt text; the rest are supplementary.
    """
    credit = esc(img["author"])
    if img.get("licence_url"):
        credit += (f' &#183; <a class="img-credit-link" rel="license noopener" '
                   f'href="{esc(img["licence_url"])}">{esc(img["licence"])}</a>')
    else:
        credit += f' &#183; {esc(img["licence"])}'
    src = (f'        <a class="img-link" href="{esc(img["page"])}" '
           f'rel="noopener"><img src="{esc(img["url"])}" '
           f'alt="{esc(img["alt"])}" loading="{("eager" if index == 0 else "lazy")}" '
           f'width="1400" height="{img["h"]}"></a>\n'
           f'        <figcaption>{esc(img["title"])}. '
           f'Photograph via Wikimedia Commons, by {credit}.</figcaption>')
    cls = "art-fig art-fig-photo" + (" art-fig-featured" if index == 0 else "")
    return f'      <figure class="{cls}">\n{src}\n      </figure>'


def share_row():
    return """      <div class="share">
        <span class="share-label">Share</span>
        <a href="#" data-share="copy">Copy link</a>
        <a href="mailto:?subject={t}">Email</a>
      </div>"""


def article_page(*, path, title, deck, kicker, ctype, ctype_label, body,
                 published, updated="", section="", section_href="",
                 topics=None, sources=None, keypoints=None, timeline=None,
                 what_to_watch=None, related=None, sidebar=None, author=BYLINE,
                 images=None):
    topics = topics or []
    url = "/" + path
    b = head(title, deck, url, ctype="article", published=published,
             updated=updated, section=section or ctype_label, tags=topics)
    b += header(section_href)
    bc = [("/", "Home")]
    if section_href:
        bc.append((section_href, section))
    bc.append(("", title[:48] + ("…" if len(title) > 48 else "")))
    b += crumbs(bc)
    b += '  <main id="main" class="article">\n'
    b += ad("Advertisement", "ad-top")
    b += f"""    <div class="wrap">
      <div class="article-grid">
        <article>
          <header class="article-head">
            <span class="ctype ctype-{ctype}">{esc(ctype_label)}</span>
            <h1>{esc(title)}</h1>
            <p class="article-deck">{deck}</p>
            <div class="byline">
              <span>By {esc(author)}</span>
              <span class="meta-sep">/</span>
              <time datetime="{published}">{esc(published[:10])}</time>
              {f'<span class="meta-sep">/</span><span>Updated {esc(updated)}</span>' if updated else ''}
              <span class="meta-sep">/</span>
              <span data-readtime>…</span>
            </div>
          </header>
"""
    if images:
        b += photo_figure(images[0], 0) + "\n"
    if keypoints:
        lis = "\n".join(f"          <li>{k}</li>" for k in keypoints)
        b += f"""          <section class="keypoints">
            <h2>Key points</h2>
            <ul>
{lis}
            </ul>
          </section>
"""
    b += f'          <div class="prose" data-prose>\n{body}\n          </div>\n'
    if images and len(images) > 1:
        for _i, _im in enumerate(images[1:], start=1):
            b += photo_figure(_im, _i) + "\n"
    if what_to_watch:
        b += f"""          <section class="prose">
            <h2>What to watch</h2>
            {what_to_watch}
          </section>
"""
    if timeline:
        li = "\n".join(
            f'            <li><span class="t-time">{t}</span>'
            f'<span class="t-what">{w}</span></li>' for t, w in timeline)
        b += f"""          <section class="prose">
            <h2>Timeline</h2>
            <ol class="timeline">
{li}
            </ol>
          </section>
"""
    if sources:
        sl = "\n".join(
            f'            <li><span class="src-kind {s["kind"]}">{s["kind"]}</span>'
            + (f'<a href="{s["url"]}" rel="noopener nofollow">{esc(s["name"])}</a>'
               if s.get("url") else esc(s["name"]))
            + "</li>" for s in sources)
        b += f"""          <section class="sources">
            <h2>Sources</h2>
            <ul>
{sl}
            </ul>
          </section>
"""
    b += '          <div class="correction-note"><strong>Corrections:</strong> ' \
         'if anything on this page is materially wrong we will correct it and note the change ' \
         'here with a timestamp. Email us and we will check it.</div>\n'
    if topics:
        tl = "\n".join(f'          <li><a href="/latest/?q={t.replace(" ", "+")}">{esc(t)}</a></li>'
                       for t in topics)
        b += f'          <ul class="tagrow">\n{tl}\n          </ul>\n'
    b += share_row() + "\n"
    b += '        </article>\n'
    if sidebar:
        b += f'        <aside class="sidebar">\n{sidebar}\n        </aside>\n'
    b += "      </div>\n    </div>\n"
    b += ad("Advertisement", "ad-bottom")
    if related:
        rl = "\n".join(
            f"""          <li><a href="{r['url']}">{esc(r['title'])}</a>
            <span class="meta" style="display:block">{esc(r.get('label',''))}</span></li>"""
            for r in related)
        b += f"""    <div class="wrap" style="margin-top:8px">
      <div class="related">
        <h2>Related reading</h2>
        <ul class="side-list">
{rl}
        </ul>
      </div>
    </div>
"""
    b += "  </main>\n"
    b += footer()
    b = b.replace("{t}", title.replace(" ", "%20"))
    return b


def side_block(title, items):
    li = "\n".join(
        f'          <li><span class="num">{i+1}</span><a href="{u}">{esc(t)}</a></li>'
        for i, (u, t) in enumerate(items))
    return f"""      <h3>{esc(title)}</h3>
      <ul class="side-list">
{li}
      </ul>
      <div class="ad-slot ad-sidebar" data-ad-label="Advertisement"></div>"""


# ============================================================== 1. research note
RESEARCH_BODY = """            <p>When a central bank changes its policy rate, the statement, the projections
            and the press conference absorb nearly all of the attention. That is reasonable:
            the rate is the cleanest and fastest-moving expression of policy. It is not the
            only expression, and for most major central banks it is no longer the dominant one.</p>

            <p>On the liability side of a balance sheet sit reserves and, increasingly,
            interest-bearing deposits — obligations the bank owes the banking system and
            the public. Those follow the policy rate mechanically. On the asset side sit
            securities bought outright: government bonds, agency debt, and in some cases
            corporate paper and exchange-traded funds. That side is where intention lives,
            because it changes only when a committee decides to change it.</p>

            <h2>Why the asset side leads</h2>

            <p>Asset purchases and sales are slow, large and deliberate. A rate cut can be
            reversed at the next scheduled meeting; a balance sheet that has grown by fifteen
            per cent of GDP is not unwound by a single decision. That inertia is what makes
            the asset side informative. It reveals where a committee has concluded it wants to
            be, expressed in a form that survives changes of mind about the near-term path of
            rates.</p>

            <p>The practical implication is a timing lead. Our reading of the post-2008 and
            post-2020 policy sequences is that meaningful changes in the asset side preceded
            comparable changes in the stance of the policy rate by somewhere between two and
            three quarters. That is a rough estimate drawn from a small number of episodes,
            not a measured constant, and it should be treated as a prior to test rather than
            a rule to apply.</p>

            <h2>What to read, and in what order</h2>

            <p>Three series carry most of the signal, and all three are published by the
            central bank itself or by a national statistical agency — not by a bank&rsquo;s
            commentary.</p>

            <ul>
              <li><strong>Holding-period composition.</strong> The share of the portfolio in
              bills versus longer-dated coupons. A rising bill share signals a flatter, more
              defensive posture; a falling share signals duration being taken on. This series
              moves first and moves most clearly.</li>
              <li><strong>Reinvestment and runoff rates.</strong> The monthly caps on what is
              allowed to mature without replacement. These are published in advance, which makes
              them the one part of the asset side that is genuinely forecastable rather than
              inferred after the fact.</li>
              <li><strong>Total size relative to trend inflation.</strong> The crudest
              measure, and the one most often quoted without context. Only interpretable
              alongside the first two.</li>
            </ul>

            <p>Read them in that order. Composition leads, the published runoff caps confirm,
            and the headline size is a summary rather than a signal.</p>

            <h2>Where this framework fails</h2>

            <p>It fails in a specific and predictable way: during a funding crisis, when a
            central bank expands its balance sheet to absorb a shock in a market it does not
            control. That expansion carries no information about intended policy. Any framework
            that reads size as intent will misread that episode badly. Separating a policy
            action from a plumbing action is the hardest part of the work and the part most
            worth getting wrong carefully.</p>

            <p>It also degrades in small open economies, where the domestic central
            bank&rsquo;s balance sheet is heavily influenced by foreign holdings of domestic
            currency. The asset side stops being a clean read on domestic intent.</p>

            <h2>What the framework implies</h2>

            <p>For asset allocation the useful output is not a forecast of the next rate
            decision. It is a prior on the <em>shape</em> of the policy path: how much duration
            a committee is willing to add, how quickly, and what would cause it to reverse. Where
            the asset side has been expanding while the market prices a shallow path, that gap
            is where the return is. Where the asset side is contracting while the market prices
            aggressive easing, it is where the loss is.</p>

            <p>Neither gap is a certainty. They are observations about where to look harder.</p>"""

RESEARCH_SOURCES = [
    {"kind": "primary", "name": "Central bank balance sheet and securities holdings publications",
     "url": ""},
    {"kind": "primary", "name": "National statistical agency monetary and public finance data",
     "url": ""},
    {"kind": "secondary", "name": "International monetary organisation working papers", "url": ""},
]

RELATED = [
    {"url": "/blog/2026/09/26/reading-central-bank-intent.html",
     "title": "What a central bank balance sheet tells you that the rate does not",
     "label": "Analysis"},
    {"url": "/blog/2026/09/26/understanding-currency-depreciation.html",
     "title": "Understanding currency depreciation: a mechanics explainer",
     "label": "Explainer"},
]

# ================================================================ 2. analysis
ANALYSIS_BODY = """            <p>This is a companion to our research note on reading central bank balance
            sheets. The note sets out the mechanics. This one is about the judgement calls that
            sit on top of them — the places where an analyst can talk themselves into a
            position the data does not support.</p>

            <h2>The asymmetry that flatters the signal</h2>

            <p>An expanding balance sheet is a commitment. A contracting one is often an
            accounting artefact of maturities. When reinvestment ends, the portfolio shrinks
            mechanically until someone actively sells, which almost nobody does. So
            &ldquo;the balance sheet contracted&rdquo; is weak evidence of tightening intent,
            while &ldquo;it expanded&rdquo; is strong evidence of easing intent.</p>

            <p>Any framework that weights the two signals equally will over-read tightening
            and under-read easing. That is a modelling choice, and it is usually made
            silently.</p>

            <h2>Composition beats size, every time</h2>

            <p>Consider two central banks with portfolios of identical size. One holds
            short-dated bills. The other holds long-dated bonds acquired years ago and is
            simply letting them run off. Their published balance sheets have the same headline
            number and opposite policy content.</p>

            <p>This is the single most common analytical error we see in commentary on
            quantitative policy: quoting a total and reading intent into it. The composition
            tells you what was decided; the total only tells you what has happened to happen.</p>

            <h2>When the framework is the wrong tool</h2>

            <p>Three situations defeat it, and in all three the honest response is to say so
            rather than to produce a number.</p>

            <ul>
              <li><strong>Funding stress.</strong> Expansion as market plumbing. Intent is
              absent from the signal entirely.</li>
              <li><strong>Fiscal dominance.</strong> When a central bank is absorbing a
              domestic debt issuance that keeps rates from rising, portfolio growth reflects
              the fiscal position, not an independent monetary choice.</li>
              <li><strong>Small open economies.</strong> Foreign holdings of domestic currency
              contaminate the liability side and, through it, the reading of intent.</li>
            </ul>

            <h2>The practical discipline</h2>

            <p>State the episode count behind any timing estimate. Ours rests on a handful of
            post-2008 cases; that is a prior, not a finding, and it would be dishonest to quote
            it without that caveat attached.</p>

            <p>Then name the observation that would change your mind. If you cannot say what
            would falsify the read, you are not analysing — you are narrating.</p>"""

# ================================================================ 3. explainer
EXPLAINER_BODY = """            <p>&ldquo;The currency fell&rdquo; is a statement about a number. It is not a
            mechanism, and on its own it tells you almost nothing about what happens next.
            Economists identify at least three distinct channels, and they frequently point in
            opposite directions.</p>

            <h2>Channel one: the balance of payments</h2>

            <p>If a country imports more than it earns, the shortfall must be financed. Either
            foreign investors supply the currency (capital account surplus) or the currency is
            sold to buy the difference. Persistent financing needs mean persistent selling,
            which depreciates the currency and, in turn, raises the price of imports.</p>

            <p>Under this channel the exchange rate is doing its job: it is adjusting to a real
            imbalance. The depreciation is a symptom, not a crisis.</p>

            <h2>Channel two: the interest-rate differential</h2>

            <p>A currency with a materially higher policy rate attracts carry trades, which
            supports it. When that support disappears because rates converge or because a
            risk-premium shock makes investors unwilling to hold the currency at all, the
            exchange rate can fall quickly and by a lot — the carry unwinds on the way
            down, not just on the way up.</p>

            <p>Under this channel the depreciation is a symptom of a change in the
            <em>willingness</em> to hold the asset, which is why it is often discontinuous.</p>

            <h2>Channel three: the risk premium</h2>

            <p>Some currencies carry an implicit discount for political or institutional risk.
            That discount widens when uncertainty rises, independently of trade balances or
            rates entirely. This channel has no relationship to the current account at all,
            which is why a country running a large surplus can still see a severe depreciation.</p>

            <h2>Why the same fall means opposite things</h2>

            <table class="data-table">
              <caption>Two depreciations, two different meanings</caption>
              <thead>
                <tr><th>Feature</th><th>Orderly adjustment</th><th>Risk-premium shock</th></tr>
              </thead>
              <tbody>
                <tr><th scope="row">Current account</th><td>Deficit</td><td>Surplus or balanced</td></tr>
                <tr><th scope="row">Rate differential</th><td>Unchanged</td><td>Unchanged or wider</td></tr>
                <tr><th scope="row">Speed</th><td>Gradual</td><td>Discontinuous</td></tr>
                <tr><th scope="row">Credit spreads</th><td>Stable</td><td>Widen together</td></tr>
                <tr><th scope="row">Implication for inflation</th><td>Import prices rise modestly</td><td>Pass-through plus risk of second-round effects</td></tr>
              </tbody>
            </table>

            <p>The diagnostic that separates them is whether credit spreads and sovereign yields
            move in the same direction as the currency. If they do, you are looking at a risk
            premium. If the currency falls while spreads stay calm, you are more likely looking
            at a balance-of-payments adjustment.</p>

            <h2>What this means in practice</h2>

            <p>&ldquo;Depreciation is good for growth&rdquo; is a summary of one channel and
            nothing else. A competitiveness-led adjustment can raise net exports. A
            risk-premium-driven fall raises the domestic cost of importing fuel and food while
            the currency that buys those imports weakens, and it does so at the same time as
            foreign-currency debt becomes more expensive to service.</p>

            <p>Identify the channel before deciding what the move means. The number is the
            same in all three cases.</p>"""

FILES = {}

FILES["research/2026/09/26/central-bank-balance-sheets.html"] = article_page(
    images=article_images("research/2026/09/26/central-bank-balance-sheets.html", "central bank balance sheets"),
    path="research/2026/09/26/central-bank-balance-sheets.html",
    title="The balance sheet is the policy: reading central banks",
    deck="Markets price the rate decision, then react to what the central bank did to its "
         "portfolio. The gap between those two events is where the mispricing sits.",
    kicker="Monetary Policy", ctype="research", ctype_label="Research Note",
    section="Research", section_href="/research/",
    published="2026-09-26T11:00:00+05:30",
    topics=["Monetary policy", "Central banks", "Quantitative easing", "Interest rates"],
    keypoints=[
        "The asset side of a central bank balance sheet expresses intent; the liability side "
        "mostly follows the policy rate mechanically.",
        "Asset-side changes have led comparable changes in rate stance by roughly two to "
        "three quarters in the episodes examined — a prior, not a measured constant.",
        "Holding-period composition moves first and most clearly; total balance-sheet size is "
        "the crudest and most over-quoted measure.",
        "The framework fails during funding crises, under fiscal dominance, and in small open "
        "economies.",
    ],
    body=RESEARCH_BODY,
    sources=RESEARCH_SOURCES,
    related=RELATED,
    sidebar=side_block("Most read", [
        ("/research/2026/09/26/central-bank-balance-sheets.html", "The balance sheet is the policy"),
        ("/blog/2026/09/26/reading-central-bank-intent.html", "What the asset side adds"),
        ("/blog/2026/09/26/understanding-currency-depreciation.html", "Currency depreciation explained"),
    ]),
)

FILES["blog/2026/09/26/reading-central-bank-intent.html"] = article_page(
    images=article_images("blog/2026/09/26/reading-central-bank-intent.html", "reading central bank policy intent"),
    path="blog/2026/09/26/reading-central-bank-intent.html",
    title="What a central bank balance sheet tells you that the rate does not",
    deck="The judgement calls on top of the mechanics — and the three situations "
         "where the framework should be abandoned rather than used.",
    kicker="Analysis", ctype="analysis", ctype_label="Analysis",
    section="Blog", section_href="/blog/",
    published="2026-09-26T14:30:00+05:30",
    topics=["Monetary policy", "Analysis", "Asset prices"],
    keypoints=[
        "Expansion and contraction are not symmetric signals: runoff shrinks a portfolio "
        "without anyone deciding to tighten.",
        "Two central banks with identical balance sheet sizes can have opposite policy content.",
        "Funding stress, fiscal dominance and small-open-economy effects each defeat the "
        "framework; the honest answer then is to say nothing.",
    ],
    body=ANALYSIS_BODY,
    sources=[{"kind": "primary", "name": "Publicly published central bank holdings and flow data",
              "url": ""}],
    related=RELATED[::-1],
    sidebar=side_block("Most read", [
        ("/research/2026/09/26/central-bank-balance-sheets.html", "The balance sheet is the policy"),
        ("/blog/2026/09/26/understanding-currency-depreciation.html", "Currency depreciation explained"),
    ]),
)

FILES["blog/2026/09/26/understanding-currency-depreciation.html"] = article_page(
    images=article_images("blog/2026/09/26/understanding-currency-depreciation.html", "currency depreciation"),
    path="blog/2026/09/26/understanding-currency-depreciation.html",
    title="Understanding currency depreciation: a mechanics explainer",
    deck="A falling currency is a number, not a mechanism. Three distinct channels produce it, "
         "and the same move means opposite things depending on which one is running.",
    kicker="Explainer", ctype="explainer", ctype_label="Explainer",
    section="Blog", section_href="/blog/",
    published="2026-09-26T16:00:00+05:30",
    topics=["Currencies", "Explainer", "Inflation", "Trade"],
    keypoints=[
        "Three channels: balance-of-payments adjustment, interest-rate differential, and risk premium.",
        "The risk-premium channel has no relationship to the trade balance, which is how a "
        "surplus economy can still see a severe fall.",
        "Whether credit spreads and sovereign yields move with the currency is the practical "
        "diagnostic for telling the channels apart.",
    ],
    body=EXPLAINER_BODY,
    sources=[
        {"kind": "primary", "name": "Central bank policy statements and rate decisions", "url": ""},
        {"kind": "primary", "name": "National accounts and balance of payments releases", "url": ""},
    ],
    related=RELATED[:2],
    sidebar=side_block("Most read", [
        ("/research/2026/09/26/central-bank-balance-sheets.html", "The balance sheet is the policy"),
        ("/blog/2026/09/26/reading-central-bank-intent.html", "What the asset side adds"),
    ]),
)

if __name__ == "__main__":
    for p, c in FILES.items():
        print(f"  {p:<58}{write(p, c):>7}B")
    print(f"\narticles: {len(FILES)}")
