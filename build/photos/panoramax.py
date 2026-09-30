# -*- coding: utf-8 -*-
"""Photos Panoramax (prises depuis la rue, licences Etalab 2.0 ou CC-BY-SA 4.0).

Pour chaque EHPAD dont la position est celle de l'adresse : recherche des photos qui « regardent »
ce point à moins de 45 m (API fédérée api.panoramax.xyz, paramètre place_position), choix de la
meilleure, puis recadrage en perspective dans la direction de l'EHPAD pour les vues à 360°.

Filtre strict avant tri visuel : 6 à 35 m de l'adresse, EHPAD dans le champ de la photo,
prise en 2018 ou après. Le tri visuel (build/photos/tri_panoramax.json) décide de la publication :
une photo du mauvais bâtiment est pire que pas de photo.
Sortie : cache/pnx/<finess>.jpg (640 × 420, pour le tri) et cache/pnx.json (source, licence, date)."""
import io, json, math, os, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import get, positions, CACHE
D = os.path.join(CACHE, 'pnx'); os.makedirs(D, exist_ok=True)


def cap(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2); dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2); x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def distance(lat1, lon1, lat2, lon2):
    return math.hypot((lat2 - lat1) * 111000, (lon2 - lon1) * 111000 * math.cos(math.radians(lat1)))


def perspective(eq, lacet, champ=75, L=640, Ht=420, tangage=6):
    h, w = eq.shape[:2]; f = (L / 2) / math.tan(math.radians(champ / 2))
    xs, ys = np.meshgrid(np.arange(L) - L / 2, np.arange(Ht) - Ht / 2)
    x = xs.astype(float); y = -ys.astype(float); z = np.full_like(x, f)
    t = math.radians(tangage); y2 = y * math.cos(t) + z * math.sin(t); z2 = -y * math.sin(t) + z * math.cos(t)
    lon = np.arctan2(x, z2) + math.radians(lacet); lat = np.arctan2(y2, np.sqrt(x ** 2 + z2 ** 2))
    u = ((lon / (2 * math.pi) + 0.5) % 1.0) * w; v = (0.5 - lat / math.pi) * h
    return Image.fromarray(eq[np.clip(v.astype(int), 0, h - 1), np.clip(u.astype(int), 0, w - 1)])


def candidats(lat, lon):
    raw = get(f'https://api.panoramax.xyz/api/search?place_position={lon},{lat}&place_distance=0-45&limit=10', delai=25)
    try: d = json.loads(raw)
    except Exception: return None
    out = []
    for f in d.get('features', []):
        pr = f['properties']; plon, plat = f['geometry']['coordinates']
        champ = (pr.get('pers:interior_orientation') or {}).get('field_of_view')
        az = pr.get('view:azimuth') or 0; c = cap(plat, plon, lat, lon)
        ecart = abs((c - az + 540) % 360 - 180)
        lien = next((l['href'] for l in f.get('links', []) if l.get('rel') == 'via'), None)
        out.append({'id': f['id'], 'href': f['assets']['sd']['href'], 'champ': champ, 'az': az, 'cap': c,
                    'd': distance(plat, plon, lat, lon), 'ecart': ecart, 'date': pr.get('datetime', '')[:10],
                    'licence': pr.get('license'), 'instance': lien,
                    'auteur': pr.get('geovisio:producer')})
    return out


def admissible(c):
    dans_champ = c['champ'] == 360 or (c['champ'] and c['ecart'] < c['champ'] / 2 - 10)
    return dans_champ and 6 <= c['d'] <= 35 and (c['date'][:4] or '0') >= '2018'


def note(c):
    return -abs(c['d'] - 18) / 6 + (2 if c['champ'] == 360 else 0) + (int(c['date'][:4]) - 2018) / 4


def traite(fin, lat, lon):
    dest = os.path.join(D, fin + '.jpg')
    if os.path.exists(dest + '.json'): return json.load(open(dest + '.json'))
    cs = candidats(lat, lon)
    if cs is None: return {'fin': fin, 'etat': 'erreur'}
    bons = [c for c in cs if admissible(c)]
    if not bons:
        r = {'fin': fin, 'etat': 'aucune' if not cs else 'filtre'}
    else:
        c = max(bons, key=note)
        try: img = Image.open(io.BytesIO(get(c['href']))).convert('RGB')
        except Exception: return {'fin': fin, 'etat': 'erreur'}
        im = perspective(np.array(img), (c['cap'] - c['az'] + 540) % 360 - 180) if c['champ'] == 360 else img
        if c['champ'] != 360: im.thumbnail((640, 420))
        im.save(dest, quality=85)
        r = {'fin': fin, 'etat': 'photo', **{k: c[k] for k in ('id', 'd', 'champ', 'date', 'licence', 'instance', 'auteur')}}
    json.dump(r, open(dest + '.json', 'w'))
    return r


if __name__ == '__main__':
    import collections
    pos, _ = positions()
    travail = [(f, p[0], p[1]) for f, p in pos.items() if p]
    res, cpt = [], collections.Counter()
    with ThreadPoolExecutor(8) as ex:
        for i, r in enumerate(ex.map(lambda a: traite(*a), travail)):
            res.append(r); cpt[r['etat']] += 1
            if i % 250 == 0: print(i, dict(cpt), flush=True)
    json.dump({r['fin']: r for r in res}, open(os.path.join(CACHE, 'pnx.json'), 'w'), ensure_ascii=False)
    print('fin', dict(cpt))
