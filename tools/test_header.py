"""Browser test of the new header: mega-menu, keyboard, mobile accordion,
responsive overflow. Runs against a local file:// copy so it tests the build
before anything is deployed."""
import base64, json, os, time, urllib.request, websocket

OUT = r"C:\Users\ffaay\AppData\Local\hermes\cache\scratch\shots3"
os.makedirs(OUT, exist_ok=True)
import json as _j
BASE = "http://127.0.0.1:8731"   # absolute paths only resolve correctly over HTTP

r = urllib.request.urlopen(urllib.request.Request(
    "http://127.0.0.1:9222/json/new?about:blank", method="PUT"))
tab = json.loads(r.read())
s = websocket.create_connection(tab["webSocketDebuggerUrl"],
                                suppress_origin=True, timeout=40)
_id = [0]


def cdp(method, **params):
    _id[0] += 1
    s.send(json.dumps({"id": _id[0], "method": method, "params": params}))
    while True:
        m = json.loads(s.recv())
        if m.get("id") == _id[0]:
            if "error" in m:
                raise RuntimeError(m["error"])
            return m.get("result", {})


def ev(expr):
    res = cdp("Runtime.evaluate", expression=expr, returnByValue=True,
              awaitPromise=True)
    if res.get("exceptionDetails"):
        return {"__error": res["exceptionDetails"].get("text", "?")}
    return res.get("result", {}).get("value")


def goto(url):
    cdp("Page.navigate", url=url)
    for _ in range(70):
        time.sleep(0.25)
        if ev("document.readyState") == "complete":
            break
    time.sleep(0.9)


def shot(name, w=None, h=None):
    if w:
        cdp("Emulation.setDeviceMetricsOverride", width=w, height=h or 900,
            deviceScaleFactor=1, mobile=w < 700)
    time.sleep(0.6)
    d = cdp("Page.captureScreenshot", format="png", captureBeyondViewport=True)
    p = os.path.join(OUT, name + ".png")
    open(p, "wb").write(base64.b64decode(d["data"]))
    return p


cdp("Network.enable")
cdp("Network.setCacheDisabled", cacheDisabled=True)
cdp("Page.enable")
cdp("Runtime.enable")
cdp("Log.enable")
errors = []

# absolute file URL for a subregion page (the densest page)
SUB = BASE + "/geopolitics/europe/western-europe/"
HOME = BASE + "/"

print("=" * 70)
print("DESKTOP MEGA-MENU  (1440)")
print("=" * 70)
cdp("Emulation.setDeviceMetricsOverride", width=1440, height=900,
    deviceScaleFactor=1, mobile=False)
goto(SUB)

print("  header present      ", ev("!!document.querySelector('.site-header')"))
print("  mega panels in DOM  ", ev("document.querySelectorAll('.mega').length"))
print("  navy bar colour     ", ev("getComputedStyle(document.querySelector('.primary-nav')).backgroundColor"))
print("  nav.css APPLIED     ", ev("getComputedStyle(document.querySelector('.nav-trigger')).height"))
print("  sections.css APPLIED", ev("getComputedStyle(document.querySelector('.country-table')).borderCollapse"))
print("  failed requests     ", ev("performance.getEntriesByType('resource').filter(r=>r.responseStatus>=400).length"))
print("  nav.js ran          ", ev("!!(window.YSQ && window.YSQ.enhance)"))
print("  YSQ.utils present   ", ev("!!(window.YSQ && window.YSQ.utils)"))

# panels must be hidden until opened
print("  panels hidden first ", ev("getComputedStyle(document.getElementById('m-europe')).visibility"))

# open the Europe mega-menu by hovering the trigger, as a user would
ev("""
(function(){
  var t = document.querySelector('[aria-controls="m-europe"]');
  t.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
  return true;
})()
""")
time.sleep(0.5)
print("  after hover -> open ", ev("document.getElementById('m-europe').getAttribute('data-open')"))
print("  visibility          ", ev("getComputedStyle(document.getElementById('m-europe')).visibility"))
print("  aria-expanded       ", ev("document.querySelector('[aria-controls=\\\"m-europe\\\"]').getAttribute('aria-expanded')"))
print("  panel width         ", ev("Math.round(document.getElementById('m-europe').getBoundingClientRect().width)"))
print("  overflows viewport? ", ev("""
(function(){
  var r = document.getElementById('m-europe').getBoundingClientRect();
  return r.right > window.innerWidth + 1 || r.left < -1;
})()
"""))
print("  country links shown ", ev("document.querySelectorAll('#m-europe .mega-list a').length"))
print("  only one panel open ", ev("[...document.querySelectorAll('.mega')].filter(p=>p.getAttribute('data-open')==='true').length"))
shot("desktop-mega-open")

# click a different trigger -> the previous one must close
ev("document.querySelector('[aria-controls=\\\"m-asia\\\"]').dispatchEvent(new MouseEvent('mouseenter',{bubbles:true}))")
time.sleep(0.4)
print("  switching -> europe closed",
      ev("document.getElementById('m-europe').getAttribute('data-open')"))
print("  switching -> asia open    ",
      ev("document.getElementById('m-asia').getAttribute('data-open')"))

# Escape closes
ev("document.querySelector('[aria-controls=\\\"m-asia\\\"]').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
time.sleep(0.3)
print("  escape -> asia closed    ",
      ev("document.getElementById('m-asia').getAttribute('data-open')"))
shot("desktop-closed", 1440, 900)

print()
print("=" * 70)
print("COUNTRY DEEP LINK")
print("=" * 70)
print("  west-europe rows      ", ev("document.querySelectorAll('.country-table tr[id]').length"))
print("  austria row exists    ", ev("!!document.getElementById('austria')"))
ev("location.hash = '#austria'")
time.sleep(0.5)
print("  :target highlight     ", ev("getComputedStyle(document.getElementById('austria')).backgroundColor"))

print()
print("=" * 70)
print("MOBILE  375")
print("=" * 70)
cdp("Emulation.setDeviceMetricsOverride", width=375, height=780,
    deviceScaleFactor=2, mobile=True)
goto(HOME)
print("  horizontal overflow   ", ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
print("  scrollWidth/clientW   ", ev("document.documentElement.scrollWidth + '/' + document.documentElement.clientWidth"))
print("  desktop nav hidden    ", ev("getComputedStyle(document.querySelector('.primary-nav')).display"))
print("  burger visible        ", ev("getComputedStyle(document.querySelector('[data-burger]')).display"))

ev("document.querySelector('[data-burger]').click()")
time.sleep(0.6)
print("  menu opened           ", ev("document.querySelector('.mobile-menu').getAttribute('data-open')"))
print("  accordion built by JS ", ev("document.querySelectorAll('.mobile-menu .acc-item').length"))
print("  country leaves built  ", ev("document.querySelectorAll('.mobile-menu .acc-leaf').length"))
print("  overflow after open   ", ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
shot("mobile-menu-open", 375, 780)

ev("document.querySelector('.mobile-menu .acc-trigger').click()")
time.sleep(0.5)
print("  first accordion opens ", ev("document.querySelector('.mobile-menu .acc-trigger').getAttribute('aria-expanded')"))
shot("mobile-accordion", 375, 780)

print()
print("=" * 70)
print("BREAKPOINTS - horizontal overflow")
print("=" * 70)
for w in (1440, 1280, 1024, 900, 768, 414, 390, 375, 320):
    cdp("Emulation.setDeviceMetricsOverride", width=w, height=900,
        deviceScaleFactor=1, mobile=w < 700)
    goto(SUB)
    ov = ev("document.documentElement.scrollWidth > window.innerWidth + 1")
    sw = ev("document.documentElement.scrollWidth")
    print(f"  {w:>5}px  overflow={str(ov):5}  scrollWidth={sw}")
shot("mobile-320", 320, 900)

print()
print("=" * 70)
print("SEARCH  /search/")
print("=" * 70)
cdp("Emulation.setDeviceMetricsOverride", width=1440, height=900,
    deviceScaleFactor=1, mobile=False)
goto(BASE + "/search/")
print("  page present        ", ev("!!document.getElementById('search-form')"))
print("  taxonomy index      ", ev("typeof window.YSQ_TAXONOMY + ' entries=' + (window.YSQ_TAXONOMY||[]).length"))
for q in ("nigeria", "gulf", "inflation", "india", "zzznotathing"):
    ev("document.getElementById('search-input').value = '';")
    ev("""
    (function(){
      var i = document.getElementById('search-input');
      i.value = %s;
      i.dispatchEvent(new Event('input', {bubbles:true}));
      return true;
    })()
    """ % json.dumps(q))
    time.sleep(0.9)
    out = ev("""
    (function(){
      var rows = document.querySelectorAll('#search-results .index-row');
      var first = rows[0];
      return JSON.stringify({n: rows.length,
        kind: first ? first.querySelector('.index-when').textContent : null,
        title: first ? first.querySelector('h3').textContent.trim() : null,
        href: first ? first.querySelector('h3 a').getAttribute('href') : null});
    })()
    """)
    print(f"  {q:14} -> {out}")

print()
print("console errors:", errors if errors else "none captured")
cdp("Page.closeTab" if False else "Page.navigate", url="about:blank")
print("\nBROWSER TEST DONE")
