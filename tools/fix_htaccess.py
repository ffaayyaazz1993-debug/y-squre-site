"""Upload .htaccess through the SAME /execute/Fileman/upload_files path the
deploy driver uses, so the result is directly comparable. Reports the server's
verbatim reply."""
import base64, json, os, re, time, urllib.request, websocket

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


def ev(expr, t=70):
    return call("Runtime.evaluate",
                {"expression": expr, "returnByValue": True, "awaitPromise": True}, t
                ).get("result", {}).get("result", {}).get("value")


def js_exists(abspath):
    return """(async function(){
      var fd=new URLSearchParams();
      fd.set('cpanel_jsonapi_version','2');
      fd.set('cpanel_jsonapi_module','Fileman');
      fd.set('cpanel_jsonapi_func','list_files');
      fd.set('dir', %s);
      var r=await fetch(CPANEL.security_token+'/json-api/cpanel',
        {method:'POST',body:fd.toString(),credentials:'include',
         headers:{'Content-Type':'application/x-www-form-urlencoded'}});
      return (await r.text()).substring(0,200);
    })()""" % json.dumps(abspath)


def js_unlink(abspath):
    return """(async function(){
      var fd=new URLSearchParams();
      fd.set('cpanel_jsonapi_version','2');
      fd.set('cpanel_jsonapi_module','Fileman');
      fd.set('cpanel_jsonapi_func','fileop');
      fd.set('op','unlink');
      fd.set('sourcefiles', %s);
      var r=await fetch(CPANEL.security_token+'/json-api/cpanel',
        {method:'POST',body:fd.toString(),credentials:'include',
         headers:{'Content-Type':'application/x-www-form-urlencoded'}});
      return (await r.text()).substring(0,200);
    })()""" % json.dumps(abspath)


raw = open(os.path.join(r"C:\Users\ffaay\AppData\Local\hermes\cache\scratch\stage_ysq", ".htaccess"), "rb").read()
b64 = base64.b64encode(raw).decode()
print(f"local .htaccess: {len(raw)} bytes\n")

print("exists check:", (ev(js_exists("/public_html")) or "")[:150])
print("\nunlink:", (ev(js_unlink("/home2/a1790256/public_html/.htaccess")) or "")[:150])

# identical to the driver's js_upload
up = ev("""(async function(){
  var bin=atob(%s); var u=new Uint8Array(bin.length);
  for(var i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
  var fd=new FormData();
  fd.append('dir', "/public_html");
  fd.append('name', ".htaccess");
  fd.append('file', new File([u], ".htaccess", {type:'application/octet-stream'}));
  var r=await fetch(CPANEL.security_token+'/execute/Fileman/upload_files',
    {method:'POST',body:fd,credentials:'include'});
  return (await r.text()).substring(0,600);
})()""" % json.dumps(b64))
print("\nupload reply:", up)
