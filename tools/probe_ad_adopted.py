"""Confirm the hiding rule lives in adopted stylesheets, and audit page coverage.

document.styleSheets does not include constructable stylesheets, so an
extension using CSSStyleSheet/adoptedStyleSheets is invisible to every probe
that walked document.styleSheets. That is why no rule was ever found.

Separately: which page types actually emit a slot? /geopolitics/europe/ was
measured with none at all, so the "every page" coverage needs an audit.
"""
import glob, json, os, re, time, urllib.request, websocket

R = r"C:\Users\ffaay\y-squre-site"
BASE = "http://127.0.0.1:9222"

tabs = json.loads(urllib.request.urlopen(BASE + "/json", timeout=10).read())
tid = [t for t in tabs if t.get("type") == "page"][0]["id"]
t = [x for x in tabs if x["id"] == tid][0]
s = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True, timeout=40)
_id = [1]


def send(method, params=None, wait=30):
    _id[0] += 1
    s.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
    t0 = time.time()
    while time.time() - t0 < wait:
        try:
            d = json.loads(s.recv())
        except Exception:
            return None
        if d.get("id") == _id[0]:
            return d.get("result")
    return None


def ev(e, tmo=30):
    r = send("Runtime.evaluate",
             {"expression": e, "returnByValue": True, "awaitPromise": True}, tmo)
    return (r or {}).get("result", {}).get("value")


send("Emulation.clearDeviceMetricsOverride")
time.sleep(1)
send("Page.navigate", {"url": "https://y-squre.com/latest/?cb=%d" % int(time.time())})
time.sleep(10)

print("=== adoptedStyleSheets: the blind spot in every earlier probe ===")
print(ev("""(function(){
  var a=document.adoptedStyleSheets||[];
  return {count:a.length, rules:a.map(function(sh,i){
    try{
      var hits=Array.from(sh.cssRules).map(function(r){return r.cssText;})
        .filter(function(t){return /ad-|\\[class\\^|\\[id\\^/.test(t);});
      return {i:i, total:sh.cssRules.length, adRules:hits.slice(0,4)};
    }catch(e){ return {i:i, error:e.message}; }})};})()"""))

print("\n=== re-test the class matrix with adopted sheets disabled ===")
print(ev("""(function(){
  var a=document.adoptedStyleSheets||[];
  var before={};
  var main=document.querySelector('main');
  function test(cls){
    var d=document.createElement('div');
    d.className=cls; main.insertBefore(d, main.firstChild);
    var v=getComputedStyle(d).display; d.remove(); return v;
  }
  before['ad-slot (adopted active)']=test('ad-slot');
  var saved=Array.prototype.slice.call(a);
  try{
    document.adoptedStyleSheets=[];
    before['ad-slot (adopted cleared)']=test('ad-slot');
    before['ad-inline (adopted cleared)']=test('ad-inline');
  }finally{ document.adoptedStyleSheets=saved; }
  before['ad-slot (restored)']=test('ad-slot');
  return before;})()"""))

s.close()

print("\n" + "=" * 70)
print("PAGE COVERAGE AUDIT: which generated pages emit an ad slot?")
print("=" * 70)
groups = {
    "home": ["index.html"],
    "latest": ["latest/index.html"],
    "blog index": ["blog/index.html"],
    "research index": ["research/index.html"],
    "article": ["blog/2026/09/26/understanding-currency-depreciation.html",
                "research/2026/09/26/central-bank-balance-sheets.html"],
    "explainer": ["explainer/japan/macro-transmission.html",
                  "explainer/france/macro-transmission.html"],
    "region page": ["geopolitics/europe/index.html", "geopolitics/asia/index.html"],
    "section page": ["macro/index.html", "markets/index.html", "geopolitics/index.html"],
    "static/legal": ["about/index.html", "privacy/index.html",
                     "advertising/index.html", "contact/index.html"],
}
for label, files in groups.items():
    for f in files:
        p = os.path.join(R, f.replace("/", os.sep))
        if not os.path.exists(p):
            print("  %-14s %-56s FILE MISSING" % (label, f))
            continue
        h = open(p, encoding="utf-8").read()
        n = len(re.findall(r'class="ad-slot', h))
        below = "yes" if re.search(r'<main[^>]*>\s*<div class="ad-slot', h) else "NO"
        print("  %-14s %-56s slots=%-2d first-slot-below-header=%s"
              % (label, f, n, below))
