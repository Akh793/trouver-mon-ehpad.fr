# -*- coding: utf-8 -*-
"""Choisit la vignette de chaque EHPAD et l'écrit dans site/img/e/<finess>.webp.

Ordre : Wikimedia (sauf photos rejetées au tri, tri_wikimedia.json) > Panoramax (seulement les
photos gardées au tri, tri_panoramax.json) > vue aérienne IGN > aucune (illustration côté site).
Écrit photos.json : { finess: code } lu par split_data_v2.py (colonne « photo ») :
  "w|<auteur>|<licence>"   photo Wikimedia Commons
  "p|<auteur>|<licence>"   photo Panoramax
  "i"                      vue aérienne IGN
  absent                   pas d'image (position inconnue ou approximative)
et credits.json (source de chaque photo, pour la page des crédits)."""
import json, os, re, sys, glob
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import CACHE, SORTIE, enregistre, positions
B = os.path.dirname(os.path.abspath(__file__))
LIC = {'etalab-2.0': 'Licence Ouverte', 'CC-BY-SA-4.0': 'CC BY-SA 4.0', 'CC-BY-4.0': 'CC BY 4.0'}


def charge(n, defaut):
    p = os.path.join(B, n)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else defaut


def court(auteur):
    a = re.sub(r'\s*\(.*?\)|https?://\S+', '', auteur or '').strip(' .,;')
    a = re.sub(r'^(This illustration was made by|Photo by|Own work by)\s+', '', a, flags=re.I)
    return (a[:28] + '…') if len(a) > 29 else (a or 'Wikimedia Commons')


if __name__ == '__main__':
    pos, rows = positions()
    wm = charge('cache/wm.json', {}); pnx = charge('cache/pnx.json', {})
    rejet_wm = set(charge('tri_wikimedia.json', {}).get('rejetees', []))
    garde_pnx = set(charge('tri_panoramax.json', {}).get('gardees', []))
    codes, credits, cpt = {}, [], {'w': 0, 'p': 0, 'i': 0, 'aucune': 0}
    os.makedirs(SORTIE, exist_ok=True)
    for fin in sorted(rows):
        src = None
        if fin in wm and fin not in rejet_wm and os.path.exists(os.path.join(CACHE, 'wm', fin + '.jpg')):
            x = wm[fin]; src = os.path.join(CACHE, 'wm', fin + '.jpg')
            codes[fin] = f"w|{court(x['auteur'])}|{x['licence']}"
            credits.append({'fin': fin, 'source': 'Wikimedia Commons', 'auteur': x['auteur'], 'licence': x['licence'],
                            'licence_url': x.get('licence_url'), 'lien': x['page']})
        elif fin in garde_pnx and pnx.get(fin, {}).get('etat') == 'photo':
            x = pnx[fin]; src = os.path.join(CACHE, 'pnx', fin + '.jpg')
            codes[fin] = f"p|{court(x.get('auteur'))}|{LIC.get(x['licence'], x['licence'])}"
            credits.append({'fin': fin, 'source': 'Panoramax', 'auteur': x.get('auteur') or '', 'licence': LIC.get(x['licence'], x['licence']),
                            'lien': f"https://api.panoramax.xyz/#focus=pic&pic={x['id']}", 'date': x['date']})
        elif pos.get(fin) and os.path.exists(os.path.join(CACHE, 'ign', fin + '.webp')):
            src = os.path.join(CACHE, 'ign', fin + '.webp'); codes[fin] = 'i'
        if src:
            cpt[codes[fin][0]] += 1
            enregistre(Image.open(src), fin)
        else:
            cpt['aucune'] += 1
    # vignettes d'établissements disparus ou désormais sans image
    for p in glob.glob(os.path.join(SORTIE, '*.webp')):
        if os.path.basename(p)[:-5] not in codes: os.remove(p)
    json.dump(codes, open(os.path.join(B, 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(credits, open(os.path.join(B, 'credits.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(cpt)
