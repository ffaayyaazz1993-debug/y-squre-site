"""Generate the JSON feeds the Android app consumes.

The app fetches these at runtime, so a new article appears in the app without
an app update. Two files:

  assets/data/articles.json   every article the site has published, with the
                              region/subregion taxonomy a Global News client
                              filters by
  assets/data/taxonomy.json   the region > subregion > country tree plus the
                              section list, so the app can build its dropdown
                              from the same data the site nav uses

Both are derived from the built HTML and geography.json, so they cannot drift
from the pages they describe.
"""
import sys, os, json, re, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_nav as N
from gen_lib import ROOT, write

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, "..", "assets", "data", "geography.json")

META = [
    ("title", r"<title>(.*?)</title>"),
    ("desc", r'<meta name="description" content="(.*?)"'),
    ("published", r'<meta property="article:published_time" content="(.*?)"'),
    ("ctype", r'class="ctype ctype-(\w+)"'),
    ("h1", r"<h1>(.*?)</h1>"),
    ("deck", r'<p class="article-deck">(.*?)</p>'),
]


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def prose_html(path):
    """Inner HTML of the article's prose block, extracted by div depth.

    The body is shipped to the app as HTML so headings, lists and emphasis
    survive; the app renders it with its own typography rather than loading the
    site's page chrome.
    """
    s = open(path, encoding="utf-8").read()
    start = s.find('<div class="prose" data-prose>')
    if start < 0:
        return ""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            # m.start() is relative to s[start:], so the inner block runs to
            # start + m.start() in the full string.
            inner = s[start:start + m.start()]
            gt = inner.find(">")
            return inner[gt + 1:].strip()
    return ""

def parse_article(path):
    s = open(path, encoding="utf-8").read()
    out = {}
    for key, pat in META:
        m = re.search(pat, s, re.S)
        out[key] = strip_tags(m.group(1)) if m else ""
    # Paths from glob are absolute; the feed carries site-relative URLs.
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    out["url"] = "/" + rel
    out["body"] = prose_html(path)
    # Region/subregion from the geopolitics path:
    #   geopolitics/<region>/<subregion?>/<...>/file.html
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    m = re.search(r"geopolitics/([^/]+)(?:/([^/]+))?/", rel)
    if m:
        out["region"] = m.group(1)
        out["subregion"] = m.group(2) or ""
        out["section"] = "global"
        return out
    # Everything else is filed under its top directory.
    out["region"] = ""
    out["subregion"] = ""
    out["section"] = rel.split("/")[0]
    return out


def taxonomy():
    g = json.load(open(GEO, encoding="utf-8"))
    regions = []
    for r in N.REGIONS:
        regions.append({
            "slug": r["slug"],
            "name": r["name"],
            "path": r["path"],
            "lede": r.get("lede", ""),
            "sections": [
                {
                    "slug": s["slug"],
                    "name": s["name"],
                    "path": f"{r['path']}{s['slug']}/",
                    "countries": [
                        {"name": c["name"], "anchor": c.get("anchor", "")}
                        for c in s.get("countries", [])
                    ],
                }
                for s in r.get("sections", [])
            ],
        })
    sections = [
        {"slug": t["slug"], "name": t["name"], "path": t["path"]}
        for t in g["topics"]
    ]
    return {"regions": regions, "sections": sections}


def main():
    arts = []
    for pat in ("geopolitics/**/*.html", "research/**/*.html",
                "blog/**/*.html", "markets/**/*.html",
                "business/**/*.html", "crypto/**/*.html"):
        for p in glob.glob(os.path.join(ROOT, pat), recursive=True):
            if os.path.basename(p) == "index.html":
                continue
            a = parse_article(p)
            if a.get("h1"):
                arts.append(a)
    arts.sort(key=lambda a: a.get("published", ""), reverse=True)
    payload = {"generated": "build", "articles": arts}
    write("assets/data/articles.json", json.dumps(payload, indent=1,
                                                  ensure_ascii=False))
    tax = taxonomy()
    write("assets/data/taxonomy.json", json.dumps(tax, indent=1,
                                                 ensure_ascii=False))
    print(f"articles.json: {len(arts)} articles")
    print(f"taxonomy.json: {len(tax['regions'])} regions "
          f"{len(tax['sections'])} sections")


if __name__ == "__main__":
    main()
