# -*- coding: utf-8 -*-
"""Quatre corrections d'affichage, idempotentes.

1. Police absente sur /retours/ — les URL de fontface.css étaient relatives :
   dans une page servie depuis un sous-dossier, elles pointaient vers
   /retours/assets/fonts/… qui n'existe pas, et le navigateur retombait sur la
   police système. Même cause pour l'icône et le préchargement. Les six pages
   bâties par build_pages.py sont concernées dès qu'elles ne sont pas à la
   racine ; 404.html l'est aussi, puisqu'il est rendu sous l'adresse demandée.

2. Texte bleu sur fond orange au survol du bouton « Vos retours » du menu :
   .nav a:hover (0,2,1) l'emportait sur .nav-avis:hover (0,2,0) pour la
   couleur. Le bouton porte désormais le même poids de sélecteur.

3. et 4. Le survol des cartes reprend la couleur d'accent de sa section —
   bleu pour « Pour aller plus loin » et « D'où viennent ces données »,
   corail pour « Parcourir sans calculer », comme dans leurs titres.
"""
import re, sys

n = 0

# ── 1. chemins absolus pour la police, l'icône et le préchargement
s = open('fontface.css', encoding='utf-8').read()
s2, k = re.subn(r'url\(assets/fonts/', 'url(/assets/fonts/', s)
if k:
    open('fontface.css', 'w', encoding='utf-8').write(s2); n += k
    print(f'fontface.css : {k} URL passées en chemin absolu')

s = open('build_pages.py', encoding='utf-8').read()
s2, k1 = re.subn(r'href="favicon\.svg"', 'href="/favicon.svg"', s)
s2, k2 = re.subn(r'href="assets/fonts/inter-latin\.woff2"',
                 'href="/assets/fonts/inter-latin.woff2"', s2)
s2, k3 = re.subn(r'src="assets/pages\.js"', 'src="/assets/pages.js"', s2)
if k1 + k2 + k3:
    open('build_pages.py', 'w', encoding='utf-8').write(s2); n += k1 + k2 + k3
    print(f'build_pages.py : icône {k1}, préchargement {k2}, script {k3}')

# ── 2. le bouton du menu ne doit plus hériter du bleu de .nav a:hover
s = open('site.css', encoding='utf-8').read()
s2, k = re.subn(r'(?<!,)\.nav-avis:hover\{background:var\(--orange\);color:#fff\}',
                '.nav .nav-avis:hover,.nav-avis:hover{background:var(--sur-or);color:#fff}', s)
if k:
    s = s2; n += k
    print('site.css : survol du bouton du menu corrigé (texte blanc, plus bleu)')

# ── 3 et 4. accent de section au survol des cartes
BLOC = """
/* Le survol d'une carte reprend l'accent de sa section : bleu là où le titre
   l'est, corail dans « Parcourir sans calculer ». Sans cela toutes les cartes
   du site réagissaient du même gris, et rien ne rattachait la carte survolée
   à la bande où elle se trouve. La teinte reste très pâle : c'est un repère
   de survol, pas une sélection. */
.g-card{transition:background .16s ease-out,border-color .16s ease-out,box-shadow .16s ease-out}
#bande-guides .g-card:hover,#bande-sources .g-card:hover,
#bande-sources .non-sim li:hover,.src-card:hover{
  background:var(--ti-bl2);border-color:var(--bd-bl2);box-shadow:0 6px 16px rgba(37,72,255,.10)}
#bande-explorer .g-card:hover{
  background:var(--ti-co2);border-color:var(--bd-co);box-shadow:0 6px 16px rgba(255,99,71,.12)}
@media (prefers-reduced-motion:reduce){.g-card{transition:none}}
"""
if '#bande-explorer .g-card:hover' not in s:
    s = s.rstrip() + '\n' + BLOC
    n += 1
    print('site.css : accent de section ajouté au survol des cartes')

# teintes corail manquantes dans les deux palettes
for marqueur, ajout in (
        ('--ti-bl:#eef2ff;--ti-bl2:#f6f8ff;', '--ti-co2:#fff6f4;--bd-co:#ffc9bd;'),
        ('--ti-bl:#1a2340;--ti-bl2:#171f36;', '--ti-co2:#31201c;--bd-co:#7c4a3c;')):
    if marqueur in s and ajout not in s:
        s = s.replace(marqueur, marqueur + ajout, 1); n += 1
        print('site.css : teintes corail ajoutées à la palette')

open('site.css', 'w', encoding='utf-8').write(s)
print('---', n, 'modification(s)' if n else 'rien à faire (déjà appliqué)')
