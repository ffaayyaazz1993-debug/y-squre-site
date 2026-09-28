"""Is the cPanel session still authenticated, or does the user need to log in?

The deploy failures were WebSocketTimeoutException, not an auth error, which
points at a stale File Manager tab rather than a dead session. But "looks
logged in" from the URL alone is not proof: cPanel leaves a cpsess token in the
URL of a page that has already expired server-side.

The honest test is a real authenticated API call. A live session answers with a
JSON result; an expired one answers with a login page or a redirect. Try the
stale tab first, and if it times out, close it and open a fresh tab on the same
session before concluding anything -- because a timeout and a logout look
identical from the outside until one of them is ruled out.
"""
import json, time, urllib.error, urllib.parse, urllib.request, websocket

CDP = "http://127.0.0.1:9222"
ORIGIN = "https://sh00021.bigrock.com:2083"
# Do not assume the host: read the origin off the live cPanel tab instead.
CPANEL_HOST = "sh00021.bigrock.com:2083"


def tabs():
    return json.loads(urllib.request.urlopen(CDP + "/json/list", timeout=10).read())


def open_ws(tid, timeout=12):
    t = [x for x in tabs() if x["id"] == tid][0]
    return websocket.create_connection(t["webSocketDebuggerUrl"],
                                       suppress_origin=True, timeout=timeout)


class C:
    def __init__(self, tid, timeout=12):
        self.s = open_ws(tid, timeout)
        self.s.settimeout(timeout)
        self.n = 0

    def call(self, m, p=None, t=12):
        self.n += 1
        self.s.send(json.dumps({"id": self.n, "method": m, "params": p or {}}))
        end = time.time() + t
        while time.time() < end:
            try:
                d = json.loads(self.s.recv())
            except websocket.WebSocketTimeoutException:
                raise TimeoutError(m)
            if d.get("id") == self.n:
                return d
        raise TimeoutError(m)

    def js(self, e, t=12):
        r = self.call("Runtime.evaluate",
                      {"expression": e, "returnByValue": True, "awaitPromise": True}, t)
        return (r.get("result", {}).get("result", {}) or {}).get("value")

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


# A harmless authenticated call: ask cPanel to list the docroot.
PROBE = """(async function(){
  try{
    var b=new URLSearchParams();
    b.set('action','Fileman::list_files');
    b.set('path','/home2/a1790256/public_html');
    b.set('per_page','3');
    var r=await fetch(location.origin+'/cpsessSESS/json-api/cpanel?',
      {cache:'no-store',
      method:'POST', credentials:'same-origin',
      headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:b.toString()});
    var txt=await r.text();
    return {status:r.status, redirected:r.redirected, finalUrl:r.url,
            ctype:r.headers.get('content-type'),
            looksLikeLogin:/name="password"|id="user_pass"|Login|cpanel-login/i.test(txt),
            bodyHead:txt.slice(0,180)};
  }catch(e){ return {error:String(e)}; }
})()"""


def try_tab(tid, sess, label):
    c = C(tid)
    try:
        title = c.js("document.title")
        who = c.js("document.body.innerText.slice(0,60).replace(/\\s+/g,' ')")
        res = c.js(PROBE.replace("SESS", sess), 20)
        st = (res or {}).get("status")
        login = (res or {}).get("looksLikeLogin")
        # 404 means the route was wrong, not that the session died. Judge auth
        # on a login page, a redirect, or JSON coming back at all.
        ok = (not login) and (st == 200 or (res or {}).get("isJson") is True)
        print("  [%s] title=%r" % (label, (title or "")[:34]))
        print("       page text : %r" % (who or "")[:60])
        print("       api status: %s  ctype=%s  json=%s  login-page=%s" % (
            (res or {}).get("status"), (res or {}).get("ctype"),
            (res or {}).get("isJson"), (res or {}).get("looksLikeLogin")))
        if not ok:
            print("       body      : %r" % ((res or {}).get("bodyHead") or (res or {}).get("error") or "")[:150])
        print("       VERDICT   :", "SESSION IS LIVE" if ok else "NOT AUTHENTICATED")
        return ok
    except TimeoutError as e:
        print("  [%s] CDP call %s timed out -- tab is stale, not necessarily logged out" % (label, e))
        return None
    except Exception as e:
        print("  [%s] error: %s" % (label, e))
        return None
    finally:
        c.close()


def new_tab(url):
    req = urllib.request.Request(CDP + "/json/new?" + urllib.parse.quote(url, safe=""),
                                 method="PUT")
    return json.loads(urllib.request.urlopen(req, timeout=15).read())["id"]


all_tabs = tabs()
sess = None
for t in all_tabs:
    if t.get("type") == "page" and "cpsess" in t.get("url", ""):
        import re
        m = re.search(r"cpsess(\d+)", t["url"])
        if m:
            sess = m.group(1)
            break
print("live cpsess token found:", bool(sess))
fm = [t for t in all_tabs if t.get("type") == "page" and "filemanager" in t.get("url", "")]
print("filemanager tabs:", len(fm))
if fm:
    print("  fm tab title:", (fm[0].get("title") or "")[:40])

print("\n=== 1. the existing File Manager tab ===")
r1 = try_tab(fm[0]["id"], sess, "existing") if (fm and sess) else None

if r1 is not True and sess:
    print("\n=== 2. fresh tab on the same session (stale-tab recovery) ===")
    tid = new_tab("%s/cpsess%s/frontend/index.html?fileop=open" % (ORIGIN, sess))
    time.sleep(7)
    r2 = try_tab(tid, sess, "fresh")
    if r2 is True:
        print("\nCONCLUSION: session is fine. The original failure was a stale")
        print("File Manager tab. No re-login needed -- deploy should use a fresh tab.")
    elif r2 is None:
        print("\nCONCLUSION: fresh tab ALSO timed out. Needs a different fix, not a login.")
    else:
        print("\nCONCLUSION: session is genuinely EXPIRED -- please log in again.")
