"""Verify the Latin America & Caribbean withdrawal: nav gone, pages deleted,
301s resolving, nothing else broken."""
import json, re, urllib.error, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36")


class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a):
        return None


nr = urllib.request.build_opener(NoRedir)
follow = urllib.request.build_opener()
def slugify(name):
    import unicodedata
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    n = n.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")


bad = []


def raw(p):
    rq = urllib.request.Request("https://y-squre.com" + p, headers={"User-Agent": UA})
    try:
        with nr.open(rq, timeout=20) as r:
            return r.status, r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "")
    except Exception as e:
        return str(e)[:30], ""


def code(p):
    rq = urllib.request.Request("https://y-squre.com" + p, headers={"User-Agent": UA})
    try:
        with follow.open(rq, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)[:30]


print("=== the deleted pages must 301 to /geopolitics/ ===")
for p in ["/geopolitics/latin-america/", "/geopolitics/latin-america/south-america/",
          "/geopolitics/latin-america/central-america-latam/",
          "/geopolitics/latin-america/caribbean-latam/",
          "/geopolitics/north-america/central-america/", "/geopolitics/north-america/caribbean/"]:
    st, loc = raw(p)
    good = st == 301 and loc.endswith("/geopolitics/")
    if not good:
        bad.append(p)
    print(f"  {'OK  ' if good else 'FAIL'} {st} {p:48} -> {loc.replace('https://y-squre.com','') or '(none)'}")

print("\n=== the surviving 6 regions must be 200 ===")
for p in ["/geopolitics/", "/geopolitics/north-america/", "/geopolitics/europe/",
          "/geopolitics/europe/western-europe/", "/geopolitics/middle-east-north-africa/",
          "/geopolitics/middle-east-north-africa/gulf/", "/geopolitics/sub-saharan-africa/",
          "/geopolitics/sub-saharan-africa/west-africa/", "/geopolitics/asia/",
          "/geopolitics/asia/south-asia/", "/geopolitics/oceania-pacific/"]:
    c = code(p)
    if c != 200:
        bad.append(p)
    print(f"  {'OK  ' if c==200 else 'FAIL'} {c}  {p}")

print("\n=== the rest of the site ===")
for p in ["/", "/latest/", "/macro/", "/markets/", "/research/", "/blog/",
          "/search/", "/account/", "/about/", "/contact/", "/privacy/", "/terms/",
          "/disclaimer/", "/editorial-policy/", "/advertising/", "/404/",
          "/robots.txt", "/sitemap.xml", "/ads.txt"]:
    c = code(p)
    if c != 200:
        bad.append(p)
    print(f"  {'OK  ' if c==200 else 'FAIL'} {c}  {p}")

print("\n=== earlier redirects must still work ===")
for old, want in [("/geopolitics/africa/", "/geopolitics/sub-saharan-africa/"),
                  ("/geopolitics/middle-east/", "/geopolitics/middle-east-north-africa/"),
                  ("/geopolitics/pacific/", "/geopolitics/oceania-pacific/"),
                  ("/geopolitics/united-kingdom/", "/geopolitics/europe/western-europe/"),
                  ("/geopolitics/europe/nordics/", "/geopolitics/europe/northern-europe/"),
                  ("/geopolitics/asia/west-asia/", "/geopolitics/asia/caucasus/")]:
    st, loc = raw(old)
    good = st == 301 and loc.endswith(want)
    if not good:
        bad.append(old)
    print(f"  {'OK  ' if good else 'FAIL'} {st} {old:34} -> {loc.replace('https://y-squre.com','')}")

print("\n=== nav must no longer mention Latin America, and must have 11 triggers ===")
rq = urllib.request.Request("https://y-squre.com/", headers={"User-Agent": UA})
with follow.open(rq, timeout=20) as r:
    home = r.read().decode("utf-8", "replace")
hdr = home[home.index("<header"):home.index("</header>")]
triggers = re.findall(r'class="nav-trigger"[^>]*>\s*([^<]+?)\s*<', hdr)
print("  'Latin America' in nav :", "Latin America" in hdr, "(must be False)")
print("  'latin-america' in nav :", "latin-america" in hdr, "(must be False)")
print(f"  triggers rendered      : {len(triggers)}")
print("  labels: " + " | ".join(t.strip() for t in triggers))
if "Latin America" in hdr or "latin-america" in hdr or len(triggers) != 11:
    bad.append("nav")

print("\n=== every country anchor in the surviving taxonomy ===")
geo = json.load(open(r"C:\Users\ffaay\y-squre-site\assets\data\geography.json", encoding="utf-8"))
tot = miss = 0
for r in geo["regions"]:
    for sec in r["sections"]:
        page = r["path"] + sec["slug"] + "/"
        c = code(page)
        if c != 200:
            miss += len(sec["countries"])
            bad.append(page)
            continue
        rq = urllib.request.Request("https://y-squre.com" + page, headers={"User-Agent": UA})
        with follow.open(rq, timeout=20) as resp:
            body = resp.read().decode("utf-8", "replace")
        for co in sec["countries"]:
            tot += 1
            cid = co.get("slug") or slugify(co["name"])
            if f'id="{cid}"' not in body:
                miss += 1
                bad.append(f"{page}#{cid}")
print(f"  {tot-miss}/{tot} country anchors resolve")

print("\n" + "=" * 58)
print("PROBLEMS:", len(bad))
for b in bad[:15]:
    print("   ", b)
print("ALL GREEN" if not bad else "NOT CLEAN")
