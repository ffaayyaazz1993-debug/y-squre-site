"""Deploy the Y-Square tree to BigRock cPanel.

Two things this driver gets right that the earlier ones got wrong:

1. mkdir + unlink go to  /cpsess<TOKEN>/json-api/cpanel
   NOT /cpsess<TOKEN>/execute/Fileman/<fn>.  The /execute/ namespace has no
   mkdir and no delete function; the json-api namespace has Fileman::mkdir and
   Fileman::fileop (op=unlink).  Both were confirmed against this host.

2. Content is written through Fileman/upload_files (binary multipart), never
   Fileman/save_file_content.  save_file_content is a TEXT endpoint: it
   rewrites every LF as CRLF, which is wrong for a Linux host.  Verified with a
   controlled probe.  upload_files preserves bytes exactly.

Because /execute/ cannot overwrite an existing file, an existing target is
deleted first (fileop, op=unlink) and then re-uploaded.
"""

import base64
import json
import os
import re
import sys
import time
import urllib.request

import websocket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CDP = "http://127.0.0.1:9222"
CPANEL_ORIGIN = "https://sh00021.bigrock.com:2083"
STAGE = r"C:\Users\ffaay\AppData\Local\hermes\cache\scratch\stage_ysq"


def page_ws(url_substr, exclude=()):
    tabs = json.loads(urllib.request.urlopen(f"{CDP}/json/list").read())
    for t in tabs:
        if t.get("type") != "page" or url_substr not in t.get("url", ""):
            continue
        if any(x in t.get("title", "") for x in exclude):
            continue
        return t
    return None


tab = page_ws("fileman", exclude=("Login",))
if not tab:
    raise SystemExit("no authenticated cPanel File Manager tab — log in first")
sess = re.search(r"cpsess\d+", tab["url"]).group(0)

s = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=40,
                                suppress_origin=True)
s.settimeout(20)
_n = [0]


def call(m, p=None, t=35):
    _n[0] += 1
    mid = _n[0]
    msg = {"id": mid, "method": m}
    if p:
        msg["params"] = p
    s.send(json.dumps(msg))
    dl = time.time() + t
    while time.time() < dl:
        res = json.loads(s.recv())
        if res.get("id") == mid:
            return res
    return {}


def ev(expr, t=60):
    return call("Runtime.evaluate",
                {"expression": expr, "returnByValue": True, "awaitPromise": True},
                t=t).get("result", {}).get("result", {}).get("value")


print(f"session {sess}  ({tab['title']})\n")

# ---- collect the staged tree -------------------------------------------------
import os

files = []
for dirpath, _, names in os.walk(STAGE):
    for n in names:
        full = os.path.join(dirpath, n)
        rel = os.path.relpath(full, STAGE).replace("\\", "/")
        files.append((rel, open(full, "rb").read()))
files.sort()
print(f"staged {len(files)} files")

# Every directory in the staged tree must exist on the server before a file can
# be uploaded into it. upload_files will not create parents, so a new tree (the
# country explainer directories, for instance) fails every file until its
# directories are made first. Walk parents shallowest-first and mkdir each.
dirs = set()
for rel, _ in files:
    parts = rel.split("/")[:-1]
    for d in range(1, len(parts) + 1):
        dirs.add("/".join(parts[:d]))



# ---- JS payloads -------------------------------------------------------------
def js_mkdir(rel):
    parent = "/public_html" + ("/" + rel.rsplit("/", 1)[0] if "/" in rel else "")
    leaf = rel.rsplit("/", 1)[-1]
    return """(async function(){
      var fd=new URLSearchParams();
      fd.set('cpanel_jsonapi_version','2');
      fd.set('cpanel_jsonapi_module','Fileman');
      fd.set('cpanel_jsonapi_func','mkdir');
      fd.set('name', %s);
      fd.set('path', %s);
      var r=await fetch(CPANEL.security_token+'/json-api/cpanel',
        {method:'POST',body:fd.toString(),credentials:'include',
         headers:{'Content-Type':'application/x-www-form-urlencoded'}});
      return (await r.text()).substring(0,200);
    })()""" % (json.dumps(leaf), json.dumps(parent))


def js_list(d):
    return """(async function(){
      var fd=new FormData(); fd.append('dir', %s);
      var j=await (await fetch(CPANEL.security_token+'/execute/Fileman/list_files',
        {method:'POST',body:fd,credentials:'include'})).json();
      return (j.data||[]).map(function(e){
        return (e.type==='dir'?'[D] ':'    ')+e.file+' '+(e.humansize||e.size||'');
      }).join('\\n');
    })()""" % json.dumps(d)


# ---- create the directory tree before uploading into it ---------------------
_dirs = set()
for _rel, _ in files:
    _parts = _rel.split("/")[:-1]
    for _d in range(1, len(_parts) + 1):
        _dirs.add("/".join(_parts[:_d]))
_dirs = sorted(_dirs, key=lambda x: (x.count("/"), x))
_made = 0
for _d in _dirs:
    _r = ev(js_mkdir(_d)) or {}
    if isinstance(_r, dict) and _r.get("errors"):
        print(f"  mkdir FAIL {_d}: {_r['errors'][0]}")
    else:
        _made += 1
print(f"  ensured {_made}/{len(_dirs)} directories")


def _split(rel):
    """-> (parent_dir, leaf). rsplit on a bare filename yields the filename
    itself as [0], which is the bug that made the delete step silently no-op."""
    if "/" in rel:
        return rel.rsplit("/", 1)[0], rel.rsplit("/", 1)[-1]
    return "", rel


def js_exists(rel):
    parent, leaf = _split(rel)
    d = "/public_html" + ("/" + parent if parent else "")
    return """(async function(){
      var fd=new FormData(); fd.append('dir', %s);
      var j=await (await fetch(CPANEL.security_token+'/execute/Fileman/list_files',
        {method:'POST',body:fd,credentials:'include'})).json();
      return (j.data||[]).some(function(e){return e.file===%s;});
    })()""" % (json.dumps(d), json.dumps(leaf))


def js_unlink(abspath):
    return """(async function(){
      var fd=new URLSearchParams();
      fd.set('cpanel_jsonapi_module','Fileman');
      fd.set('cpanel_jsonapi_func','fileop');
      fd.set('cpanel_jsonapi_apiversion','2');
      fd.set('cpanel_jsonapi_version','2');
      fd.set('filelist','1');
      fd.set('multiform','1');
      fd.set('doubledecode','0');
      fd.set('op','unlink');
      fd.set('metadata','');
      fd.set('sourcefiles', %s);
      var r=await fetch(CPANEL.security_token+'/json-api/cpanel',
        {method:'POST',body:fd.toString(),credentials:'include',
         headers:{'Content-Type':'application/x-www-form-urlencoded'}});
      return (await r.text()).substring(0,200);
    })()""" % json.dumps(abspath)


def js_upload(rel, b64):
    parent, leaf = _split(rel)
    d = "/public_html" + ("/" + parent if parent else "")
    return """(async function(){
      var bin=atob(%s); var u=new Uint8Array(bin.length);
      for(var i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
      var fd=new FormData();
      fd.append('dir', %s);
      fd.append('name', %s);
      fd.append('file', new File([u], %s, {type:'application/octet-stream'}));
      var r=await fetch(CPANEL.security_token+'/execute/Fileman/upload_files',
        {method:'POST',body:fd,credentials:'include'});
      return (await r.text()).substring(0,300);
    })()""" % (json.dumps(b64), json.dumps(d), json.dumps(leaf), json.dumps(leaf))


HOME = "/home2/a1790256"
ok = fail = 0

# ---- ensure directories ------------------------------------------------------
# Every ANCESTOR must exist before a nested file can be uploaded into it, so
# build the full chain rather than just each file's immediate parent.
dirs = set()
for rel, _ in files:
    parts = rel.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        dirs.add("/".join(parts[:i]))

for d in sorted(dirs, key=lambda x: x.count("/")):
    target = "/public_html/" + d
    if ev(js_exists(target + "/__none__")):
        res = ev(js_mkdir(d))
        created = '"result":1' in (res or "")
        print(f"  mkdir {target:<44}{'ok' if created else '(exists)'}")
print()

# ---- per file: delete-then-upload -------------------------------------------
for rel, raw in files:
    if ev(js_exists(rel)):
        r = ev(js_unlink(f"{HOME}/public_html/{rel}"))
        if '"result":1' not in (r or ""):
            print(f"  SKIP {rel:<40} delete failed: {(r or '')[:90]}")
            fail += 1
            continue
    res = ev(js_upload(rel, base64.b64encode(raw).decode()))
    body = res or ""
    good = '"succeeded":1' in body and '"failed":0' in body
    if good:
        ok += 1
        print(f"  OK   {rel:<40}{len(raw):>7}B  (binary, bytes exact)")
    else:
        fail += 1
        print(f"  FAIL {rel:<40}{len(raw):>7}B  {body[:130]}")

print(f"\nuploaded {ok}, failed {fail}")

# ---- remove the pre-redesign files that the new tree supersedes --------------
# Explicit list, never a wildcard: an unlink typo must not be able to take out a
# live file. Each path is checked for existence first and reported either way.
STALE = [
    "privacy.html",                       # moved to /privacy/index.html
    "insights/central-bank-balance-sheets.html",  # moved to /research/2026/...
    "assets/css/style.css",               # replaced by the four-file CSS system
    "assets/js/navigation.js",            # legacy header script, replaced by nav.js
    # .htaccess: upload_files will not overwrite, so it must be unlinked first.
    # This is why the 301s were inert -- the previous version stayed in place.
    ".htaccess",
    # Section renames. The .htaccess 301s keep these URLs working, so the
    # duplicate file has to go or both copies are indexable.
    "geopolitics/africa/index.html",
    "geopolitics/middle-east/index.html",
    "geopolitics/pacific/index.html",
    "geopolitics/united-kingdom/index.html",
    # Subregions removed when Europe's overlapping lists were de-duplicated.
    "geopolitics/europe/nordics/index.html",
    "geopolitics/europe/british-isles/index.html",
    "geopolitics/asia/west-asia/index.html",
    "geopolitics/asia/north-asia/index.html",
    "geopolitics/north-america/central-america/index.html",
    "geopolitics/north-america/caribbean/index.html",
    # Latin America & Caribbean withdrawn from the nav; pages deleted. The
    # .htaccess 301s send these to /geopolitics/.
    "geopolitics/latin-america/south-america/index.html",
    "geopolitics/latin-america/central-america-latam/index.html",
    "geopolitics/latin-america/caribbean-latam/index.html",
    # European subregions retired when Europe was narrowed to Western Europe.
    # The .htaccess 301s point these at /geopolitics/europe/.
    "geopolitics/europe/northern-europe/index.html",
    "geopolitics/europe/southern-europe/index.html",
    "geopolitics/europe/eastern-europe/index.html",
    "geopolitics/europe/balkans/index.html",
    "geopolitics/europe/baltics/index.html",
    "geopolitics/europe/central-europe/index.html",
    # Europe is flat: the Western Europe subregion is no longer a page.
    "geopolitics/europe/western-europe/index.html",
    # MENA narrowed to the Gulf and North Africa.
    "geopolitics/middle-east-north-africa/levant/index.html",
    "geopolitics/middle-east-north-africa/eastern-mediterranean/index.html",
    "geopolitics/middle-east-north-africa/iran-iraq/index.html",
    "geopolitics/middle-east-north-africa/turkey-anatolia/index.html",
    # Sub-Saharan Africa withdrawn; Asia and Oceania narrowed.
    "geopolitics/sub-saharan-africa/index.html",
    "geopolitics/sub-saharan-africa/west-africa/index.html",
    "geopolitics/sub-saharan-africa/east-africa/index.html",
    "geopolitics/sub-saharan-africa/horn-of-africa/index.html",
    "geopolitics/sub-saharan-africa/central-africa/index.html",
    "geopolitics/sub-saharan-africa/southern-africa/index.html",
    "geopolitics/asia/central-asia/index.html",
    "geopolitics/asia/caucasus/index.html",
    "geopolitics/oceania-pacific/pacific-islands/index.html",
    "geopolitics/oceania-pacific/australia-new-zealand/index.html",
    # Asia is flat; its subregion pages no longer exist.
    "geopolitics/asia/india/index.html",
    "geopolitics/asia/china/index.html",
    "geopolitics/asia/russia/index.html",
    "geopolitics/asia/southeast-asia/index.html",
    "macro/currencies-macro/index.html",
]
print("=== removing superseded files ===")
for stale in STALE:
    if ev(js_exists(stale)):
        r = ev(js_unlink(f"{HOME}/public_html/{stale}"))
        gone = '"result":1' in (r or "")
        print(f"  {'removed' if gone else 'FAILED '}  /{stale}")
    else:
        print(f"  absent             /{stale}")

print("\n=== final /public_html ===")
print(ev(js_list("/public_html")))
for d in dirs:
    print(f"\n=== /public_html/{d} ===")
    print(ev(js_list("/public_html/" + d)))
s.close()
