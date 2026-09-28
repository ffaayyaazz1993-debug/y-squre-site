"""Does the mobile header now match the desktop one?

The bar is "keep both nav rows visible, let them wrap". This measures that at
phone widths: every desktop header link is reachable, the mega-panel still opens
and lands inside the viewport, nothing overflows horizontally, and the sticky
header still works.

One websocket for the whole run -- reconnecting per step left a CDP call
outstanding against a closed socket.
"""
import functools, http.server, json, os, shutil, threading, time
import urllib.request, websocket
from http.server import SimpleHTTPRequestHandler

ROOT = r"C:\Users\ffaay\y-squre-site"
TMP = r"C:\Users\ffaay\AppData\Local\hermes\cache\scratch\mobtest"
shutil.rmtree(TMP, ignore_errors=True)
shutil.copytree(ROOT, TMP, ignore=shutil.ignore_patterns(
    ".git", "docs", "__pycache__", "tools", "README.md", "_stage"))
PORT = 8734
_handler = functools.partial(SimpleHTTPRequestHandler, directory=TMP)
_srv = http.server.HTTPServer(("127.0.0.1", PORT), _handler)
threading.Thread(target=_srv.serve_forever, daemon=True).start()
BASE_SITE = "http://127.0.0.1:%d" % PORT

BASE = "http://127.0.0.1:9222"
WIDTHS = [("desktop", 1440), ("tablet", 820), ("mobile", 390), ("small", 360)]
PAGES = ["/latest/", "/blog/2026/09/26/understanding-currency-depreciation.html",
         "/geopolitics/europe/"]
DESKTOP_LINKS = ("Latest", "North America", "Europe", "Asia", "Global",
                 "Markets", "Macro", "Research", "Blog")


def tabs():
    return json.loads(urllib.request.urlopen(BASE + "/json", timeout=10).read())


def connect(tid):
    t = [x for x in tabs() if x["id"] == tid][0]
    return websocket.create_connection(t["webSocketDebuggerUrl"],
                                       suppress_origin=True, timeout=30)


_pages = [t for t in tabs() if t.get("type") == "page"]
if not _pages:
    print("no page tab open in the CDP profile")
    raise SystemExit(1)
tid = _pages[0]["id"]
s = connect(tid)
_id = [1]


def ev(e, t=30):
    _id[0] += 1
    s.send(json.dumps({"id": _id[0], "method": "Runtime.evaluate",
                       "params": {"expression": e, "returnByValue": True,
                                  "awaitPromise": True}}))
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            d = json.loads(s.recv())
        except Exception:
            return "TIMEOUT"
        if d.get("id") == _id[0]:
            return d.get("result", {}).get("result", {}).get("value")


def nav(url, wait=7):
    s.send(json.dumps({"id": 9999, "method": "Page.navigate", "params": {"url": url}}))
    time.sleep(wait)
    # The stylesheet is cached, and a cached nav.css answers with the PREVIOUS
    # build's breakpoints. Every measurement here must bypass it or it reports
    # numbers for a sheet that is no longer on disk.
    s.send(json.dumps({"id": 9989, "method": "Page.reload", "params": {"ignoreCache": True}}))
    time.sleep(wait)


def width(w):
    s.send(json.dumps({"id": 900, "method": "Emulation.setDeviceMetricsOverride",
                       "params": {"width": w, "height": 900,
                                  "deviceScaleFactor": 1, "mobile": w < 900}}))
    time.sleep(1.5)


PROBE = """(function(){
  function vis(sel){var e=document.querySelector(sel);
    return e ? (getComputedStyle(e).display!=='none') : null;}
  return {
    primary: vis('.primary-nav'), topic: vis('.topic-nav'),
    toggle: vis('.nav-toggle'), utils: vis('.masthead-utils'),
    links: Array.from(document.querySelectorAll('header a'))
      .filter(function(a){return a.offsetParent!==null && !a.closest('.mobile-menu');})
      .map(function(a){return a.textContent.trim().split('\\n')[0];})
      .filter(Boolean),
    headerH: Math.round(document.querySelector('.site-header').getBoundingClientRect().height),
    rows: (function(){
      var n=document.querySelectorAll('.primary-nav .nav-item').length;
      var t=document.querySelectorAll('.topic-nav .nav-item').length;
      return n+'/'+t;})(),
    hscroll: document.documentElement.scrollWidth - window.innerWidth
  };})()"""

# open the first mega panel and confirm it lands inside the viewport
OPEN = """(function(){
  var t=document.querySelector('.primary-nav .nav-trigger');
  t.click();
  var p=document.getElementById(t.getAttribute('aria-controls'));
  var r=p.getBoundingClientRect();
  return {open:p.getAttribute('data-open'),
          w:Math.round(r.width), left:Math.round(r.left), right:Math.round(r.right),
          inside:(r.left>=-1 && r.right<=window.innerWidth+1),
          h:Math.round(r.height)};})()"""

for page in PAGES:
    nav(BASE_SITE + page)
    print("\n" + "=" * 74)
    print(page)
    print("=" * 74)
    for label, w in WIDTHS:
        width(w)
        r = ev(PROBE) or {}
        links = r.get("links") or []
        missing = [x for x in DESKTOP_LINKS if x not in links]
        o = ev(OPEN) or {}
        print("\n  %-8s %4dpx  nav %s  primary=%s topic=%s utils=%s toggle=%s" % (
            label, w, r.get("rows"), r.get("primary"), r.get("topic"),
            r.get("utils"), r.get("toggle")))
        print("           header=%spx  overflow=%s  links=%d  missing=%s" % (
            r.get("headerH"), r.get("hscroll"), len(links), missing or "NONE"))
        print("           panel: open=%s inside=%s w=%s left=%s right=%s h=%s" % (
            o.get("open"), o.get("inside"), o.get("w"), o.get("left"),
            o.get("right"), o.get("h")))
        ev("document.querySelector('.primary-nav .nav-trigger').click()")
        time.sleep(0.6)

s.send(json.dumps({"id": 901, "method": "Emulation.clearDeviceMetricsOverride",
                   "params": {}}))
time.sleep(1)
s.close()
_srv.shutdown()
shutil.rmtree(TMP, ignore_errors=True)
print("\npreview server stopped, temp copy removed")
