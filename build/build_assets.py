# -*- coding: utf-8 -*-
"""Régénère les deux fichiers partagés par les pages de contenu :
   site/assets/site.css et site/assets/pages.js.

   À lancer depuis le dossier « build » :  python build_assets.py

   Pourquoi ce script existe : build_seo.py fait la même chose, mais il commence par
   charger les bases de données sources (merged_v2.json et les autres), qui ne sont pas
   versionnées — elles pèsent plus de 100 Mo et se retéléchargent (voir MAINTENANCE.md
   §2.2). Quand on ne modifie que le style, ce détour n'a pas lieu d'être.
"""
import os

B = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(B, '..', 'site')

fontface = open(os.path.join(B, 'fontface.css'), encoding='utf-8').read()
fontface = fontface.replace('url(assets/fonts/', 'url(/assets/fonts/')
css = (fontface + '\n'
       + open(os.path.join(B, 'site.css'), encoding='utf-8').read() + '\n'
       + open(os.path.join(B, 'seo.css'), encoding='utf-8').read())

os.makedirs(os.path.join(SITE, 'assets'), exist_ok=True)
open(os.path.join(SITE, 'assets', 'site.css'), 'w', encoding='utf-8', newline='\n').write(css)

js = open(os.path.join(B, 'seo_pages.js'), encoding='utf-8').read()
open(os.path.join(SITE, 'assets', 'pages.js'), 'w', encoding='utf-8', newline='\n').write(js)

print('assets/site.css : %d Ko | assets/pages.js : %d Ko'
      % (len(css.encode()) // 1024, len(js.encode()) // 1024))
