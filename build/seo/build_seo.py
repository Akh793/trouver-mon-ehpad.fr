# -*- coding: utf-8 -*-
"""
Génère les pages de contenu de trouver-mon-ehpad.fr à partir de la base des 7 417 EHPAD :
région → département → ville → établissement, plus les pages nationales, les guides et les sitemaps.

Règles appliquées (voir MAINTENANCE.md §10) :
  · une page n'est créée que si elle apporte une information que les autres pages n'ont pas ;
  · une commune n'a sa page que si elle compte au moins 2 établissements ;
  · un établissement n'a sa fiche que s'il a un tarif déclaré ou une évaluation publiée ;
  · aucun chiffre n'est écrit s'il n'est pas calculé à partir des données réelles.

Usage :  python3 seo/build_seo.py [--villes-min 2] [--fiches toutes|documentees]
"""
import os, sys, json, math, shutil, collections, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import geo, layout, pieces
from base import (charge, slug, esc, nb, eur, eur2, pct, mois_eur, stats, mediane, lien_calc,
                  nom_etab, titre, SITE, B, DOMAINE, MARQUE, MOIS, MAJ, MAJ_ISO, CNSA_MAJ)
from pieces import kpis, cta, tableau, qa, sources, explique_heberg, bloc_financement, STATUTS, ash_cell

OUT = os.path.abspath(os.path.join(B, '..', 'site'))
URLS = []          # (url, priorite, type) pour les sitemaps

INFLATION_2018_2025 = 17.2     # INSEE, indice des prix à la consommation, cumul 2018 → 2025


def ecrire(url, html, prio=0.6, type_page='page'):
    chemin = os.path.join(OUT, url.strip('/'), 'index.html') if url.endswith('/') else os.path.join(OUT, url.lstrip('/'))
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    open(chemin, 'w', encoding='utf-8').write(html)
    URLS.append((url, prio, type_page))


# ------------------------------------------------------------------ géographie
def cle_ville(insee):
    """Les arrondissements de Paris, Lyon et Marseille sont rattachés à leur commune :
    personne ne cherche « EHPAD Lyon 3e », tout le monde cherche « EHPAD Lyon »."""
    if insee[:3] == '751': return '75056'
    if insee[:3] == '132': return '13055'
    if '69381' <= insee <= '69389': return '69123'
    return insee


def dist(a, b):
    if not (a['lat'] and b['lat']): return 1e9
    dlat = (a['lat'] - b['lat']) * 111
    dlon = (a['lon'] - b['lon']) * 111 * math.cos(math.radians(a['lat']))
    return math.hypot(dlat, dlon)


def phrase_dep(code):
    """« dans le Rhône », « en Corse-du-Sud », « à Paris »… pour écrire du français correct."""
    n = geo.DEPARTEMENTS[code]
    if code == '75': return 'à Paris'
    if code in ('971', '972', '973', '976'): return 'en ' + n
    if code == '974': return 'à La Réunion'
    if code == '975': return 'à Saint-Pierre-et-Miquelon'
    if n[0] in 'AEIOUYÀÉÈÎÔ' or code in ('2A', '2B'): return 'en ' + n
    if n.startswith('Hauts-') or n.startswith('Pyrénées-') or n.startswith('Côtes-') or n.startswith('Alpes-') or n.startswith('Bouches-') or n.startswith('Deux-'):
        return 'dans les ' + n
    if code in geo.FEMININS: return 'en ' + n
    return 'dans le ' + n


# =============================================================== construction
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--villes-min', type=int, default=2,
                    help='nombre minimal d’établissements pour qu’une commune ait sa page')
    ap.add_argument('--fiches', default='documentees', choices=['toutes', 'documentees'])
    args = ap.parse_args()

    rows, communes = charge()
    for r in rows:
        r['nom_aff'] = nom_etab(r)
        r['cle'] = cle_ville(r['insee'])

    # --- regroupements
    par_dep = collections.defaultdict(list)
    par_ville = collections.defaultdict(list)
    for r in rows:
        par_dep[r['dep']].append(r)
        par_ville[r['cle']].append(r)

    nom_ville = {}
    for c, lot in par_ville.items():
        cc = communes.get(c)
        nom_ville[c] = cc['nom'] if cc else lot[0]['ville_nom']

    # --- slugs : les territoires sont prioritaires, les communes en conflit portent leur département
    reserves = set(geo.REGIONS) | {slug(n) for n in geo.DEPARTEMENTS.values()} | {
        'index', 'assets', 'vendor', 'data', 'guides', 'etudes', 'aides-ehpad', 'prix-ehpad'}
    compte = collections.Counter(slug(nom_ville[c]) for c in par_ville)
    slug_ville = {}
    for c in par_ville:
        s = slug(nom_ville[c])
        if c == '75056':
            s = 'paris'                         # Paris : la commune et le département se confondent
        elif s in reserves or compte[s] > 1:
            s = f'{s}-{slug(par_ville[c][0]["dep"])}'
        slug_ville[c] = s

    url_ville = {c: f'/ehpad/{slug_ville[c]}/' for c in par_ville}
    url_dep = {d: f'/ehpad/{slug(geo.DEPARTEMENTS[d])}/' for d in par_dep}
    url_dep['75'] = '/ehpad/paris/'
    url_region = {s: f'/ehpad/{s}/' for s in geo.REGIONS}

    # --- quelles pages sont créées
    villes_page = {c for c, lot in par_ville.items() if len(lot) >= args.villes_min or c in ('75056',)}
    if args.fiches == 'toutes':
        fiches = list(rows)
    else:
        fiches = [r for r in rows if r['p'] or r['hasN']]
    url_fiche = {}
    vus = set()
    for r in fiches:
        v = slug_ville.get(r['cle'], slug(r['ville_nom']))
        u = f"/ehpad/{v}/{slug(r['nom_aff'])[:60].strip('-')}-{r['fin']}/"
        url_fiche[r['fin']] = u
        assert u not in vus, u
        vus.add(u)
    set_fiches = set(url_fiche)

    def lien_de(r):
        return url_fiche.get(r['fin']) or url_ville.get(r['cle']) or url_dep[r['dep']]

    print(f"villes avec page : {len(villes_page)} | fiches établissement : {len(fiches)} | départements : {len(par_dep)}")

    # --- statistiques nationales
    FR = stats(rows)
    ctx = {'rows': rows, 'communes': communes, 'par_dep': par_dep, 'par_ville': par_ville,
           'nom_ville': nom_ville, 'url_ville': url_ville, 'url_dep': url_dep, 'url_region': url_region,
           'url_fiche': url_fiche, 'villes_page': villes_page, 'lien_de': lien_de, 'FR': FR,
           'slug_ville': slug_ville}

    feuille_de_style()

    import territoires, fiches as mod_fiches, contenus
    territoires.construire(ctx, ecrire)
    mod_fiches.construire(ctx, ecrire, fiches)
    contenus.construire(ctx, ecrire)
    redirections(ctx)
    sitemaps()
    print(f"→ {len(URLS)} pages écrites")


def redirections(ctx):
    """Une commune à établissement unique n'a pas de page : sa page ferait doublon avec la fiche.
    L'adresse reste malgré tout devinable, on y place donc une redirection vers la fiche,
    explicitement retirée de l'indexation."""
    n = 0
    for c, lot in ctx['par_ville'].items():
        if c in ctx['villes_page']: continue
        cible = None
        for r in lot:
            if r['fin'] in ctx['url_fiche']: cible = ctx['url_fiche'][r['fin']]; break
        if not cible: continue
        u = ctx['url_ville'][c]
        chemin = os.path.join(OUT, u.strip('/'), 'index.html')
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        open(chemin, 'w', encoding='utf-8').write(
            '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex, follow">'
            f'<link rel="canonical" href="{DOMAINE}{cible}">'
            f'<meta http-equiv="refresh" content="0; url={cible}">'
            f'<title>{esc(ctx["nom_ville"][c])} — un seul EHPAD recensé</title></head>'
            f'<body><p>Un seul EHPAD est recensé dans cette commune. '
            f'<a href="{cible}">Voir sa fiche</a>.</p></body></html>')
        n += 1
    print('redirections de communes à établissement unique :', n)


def feuille_de_style():
    """Feuille de style partagée par toutes les pages de contenu : une seule requête, mise en cache
    d'une page à l'autre. La page d'accueil, elle, garde son CSS en ligne (aucune requête bloquante)."""
    import re
    ff = open(os.path.join(B, 'fontface.css'), encoding='utf-8').read()
    ff = ff.replace('url(assets/fonts/', 'url(/assets/fonts/')
    css = ff + '\n' + open(os.path.join(B, 'site.css'), encoding='utf-8').read() \
        + '\n' + open(os.path.join(B, 'seo.css'), encoding='utf-8').read()
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    open(os.path.join(OUT, 'assets', 'site.css'), 'w', encoding='utf-8').write(css)
    js = open(os.path.join(B, 'seo_pages.js'), encoding='utf-8').read()
    open(os.path.join(OUT, 'assets', 'pages.js'), 'w', encoding='utf-8').write(js)
    print('assets/site.css :', len(css.encode()) // 1024, 'Ko | assets/pages.js :', len(js.encode()) // 1024, 'Ko')


# ------------------------------------------------------------------ sitemaps
def sitemaps():
    groupes = collections.defaultdict(dict)
    for url, prio, t in URLS:
        groupes[t][url] = prio          # une adresse n'apparaît qu'une fois
    groupes = {t: sorted(d.items()) for t, d in groupes.items()}
    groupes = collections.defaultdict(list, groupes)
    # pages institutionnelles existantes
    groupes['pages'] += [('/', 1.0), ('/notre-methodologie.html', 0.6),
                         ('/qui-sommes-nous.html', 0.4)]
    index = []
    for t, lst in sorted(groupes.items()):
        morceaux = [lst[i:i + 2000] for i in range(0, len(lst), 2000)] or [[]]
        for k, m in enumerate(morceaux):
            nomf = f'sitemap-{t}.xml' if len(morceaux) == 1 else f'sitemap-{t}-{k + 1}.xml'
            corps = '\n'.join(
                f'  <url><loc>{DOMAINE}{u}</loc><lastmod>{MAJ_ISO}</lastmod><priority>{p}</priority></url>'
                for u, p in sorted(m))
            open(os.path.join(OUT, nomf), 'w', encoding='utf-8').write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + corps + '\n</urlset>\n')
            index.append(nomf)
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(f'  <sitemap><loc>{DOMAINE}/{f}</loc><lastmod>{MAJ_ISO}</lastmod></sitemap>' for f in index)
        + '\n</sitemapindex>\n')
    print('sitemaps :', ', '.join(index))


if __name__ == '__main__':
    main()
