# -*- coding: utf-8 -*-
"""Socle commun du générateur de pages : chargement des données, slugs, statistiques, formats."""
import json, re, unicodedata, statistics, collections, base64, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import geo

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # …/build
SITE = os.path.join(B, '..', 'site')

DOMAINE = 'https://trouver-mon-ehpad.fr'
MARQUE = 'Trouver mon EHPAD'
CONTACT = 'contact@trouver-mon-ehpad.fr'
MOIS = 30.5                       # jours — cohérent avec META.month de data.js
MAJ = '11/09/2026'                # dernière vérification des règles nationales
MAJ_ISO = '2026-09-11'
CNSA_MAJ = 'janvier 2026'         # dernier fichier de prix publié par la CNSA

# ---------------------------------------------------------------- chargement
def charge():
    rows = json.load(open(os.path.join(B, 'merged_v2.json'), encoding='utf-8'))
    com = json.load(open(os.path.join(B, 'communes_geo.json'), encoding='utf-8'))
    arm = json.load(open(os.path.join(B, 'arm.json'), encoding='utf-8'))
    serie = json.load(open(os.path.join(B, 'audit', 'serie_par_etab.json'), encoding='utf-8'))
    communes = {c['code']: c for c in com}
    for c in arm:
        communes[c['code']] = c
    for r in rows:
        c = communes.get(r['insee'])
        r['ville_nom'] = c['nom'] if c else titre(r['ville'])
        r['dep'] = dep_of(r['insee'], r['cp'])
        r['serie'] = serie_calculee(serie.get(r['fin']))
    return rows, communes

ANNEES = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']

def serie_calculee(brut):
    """Série annuelle du tarif d'hébergement → évolution totale et annualisée.
    Même calcul que split_data_v2.py, pour que le site et les pages disent la même chose."""
    if not brut: return None
    pts = [brut.get(a) for a in ANNEES]
    dispo = [(a, p) for a, p in zip(ANNEES, pts) if p]
    if len(dispo) < 2: return None
    (a0, p0), (a1, p1) = dispo[0], dispo[-1]
    ans = int(a1) - int(a0)
    return {'p': [round(x, 2) if x else None for x in pts],
            'e': round(100 * (p1 - p0) / p0, 1),
            'a': round(((p1 / p0) ** (1 / ans) - 1) * 100, 2) if ans else None,
            'd': a0, 'f': a1}

def dep_of(insee, cp):
    s = insee or ''
    if s[:3] in ('971', '972', '973', '974', '975', '976'): return s[:3]
    if s[:2] == '20': return '2A' if s[:3] < '202' else '2B'
    return s[:2] or (cp or '')[:2]

# ------------------------------------------------------------------- textes
def sansacc(s):
    s = unicodedata.normalize('NFD', s or '')
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

def slug(s):
    s = sansacc(s).lower().replace("'", ' ').replace('’', ' ')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return re.sub(r'-{2,}', '-', s)

PETITS = {'de', 'du', 'des', 'sur', 'sous', 'en', 'et', 'aux', 'au', 'lès', 'd', 'l'}
def titre(s):
    """Remet en forme un nom écrit tout en majuscules : « EHPAD LES TILLEULS » → « EHPAD Les Tilleuls »."""
    s = (s or '').strip()
    if not s: return ''
    if s != s.upper(): return s
    mots = re.split(r'(\s+|-|’|\')', s.lower())
    out = []
    for m in mots:
        if not m.strip() or m in ('-', '’', "'"): out.append(m); continue
        out.append(m if (m in PETITS and out) else m[:1].upper() + m[1:])
    return ''.join(out)

ACRONYMES = {'Ehpad': 'EHPAD', 'Ehpa': 'EHPA', 'Usld': 'USLD', 'Uhr': 'UHR', 'Ccas': 'CCAS',
             'Chu': 'CHU', 'Chr': 'CHR', 'Ch': 'CH', 'Chi': 'CHI', 'Ssiad': 'SSIAD', 'Had': 'HAD',
             'Marpa': 'MARPA', 'Mapa': 'MAPA', 'Mas': 'MAS', 'Fam': 'FAM', 'Cias': 'CIAS',
             'Pasa': 'PASA', 'Uva': 'UVA', 'Hopital': 'Hôpital', 'Hopitaux': 'Hôpitaux'}


def nom_etab(r):
    n = titre(re.sub(r'\s+', ' ', r['nom']).strip())
    return re.sub(r'\b(' + '|'.join(ACRONYMES) + r')\b', lambda m: ACRONYMES[m.group(1)], n)

def esc(s):
    return (str(s if s is not None else '')
            .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))

# ------------------------------------------------------------------ nombres
def nb(n, d=0):
    if n is None: return '—'
    s = f'{n:,.{d}f}'.replace(',', ' ').replace('.', ',')
    return s

def eur(n):
    return '—' if n is None else nb(round(n)) + ' €'

def eur2(n):
    return '—' if n is None else nb(n, 2) + ' €'

def pct(n, d=1):
    if n is None: return '—'
    return ('+' if n > 0 else '') + nb(n, d) + ' %'

def mois_eur(prix_jour):
    """Prix journalier CNSA → coût mensuel d'hébergement."""
    return None if prix_jour is None else prix_jour * MOIS

# ------------------------------------------------------------- statistiques
def mediane(vals):
    v = sorted(x for x in vals if x is not None)
    return statistics.median(v) if v else None

def stats(lot):
    """Statistiques d'un ensemble d'établissements. Aucune valeur inventée :
    tout indicateur non calculable vaut None et n'est pas affiché."""
    prix = [r['p'] for r in lot if r['p']]
    evol = [r['serie']['e'] for r in lot if r.get('serie') and r['serie'].get('e') is not None] \
        if any(r.get('serie') for r in lot) else []
    st = collections.Counter(r['statut'] for r in lot if r['statut'] is not None)
    return {
        'n': len(lot),
        'n_prix': len(prix),
        'med': mediane(prix),
        'mini': min(prix) if prix else None,
        'maxi': max(prix) if prix else None,
        'q1': statistics.quantiles(prix, n=4)[0] if len(prix) >= 5 else None,
        'q3': statistics.quantiles(prix, n=4)[2] if len(prix) >= 5 else None,
        'ash': sum(1 for r in lot if r['ash'] == 1),
        'ash_conf': sum(1 for r in lot if r['ash'] == 2),
        'public': st.get(0, 0), 'assoc': st.get(1, 0), 'prive': st.get(2, 0),
        'has': sum(1 for r in lot if r['hasN']),
        'has_ab': sum(1 for r in lot if r['hasN'] in ('A', 'B')),
        'cap': sum(r['cap'] for r in lot if r['cap']) or None,
        'evol_med': mediane(evol) if len(evol) >= 5 else None,
        'n_evol': len(evol),
    }

# --------------------------------------------- lien profond vers le calculateur
def lien_calc(cp=None, insee=None, rayon=20, finess=None):
    """Ouvre le calculateur déjà réglé sur la commune (et l'établissement) consultés.
    L'état est encodé comme un lien de partage : aucun nom, aucune donnée personnelle."""
    o = {}
    if cp: o['cp'] = cp
    if rayon: o['rayon'] = rayon
    if insee: o['i'] = insee
    if finess: o['f'] = finess
    if not o: return '/'
    s = base64.b64encode(json.dumps(o, ensure_ascii=False).encode()).decode()
    return '/#s=' + s
