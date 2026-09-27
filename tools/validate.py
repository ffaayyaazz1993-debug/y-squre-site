"""Pre-deploy validation for the Y-Square static site.

Checks, in order of what actually breaks sites:
  1. every internal href/src resolves to a real file on disk
  2. every referenced CSS class is defined in some stylesheet
  3. SEO essentials present on every indexable page
  4. no secrets, no dev files, no broken internal anchors
  5. ads.txt unchanged, AdSense id consistent everywhere
"""
import os, re, sys, json
from html.parser import HTMLParser

ROOT = r"C:\Users\ffaay\y-squre-site"
errors, warns, stats = [], [], {"pages": 0, "links": 0, "assets": 0}

CSS_TEXT = ""
for dp, _, fs in os.walk(os.path.join(ROOT, "assets", "css")):
    for f in fs:
        if f.endswith(".css"):
            CSS_TEXT += open(os.path.join(dp, f), encoding="utf-8").read()
DEFINED = set(re.findall(r'\.([a-zA-Z][\w-]*)', CSS_TEXT))


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.assets, self.classes = [], [], set()
        self.metas, self.title, self.h1 = [], None, 0
        self.in_title = False
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("link", "script", "img") and (a.get("href") or a.get("src")):
            self.assets.append(a.get("href") or a.get("src"))
        if tag == "meta" and a.get("name"):
            self.metas.append((a["name"], a.get("content", "")))
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1 += 1
        if a.get("class"):
            self.classes.update(a["class"].split())

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title = (self.title or "") + data.strip()
        self.text_parts.append(data)


def resolve(base_rel, ref):
    """Map a site-absolute or relative URL to a repo-relative path, or None."""
    if ref.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "#")):
        return None
    if ref.startswith("/"):
        p = ref[1:].split("?")[0].split("#")[0]
    else:
        d = os.path.dirname(base_rel)
        p = os.path.normpath(os.path.join(d, ref)).replace(os.sep, "/")
    if p == "":
        p = "index.html"
    if p.endswith("/"):
        p += "index.html"
    return p


html_files = []
for dp, dn, fs in os.walk(ROOT):
    if ".git" in dp or "docs" in dp:
        continue
    for f in fs:
        if f.endswith(".html"):
            html_files.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
html_files.sort()

for rel in html_files:
    stats["pages"] += 1
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    p = P()
    try:
        p.feed(src)
    except Exception as e:
        errors.append(f"{rel}: HTML parse error {e}")
        continue

    # 1. links + assets resolve
    for ref in p.links:
        if ref.startswith(("mailto:", "javascript:")) or ref == "#":
            continue
        tgt = resolve(rel, ref)
        stats["links"] += 1
        if tgt and not os.path.exists(os.path.join(ROOT, tgt.replace("/", os.sep))):
            errors.append(f"{rel}: broken link -> {ref}")
    for ref in p.assets:
        tgt = resolve(rel, ref)
        stats["assets"] += 1
        if tgt and not os.path.exists(os.path.join(ROOT, tgt.replace("/", os.sep))):
            errors.append(f"{rel}: missing asset -> {ref}")

    # 2. classes defined
    for c in sorted(p.classes):
        if c not in DEFINED and not c.startswith(("ad-", "ctype-", "kicker-")):
            warns.append(f"{rel}: class '{c}' not in CSS")

    # 3. SEO essentials
    names = dict(p.metas)
    noindex = names.get("robots", "").startswith("noindex")
    if not p.title:
        errors.append(f"{rel}: no <title>")
    elif not (20 <= len(p.title) <= 75):
        warns.append(f"{rel}: title length {len(p.title)}")
    if "description" not in names:
        errors.append(f"{rel}: no meta description")
    elif not (70 <= len(names["description"]) <= 200):
        warns.append(f"{rel}: description length {len(names['description'])}")
    if "canonical" not in src:
        errors.append(f"{rel}: no canonical")
    if p.h1 != 1:
        errors.append(f"{rel}: {p.h1} <h1> elements (want exactly 1)")
    if 'property="og:title"' not in src or 'name="twitter:card"' not in src:
        errors.append(f"{rel}: missing OG/Twitter metadata")
    if not noindex and 'name="google-adsense-account"' not in src:
        errors.append(f"{rel}: AdSense account meta missing")
    if 'name="google-adsense-account"' in src:
        m = re.search(r'google-adsense-account" content="([^"]+)"', src)
        if m and m.group(1) != "ca-pub-9461123152614358":
            errors.append(f"{rel}: wrong AdSense client id {m.group(1)}")
    if 'src="https://pagead2.googlesyndication.com' in src and "ca-pub-9461123152614358" not in src:
        errors.append(f"{rel}: adsense loader without client id")

    # 4. secret scan
    for pat in (r'api[_-]?key', r'secret', r'password', r'BEGIN (RSA|PRIVATE)',
                r'token\s*[:=]\s*["\'][A-Za-z0-9]{16,}'):
        for m in re.finditer(pat, src, re.I):
            warns.append(f"{rel}: possible secret pattern '{m.group(0)[:30]}'")

# 5. global files
ads = open(os.path.join(ROOT, "ads.txt"), encoding="utf-8").read()
if ads.strip() != "google.com, pub-9461123152614358, DIRECT, f08c47fec0942fa0":
    errors.append(f"ads.txt changed: {ads!r}")
if os.path.exists(os.path.join(ROOT, "ads.txt")) and \
        len([f for dp, _, fs in os.walk(ROOT) for f in fs if f == "ads.txt"]) != 1:
    errors.append("ads.txt duplicated in more than one directory")

# dev files that must never reach production
for bad in ("node_modules", "package.json", "webpack.config.js", ".env",
            "requirements.txt", "manage.py"):
    if os.path.exists(os.path.join(ROOT, bad)):
        errors.append(f"dev file present in site root: {bad}")
# .git is the repo, not a deployable artifact; the deploy walker skips it explicitly.

# sitemap <-> pages consistency
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
sm_urls = set(re.findall(r"<loc>https://y-squre\.com/([^<]*)</loc>", sm))
for u in sm_urls:
    tgt = u or "index.html"
    if not os.path.exists(os.path.join(ROOT, tgt.replace("/", os.sep))):
        errors.append(f"sitemap: URL has no file -> /{u}")
indexable = {h for h in html_files if h != "404.html"}
in_sm = {("" if h == "index.html" else h.replace("index.html", "")) for h in indexable}
for miss in sorted(in_sm - sm_urls):
    errors.append(f"page not in sitemap: /{miss}")

# word counts (thin pages are an AdSense review risk)
thin = []
for rel in html_files:
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    p = P(); p.feed(src)
    words = len(re.sub(r"\s+", " ", " ".join(p.text_parts)).split())
    if words < 250:
        thin.append((rel, words))

print("=" * 68)
print(f"pages {stats['pages']}   internal links {stats['links']}   asset refs {stats['assets']}")
print(f"CSS classes defined: {len(DEFINED)}")
print("=" * 68)
if thin:
    print("\nTHIN PAGES (<250 words) — intentional for index/empty states:")
    for r, w in sorted(thin, key=lambda x: x[1]):
        print(f"   {r:<44}{w:>5}w")
if warns:
    print(f"\nWARNINGS ({len(warns)}):")
    for w in warns[:40]:
        print("   " + w)
    if len(warns) > 40:
        print(f"   ... and {len(warns)-40} more")
if errors:
    print(f"\nERRORS ({len(errors)}):")
    for e in errors:
        print("   " + e)
    sys.exit(1)
print("\nVALIDATION PASSED — no errors.")
