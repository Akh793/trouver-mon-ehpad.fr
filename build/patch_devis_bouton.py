# -*- coding: utf-8 -*-
"""Pose le bouton « Comparer vos devis » dans les menus. Idempotent.

Vert profond plutôt qu'ambre : la barre porte déjà « Vos retours » en ambre, et
deux boutons de la même couleur ne se distinguent plus. Le vert dit « argent
économisé » sans emprunter le corail, réservé à l'action principale du site.
Teinte --ve-btn, et non --vert : blanc sur #0f8a5f ne donne que 4,35:1, sous le
seuil AA de 4,5. #0b6b4a en donne 6,6.
"""
import re

n = 0

# ── 1. palette : une teinte par thème, le vert clair du thème sombre ne peut
#       pas porter du texte blanc.
c = open('site.css', encoding='utf-8').read()
for marqueur, ajout in (
        ('--vert:#0f8a5f;--orange:#e08a00;--rouge:#d1344b;', '--ve-btn:#0b6b4a;'),
        ('--vert:#3fbf8c;--orange:#f0a93a;--rouge:#f2647c;', '--ve-btn:#16785a;')):
    if marqueur in c and ajout not in c.split(marqueur)[1][:40]:
        c = c.replace(marqueur, marqueur + ajout, 1); n += 1

BLOC = """
/* Bouton « Comparer vos devis ». Vert profond : distinct de l'ambre de « Vos
   retours » et du corail de l'action principale, et 6,6:1 sous du blanc. */
.nav-devis,.tb-devis{background:var(--ve-btn);color:#fff;border-radius:999px;font-weight:600;
  text-decoration:none;white-space:nowrap;transition:transform .14s ease-out,box-shadow .14s ease-out,filter .14s}
.nav-devis{padding:.2rem .8rem;box-shadow:0 2px 8px rgba(11,107,74,.28)}
.nav .nav-devis:hover,.nav-devis:hover,.tb-devis:hover{color:#fff;filter:brightness(1.12);
  transform:translateY(-1px);box-shadow:0 6px 16px rgba(11,107,74,.38)}
.tb-devis{padding:.5rem 1rem;font-size:.85rem;box-shadow:0 4px 14px rgba(11,107,74,.26)}
.tb-menu a.menu-devis{color:var(--ve-btn);font-weight:600}
@media (max-width:1180px){.tb-devis{display:none}}
@media (hover:none){.nav-devis:hover,.tb-devis:hover{transform:none}}
@media (prefers-reduced-motion:reduce){.nav-devis,.tb-devis{transition:none}
  .nav-devis:hover,.tb-devis:hover{transform:none}}
"""
if '.nav-devis' not in c:
    c = c.rstrip() + '\n' + BLOC; n += 1
open('site.css', 'w', encoding='utf-8').write(c)
print('site.css :', 'bouton et palette posés' if n else 'déjà en place')

LIEN_NAV = '<a href="/comparer-devis-ehpad/" class="nav-devis">Comparer vos devis</a>'
LIEN_TB  = '<a href="/comparer-devis-ehpad/" class="tb-devis">Comparer vos devis</a>'
LIEN_MENU = '<a href="/comparer-devis-ehpad/" class="menu-devis">Comparer vos devis</a>'

# ── 2. accueil : la barre de navigation sous le titre, juste après la carte
s = open('index.template.html', encoding='utf-8').read()
k = 0
if 'nav-devis' not in s:
    s, k1 = re.subn(r'(<nav aria-label="Navigation principale" class="nav print-hide">\n\s*<a href="#bande-carte">La carte des restes à charge</a>\n)',
                    r'\1      ' + LIEN_NAV + '\n', s, count=1)
    k += k1
if 'menu-devis' not in s:
    s, k2 = re.subn(r'(<a href="#bande-carte">La carte des restes à charge</a>\n\s*<a href="#bande-route">)',
                    lambda m: m.group(1).replace('<a href="#bande-route">', LIEN_MENU + '\n            <a href="#bande-route">'), s, count=1)
    k += k2
if 'tb-devis' not in s:
    s, k3 = re.subn(r'(<a href="/retours/" class="tb-avis">Vos retours</a>)',
                    LIEN_TB + r'\n        \1', s, count=1)
    k += k3
open('index.template.html', 'w', encoding='utf-8').write(s)
print('index.template.html :', k, 'insertion(s)')

# ── 3. pages annexes et pages de contenu : barre haute et menu déroulant
for f, motifs in (('build_pages.py', True), ('seo/layout.py', True)):
    s = open(f, encoding='utf-8').read()
    k = 0
    if 'tb-devis' not in s:
        s, k1 = re.subn(r'(<a href="/retours/" class="tb-avis">Vos retours</a>)',
                        LIEN_TB + r'\n\1', s, count=1); k += k1
    if 'menu-devis' not in s:
        s, k2 = re.subn(r'(<a href="/retours/">Vos retours</a>)',
                        LIEN_MENU + r'\n\1', s, count=1); k += k2
    open(f, 'w', encoding='utf-8').write(s)
    print(f'{f} : {k} insertion(s)')

# ── 4. la page doit figurer au sitemap
b = open('seo/build_seo.py', encoding='utf-8').read()
if 'comparer-devis-ehpad' not in b:
    print('⚠️  seo/build_seo.py : penser à ajouter la page au sitemap (non automatisé ici)')
