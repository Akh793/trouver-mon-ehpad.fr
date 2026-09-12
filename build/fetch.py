import urllib.request, json, gzip, time, sys, io
def get(url, tries=6, timeout=90, raw=False):
    last=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'mon-ehpad-build/1.0','Accept':'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d=r.read()
            return d if raw else json.loads(d)
        except Exception as e:
            last=e; time.sleep(1.5*(i+1))
    raise last
if __name__=='__main__':
    p=get("https://tabular-api.data.gouv.fr/api/resources/cd04df7c-f78e-461b-aa9d-1df1e5b2d5cf/profile/")
    prof=p.get('profile',p)
    cols=prof.get('columns',{}) if isinstance(prof,dict) else {}
    print(json.dumps(list(cols.keys()), ensure_ascii=False))
    print('nb lignes', prof.get('nb_lines') if isinstance(prof,dict) else '?')
