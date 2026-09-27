"""Generate region, subregion and topic pages from assets/data/geography.json.

Each subregion page carries a real country table with an id per country, so a
country link in the mega-menu deep-links to a row that exists rather than
opening a thin page. That is the whole point of decision 2: the anchors have
to land on content, not on an empty stub.

Reporting sections render the honest empty state. No event, source, statistic
or timestamp is invented anywhere in this file.
"""

import sys, os, json, html, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_nav as N
from gen_page import render, emit
from gen_lib import esc, write

EMPTY_NEWS = '''
      <div class="empty-state">
        <p class="empty-kicker">No verified reports published yet</p>
        <p>Y-Square publishes event reporting only when it can be attributed to
        a named, checkable source. Nothing has been published under
        {label} yet, and we would rather show you an empty section than fill
        it with material we cannot stand behind.</p>
        <p>Analysis, explainers and research notes in adjacent sections are
        published and clearly labelled as opinion rather than reporting.</p>
        <ul class="empty-links">
{links}
        </ul>
      </div>'''


def _nav_siblings(region):
    """Other subregions in the same region, as internal links."""
    return "\n".join(
        f'          <li><a href="/geopolitics/{region["slug"]}/{s["slug"]}/">{esc(s["name"])}</a></li>'
        for s in region["sections"] if s["slug"] != region.get("_cur"))


def region_page(region):
    slug, name = region["slug"], region["name"]

    # Subregion cards, each with its country count and scope line.
    cards = []
    for s in region["sections"]:
        n = len(s["countries"])
        cards.append(f'''
        <a class="sec-card" href="/geopolitics/{slug}/{s["slug"]}/">
          <h3>{esc(s["name"])}</h3>
          <p class="sec-card-scope">{esc(s["scope"])}</p>
          <p class="sec-card-meta">{n} countr{"y" if n == 1 else "ies"}</p>
        </a>''')

    crumbs = N.breadcrumb([("Home", "/"), ("Geopolitics", "/geopolitics/"),
                           (name, None)])

    body = f'''  <main id="main" class="wrap page">
{crumbs}
    <h1>{esc(name)}</h1>
    <p class="page-lede">{esc(region["lede"])}</p>

    <div class="empty-state">
      <p class="empty-kicker">No verified reports published yet</p>
      <p>Event reporting appears here only when it can be attributed to a
      named, checkable source. Nothing has been published for {esc(name)} yet.</p>
    </div>

    <h2 class="section-h">Subregions</h2>
    <div class="sec-grid">
{chr(10).join(cards)}
    </div>
'''
    if region.get("also"):
        body += f'''
    <p class="page-note"><strong>Note on classification.</strong> {esc(region["also"][0])}</p>
'''
    body += "  </main>\n"

    return {
        "path": f"/geopolitics/{slug}/index.html",
        "url": f"/geopolitics/{slug}/",
        "title": f"{name} Geopolitics & Economic Coverage | Y-Square",
        "desc": (f"Geopolitical and economic coverage across {name.lower()}, "
                 f"organised by subregion. Subregion hubs list every country "
                 f"Y-Square tracks and what it covers there."),
        "h1": name,
        "body": body,
        "section": "geopolitics",
    }


def subregion_page(region, sec):
    slug, name = region["slug"], region["name"]
    base = f"/geopolitics/{slug}/{sec['slug']}/"

    # The country table. One id per country, matching the anchor the mega-menu
    # links to. Each row states what Y-Square covers for that country, so the
    # deep link lands on real editorial scope rather than a bare name.
    rows = []
    for c in sec["countries"]:
        rows.append(f'''        <tr id="{c["anchor"]}">
          <th scope="row"><a href="{base}#{c["anchor"]}">{esc(c["name"])}</a></th>
          <td>{esc(sec["scope"])}</td>
          <td class="td-empty">No verified report yet</td>
        </tr>''')

    # Other subregions, for crawl depth and reader context.
    others = [s for s in region["sections"] if s["slug"] != sec["slug"]]
    other_links = "\n".join(
        f'          <li><a href="/geopolitics/{slug}/{s["slug"]}/">{esc(s["name"])}</a></li>'
        for s in others)

    crumbs = N.breadcrumb([("Home", "/"), ("Geopolitics", "/geopolitics/"),
                           (name, region["path"]), (sec["name"], None)])

    body = f'''  <main id="main" class="wrap page">
{crumbs}
    <p class="kicker"><a href="{region["path"]}">{esc(name)}</a></p>
    <h1>{esc(sec["name"])}</h1>
    <p class="page-lede">{esc(sec["scope"])}</p>

    <div class="empty-state">
      <p class="empty-kicker">No verified reports published yet</p>
      <p>Nothing has been reported for {esc(sec["name"])} that we could
      attribute to a named source. The country table below states the scope we
      cover here, so you can see what this section will contain.</p>
    </div>

    <h2 class="section-h">Countries in {esc(sec["name"])}</h2>
    <p class="table-note">{len(sec["countries"])} countries. Each links to its
    row. Y-Square tracks all of them; it reports on a country when a
    development is verifiable and material.</p>
    <table class="country-table">
      <caption class="sr-only">Countries in {esc(sec["name"])}</caption>
      <thead>
        <tr><th scope="col">Country</th><th scope="col">Y-Square scope</th>
            <th scope="col">Latest</th></tr>
      </thead>
      <tbody>
{chr(10).join(rows)}
      </tbody>
    </table>

    <h2 class="section-h">Other {esc(name)} subregions</h2>
    <ul class="link-list">
{other_links}
    </ul>
  </main>
'''
    return {
        "path": base + "index.html",
        "url": base,
        "title": f"{sec['name']} — {name} | Y-Square",
        "desc": (f"{sec['name']} coverage: {sec['scope'][:120].rstrip()} "
                 f"Country-by-country scope for {name.lower()}."),
        "h1": sec["name"],
        "body": body,
        "section": "geopolitics",
    }


def topic_page(topic):
    """Topical hub. Lists its children with their scope, and states plainly
    whether the section is reporting or opinion."""
    is_blog = topic["slug"] == "blog"
    rows = []
    for c in topic["children"]:
        rows.append(f'''        <a class="sec-card" href="{topic["path"]}{c["slug"]}/">
          <h3>{esc(c["name"])}</h3>
          <p class="sec-card-scope">{esc(c["scope"])}</p>
        </a>''')

    if is_blog:
        kinds = "".join(
            f'<span class="type-chip" data-type="{c["id"]}">{esc(c["label"])}</span>'
            for c in N.CONTENT_TYPES)
        note = f'''
    <div class="type-legend">
      <h2 class="section-h">What each label means</h2>
      <p class="table-note">Blog content is opinion, interpretation and
      explanation. It is never event reporting, and it is never presented as
      fact about what happened.</p>
      <div class="mega-types">{kinds}</div>
    </div>'''
    else:
        note = ""

    crumbs = N.breadcrumb([("Home", "/"), (topic["name"], None)])
    body = f'''  <main id="main" class="wrap page">
{crumbs}
    <h1>{esc(topic["name"])}</h1>
    <p class="page-lede">{esc(topic["lede"])}</p>
{note}
    <h2 class="section-h">Sections</h2>
    <div class="sec-grid">
{chr(10).join(rows)}
    </div>
  </main>
'''
    return {
        "path": topic["path"] + "index.html",
        "url": topic["path"],
        "title": f"{topic['name']} | Y-Square",
        "desc": topic["lede"][:155],
        "h1": topic["name"],
        "body": body,
        "section": topic["slug"],
    }


def topic_child_page(topic, child):
    base = f"{topic['path']}{child['slug']}/"
    crumbs = N.breadcrumb([("Home", "/"), (topic["name"], topic["path"]),
                           (child["name"], None)])
    is_blog = topic["slug"] == "blog"
    lead = (f'{esc(child["name"])} is part of {topic["name"].lower()} content: '
            f'analysis, opinion and explainers, not event reporting.'
            if is_blog else
            f'Y-Square coverage of {child["name"].lower()} under {topic["name"].lower()}.')

    body = f'''  <main id="main" class="wrap page">
{crumbs}
    <h1>{esc(child["name"])}</h1>
    <p class="page-lede">{esc(child["scope"])}</p>

    <div class="empty-state">
      <p class="empty-kicker">No verified reports published yet</p>
      <p>{lead} Nothing has been published here that we could attribute to a
      named source, so this page carries no reports rather than a placeholder.</p>
    </div>

    <h2 class="section-h">Related sections</h2>
    <ul class="link-list">
      <li><a href="{topic["path"]}">All {esc(topic["name"])}</a></li>
{chr(10).join(f'      <li><a href="{topic["path"]}{c["slug"]}/">{esc(c["name"])}</a></li>' for c in topic["children"] if c["slug"] != child["slug"])}
    </ul>
  </main>
'''
    return {
        "path": base + "index.html",
        "url": base,
        "title": f"{child['name']} — {topic['name']} | Y-Square",
        "desc": child["scope"][:155],
        "h1": child["name"],
        "body": body,
        "section": topic["slug"],
    }


def geopolitics_index():
    """The section index. Generated from the taxonomy so it cannot list a
    region slug that no longer exists."""
    cards = []
    for r in N.REGIONS:
        n = sum(len(s_["countries"]) for s_ in r["sections"])
        cards.append(f'''        <a class="sec-card" href="{r["path"]}">
          <h3>{esc(r["name"])}</h3>
          <p class="sec-card-scope">{esc(r["lede"])}</p>
          <p class="sec-card-meta">{len(r["sections"])} subregions &middot; {n} countries</p>
        </a>''')
    g = N.TOPICS["global"]
    cards.append(f'''        <a class="sec-card" href="{g["path"]}">
          <h3>{esc(g["name"])}</h3>
          <p class="sec-card-scope">{esc(g["lede"])}</p>
          <p class="sec-card-meta">{len(g["children"])} sections</p>
        </a>''')

    body = f'''  <main id="main" class="wrap page">
{N.breadcrumb([("Home", "/"), ("Geopolitics", None)])}
    <h1>Geopolitics</h1>
    <p class="page-lede">Coverage organised by region, then subregion, then
    country. Each region page lists its subregions; each subregion page lists
    every country Y-Square tracks there and states what it covers.</p>

    <div class="empty-state">
      <p class="empty-kicker">No verified reports published yet</p>
      <p>Event reporting appears here only when it can be attributed to a
      named, checkable source. Nothing has been published yet. The structure
      below is live and navigable.</p>
    </div>

    <h2 class="section-h">Regions</h2>
    <div class="sec-grid">
{chr(10).join(cards)}
    </div>
  </main>
'''
    return {
        "path": "/geopolitics/index.html",
        "url": "/geopolitics/",
        "title": "Geopolitics by Region | Y-Square",
        "desc": ("Geopolitical coverage organised by region, subregion and "
                 "country. Region hubs, subregion country tables and coverage scope."),
        "h1": "Geopolitics",
        "body": body,
        "section": "geopolitics",
    }


def build_all():
    pages = [geopolitics_index()]
    for r in N.REGIONS:
        pages.append(region_page(r))
        for s in r["sections"]:
            pages.append(subregion_page(r, s))
    for t in N.TOPICS.values():
        pages.append(topic_page(t))
        for c in t["children"]:
            pages.append(topic_child_page(t, c))
    return pages


def prune():
    """Delete region/subregion directories the taxonomy no longer defines.

    Without this, a removed subregion leaves a stale directory holding a page
    built from the PREVIOUS taxonomy. That page carries the old header, so it
    still links to countries by their old subregion, and every one of those
    links dangles. The validator catches it, but only after the fact.
    """
    import gen_nav as N
    from gen_lib import ROOT
    removed = []
    want_region = {r["slug"] for r in N.REGIONS} | {"global"}
    base = os.path.join(ROOT, "geopolitics")
    for d in sorted(os.listdir(base)):
        full = os.path.join(base, d)
        if not os.path.isdir(full):
            continue
        if d not in want_region:
            shutil.rmtree(full)
            removed.append("geopolitics/" + d)
            continue
        region = next((r for r in N.REGIONS if r["slug"] == d), None)
        if not region:
            continue
        want_sub = {s_["slug"] for s_ in region["sections"]}
        for sd in sorted(os.listdir(full)):
            sfull = os.path.join(full, sd)
            if os.path.isdir(sfull) and sd not in want_sub:
                shutil.rmtree(sfull)
                removed.append(f"geopolitics/{d}/{sd}")
    return removed


if __name__ == "__main__":
    gone = prune()
    for g in gone:
        print(f"  pruned  {g}")
    pages = build_all()
    total = emit(pages)
    print(f"  {len(pages)} section pages, {total:,} bytes")
    regions = sum(1 for p in pages if p["path"].count("/") == 4 and "geopolitics" in p["path"])
    print(f"  regions={regions}  subregions={sum(1 for p in pages if p['path'].count('/')==5 and 'geopolitics' in p['path'])}  "
          f"topics={sum(1 for p in pages if p['path'].count('/')==3 and 'geopolitics' not in p['path'])}")
