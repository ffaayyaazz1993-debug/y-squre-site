"""Recover a wedged cPanel File Manager tab and deploy.

A WebSocketTimeoutException against the File Manager means the tab's renderer is
wedged -- the page is loaded, the websocket connects, and it simply stops
replying. It is NOT an expired session. Re-authenticating for this wastes the
user a login prompt and changes nothing, so do not go looking for credentials.

Fix: open a fresh tab on the SAME URL and work there. A fresh renderer answers
immediately if the session was always valid.
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

R = r"C:\Users\ffaay\y-squre-site"
CDP = "http://127.0.0.1:9222"
FM_HINT = "/frontend/jupiter/filemanager/"


def fm_tab():
    for t in json.loads(urllib.request.urlopen(CDP + "/json/list", timeout=10).read()):
        if t.get("type") == "page" and FM_HINT in t.get("url", ""):
            return t
    return None


def probe(tab, label):
    """A wedged renderer times out on even document.title."""
    import websocket
    s = websocket.create_connection(tab["webSocketDebuggerUrl"], suppress_origin=True, timeout=12)
    i = [1]

    def ev(e, tmo=8):
        i[0] += 1
        s.send(json.dumps({"id": i[0], "method": "Runtime.evaluate",
                           "params": {"expression": e, "returnByValue": True}}))
        t0 = time.time()
        while time.time() - t0 < tmo:
            try:
                d = json.loads(s.recv())
            except Exception:
                return "TIMEOUT"
            if d.get("id") == i[0]:
                return d.get("result", {}).get("result", {}).get("value")
    try:
        r = ev("document.title")
    finally:
        s.close()
    print("   %-28s -> %s" % (label, r))
    return r != "TIMEOUT"


print("=== is the current File Manager tab alive? ===")
old = fm_tab()
alive = probe(old, "existing FM tab") if old else False

if not alive:
    print("\n=== renderer is wedged; opening a FRESH tab on the same URL ===")
    url = old["url"] if old else ""
    if not url:
        print("   no File Manager tab at all -- cannot recover automatically")
        sys.exit(2)
    # Chrome requires PUT on /json/new. A GET returns 405 Method Not Allowed,
    # which reads like a CDP failure but is just the wrong verb.
    req = urllib.request.Request(
        CDP + "/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
    new = json.loads(urllib.request.urlopen(req, timeout=15).read())
    time.sleep(7)
    print("   new tab:", new["id"][:6], new["url"][:70])
    if not probe(new, "fresh FM tab"):
        print("   fresh tab also unresponsive -- the SESSION may have expired.")
        print("   Ask the user to log in again; do not retry blindly.")
        sys.exit(3)
    # close the wedged one so the deploy helper cannot pick it again
    try:
        urllib.request.urlopen(CDP + "/json/close/" + old["id"], timeout=8).read()
        print("   closed the wedged tab")
    except Exception as e:
        print("   (could not close wedged tab:", type(e).__name__, ")")

print("\n=== deploying against the live tab ===")
PY = r"C:\Users\ffaay\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
r = subprocess.run([PY, os.path.join(R, "tools", "deploy_full.py")],
                   capture_output=True, text=True, timeout=595)
lines = [l for l in r.stdout.splitlines() if "uploaded" in l or "removed" in l]
print("   exit", r.returncode)
for l in lines[-6:]:
    print("   ", l.strip()[:96])
if r.returncode:
    tail = (r.stderr or "").splitlines()[-3:]
    print("   err:", " / ".join(x.strip()[:80] for x in tail))

print("\n=== .htaccess ===")
r2 = subprocess.run([PY, os.path.join(R, "tools", "fix_htaccess.py")],
                    capture_output=True, text=True, timeout=300)
print("   exit", r2.returncode, " ".join(
    l.strip()[:70] for l in (r2.stdout + r2.stderr).splitlines()[-2:] if l.strip()))
