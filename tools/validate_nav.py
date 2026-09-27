"""Validate the header/taxonomy build: anchors, header presence, dead links."""
import os, re, json, sys

R = r"C:\Users\ffaay\y-squre-site"

pages = []
for dp, dn, fs in os.walk(R):
    if ".git" in dp or "docs" in dp:
        continue
    for f in fs:
        if f == "index.html":
            pages.append("/" + os.path.relpath(os.path.join(dp, f), R)
                         .replace("\\", "/").replace("/index.html", "/"))

hrefs, ids = set(), set()
missing_files = []
for p in pages:
    # p is a URL ("/about/"); the file it came from needs index.html re-appended.
    rel = p.lstrip("/")
    fp = os.path.join(R, rel.replace("/", os.sep))
    fp = fp if rel.endswith(".html") else os.path.join(fp, "index.html")
    t = open(fp, encoding="utf-8").read()
    for m in re.finditer(r'href="(/geopolitics/[^"#]+/)#([\w-]+)"', t):
        hrefs.add(m.group(1) + m.group(2))
    for m in re.finditer(r'<tr id="([\w-]+)"', t):
        ids.add(p + m.group(1))
    # every internal link must resolve to a real file
    for m in re.finditer(r'href="(/[^"#?]+)', t):
        u = m.group(1)
        if u.startswith(("/assets", "/search", "/account")):
            continue
        fp = os.path.join(R, u.lstrip("/").replace("/", os.sep))
        if u.endswith("/"):
            fp = os.path.join(fp, "index.html")
        if not os.path.exists(fp):
            missing_files.add((p, u)) if isinstance(missing_files, set) else missing_files.append((p, u))

dangling = sorted(hrefs - ids)
orphans = sorted(ids - hrefs)

print(f"pages                 {len(pages)}")
print(f"country anchor links  {len(hrefs)}")
print(f"country table rows    {len(ids)}")
print(f"dangling anchors      {len(dangling)}  {dangling[:4] if dangling else ''}")
print(f"orphan row ids        {len(orphans)}  {orphans[:4] if orphans else ''}")
print(f"broken internal links {len(missing_files)}")
for p, u in sorted(missing_files)[:10]:
    print(f"    {u}   (linked from {p})")

# header integrity on a representative page
sample = "/geopolitics/europe/western-europe/index.html"
t = open(os.path.join(R, sample.lstrip("/").replace("/", os.sep)), encoding="utf-8").read()
trig = set(re.findall(r'aria-controls="(m-[\w-]+)"', t))
pans = set(re.findall(r'<div class="mega" id="(m-[\w-]+)"', t))
print(f"\ntriggers {len(trig)}  panels {len(pans)}  "
      f"{'MATCH' if trig == pans else 'MISMATCH ' + str(trig ^ pans)}")
print(f"skip-link occurrences  {t.count('skip-link')} (must be 1)")
print(f"nav.css linked         {'/assets/css/nav.css' in t}")
print(f"nav.js linked          {'/assets/js/nav.js' in t}")
print(f"dupe <h1>              {t.count('<h1>')} (must be 1)")
print(f"aria-expanded on every trigger: "
      f"{t.count('aria-expanded=') >= len(trig)}")

ok = (not dangling and not missing_files and trig == pans
      and t.count("skip-link") == 1 and t.count("<h1>") == 1)
print("\n" + ("VALIDATION PASSED" if ok else "VALIDATION FAILED"))
sys.exit(0 if ok else 1)
