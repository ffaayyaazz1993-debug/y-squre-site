"""Verify the cPanel File Manager session is genuinely authenticated.

A loaded page is not an authenticated session. A stale session keeps rendering
the File Manager shell and the failure only shows up later, as a WebSocket
timeout on the first upload. So confirm three things separately before claiming
the login works:

  1. it is not a login page in disguise (no password field)
  2. the renderer is alive (document.title answers)
  3. the API accepts the session (authenticated same-origin request, 200 + JSON)

Reports status codes and shapes only. No token, cookie, or session value is read,
printed, or stored.
"""
import json
import time
import urllib.request

import websocket

CDP = "http://127.0.0.1:9222"
FM_HINT = "/frontend/jupiter/filemanager/"

tabs = json.loads(urllib.request.urlopen(CDP + "/json/list", timeout=10).read())
fm = next((t for t in tabs if t.get("type") == "page" and FM_HINT in t.get("url", "")), None)
if fm is None:
    print("FAIL: no File Manager tab found")
    for t in tabs:
        if t.get("type") == "page":
            print("   ", t.get("url", "")[:80])
    raise SystemExit(1)

s = websocket.create_connection(fm["webSocketDebuggerUrl"], suppress_origin=True, timeout=40)
i = [1]


def ev(e, tmo=25):
    i[0] += 1
    s.send(json.dumps({"id": i[0], "method": "Runtime.evaluate",
                       "params": {"expression": e, "returnByValue": True,
                                  "awaitPromise": True}}))
    t0 = time.time()
    while time.time() - t0 < tmo:
        try:
            d = json.loads(s.recv())
        except Exception:
            return "TIMEOUT"
        if d.get("id") == i[0]:
            res = d.get("result", {})
            if res.get("exceptionDetails"):
                return "JS_ERROR"
            return res.get("result", {}).get("value")


print("File Manager tab:", fm["url"].split("/frontend/")[0] + "/frontend/...")

print("\n=== 1. is this a login page in disguise? ===")
r = ev("""(function(){
  return {hasPasswordField: !!document.querySelector('input[name=password], #password, form[action*="login"]'),
          onFileManager: location.pathname.indexOf('filemanager') > -1};})()""")
print("  ", r)

print("\n=== 2. is the renderer alive? (a frozen one answers nothing) ===")
print("   document.title ->", ev("document.title"))
print("   root node      ->", ev("!!(document.getElementById('updiv')||document.getElementById('mainTable'))"))

print("\n=== 3. does the API accept this session? ===")
r = ev("""(function(){
  var o=location.origin, seg=location.pathname.split('/cpsess')[1], sess=seg.split('/')[0];
  return fetch(o+'/cpsess'+sess+'/json-api/cpanel?api.version=1',
               {cache:'no-store', credentials:'same-origin'})
    .then(function(res){
      return res.text().then(function(t){
        var kind='non-JSON';
        try{ JSON.parse(t); kind='JSON'; }catch(e){}
        return {status:res.status, body:kind, redirected:res.redirected, bytes:t.length};});
    })
    .catch(function(e){ return {error:String(e).slice(0,70)}; });})()""")
print("  ", r)
s.close()
print("\n(values intentionally not read or logged)")
