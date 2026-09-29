# -*- coding: utf-8 -*-
"""Signale à IndexNow (Bing, Yandex, Seznam, Naver… — pas Google) les pages modifiées.

Les adresses viennent de seo/lastmod.json : toutes celles dont la date de modification est celle
passée en argument (par défaut : la plus récente). La clé est publiée à la racine du site
(/<clé>.txt), ce qui prouve que la demande vient bien du propriétaire du domaine.
À lancer APRÈS la mise en ligne (git push), sinon les moteurs trouvent les anciennes pages.
Usage : python3 indexnow.py [AAAA-MM-JJ] [--simuler]"""
import json, os, sys, urllib.request
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
    with urllib.request.urlopen(req, timeout=60) as r:
        print('lot', i // 10000 + 1, ':', r.status, '(200 ou 202 = accepté)')
