"""Live check: Europe is flat, 'Western Europe' is gone, retired URLs resolve."""
import urllib.error, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36")
follow = urllib.request.build_opener()
bad = []


def get(p):
    rq = urllib.request.Request("https://y-squre.com" + p, headers={"User-Agent": UA})
    try:
        with follow.open(rq, timeout=20) as r:
            return r.status, r.geturl(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, p, ""
    except Exception as e:
        return str(e)[:30], p, ""


print("=== retired European subregions -> /geopolitics/europe/ ===")
for s in ["western-europe", "northern-europe", "southern-europe", "eastern-europe",
          "balkans", "baltics", "central-europe", "nordics", "british-isles"]:
    st, final, _ = get(f"/geopolitics/europe/{s}/")
    good = st == 200 and final.endswith("/geopolitics/europe/")
    if not good:
        bad.append(s)
    print(f"  {'OK  ' if good else 'FAIL'} {st} /geopolitics/europe/{s:18} -> {final.replace('https://y-squre.com','')}")

print("\n=== other rules that pointed into the retired pages ===")
for p, want in [("/geopolitics/united-kingdom/", "/geopolitics/europe/"),
                ("/geopolitics/asia/north-asia/", "/geopolitics/europe/")]:
    st, final, _ = get(p)
    good = st == 200 and final.endswith(want)
    if not good:
        bad.append(p)
    print(f"  {'OK  ' if good else 'FAIL'} {st} {p:36} -> {final.replace('https://y-squre.com','')}")

print("\n=== the Europe page ===")
st, final, body = get("/geopolitics/europe/")
print("  status                :", st)
print("  'Western Europe' found:", "Western Europe" in body, "(must be False)")
import re
h1 = re.search(r"<h1>([^<]*)</h1>", body)
print("  h1                    :", h1.group(1) if h1 else "?")
print("  section headings      :", re.findall(r'class="section-h">([^<]+)<', body))
rows = re.findall(r'<tr id="([a-z-]+)"', body)
print("  country rows          :", rows)
if rows != ["france", "germany", "switzerland", "united-kingdom"]:
    bad.append("europe rows")

print("\n=== the nav: no Western Europe, 11 triggers ===")
_, _, home = get("/")
hdr = home[home.index("<header"):home.index("</header>")]
print("  'Western Europe' in nav:", "Western Europe" in hdr, "(must be False)")
trig = re.findall(r'class="nav-trigger"[^>]*>\s*([^<]+?)\s*<', hdr)
print(f"  triggers              : {len(trig)}")
print("  labels                : " + " | ".join(t.strip() for t in trig))
if len(trig) != 11 or "Western Europe" in hdr:
    bad.append("nav")
import re as _re
_i = hdr.index('id="m-europe"')
_j = hdr.index('id="m-', _i + 20)
print("  m-europe country links:",
      _re.findall(r'<li><a href="(/geopolitics/europe/#[a-z-]+)">([^<]+)</a></li>', hdr[_i:_j]))

print("\n=== the rest of the site ===")
for p in ["/", "/latest/", "/geopolitics/", "/geopolitics/north-america/",
          "/geopolitics/middle-east-north-africa/", "/geopolitics/sub-saharan-africa/",
          "/geopolitics/asia/", "/geopolitics/asia/caucasus/",
          "/geopolitics/oceania-pacific/", "/macro/", "/markets/", "/research/",
          "/blog/", "/search/", "/account/", "/about/", "/contact/", "/privacy/",
          "/404/", "/robots.txt", "/sitemap.xml", "/ads.txt"]:
    st, _, _ = get(p)
    if st != 200:
        bad.append(p)
    print(f"  {'OK  ' if st==200 else 'FAIL'} {st}  {p}")

print("\n=== sitemap must not list the retired pages ===")
_, _, sm = get("/sitemap.xml")
for s in ["western-europe", "northern-europe", "southern-europe", "eastern-europe",
          "balkans", "baltics", "central-europe", "latin-america", "_stage"]:
    if s in sm:
        bad.append(f"sitemap:{s}")
print("  retired slugs present :", [s for s in ["western-europe", "northern-europe",
      "southern-europe", "eastern-europe", "balkans", "baltics", "central-europe",
      "latin-america", "_stage"] if s in sm] or "none")
print("  total URLs            :", sm.count("<loc>"))

print("\n" + "=" * 56)
print("PROBLEMS:", len(bad))
for b in bad:
    print("   ", b)
print("ALL GREEN" if not bad else "NOT CLEAN")
