"""Final live verification, testing each path for what it SHOULD do rather than
assuming 404. A retired path that 301s to a live page is correct, not a failure.
"""
import urllib.error, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36")


class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a):
        return None


nr = urllib.request.build_opener(NoRedir)
follow = urllib.request.build_opener()
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


print("=== retired paths: must 301 to a LIVE page ===")
REDIRECTS = {
    "/geopolitics/africa/": "/geopolitics/sub-saharan-africa/",
    "/geopolitics/middle-east/": "/geopolitics/middle-east-north-africa/",
    "/geopolitics/pacific/": "/geopolitics/oceania-pacific/",
    "/geopolitics/united-kingdom/": "/geopolitics/europe/western-europe/",
    "/geopolitics/europe/nordics/": "/geopolitics/europe/northern-europe/",
    "/geopolitics/europe/british-isles/": "/geopolitics/europe/western-europe/",
    "/geopolitics/asia/west-asia/": "/geopolitics/asia/caucasus/",
    "/geopolitics/asia/north-asia/": "/geopolitics/europe/eastern-europe/",
    "/geopolitics/north-america/central-america/": "/geopolitics/latin-america/central-america-latam/",
    "/geopolitics/north-america/caribbean/": "/geopolitics/latin-america/caribbean-latam/",
}
for old, want in REDIRECTS.items():
    st, loc = raw(old)
    target_ok = code(want) == 200
    good = st == 301 and loc.endswith(want) and target_ok
    if not good:
        bad.append(old)
    print(f"  {'OK  ' if good else 'FAIL'} {st} {old:44} -> {loc.replace('https://y-squre.com','') or '(none)'}  [target {'live' if target_ok else 'DEAD'}]")

print("\n=== fully removed paths: must 404 ===")
for p in ["/macro/currencies-macro/", "/insights/", "/assets/js/navigation.js",
          "/assets/css/style.css", "/privacy.html"]:
    c = code(p)
    if c != 404:
        bad.append(p)
    print(f"  {'OK  ' if c==404 else 'FAIL'} {c}  {p:44} {'gone' if c==404 else 'unexpected'}")

print("\n=== live routes: must 200 ===")
LIVE = ["/", "/latest/", "/geopolitics/", "/geopolitics/north-america/",
        "/geopolitics/latin-america/", "/geopolitics/latin-america/south-america/",
        "/geopolitics/latin-america/central-america-latam/",
        "/geopolitics/latin-america/caribbean-latam/",
        "/geopolitics/europe/", "/geopolitics/europe/western-europe/",
        "/geopolitics/europe/northern-europe/", "/geopolitics/europe/eastern-europe/",
        "/geopolitics/asia/", "/geopolitics/asia/caucasus/",
        "/geopolitics/asia/south-asia/", "/geopolitics/asia/southeast-asia/",
        "/geopolitics/middle-east-north-africa/", "/geopolitics/middle-east-north-africa/gulf/",
        "/geopolitics/sub-saharan-africa/", "/geopolitics/sub-saharan-africa/west-africa/",
        "/geopolitics/oceania-pacific/", "/macro/", "/macro/currencies/", "/markets/",
        "/markets/currencies/", "/research/", "/blog/", "/search/", "/account/",
        "/about/", "/contact/", "/privacy/", "/terms/", "/disclaimer/",
        "/editorial-policy/", "/advertising/", "/404/",
        "/robots.txt", "/sitemap.xml", "/ads.txt",
        "/assets/css/nav.css", "/assets/css/sections.css", "/assets/css/search.css",
        "/assets/js/nav.js", "/assets/js/search.js", "/assets/data/geography.json"]
n_ok = 0
for p in LIVE:
    c = code(p)
    good = c == 200
    n_ok += good
    if not good:
        bad.append(p)
        print(f"  FAIL {c}  {p}")
print(f"  {n_ok}/{len(LIVE)} live routes return 200")

print("\n=== country anchors: sample the whole taxonomy ===")
import json, re
geo = json.load(open(r"C:\Users\ffaay\y-squre-site\assets\data\geography.json", encoding="utf-8"))
checked = miss = 0
for r in geo["regions"]:
    for sec in r["sections"]:
        page = f"/{r['top']}/{r['slug']}/{sec['slug']}/"
        c = code(page)
        if c != 200:
            miss += 1
            bad.append(page)
            continue
        rq = urllib.request.Request("https://y-squre.com" + page, headers={"User-Agent": UA})
        try:
            with follow.open(rq, timeout=20) as resp:
                body = resp.read().decode("utf-8", "replace")
        except Exception:
            miss += 1
            continue
        for co in sec["countries"]:
            checked += 1
            if f'id="{co["slug"]}"' not in body:
                miss += 1
                bad.append(f"{page}#{co['slug']}")
print(f"  {checked - miss}/{checked} country anchors resolve")

print("\n" + "=" * 60)
print("PROBLEMS:", len(bad))
for b in bad[:20]:
    print("   ", b)
print("ALL GREEN" if not bad else "NOT CLEAN")
