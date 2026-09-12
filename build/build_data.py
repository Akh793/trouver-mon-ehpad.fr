# -*- coding: utf-8 -*-
"""Construit les fichiers de données de mon-ehpad.fr à partir des sources ouvertes téléchargées."""
import json, csv, math, os, re, unicodedata
import pandas as pd

OUT = '../site'
os.makedirs(OUT + '/data', exist_ok=True)

def f(x):
    if x is None: return None
    if isinstance(x, str):
        x = x.replace(',', '.').strip()
        if not x: return None
    try:
        v = float(x)
    except Exception:
        return None
    if v != v: return None
    return round(v, 2)

# ---------- FINESS ----------
fin = json.load(open('finess_ehpad.json'))
# géocodage complémentaire (BAN)
geo = {}
with open('geocoded.csv', newline='', encoding='utf-8') as fh:
    for r in csv.DictReader(fh):
        try: sc = float(r.get('result_score') or 0)
        except: sc = 0
        if sc < 0.35 or not r.get('latitude'): continue
        geo[r['id']] = (float(r['latitude']), float(r['longitude']), r.get('result_type'))

# ---------- CNSA prix (2025 cumulé + janvier 2026) ----------
def read_cnsa(path):
    rows = {}
    with open(path, newline='', encoding='utf-8-sig') as fh:
        for r in csv.DictReader(fh, delimiter=';'):
            fid = (r.get('finessEt') or '').strip()
            if fid: rows[fid] = r
    return rows
c2025 = read_cnsa('cnsa_2025.csv')
c2026 = read_cnsa('cnsa_202601.csv')
prix = dict(c2025); prix.update(c2026)          # janvier 2026 prime sur 2025
print('prix CNSA :', len(c2025), '(2025) +', len(c2026), '(01/2026) =', len(prix), 'établissements')

# ---------- CNSA 2020 retraitée (statut, habilitation, capacité, prix 2020) ----------
r2020 = pd.read_pickle('cnsa2020.pkl')
r2020['finesset'] = r2020['finesset'].astype(str).str.zfill(9)
STAT = {'1-Public': 0, '2-Privé non lucratif': 1, '3-Privé commercial': 2}
h2020 = {}
for _, r in r2020.iterrows():
    h2020[r['finesset']] = {
        'statut': STAT.get(str(r['STATUT_JUR']).strip()),
        'ash': 1 if str(r['HAS']).strip().upper() == 'OUI' else (0 if str(r['HAS']).strip().upper() == 'NON' else None),
        'cap': int(r['nb_capins_HP']) if pd.notna(r['nb_capins_HP']) else None,
        'p2020': f(r['prixHebPermCs']),
    }

# ---------- HAS ----------
has = pd.read_pickle('has_ehpad.pkl')
HSTAT = {'Public': 0, 'Privé à but non lucratif': 1, 'Privé commercial': 2}
hmap = {}
for _, r in has.iterrows():
    fid = str(r['finess_geo']).strip().zfill(9)
    d = r['eval_date_fin']
    hmap[fid] = {
        'note': (str(r['indice_qualite']).strip() if pd.notna(r['indice_qualite']) else None),
        'date': (str(d)[:10] if pd.notna(d) else None),
        'org': (str(r['oe_nom']).strip()[:60] if pd.notna(r['oe_nom']) else None),
        'moy': f(r['moy_objectifs_100']),
        'ch': [f(r['cotation_chapitre_1']), f(r['cotation_chapitre_2']), f(r['cotation_chapitre_3'])],
        'ci': int(r['nb_ci_sup_3_5']) if pd.notna(r['nb_ci_sup_3_5']) else None,
        'statut': HSTAT.get(str(r['essms_statut_juridique']).strip()),
        'lat': f(r['latitude']), 'lon': f(r['longitude']),
    }

# ---------- Alim'confiance (par SIRET) ----------
alim = {}
for r in json.load(open('alim.json')):
    s = (r.get('siret') or '').strip()
    if not s: continue
    d = (r.get('date_inspection') or '')[:10]
    prev = alim.get(s)
    if prev and prev[1] >= d: continue
    alim[s] = [r.get('synthese_eval_sanit'), d, r.get('type_suite')]

# ---------- Habilitation ASH : mode de fixation tarifaire (règle CNSA) ----------
MFT_ASH = {'08','09','21','40','41','44','45','48','50','52','56'}

# ---------- assemblage ----------
rows, stats = [], {'geo_ok':0,'geo_ban':0,'geo_has':0,'geo_none':0,'prix':0,'has':0,'alim':0}
mft_vs_csa = {'ok':0,'ko':0}
statut_from_code = {}
for e in fin:
    fid = (e['finess'] or '').strip().zfill(9)
    lat, lon, approx = f(e.get('lat')), f(e.get('lon')), 0
    if lat and lon: stats['geo_ok'] += 1
    elif fid in geo:
        lat, lon = round(geo[fid][0], 6), round(geo[fid][1], 6)
        approx = 1 if geo[fid][2] in ('municipality', 'locality') else 0
        stats['geo_ban'] += 1
    elif fid in hmap and hmap[fid]['lat']:
        lat, lon, approx = hmap[fid]['lat'], hmap[fid]['lon'], 0
        stats['geo_has'] += 1
    else:
        stats['geo_none'] += 1

    p = prix.get(fid)
    if p: stats['prix'] += 1
    o2 = h2020.get(fid, {})
    h = hmap.get(fid)
    if h: stats['has'] += 1
    a = alim.get((e.get('siret') or '').strip())
    if a: stats['alim'] += 1

    csa = f(p.get('prixHebPermCsa')) if p else None
    cda = f(p.get('prixHebPermCda')) if p else None
    mft = (e.get('mft') or '').strip()
    ash_mft = 1 if mft in MFT_ASH else (0 if mft else None)
    if csa or cda:
        ash, ashsrc = 1, 'csa'      # prix aide sociale déclaré 2025/2026
    elif o2.get('ash') is not None:
        ash, ashsrc = o2['ash'], '2020'
    elif ash_mft is not None:
        ash, ashsrc = ash_mft, 'mft'
    else:
        ash, ashsrc = None, None
    if (csa or cda) and ash_mft is not None:
        mft_vs_csa['ok' if ash_mft == 1 else 'ko'] += 1

    statut = o2.get('statut')
    statutsrc = '2020'
    if statut is None and h and h['statut'] is not None:
        statut, statutsrc = h['statut'], 'has'
    if statut is None: statutsrc = None
    if statut is not None and (e.get('pm_statut') or ''):
        statut_from_code.setdefault(e['pm_statut'], {}).setdefault(statut, 0)
        statut_from_code[e['pm_statut']][statut] += 1

    rows.append({
        'fin': fid, 'nom': (e.get('nom') or '').strip(), 'cp': e.get('cp') or '', 'ville': (e.get('ville') or '').title(),
        'insee': e.get('insee') or '', 'lat': lat, 'lon': lon, 'approx': approx,
        'p': f(p.get('prixHebPermCs')) if p else None,
        'pcd': f(p.get('prixHebPermCd')) if p else None,
        'pa': csa or cda,
        't12': f(p.get('TARIF_GIR_12')) if p else None,
        't34': f(p.get('TARIF_GIR_34')) if p else None,
        't56': f(p.get('TARIF_GIR_56')) if p else None,
        'maj': (p.get('DATE_MAJ') or '')[:7] if p else None,
        'temp': f(p.get('prixHebTempCs')) if p else None,
        'linge': f(p.get('PRIX_LINGE')) if p else None,
        'lingeU': (p.get('UNITE_PRIX_LINGE') or '').strip() if p else '',
        'nIncl': sum(1 for i in range(1,12) if p and (p.get('PREST%d'%i) or '').strip() in ('1','true','True')) if p else 0,
        'nSus': sum(1 for i in range(1,12) if p and (p.get('PRESTSUS%d'%i) or '').strip() in ('1','true','True')) if p else 0,
        'inclTxt': ((p.get('AUTRE_PRESTATION_INCLUSE') or '').strip()[:160] if p else ''),
        'susTxt': ((p.get('AUTRES_PRIX_OU_PRESTATIONS') or '').strip()[:160] if p else ''),
        'ash': ash, 'ashsrc': ashsrc, 'statut': statut, 'statutsrc': statutsrc,
        'cap': o2.get('cap'), 'p2020': o2.get('p2020'),
        'hasN': h['note'] if h else None, 'hasD': h['date'] if h else None, 'hasO': h['org'] if h else None,
        'hasM': h['moy'] if h else None, 'hasC': h['ch'] if h else None, 'hasCI': h['ci'] if h else None,
        'alim': a, 'tel': (e.get('tel') or '').strip(), 'adr': (e.get('adr') or '').strip()[:80],
        'pm': (e.get('pm_nom') or '').strip()[:60], 'siren': (e.get('pm_siren') or '').strip(),
        'ouv': (e.get('ouverture') or '')[:4],
    })

print('EHPAD :', len(rows))
print('couverture :', stats)
print('concordance mft/prix aide sociale :', mft_vs_csa)
json.dump(rows, open('merged.json', 'w'), ensure_ascii=False)
json.dump(statut_from_code, open('statut_codes.json','w'))
