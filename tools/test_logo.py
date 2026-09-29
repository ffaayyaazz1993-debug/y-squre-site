"""Verify the header after two coupled changes: the logo is no longer a link, and
/latest/ is now the front page.

The risk worth testing is not the markup -- it is that a non-anchor wordmark
inherits different computed styles than the anchor it replaced (an <a> is
inline-flex-ish and gets UA link styling; a <span> does not), and that a reader
can still get to the front page now that the logo is dead. Both are measured
rather than assumed.
"""
import functools
import http.server
import json
import os
import shutil
import threading
import time
import urllib.request

import websocket
from http.server import SimpleHTTPRequestHandler

ROOT = r"C:\Users\ffaay\y-squre-site"
TMP = r"C:\Users\ffaay\AppData\Local\hermes\cache\scratch\logochk"
shutil.rmtree(TMP, ignore_errors=True)
shutil.copytree(ROOT, TMP, ignore=shutil.ignore_patterns(
    ".git", "docs", "__pycache__", "tools", "README.md", "_stage"))
PORT = 8749
_srv = http.server.HTTPServer(("127.0.0.1", PORT),
                              functools.partial(SimpleHTTPRequestHandler, directory=TMP))
threading.Thread(target=_srv.serve_forever, daemon=True).start()
SITE = "http://127.0.0.1:%d" % PORT

tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list", timeout=10).read())
tid = [t for t in tabs if t.get("type") == "page"][0]["id"]
t = [x for x in tabs if x["id"] == tid][0]
s = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True, timeout=40)
i = [1]


def ev(e, tmo=30):
    i[0] += 1
    s.send(json.dumps({"id": i[0], "method": "Runtime.evaluate",
                       "params": {"expression": e, "returnByValue": True, "awaitPromise": True}}))
    t0 = time.time()
    while time.time() - t0 < tmo:
        try:
            d = json.loads(s.recv())
        except Exception:
            return "TIMEOUT"
        if d.get("id") == i[0]:
            return d.get("result", {}).get("result", {}).get("value")


def size(w, h=900):
    s.send(json.dumps({"id": 900, "method": "Emulation.setDeviceMetricsOverride",
                       "params": {"width": w, "height": h, "deviceScaleFactor": 1,
                                  "mobile": w < 900}}))
    time.sleep(1.0)
    ev("window.dispatchEvent(new Event('resize'))")
    time.sleep(0.4)


size(1440)
s.send(json.dumps({"id": 9999, "method": "Page.navigate",
                   "params": {"url": SITE + "/latest/?cb=%d" % int(time.time())}}))
time.sleep(6)
s.send(json.dumps({"id": 9989, "method": "Page.reload", "params": {"ignoreCache": True}}))
time.sleep(5)

print("=== the wordmark must look identical, and do nothing ===")
print(ev("""(function(){
  var b=document.querySelector('.brand'), n=document.querySelector('.brand-name');
  var cs=getComputedStyle(b), ns=getComputedStyle(n);
  var r=b.getBoundingClientRect();
  return {tag:b.tagName, href:b.getAttribute('href'), hasHref:b.hasAttribute('href'),
          tabIndex:b.tabIndex, cursor:cs.cursor, userSelect:cs.userSelect,
          display:cs.display, visible:r.width>0&&r.height>0,
          text:n.textContent.trim(), fontSize:ns.fontSize,
          color:ns.color, ariaLabel:b.getAttribute('aria-label')};})()"""))

print("\n=== clicking it must not navigate ===")
print(ev("""(function(){
  var b=document.querySelector('.brand');
  var before=location.href;
  b.click();
  return {hrefBefore:before.split('/').slice(2,3).join('/'), hrefAfter:location.href===before,
          stillSame:location.href===before};})()"""))

print("\n=== the front page is still reachable, without the logo ===")
print(ev("""(function(){
  var links=Array.from(document.querySelectorAll('a[href="/latest/"]'));
  return {linksToLatest:links.length,
          firstLabels:links.slice(0,3).map(function(a){return a.textContent.trim().slice(0,22);})};})()"""))

print("\n=== layout across widths: logo sized, nav intact, no overflow ===")
print("%-7s %-8s %-9s %-8s %-8s %-7s %s"
      % ("WIDTH", "logoW", "logoH", "header", "adTop", "OVERFL", "navItems"))
bad = 0
for w in (1440, 1100, 860, 768, 480, 390, 360, 320):
    size(w)
    r = ev("""(function(){
      var b=document.querySelector('.brand'), h=document.querySelector('.site-header');
      var a=document.querySelector('.ad-top'), r=b.getBoundingClientRect();
      return {lw:Math.round(r.width), lh:Math.round(r.height),
              hh:Math.round(h.getBoundingClientRect().height),
              at:getComputedStyle(a).top,
              of:document.documentElement.scrollWidth-window.innerWidth,
              ni:document.querySelectorAll('.primary-nav .nav-item').length};})()""") or {}
    ok = r.get("lw", 0) > 40 and r.get("of", 1) <= 0 and r.get("ni", 0) == 7
    if not ok:
        bad += 1
    print("%-7d %-8s %-9s %-8s %-8s %-7s %-5s %s"
          % (w, r.get("lw"), r.get("lh"), r.get("hh"), r.get("at"), r.get("of"),
             r.get("ni"), "OK" if ok else "** CHECK **"))
print("\nproblem widths:", bad)

s.send(json.dumps({"id": 901, "method": "Emulation.clearDeviceMetricsOverride", "params": {}}))
s.close()
_srv.shutdown()
shutil.rmtree(TMP, ignore_errors=True)
print("preview stopped")
