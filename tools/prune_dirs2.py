"""Remove the empty directories, using the operation the cPanel File Manager UI
actually uses. rmdir is rejected by api2_fileop on this host; the UI's own
folder-delete path is Fileman::fileop with op=unlink against the folder path.
"""
import json, re, urllib.request, websocket

tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=8).read())
fmm = next(t for t in tabs if "filemanager" in t.get("url", ""))
s = websocket.create_connection(fmm["webSocketDebuggerUrl"], suppress_origin=True, timeout=70)
_id = [0]


def call(m, p=None, t=70):
    _id[0] += 1
    s.send(json.dumps({"id": _id[0], "method": m, "params": p or {}}))
    t0 = time.time()
    while time.time() - t0 < t:
        d = json.loads(s.recv())
        if d.get("id") == _id[0]:
            return d
    return {}


def ev(e, t=70):
    return call("Runtime.evaluate",
                {"expression": e, "returnByValue": True, "awaitPromise": True}, t
                ).get("result", {}).get("result", {}).get("value")


import time

def op(operation, abs_path, extra=None):
    return """(async function(){
      var fd=new URLSearchParams();
      fd.set('cpanel_jsonapi_version','2');
      fd.set('cpanel_jsonapi_module','Fileman');
      fd.set('cpanel_jsonapi_func','fileop');
      fd.set('op', %s);
      fd.set('sourcefiles', %s);
      %s
      var r=await fetch(CPANEL.security_token+'/json-api/cpanel',
        {method:'POST',body:fd.toString(),credentials:'include',
         headers:{'Content-Type':'application/x-www-form-urlencoded'}});
      return (await r.text()).substring(0,300);
    })()""" % (json.dumps(operation), json.dumps(abs_path), extra or "")


HOME = "/home2/a1790256/public_html"
DIRS = [
    # Retired ONLY. These must mirror deploy_full.py's STALE list of retired
    # paths, never any directory the current taxonomy generates -- this sweep
    # runs AFTER the upload pass, so listing a live page here deletes the copy
    # that was just deployed.
    "/geopolitics/asia/west-asia",
    "/geopolitics/asia/north-asia",
    "/geopolitics/north-america/central-america",
    "/geopolitics/north-america/caribbean",
    "/geopolitics/europe/nordics",
    "/geopolitics/europe/british-isles",
    "/geopolitics/africa",
    "/geopolitics/middle-east",
    "/geopolitics/pacific",
    "/geopolitics/united-kingdom",
    "/macro/currencies-macro",
    "/insights",
]

print("=== deleting empty dirs with op=unlink ===")
for d in DIRS:
    body = ev(op("unlink", f"{HOME}{d}")) or ""
    m = re.search(r'"data":\s*\{\s*"result":\s*(\d)', body) or \
        re.search(r'"data":\s*\[\s*\{\s*"result":\s*(\d)', body)
    good = bool(m and m.group(1) == "1")
    print(f"  {'OK   ' if good else 'FAIL '} {d:44} {(body[:90])}")
