# -*- coding: utf-8 -*-
"""Découpe les données v2 par département et produit les tables nationales du site."""
import json, os, collections, statistics, glob
import pandas as pd

A = 'audit/'
OUT = '../site/data'
os.makedirs(OUT + '/dep', exist_ok=True)

rows = json.load(open('merged_v2.json', encoding='utf-8'))
codes = json.load(open('statut_codes.json', encoding='utf-8'))
fin = {e['finess'].zfill(9): e for e in json.load(open('finess_ehpad.json', encoding='utf-8'))}

# --- complément de statut par code juridique FINESS (concordance ≥ 95 %, ≥ 10 observations)
best = {}
for c, v in codes.items():
    tot = sum(v.values()); b = max(v, key=v.get)
    if tot >= 10 and v[b] / tot >= 0.95:
        best[c] = int(b)
filled = 0
for r in rows:
    if r['statut'] is None:
        c = (fin.get(r['fin'], {}).get('pm_statut') or '')
        if c in best:
            r['statut'], r['statutsrc'] = best[c], 'code'; filled += 1
print('statut complété par code juridique :', filled, '| restants sans statut :', sum(1 for r in rows if r['statut'] is None))

# --- occupation du segment à recalculer pour les statuts fraîchement complétés
seg = json.load(open(A + 'ehpa_occupation_segment.json', encoding='utf-8'))
K = {'Commune densément peuplée': 1, 'Commune de densité intermédiaire': 2, 'Commune rurale': 3}
occ = {}
for s in seg:
    for lib, v in K.items():
        if str(s['densite']).startswith(lib[:22]):
            occ[(v, s['statut'])] = s['occupation']
WH, WN = 129195, 165359
for k in (1, 2, 3):
    occ[(k, 'PUBLIC')] = round((occ[(k, 'Ehpad publics hospitaliers')] * WH + occ[(k, 'Ehpad publics non hospitaliers')] * WN) / (WH + WN), 2)
MAPS = {0: 'PUBLIC', 1: 'Ehpad privés à but non lucratif', 2: 'Ehpad privés à but lucratif'}
for r in rows:
    if r['occ'] is None and r['dens'] and r['statut'] is not None:
        r['occ'] = occ.get((r['dens'], MAPS[r['statut']]))

def dep_of(insee, cp):
    s = insee or ''
    if s[:3] in ('971', '972', '973', '974', '975', '976'): return s[:3]
    if s[:2] == '20': return '2A' if s[:3] < '202' else '2B'
    return s[:2] or (cp or '')[:2]

# --- format compact (ordre documenté dans app.js et MAINTENANCE.md)
COLS = ['fin', 'nom', 'cp', 'ville', 'lat', 'lon', 'p', 'pcd', 'pa', 't12', 't34', 't56', 'maj', 'temp',
        'linge', 'lingeU', 'nIncl', 'nSus', 'inclTxt', 'susTxt', 'ash', 'ashsrc', 'statut', 'statutsrc',
        'cap', 'p2020', 'hasN', 'hasD', 'hasO', 'hasM', 'hasC', 'hasCI', 'alim', 'tel', 'adr', 'pm',
        'siren', 'ouv', 'approx', 'mft', 'mftlib', 'tarif', 'pui', 'dens', 'occ']
byd = collections.defaultdict(list)
for r in rows:
    byd[dep_of(r['insee'], r['cp'])].append([r.get(c) for c in COLS])
bbox, counts = {}, {}
for d, lst in byd.items():
    lats = [x[COLS.index('lat')] for x in lst if x[COLS.index('lat')]]
    lons = [x[COLS.index('lon')] for x in lst if x[COLS.index('lon')]]
    counts[d] = len(lst)
    if lats: bbox[d] = [round(min(lats), 3), round(min(lons), 3), round(max(lats), 3), round(max(lons), 3)]
    open(f'{OUT}/dep/ehpad-{d}.js', 'w', encoding='utf-8').write(
        'ME.dep(%s,%s);' % (json.dumps(d), json.dumps(lst, ensure_ascii=False, separators=(',', ':'))))
print('départements :', len(byd), '| total', sum(counts.values()))

# --- communes (inchangé depuis la v1)
arm = json.load(open(A.replace('audit/', '') + 'arm.json', encoding='utf-8'))
parents = {'75056', '69123', '13055'}
cps_arm = {cp for c in arm for cp in (c.get('codesPostaux') or [])}
com = [c for c in json.load(open('communes_geo.json', encoding='utf-8')) if c['code'] not in parents] + arm
for c in json.load(open('communes_geo.json', encoding='utf-8')):
    if c['code'] in parents:
        rest = [cp for cp in (c.get('codesPostaux') or []) if cp not in cps_arm]
        if rest: com.append({**c, 'codesPostaux': rest})
cbyd = collections.defaultdict(list)
for c in com:
    ctr = (c.get('centre') or {}).get('coordinates')
    if not ctr: continue
    for cp in (c.get('codesPostaux') or []):
        cbyd[c['codeDepartement']].append([cp, c['nom'], round(ctr[1], 4), round(ctr[0], 4), c['code']])
for d, lst in cbyd.items():
    lst.sort()
    open(f'{OUT}/dep/communes-{d}.js', 'w', encoding='utf-8').write(
        'ME.com(%s,%s);' % (json.dumps(d), json.dumps(lst, ensure_ascii=False, separators=(',', ':'))))
cbbox = {d: [round(min(x[2] for x in l), 3), round(min(x[3] for x in l), 3),
             round(max(x[2] for x in l), 3), round(max(x[3] for x in l), 3)] for d, l in cbyd.items()}
print('couples code postal / commune :', sum(len(v) for v in cbyd.values()))

# --- historique de prix par département (séries annuelles 2018 → 2025)
serie = json.load(open(A + 'serie_par_etab.json', encoding='utf-8'))
ANS = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
pbyd = collections.defaultdict(dict)
npx = 0
m = {r['fin']: r for r in rows}
for f9, d in serie.items():
    if f9 not in m: continue
    pts = [d.get(a) for a in ANS]
    dispo = [(a, p) for a, p in zip(ANS, pts) if p]
    if len(dispo) < 2: continue
    (a0, p0), (a1, p1) = dispo[0], dispo[-1]
    annees = int(a1) - int(a0)
    pbyd[dep_of(m[f9]['insee'], m[f9]['cp'])][f9] = {
        'p': [round(x, 2) if x else None for x in pts],
        'e': round(100 * (p1 - p0) / p0, 1),
        'a': round(((p1 / p0) ** (1 / annees) - 1) * 100, 2) if annees else None,
        'd': a0, 'f': a1}
    npx += 1
for d, v in pbyd.items():
    open(f'{OUT}/dep/prix-{d}.js', 'w', encoding='utf-8').write(
        'ME.prix(%s,%s);' % (json.dumps(d), json.dumps(v, separators=(',', ':'))))
print('séries de prix :', npx, 'établissements dans', len(pbyd), 'fichiers')

# --- table départementale : ASH (DREES 2018) + indicateurs DREES + Badiane 2023
ash = json.load(open('ash_dept.json', encoding='utf-8'))
ASH_CODE = {'2A': '20R', '2B': '20R', '69': '69D'}
def bloc_ash(code):
    a = ash.get(code, {})
    return {'nom': a.get('dep'), 'recours': a.get('recours_succession'),
            'obliges': [a.get('obliges_enfants'), a.get('obliges_gendres'), a.get('obliges_petits'), a.get('obliges_autres')],
            'gir56': a.get('gir56'),
            'ded': [a.get('ded_tutelle'), a.get('ded_mutuelle'), a.get('ded_assurance'), a.get('ded_fiscal')]}
drees = {}
for r in json.load(open('drees.json', encoding='utf-8')):
    d = str(r.get('code_dep') or '').strip()
    if not d: continue
    ind, an = r['id_indicateur'], str(r['annee'])
    cur = drees.setdefault(d, {}).get(ind)
    if cur and cur[0] >= an: continue
    try: drees[d][ind] = (an, float(r['value']))
    except: pass
bad = json.load(open(A + 'badiane_dept.json', encoding='utf-8'))
DEP = {}
for d in counts:
    dr = drees.get(d, {}); b = bad.get(d, {})
    DEP[d] = {**bloc_ash(ASH_CODE.get(d, d)),
              'ashM': (bloc_ash('69M') if d == '69' else None),
              'ash_places': dr.get('pa_part_benef_ash_places_heberg'),
              'tx_equip': dr.get('pa_tx_equip_heberg_1000_75p'),
              'n': counts.get(d, 0), 'bbox': bbox.get(d),
              'b_places': b.get('places'), 'b_ash': b.get('places_ash'), 'b_pct_ash': b.get('pct_ash'),
              'b_res': b.get('residents'), 'b_etp': b.get('etp_par_resident')}
lyonm = [c['code'] for c in json.load(open('lyonm.json', encoding='utf-8'))]
open(f'{OUT}/departements.js', 'w', encoding='utf-8').write(
    'window.ME_DEP=%s;\nwindow.ME_BBOX=%s;\nwindow.ME_LYONM=%s;' % (
        json.dumps(DEP, ensure_ascii=False, separators=(',', ':')),
        json.dumps(cbbox, separators=(',', ':')), json.dumps(lyonm, separators=(',', ':'))))
print('table départementale :', len(DEP), '| contexte Badiane pour', sum(1 for v in DEP.values() if v['b_places']))

# --- quartiles de prix par département
PCT = {}
for d, lst in byd.items():
    ps = sorted([x[COLS.index('p')] for x in lst if x[COLS.index('p')]])
    if len(ps) >= 5:
        q = statistics.quantiles(ps, n=4)
        PCT[d] = [round(q[0], 2), round(statistics.median(ps), 2), round(q[2], 2), len(ps)]
allp = sorted([r['p'] for r in rows if r['p']])
q = statistics.quantiles(allp, n=4)
PCT['FR'] = [round(q[0], 2), round(statistics.median(allp), 2), round(q[2], 2), len(allp)]
open(f'{OUT}/prix-reference.js', 'w', encoding='utf-8').write('window.ME_PCT=%s;' % json.dumps(PCT, separators=(',', ':')))
print('prix médian France :', PCT['FR'][1], '€/jour sur', PCT['FR'][3], 'établissements')
json.dump(COLS, open('cols_v2.json', 'w'))
