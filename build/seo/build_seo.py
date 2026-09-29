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

# Date de dernière modification RÉELLE de chaque page : empreinte du contenu utile (titre,
# description, <main>). Une page reconstruite à l'identique garde sa date ; une page dont le
# contenu change prend la date du jour. Google : lastmod n'est utilisé que s'il est
# « consistently and verifiably accurate » — une date identique partout ne l'est pas.
import hashlib, datetime, re as _re
LASTMOD_F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lastmod.json')
try:
    LASTMOD = json.load(open(LASTMOD_F, encoding='utf-8'))
except Exception:
    LASTMOD = {}
AUJ = datetime.date.today().isoformat()

def empreinte(html):
    m = _re.search(r'<main[^>]*>(.*)</main>', html, _re.S)
    t = _re.search(r'<title>(.*?)</title>', html, _re.S)
    dsc = _re.search(r'<meta name="description" content="([^"]*)"', html)
    utile = (t.group(1) if t else '') + '|' + (dsc.group(1) if dsc else '') + '|' + (m.group(1) if m else html)
    return hashlib.sha1(utile.encode('utf-8')).hexdigest()[:16]

def date_modif(url, html):
    h = empreinte(html)
    ancien = LASTMOD.get(url)
    if ancien and ancien[0] == h:
        return ancien[1]
    LASTMOD[url] = [h, AUJ]
    return AUJ

INFLATION_2018_2025 = 17.2     # INSEE, indice des prix à la consommation, cumul 2018 → 2025


def ecrire(url, html, prio=0.6, type_page='page'):
    chemin = os.path.join(OUT, url.strip('/'), 'index.html') if url.endswith('/') else os.path.join(OUT, url.lstrip('/'))
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    open(chemin, 'w', encoding='utf-8').write(html)
    date_modif(url, html)
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
        r['nom_url'] = nom_etab(r)          # l'adresse de la fiche ne change jamais
        r['nom_aff'] = r['nom_url']
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
    noms_lisibles(rows, nom_ville)

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
        u = f"/ehpad/{v}/{slug(r['nom_url'])[:60].strip('-')}-{r['fin']}/"
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
    import etudes
    etudes.construire(ctx, ecrire)
    redirections(ctx)
    sitemaps()
    print(f"→ {len(URLS)} pages écrites")


GENERIQUE = _re.compile(
    r"^(é|e)tablissement\s+(d[’' ]\s*)?(h[ée]r?b\w*\.?|hospitalier)\s+(pour\s+|pr\s+|de\s+|des\s+)?"
    r"(p\.\s*a\.?|p\.a\b|pa\b|pers\w*\.?)\s*([aâ]g\w*\.?)?\s*(d[ée]p\w*\.?)?\s*[-–]?\s*", _re.I)


def _prefixe_commun(a, b):
    """Préfixe commun de deux noms, coupé à une frontière de mot."""
    k = 0
    while k < min(len(a), len(b)) and a[k].lower() == b[k].lower(): k += 1
    if k < len(a) and k < len(b):
        k = a.rfind(' ', 0, k + 1)
    return a[:max(k, 0)]


def noms_lisibles(rows, nom_ville):
    """Le répertoire FINESS nomme près de 300 établissements « Etablissement d'Hebergement Pour
    Personnes Agees Dependantes » (et ses variantes, souvent sans accents) : illisible, et identique
    d'une ville à l'autre. Affichage : « EHPAD <suite du nom> », ou « EHPAD de <commune> » s'il ne
    reste rien. Deux établissements de la même commune au même nom sont départagés par leur
    adresse. L'adresse de la fiche (URL) ne bouge pas.
    Pour les titres, `nom_court` garde ce qui distingue des noms voisins qui partagent un long
    début (« EHPAD Multisites Terres de Montaigu — Résidence Agora » → « Résidence Agora »)."""
    for r in rows:
        n = r['nom_aff']
        reste = GENERIQUE.sub('', n).strip(' -–,')
        if reste != n or n.strip().upper() == 'EHPAD':
            if n.strip().upper() == 'EHPAD': reste = ''
            r['nom_aff'] = f'EHPAD {reste}' if reste and not reste.upper().startswith('EHPAD') else (
                reste or f"EHPAD de {nom_ville.get(r['cle'], r['ville_nom'])}")
    groupes = collections.defaultdict(list)
    for r in rows: groupes[r['cle']].append(r)
    for lot in groupes.values():
        vus = collections.Counter(r['nom_aff'] for r in lot)
        for r in lot:
            if vus[r['nom_aff']] > 1 and r.get('adr'):
                r['nom_aff'] = f"{r['nom_aff']} – {titre(r['adr'])}"
        for r in lot:
            for x in lot:
                if x is r: continue
                c = _prefixe_commun(r['nom_aff'], x['nom_aff'])
                if len(c) >= 18:
                    suite = r['nom_aff'][len(c):].strip(' -–,')
                    if len(suite) >= 4:
                        r['nom_court'] = suite if suite.upper().startswith('EHPAD') else f'EHPAD {suite}'
                    break


def redirections(ctx):
    """Une commune à établissement unique n'a pas de page : sa page ferait doublon avec la fiche.
    L'adresse reste malgré tout devinable, on y place donc une redirection immédiate vers la fiche.
    Google traite un meta refresh à 0 s comme une redirection permanente : pas de noindex en plus,
    qui brouillerait le signal (redirection + canonique + retrait)."""
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
    # pages institutionnelles existantes (construites par les autres scripts) : même empreinte
    for u in ('/', '/comparer-devis-ehpad/', '/notre-methodologie.html', '/qui-sommes-nous.html', '/retours/'):
        f = os.path.join(OUT, u.strip('/'), 'index.html') if u.endswith('/') else os.path.join(OUT, u.lstrip('/'))
        if os.path.exists(f): date_modif(u, open(f, encoding='utf-8').read())
    groupes['pages'] += [('/', 1.0), ('/comparer-devis-ehpad/', 0.8),
                         ('/notre-methodologie.html', 0.6),
                         ('/qui-sommes-nous.html', 0.4), ('/retours/', 0.4)]
    index = []
    dates = {}
    for t, lst in sorted(groupes.items()):
        morceaux = [lst[i:i + 2000] for i in range(0, len(lst), 2000)] or [[]]
        for k, m in enumerate(morceaux):
            nomf = f'sitemap-{t}.xml' if len(morceaux) == 1 else f'sitemap-{t}-{k + 1}.xml'
            corps = '\n'.join(
                f'  <url><loc>{DOMAINE}{u}</loc><lastmod>{LASTMOD.get(u, [0, AUJ])[1]}</lastmod></url>'
                for u, p in sorted(m))
            dates[nomf] = max(LASTMOD.get(u, [0, AUJ])[1] for u, p in m) if m else AUJ
            open(os.path.join(OUT, nomf), 'w', encoding='utf-8').write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + corps + '\n</urlset>\n')
            index.append(nomf)
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(f'  <sitemap><loc>{DOMAINE}/{f}</loc><lastmod>{dates[f]}</lastmod></sitemap>' for f in index)
        + '\n</sitemapindex>\n')
    print('sitemaps :', ', '.join(index))
    json.dump(LASTMOD, open(LASTMOD_F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)


if __name__ == '__main__':
    main()
