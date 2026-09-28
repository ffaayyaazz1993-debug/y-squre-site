"""Y-Square site generator.

One source of truth for every page so nav, footer, SEO and consent wiring can
never drift between 40+ files. Output is plain static HTML — no build step is
required to serve it; this script only exists to keep the pages consistent.

Content ethics: this generator never invents news. Reporting sections render an
explicit empty state until real reporting is added. Only analysis / explainer /
research prose is authored, and it is labelled as such on every page.
"""

import os, re, html, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://y-squre.com"
TODAY = "2026-09-26"
NOW_ISO = "2026-09-26T16:30:00+05:30"
EMAIL = "ffaayyaazz1993@gmail.com"
PUB = "pub-9461123152614358"
CLIENT = "ca-pub-9461123152614358"

NAV = [("/latest/", "Latest"), ("/geopolitics/", "Geopolitics"), ("/macro/", "Macro"),
       ("/markets/", "Markets"), ("/blog/", "Blog"), ("/research/", "Research")]

FOOTER_COLS = [
    ("Sections", [("/latest/", "Latest"), ("/geopolitics/", "Geopolitics"),
                  ("/macro/", "Macro"), ("/markets/", "Markets"),
                  ("/blog/", "Blog"), ("/research/", "Research")]),
    ("About", [("/about/index.html", "About Y-Square"), ("/contact/index.html", "Contact"),
               ("/editorial-policy/index.html", "Editorial Policy"),
               ("/advertising/index.html", "Advertising"), ("/sitemap.xml", "Sitemap")]),
    ("Legal", [("/privacy/index.html", "Privacy Policy"), ("/terms/index.html", "Terms of Use"),
               ("/disclaimer/index.html", "Investment Disclaimer"),
               ("/privacy/index.html#cookies", "Cookie Choices")]),
]

DISCLAIMER_SHORT = ("Information and education only. Not investment advice and not an offer to "
                    "buy or sell any security. Investments in securities markets are subject to "
                    "market risks. Past performance is not indicative of future results. "
                    "Y-Square is not a SEBI-registered investment adviser.")

FOOTER_DISCLAIMER = ("<strong>Disclaimer:</strong> Investments in securities markets are subject to "
                     "market risks. Read all related documents carefully before investing. Content "
                     "on this website is for information and education only and does not constitute "
                     "investment advice or a solicitation to buy or sell any security. Past "
                     "performance is not indicative of future results. Y-Square is not a "
                     "SEBI-registered investment adviser.")

NAV_HTML = "\n".join(
    f'        <li><a href="{h}">{t}</a></li>' for h, t in NAV)


def esc(s):
    return html.escape(str(s), quote=True)


def head(title, desc, url, *, ctype="website", published="", updated="",
         section="", tags=None, noindex=False, extra_css=()):
    """Standard <head>. OG + Twitter + article metadata per the brief."""
    canonical = url if url.startswith("http") else SITE + url
    tags = tags or []
    kw = "".join(f'\n    <meta name="keywords" content="{esc(t)}">' for t in tags)
    art = ""
    if ctype == "article":
        art = (
            '\n    <meta property="article:published_time" content="%s">'
            '\n    <meta property="article:section" content="%s">'
            '\n    <meta property="article:author" content="Y-Square Research">'
            % (published, esc(section or "Analysis"))
        )
        if updated:
            art += '\n    <meta property="article:modified_time" content="%s">' % updated
        if tags:
            art += "".join(f'\n    <meta property="article:tag" content="{esc(t)}">' for t in tags)
    rob = '\n    <meta name="robots" content="noindex, follow">' if noindex else ""
    css = "".join(f'\n    <link rel="stylesheet" href="{c}">' for c in
                  ["/assets/css/base.css", "/assets/css/layout.css",
                   "/assets/css/article.css", "/assets/css/nav.css", "/assets/css/sections.css",
                   "/assets/css/responsive.css"])
    # OG image is a real, on-server asset (SVG) so crawlers have something to fetch.
    ogimg = SITE + "/assets/images/logo/og-default.svg"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">{kw}{rob}
  <link rel="canonical" href="{canonical}">{css}
  <link rel="icon" href="/assets/icons/favicon.svg" type="image/svg+xml">
  <meta name="google-adsense-account" content="{CLIENT}">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CLIENT}"
          crossorigin="anonymous"></script>
  <meta name="theme-color" content="#0d2036">

  <meta property="og:type" content="{ctype}">
  <meta property="og:site_name" content="Y-Square">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{ogimg}">
  <meta property="og:locale" content="en_GB">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{ogimg}">{art}
  <script src="/assets/js/main.js" defer></script>
  <script src="/assets/js/nav.js" defer></script>
  <script src="/assets/js/consent.js" defer></script>
  <script src="/assets/js/search.js" defer></script>
</head>
<body>
"""


def header(active="/"):
    """Delegates to gen_nav so the header has exactly one definition.

    Imported lazily: gen_nav imports this module for esc()/head()/footer(),
    so a module-level import here would be circular.
    """
    import gen_nav
    return gen_nav.header(active)


def footer():
    cols = "\n".join(
        f"""      <div>
        <h4>{h}</h4>
        <ul>
{chr(10).join(f'          <li><a href="{u}">{t}</a></li>' for u, t in links)}
        </ul>
      </div>""" for h, links in FOOTER_COLS)
    return f"""  <footer class="footer">
    <div class="wrap footer-top">
      <div>
        <div class="footer-brand">Y<span>-</span>Square</div>
        <p style="font-size:.86rem;line-height:1.6">Independent research on macroeconomics,
        geopolitics and markets. Original analysis, primary sources, stated assumptions.</p>
        <p style="font-size:.86rem;margin-top:10px">
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </p>
      </div>
{cols}
    </div>
    <div class="wrap">
      <p class="footer-note footer-caution">{FOOTER_DISCLAIMER}</p>
      <div class="footer-bottom">
        <span>&copy; {TODAY[:4]} Y-Square. All rights reserved.</span>
        <span>
          <a href="#" onclick="window.ysqResetConsent(); return false;">Cookie choices</a>
          &nbsp;&middot;&nbsp; <a href="/sitemap.xml">Sitemap</a>
        </span>
      </div>
    </div>
  </footer>
</body>
</html>
"""


def ad(label, cls="ad-inline"):
    return f'  <div class="ad-slot {cls}" data-ad-label="{esc(label)}"></div>\n'


def crumbs(items):
    li = "\n".join(
        f'        <li><a href="{u}">{t}</a></li>' if u else f"        <li>{t}</li>"
        for u, t in items)
    return f'  <nav class="crumbs wrap" aria-label="Breadcrumb">\n    <ol>\n{li}\n    </ol>\n  </nav>\n'


def write(path, content):
    # Strip leading separators before joining. os.path.join(ROOT, "\\foo") on
    # Windows returns "\\foo" — the ROOT is silently discarded and the file
    # lands at the drive root. Page paths are written as site-absolute
    # ("/geopolitics/europe/index.html") because that is also the URL form,
    # so this normalisation is load-bearing, not cosmetic.
    rel = path.replace("\\", "/").lstrip("/")
    full = os.path.join(ROOT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return len(content.encode("utf-8"))


def page_head(h1, lede=None):
    p = f"      <p>{lede}</p>\n" if lede else ""
    return f'  <div class="page-head">\n    <div class="wrap">\n      <h1>{h1}</h1>\n{p}    </div>\n  </div>\n'


def article_images(page_path, subject):
    """Commons photographs for an article, with alt text written from the
    article's own subject. Returns [] when the fetch found nothing that passed
    the relevance gate -- the article then publishes without an image, which is
    the specified behaviour, not a fallback.

    Alt text describes the photograph for a reader who cannot see it. It is not
    a caption of what the article argues: these are pictures of the places the
    article is about, not illustrations of the argument.
    """
    import json as _json
    _m = os.path.join(ROOT, "assets", "img", "manifest.json")
    if not os.path.exists(_m):
        return []
    _all = _json.load(open(_m, encoding="utf-8"))
    _got = _all.get(page_path) or []
    out = []
    for _i, _g in enumerate(_got):
        out.append({
            "url": _g["url"], "page": _g["page"], "title": _g["title"],
            "author": _g["author"], "licence": _g["licence"],
            "licence_url": _g.get("licence_url", ""),
            "h": 900,
            "alt": (f"A Wikimedia Commons photograph of {_g['title'].rsplit('.', 1)[0]}, "
                    f"used in Y-Square coverage of {subject}."),
        })
    return out
