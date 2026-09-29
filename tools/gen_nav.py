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

    also = ""
    if region.get("also"):
        also = ('    <p class="mega-note">' + esc(region["also"][0]) + "</p>")

    pid = _panel_id("m", region["slug"])
    return f'''
      <div class="mega" id="{pid}" data-open="false" aria-label="{esc(region["name"])} sections">
        <div class="mega-inner">
          <div class="mega-head">
            <a class="mega-title" href="{region["path"]}">{esc(region["name"])}</a>
            <span class="mega-sub">All {esc(region["name"].lower())} coverage</span>
          </div>
          <div class="mega-cols">
{chr(10).join(cols)}
          </div>
{also}
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

    if topic["slug"] == "blog":
        kinds = "".join(
            f'<span class="type-chip" data-type="{c["id"]}">{esc(c["label"])}</span>'
            for c in CONTENT_TYPES)
        note = ('    <p class="mega-note">Blog content is analysis, opinion and '
                'explainers. It is never presented as event reporting.</p>')
    else:
        kinds = ""
        note = ""

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
          {kinds and f'<div class="mega-types">{kinds}</div>'}
{note}
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
    """Primary bar: every region.

    "Latest" used to be the first item here. It is the front page now (see the
    301 at / in .htaccess), and a nav item that links to the page you are
    already on is noise, so it moved to the wordmark: the logo carries that
    destination instead. That is the one place a reader looks for "go to the
    front page", which is why the logo had to become a real link rather than
    just losing its href.
    """
    out = []
    for r in REGIONS:
        pid = _panel_id("m", r["slug"])
        out.append(_trigger(r["name"], r["path"], pid))
        out.append(mega_region(r) + "\n      </li>")

    # The second nav row was removed: it duplicated the section hierarchy and
    # pushed the lead story down. Markets, Macro, Research and Blog now live in
    # the Global panel, which was already the row's catch-all, so all four stay
    # one click from the header and nothing is stranded.
    global_topics = dict(TOPICS["global"])
    moved = []
    for slug in ("markets", "macro", "research", "blog"):
        t = TOPICS[slug]
        moved.append({"name": t["name"], "slug": "", "scope": t["lede"],
                      "url": t["path"]})
        for c in t["children"]:
            moved.append({"name": c["name"], "slug": c["slug"],
                          "scope": c.get("scope", ""),
                          "url": t["path"] + c["slug"] + "/"})
    global_topics["children"] = list(global_topics["children"]) + moved
    pid = _panel_id("m", "global")
    out.append(_trigger(global_topics["name"], global_topics["path"], pid))
    out.append(mega_topic(global_topics) + "\n      </li>")

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
    g = TOPICS["global"]
    rows.append(f'<li class="acc-leaf"><a href="{g["path"]}">{esc(g["name"])}</a></li>')
    for r in REGIONS:
        rows.append(f'<li class="acc-leaf"><a href="{r["path"]}">{esc(r["name"])}</a></li>')
    for slug in ("markets", "macro", "research", "blog"):
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


def header(current=""):
    """The complete header block injected into every page."""
    return f'''
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="masthead">
      <div class="wrap masthead-inner">
        <a class="brand" href="/latest/">
          <span class="brand-mark" aria-hidden="true">Y</span>
          <span class="brand-text"><span class="brand-name">Y-SQURE</span></span>
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
          <a class="util-link util-signin" href="/account/index.html">Sign In</a>
        </div>
        <button class="nav-toggle" data-burger aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu">
          <span class="nav-toggle-bars" aria-hidden="true"><i></i><i></i><i></i></span>
          <span class="nav-toggle-text">Menu</span>
        </button>
      </div>
    </div>
    <nav class="primary-nav" data-nav aria-label="Sections">
      <div class="wrap">
        <ul class="nav-list nav-list-geo">
{primary_nav(current)}
        </ul>
      </div>
    </nav>
{mobile_menu()}
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
    print(f"  regions: {len(REGIONS)}  topic bar: 4  global: 1")
    # every trigger must have a matching panel id, and vice versa
    import re
    triggers = set(re.findall(r'aria-controls="(m-[\w-]+)"', h))
    panels = set(re.findall(r'<div class="mega" id="(m-[\w-]+)"', h))
    print(f"  triggers: {len(triggers)}  panels: {len(panels)}  "
          f"{'MATCH' if triggers == panels else 'MISMATCH ' + str(triggers ^ panels)}")
