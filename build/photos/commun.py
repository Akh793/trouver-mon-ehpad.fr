# -*- coding: utf-8 -*-
"""Outils communs aux scripts de photos (30/09/2026).

Vignette de la liste de résultats : 240 × 192 px (affichée en 120 × 96, écrans haute densité),
WebP. Une vignette par EHPAD, par ordre de préférence :
  1. photo Wikimedia Commons reliée à l'EHPAD par son numéro FINESS dans Wikidata (P4058 → P18) ;
  2. photo Panoramax prise depuis la rue, recadrée vers l'EHPAD, gardée après tri visuel ;
  3. vue aérienne IGN (BD ORTHO, Licence Ouverte) centrée sur l'adresse ;
  4. rien (la carte affiche une illustration) si la position n'est pas celle de l'adresse.
Aucune image Google : les conditions de Google Maps interdisent de stocker ses images."""
import json, math, os, subprocess, time, io
B = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(B, '..', '..'))
SORTIE = os.path.join(RACINE, 'site', 'img', 'e')
CACHE = os.path.join(B, 'cache')
UA = 'trouver-mon-ehpad.fr photos/1.0 (https://trouver-mon-ehpad.fr)'
W, H = 240, 192


def get(url, essais=4, delai=40):
    for k in range(essais):
        # -f : une erreur HTTP (429 « trop de requêtes », 404…) n'est pas prise pour un contenu
        r = subprocess.run(['curl', '-sSLf', '--http1.1', '-m', str(delai), '-A', UA, url], capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(2 + 3 * k)
    return b''


def positions():
    """Position retenue pour chaque EHPAD : coordonnées FINESS+ (géocodage à l'adresse, score ≥ 0,7),
    sinon géocodage BAN à l'adresse de build_data.py. Positions au centre de la commune ou trop
    arrondies (moins de 4 décimales, soit ±100 m ou pire) : écartées."""
    F = {e['finess']: e for e in json.load(open(os.path.join(B, '..', 'finess_ehpad.json'), encoding='utf-8'))}
    m = json.load(open(os.path.join(B, '..', 'merged_v2.json'), encoding='utf-8'))
    pos = {}
    for e in m:
        f = F.get(e['fin'], {})
        if f.get('lat') and float(f.get('scoreBAN') or 1) >= 0.7:
            pos[e['fin']] = (float(f['lat']), float(f['lon']), 'adresse')
        elif e.get('lat') and not e.get('approx') and len(str(e['lat']).split('.')[-1]) >= 4:
            pos[e['fin']] = (float(e['lat']), float(e['lon']), 'adresse')
        else:
            pos[e['fin']] = None
    return pos, {e['fin']: e for e in m}


def couvre(img):
    """Recadrage « cover » au format de la vignette."""
    from PIL import Image
    r = max(W / img.width, H / img.height)
    im = img.resize((max(W, round(img.width * r)), max(H, round(img.height * r))), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((l, t, l + W, t + H))


def enregistre(img, fin):
    os.makedirs(SORTIE, exist_ok=True)
    couvre(img.convert('RGB')).save(os.path.join(SORTIE, fin + '.webp'), 'WEBP', quality=72, method=6)
