"""Generate robots.txt, sitemap.xml, favicon, OG image, and the event-report
template (shipped as a template, not as a page containing an invented event)."""
import sys, os, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_lib import *  # noqa

# ------------------------------------------------------------------- inventory
PAGES = []
for dp, _, fs in os.walk(ROOT):
    if ".git" in dp:
        continue
    for f in fs:
        if f.endswith(".html"):
            rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/")
            PAGES.append(rel)
PAGES.sort()
print(f"html pages found: {len(PAGES)}")

# ------------------------------------------------------------------ robots.txt
ROBOTS = """# Y-Square — https://y-squre.com
# Robots are not blocked. AdSense review requires crawlable content.

User-agent: *
Allow: /

# Ad crawlers
User-agent: Mediapartners-Google
Allow: /

User-agent: AdsBot-Google
Allow: /

User-agent: AdsBot-Google-Mobile
Allow: /

User-agent: Googlebot-Image
Allow: /

# No server-side application yet; app.y-squre.com is a separate host and is not
# crawled from here.
Disallow: /app/

Sitemap: https://y-squre.com/sitemap.xml
"""
print("  robots.txt", write("robots.txt", ROBOTS), "B")

# ----------------------------------------------------------------- sitemap.xml
def priority_of(p):
    if p == "index.html":
        return "1.0", "daily"
    if p in ("latest/index.html", "blog/index.html", "geopolitics/index.html",
             "macro/index.html", "markets/index.html", "research/index.html"):
        return "0.9", "daily"
    if re.search(r"/20\d\d/\d\d/\d\d/", p):
        return "0.7", "monthly"
    if p == "404.html" or p.startswith("404/"):
        return None, None
    return "0.5", "monthly"

L = TODAY = "2026-09-26"
urlset = []
for p in PAGES:
    pr, cf = priority_of(p)
    if pr is None:
        continue
    loc = "https://y-squre.com/"
    if p != "index.html":
        loc += p[:-len("index.html")] if p.endswith("index.html") else p
    urlset.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{cf}</changefreq>
    <priority>{pr}</priority>
  </url>""")

SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urlset) + "\n</urlset>\n")
n = write("sitemap.xml", SITEMAP)
print(f"  sitemap.xml {n}B  ({len(urlset)} urls)")

# -------------------------------------------------------------------- favicon
FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Y-Square">
  <rect width="64" height="64" fill="#0d2036"/>
  <rect x="6" y="58" width="52" height="4" fill="#c8471f"/>
  <text x="32" y="42" font-family="Georgia, 'Times New Roman', serif" font-size="30"
        font-weight="700" fill="#ffffff" text-anchor="middle">Y</text>
  <rect x="34" y="20" width="16" height="16" fill="none" stroke="#e0653c" stroke-width="3"/>
</svg>
"""
print("  favicon", write("assets/icons/favicon.svg", FAVICON), "B")

# ------------------------------------------------------------------ OG image
OG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0d2036"/>
  <rect x="0" y="600" width="1200" height="30" fill="#c8471f"/>
  <text x="80" y="300" font-family="Georgia, 'Times New Roman', serif" font-size="104"
        font-weight="700" fill="#ffffff">Y-Square</text>
  <text x="80" y="372" font-family="Helvetica, Arial, sans-serif" font-size="34"
        fill="#93a3b8" letter-spacing="2">MACROECONOMICS &#183; GEOPOLITICS &#183; MARKETS</text>
  <text x="80" y="500" font-family="Helvetica, Arial, sans-serif" font-size="26"
        fill="#6b7a8d">Independent research and analysis</text>
</svg>
"""
print("  og-default", write("assets/images/logo/og-default.svg", OG), "B")

# ------------------------------------------------- event report TEMPLATE (unused)
# Brief section 5 asks for an event-article template. It is written here as a
# commented reference so the structure is on record, but it is NOT generated as
# a live page: doing so would require inventing an event, a timeline and sources,
# which section 20 forbids. Publish it by filling every {{FIELD}}.
TEMPLATE = """<!--
Y-SQUARE — GEOPOLITICAL EVENT REPORT TEMPLATE
=========================================
Copy to:  public_html/geopolitics/<region>/<YYYY>/<MM>/<DD>/<slug>.html
Do NOT publish this file as-is. Every {{FIELD}} must be replaced with
verified material, and a page is only published once all of them are real.

This template exists so the structure is fixed before the first report is filed.
The generator deliberately emits no example event, because an invented
headline on a research site is a liability that cannot be walked back.

REQUIRED BEFORE PUBLISHING
  {{HEADLINE}}      Factual, specific, no adjective the evidence cannot carry.
  {{DECK}}          One or two sentences of what happened, sourced.
  {{REGION}}        One of: north-america, latin-america, europe,
                    united-kingdom, asia, pacific, middle-east, africa
  {{COUNTRY}}       Optional ISO country name.
  {{PUBLISHED_ISO}} Full ISO 8601 with offset, e.g. 2026-09-26T14:05:00+05:30
  {{UPDATED_ISO}}   Same format, or empty.
  {{KEY_POINTS}}    3-5 bullets, each traceable to a named source.
  {{BODY}}          The report. Attribute contested claims in the sentence.
  {{TIMELINE}}      (item) Real timestamps only. Omit the block if unknown.
  {{BACKGROUND}}    Context the reader needs, not a history lesson.
  {{WHAT_TO_WATCH}} Observable, checkable developments. Not predictions.
  {{SOURCES}}       Primary first. Name every secondary source used.
  {{AUTHOR}}        Byline.
  {{CLASS_LABEL}}   One of: news | analysis | explainer | research
  {{REGION_HREF}}   /geopolitics/<region>/

LABELLING RULE
  A report on an event is class "news". If the page contains our own
  interpretation, either cut it or move it to /blog/ and label it "analysis".
  Never let the two share a page.

ATTRIBUTION RULE
  Write "according to <source>" for anything sourced. Never write a claim in
  the voice of Y-Square that we have only read elsewhere.

URL SCHEME
  /geopolitics/<region>/<YYYY>/<MM>/<DD>/<slug>.html
-->
"""
print("  event template", write("docs/TEMPLATES/geopolitical-event-report.template.html", TEMPLATE), "B")
print("  blog template  ", write("docs/TEMPLATES/analysis-article.template.md",
      "# Y-Square — analysis / explainer article\n\n"
      "Path:  public_html/blog/<YYYY>/<MM>/<DD>/<slug>.html\n\n"
      "Required front matter:\n"
      "  title, deck, ctype (analysis|explainer), section, published, updated,\n"
      "  topics[], keypoints[], sources[], related[]\n\n"
      "Rules: label the page in the first visible element; state the episode count\n"
      "behind any estimate; name the observation that would falsify the view.\n"), "B")
