# -*- coding: utf-8 -*-
"""Vues aériennes IGN (BD ORTHO, service WMTS de la Géoplateforme, Licence Ouverte) :
build/photos/cache/ign/<finess>.webp, centrées sur l'adresse, niveau 18 (≈ 100 m de large).
Reprise possible : les vignettes déjà faites sont sautées."""
import io, math, os, sys, json
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import get, positions, couvre, CACHE, W, H
Z = 18
URL = ('https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS'
       '&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}')
D = os.path.join(CACHE, 'ign'); os.makedirs(D, exist_ok=True)


import threading, requests, time
_local = threading.local()


def session():
    # une connexion réutilisée par fil d'exécution : bien plus rapide qu'un curl par tuile
    if not hasattr(_local, 's'):
        _local.s = requests.Session(); _local.s.headers['User-Agent'] = 'trouver-mon-ehpad.fr photos/1.0 (https://trouver-mon-ehpad.fr)'
        _local.s.verify = os.environ.get('REQUESTS_CA_BUNDLE', True)
    return _local.s


def tuile(x, y):
    for k in range(4):
        try:
            r = session().get(URL.format(z=Z, x=x, y=y), timeout=20)
            if r.status_code == 200: return Image.open(io.BytesIO(r.content)).convert('RGB')
        except Exception:
            _local.__dict__.pop('s', None)
        time.sleep(0.5 + k)
    return None


def vue(fin, lat, lon):
    dest = os.path.join(D, fin + '.webp')
    if os.path.exists(dest): return 'deja'
    n = 2 ** Z
    fx = (lon + 180) / 360 * n
    fy = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    # W × H pixels natifs autour du point (≈ 100 × 80 m en métropole), affichés à moitié taille : net sur écran dense
    px, py = fx * 256, fy * 256
    x0, y0 = int(px - W / 2), int(py - H / 2)
    tx0, ty0, tx1, ty1 = x0 // 256, y0 // 256, (x0 + W - 1) // 256, (y0 + H - 1) // 256
    grand = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            t = tuile(tx, ty)
            if t is None: return 'echec'
            grand.paste(t, ((tx - tx0) * 256, (ty - ty0) * 256))
    l, t_ = x0 - tx0 * 256, y0 - ty0 * 256
    grand.crop((l, t_, l + W, t_ + H)).save(dest, 'WEBP', quality=72, method=6)
    return 'ok'


if __name__ == '__main__':
    pos, _ = positions()
    travail = [(f, p[0], p[1]) for f, p in pos.items() if p]
    import collections
    c = collections.Counter()
    with ThreadPoolExecutor(20) as ex:
        for i, r in enumerate(ex.map(lambda a: vue(*a), travail)):
            c[r] += 1
            if i % 250 == 0: print(i, dict(c), flush=True)
    print('fin', dict(c), 'sans position utilisable', sum(1 for p in pos.values() if not p))
