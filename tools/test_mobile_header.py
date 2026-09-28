"""A 190px sticky header on a 390x844 phone is 22% of the viewport, permanently
occupied. Confirm it is usable: that the panel still opens, that the nav is
reachable, and that the sticky header does not swallow the content.

Checks the header height, the anchor scroll offset, and that a country deep link
from the mega-menu actually lands on its target rather than under the header.
"""
import functools, http.server, json, os, shutil, threading, time
import urllib.request, websocket
from http.server import SimpleHTTPRequestHandler

ROOT = r"C:\Users\ffaay\y-squre-site"
TMP = r"C:\Users\ffaay\AppData\Local\hermes\cache\scratch\mobtest2"
shutil.rmtree(TMP, ignore_errors=True)
shutil.copytree(ROOT, TMP, ignore=shutil.ignore_patterns(
    ".git", "docs", "__pycache__", "tools", "README.md", "_stage"))
PORT = 8735
_srv = http.server.HTTPServer(("127.0.0.1", PORT),
                              functools.partial(SimpleHTTPRequestHandler, directory=TMP))
threading.Thread(target=_srv.serve_forever, daemon=True).start()
SITE = "http://127.0.0.1:%d" % PORT

BASE = "http://127.0.0.1:9222"


def tabs():
    return json.loads(urllib.request.urlopen(BASE + "/json", timeout=10).read())


def connect(tid):
    t = [x for x in tabs() if x["id"] == tid][0]
    return websocket.create_connection(t["webSocketDebuggerUrl"],
                                       suppress_origin=True, timeout=30)


# Any page tab will do: the test navigates it to the preview server anyway.
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


def nav(url, wait=6):
    s.send(json.dumps({"id": 9999, "method": "Page.navigate", "params": {"url": url}}))
    time.sleep(wait)


s.send(json.dumps({"id": 900, "method": "Emulation.setDeviceMetricsOverride",
                   "params": {"width": 390, "height": 844, "deviceScaleFactor": 2,
                              "mobile": True}}))
time.sleep(1.5)

print("=== a real phone viewport: 390x844 ===")
nav(SITE + "/geopolitics/europe/")
print("viewport        :", ev("window.innerWidth+'x'+window.innerHeight"))
print("header height   :", ev("Math.round(document.querySelector('.site-header').getBoundingClientRect().height)"),
      "px =", ev("Math.round(document.querySelector('.site-header').getBoundingClientRect().height/window.innerHeight*100)"), "% of screen")

# Does a country deep link land clear of the sticky header?
print("\n=== country deep link from the mega-menu ===")
res = ev("""(async function(){
  var a=document.querySelector('a[href*="#france"]');
  if(!a) return 'no france link';
  location.href = a.getAttribute('href');
  await new Promise(function(r){setTimeout(r,2500);});
  var t=document.getElementById('france');
  if(!t) return {err:'target #france missing'};
  var r=t.getBoundingClientRect();
  var h=document.querySelector('.site-header').getBoundingClientRect().height;
  return {targetTop:Math.round(r.top), headerH:Math.round(h),
          clearOfHeader: r.top >= h - 2,
          visibleInViewport: r.top < window.innerHeight && r.bottom > 0};
})()""")
print("  ", res)

print("\n=== scrolling: does the sticky header behave? ===")
ev("window.scrollTo(0,600)"); time.sleep(1)
print("  header still on screen at scrollY=600:",
      ev("Math.round(document.querySelector('.site-header').getBoundingClientRect().top)"))
print("  content not hidden behind it       :",
      ev("(function(){var m=document.querySelector('main');if(!m)return 'no main';"
         "var r=m.getBoundingClientRect();return r.top>=0;})()"))

print("\n=== is the panel usable on a phone? ===")
p = ev("""(function(){
  document.querySelector('.primary-nav .nav-trigger').click();
  var p=document.getElementById(document.querySelector('.primary-nav .nav-trigger')
    .getAttribute('aria-controls'));
  var r=p.getBoundingClientRect();
  var links=Array.from(p.querySelectorAll('a')).filter(function(a){return a.offsetParent!==null;});
  // Measure the MENU ROWS (.mega-list a), not the panel's own title link --
  // .mega-title is a heading and is legitimately short.
  var rows=Array.from(p.querySelectorAll('.mega-list a, .mega-group-name'))
                   .filter(function(a){return a.offsetParent!==null;});
  var hs=rows.map(function(a){return Math.round(a.getBoundingClientRect().height);});
  return {open:p.getAttribute('data-open'), h:Math.round(r.height),
          fullWidth: Math.round(r.width)>=window.innerWidth-2,
          menuRows: rows.length,
          shortestRow: hs.length?Math.min.apply(null,hs):null,
          allRows44: hs.length? hs.every(function(h){return h>=44;}) : null};
})()""")
print("  ", p)
s.send(json.dumps({"id": 901, "method": "Emulation.clearDeviceMetricsOverride",
                   "params": {}}))
time.sleep(1)
s.close()
_srv.shutdown()
shutil.rmtree(TMP, ignore_errors=True)
print("\npreview server stopped")
