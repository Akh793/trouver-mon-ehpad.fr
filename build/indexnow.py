# -*- coding: utf-8 -*-
"""Signale à IndexNow (Bing, Yandex, Seznam, Naver… — pas Google) les pages modifiées.

Les adresses viennent de seo/lastmod.json : toutes celles dont la date de modification est celle
passée en argument (par défaut : la plus récente). La clé est publiée à la racine du site
(/<clé>.txt), ce qui prouve que la demande vient bien du propriétaire du domaine.
À lancer APRÈS la mise en ligne (git push), sinon les moteurs trouvent les anciennes pages.
Usage : python3 indexnow.py [AAAA-MM-JJ] [--simuler]"""
import json, os, sys, time, urllib.request, urllib.error
B = os.path.dirname(os.path.abspath(__file__))
HOTE = 'trouver-mon-ehpad.fr'
cle = open(os.path.join(B, 'indexnow.key')).read().strip()
lm = json.load(open(os.path.join(B, 'seo', 'lastmod.json'), encoding='utf-8'))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
date = args[0] if args else max(v[1] for v in lm.values())
urls = sorted(f'https://{HOTE}{u}' for u, v in lm.items() if v[1] == date)
print(f'{len(urls)} adresses modifiées le {date}')
for i in range(0, len(urls), 10000):
    lot = urls[i:i + 10000]
    corps = json.dumps({'host': HOTE, 'key': cle, 'keyLocation': f'https://{HOTE}/{cle}.txt', 'urlList': lot}).encode()
    if '--simuler' in sys.argv:
        print('simulation :', len(lot), 'adresses, premier envoi non effectué'); continue
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=corps,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    # 403 = clé refusée. Constaté le 29/09/2026 juste après un push, puis accepté (200) le lendemain
    # sans rien changer : la clé est revérifiée sur le site, qui peut être en cours de déploiement.
    for essai in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print('lot', i // 10000 + 1, ':', r.status, '(200 ou 202 = accepté)'); break
        except urllib.error.HTTPError as e:
            print('lot', i // 10000 + 1, ': refus', e.code, e.read()[:300].decode('utf-8', 'replace'))
            if e.code not in (403, 429) or essai == 3:
                sys.exit('Échec. 403 : vérifier que https://%s/%s.txt affiche la clé, puis relancer dans quelques minutes.' % (HOTE, cle))
            time.sleep(60 * essai)
