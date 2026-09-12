import urllib.request, json, time, sys, ssl
def probe(name, url, method='GET', data=None, headers=None, tries=4, timeout=60, show=400):
    h={'User-Agent':'mon-ehpad-audit/1.0','Accept':'application/json'}
    if headers: h.update(headers)
    last=None
    for i in range(tries):
        t0=time.time()
        try:
            req=urllib.request.Request(url, data=data, headers=h, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body=r.read()
                dt=int((time.time()-t0)*1000)
                print(f"[{name}] {r.status} {dt}ms {len(body)}o  {r.headers.get('Content-Type','')}")
                return body
        except urllib.error.HTTPError as e:
            print(f"[{name}] HTTP {e.code} — {e.reason}"); return None
        except Exception as e:
            last=e; time.sleep(1.5*(i+1))
    print(f"[{name}] ECHEC après {tries} essais : {last}")
    return None
