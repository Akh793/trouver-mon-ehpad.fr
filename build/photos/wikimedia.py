# -*- coding: utf-8 -*-
"""Photos Wikimedia Commons reliées à un EHPAD par Wikidata : élément portant le numéro FINESS
(propriété P4058) et une image (P18). Licences libres ; auteur et licence sont affichés.
Sortie : cache/wm/<finess>.jpg (800 px) et cache/wm.json."""
import io, json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import get, CACHE
D = os.path.join(CACHE, 'wm'); os.makedirs(D, exist_ok=True)
Q = 'SELECT ?item ?fin ?img WHERE { ?item wdt:P4058 ?fin . ?item wdt:P18 ?img }'

if __name__ == '__main__':
    for k in range(5):
        try:
            lignes = json.loads(get('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': Q, 'format': 'json'}), delai=120))['results']['bindings']; break
        except Exception: time.sleep(3)
    E = {e['fin'] for e in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'merged_v2.json'), encoding='utf-8'))}
    img = {}
    for b in lignes:
        f = b['fin']['value']
        if f in E and f not in img:
            img[f] = ('File:' + urllib.parse.unquote(b['img']['value'].split('FilePath/')[1]), b['item']['value'])
    fj = os.path.join(CACHE, 'wm.json')
    res = json.load(open(fj, encoding='utf-8')) if os.path.exists(fj) else {}
    T = [x for x in img.items() if x[0] not in res]
    for i in range(0, len(T), 15):
        lot = T[i:i + 15]
        u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({
            'action': 'query', 'titles': '|'.join(t for _, (t, _) in lot), 'prop': 'imageinfo',
            'iiprop': 'url|extmetadata', 'iiurlwidth': 800, 'format': 'json'})
        d = None
        for k in range(5):
            try: d = json.loads(get(u)); break
            except Exception: time.sleep(2 + k)
        if d is None: print('lot illisible', i); continue
        norm = {n['from']: n['to'] for n in d['query'].get('normalized', [])}
        pages = {p['title']: p for p in d['query']['pages'].values()}
        for f, (t, item) in lot:
            p = pages.get(norm.get(t, t))
            if not p or 'imageinfo' not in p: continue
            ii = p['imageinfo'][0]; m = ii.get('extmetadata', {})
            g = lambda k: re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', m.get(k, {}).get('value', ''))).strip()
            dest = os.path.join(D, f + '.jpg')
            if not os.path.exists(dest):
                open(dest, 'wb').write(get(ii['thumburl']))
            res[f] = {'titre': p['title'], 'page': ii['descriptionurl'], 'licence': g('LicenseShortName'),
                      'licence_url': g('LicenseUrl'), 'auteur': g('Artist')[:80], 'wikidata': item}
        time.sleep(0.5)
    json.dump(res, open(os.path.join(CACHE, 'wm.json'), 'w'), ensure_ascii=False, indent=0)
    print(len(res), 'photos Wikimedia')
