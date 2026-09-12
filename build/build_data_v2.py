# -*- coding: utf-8 -*-
"""
mon-ehpad.fr — construction des données v2.
Reprend merged.json (v1) et applique les corrections et enrichissements de la v2 :
  1. habilitation à l'aide sociale depuis le libellé officiel FINESS (3 états)
  2. mode de tarification (global / partiel / PUV) et pharmacie à usage intérieur
  3. indicateur HAS documenté (nb_ci_atteints) au lieu de nb_ci_sup_3_5
  4. appariement Alim'confiance élargi (SIREN + commune, candidat unique)
  5. degré de densité de la commune (INSEE) et taux d'occupation du segment (DREES EHPA 2023)
Entrées attendues dans build/ et build/audit/ — voir MAINTENANCE.md.
"""
import json, csv, collections, unicodedata, re, os
import pandas as pd

A = 'audit/'
out_dir = '../site/data'

# ---------------------------------------------------------------- 1. socle v1
rows = json.load(open('merged.json', encoding='utf-8'))
m = {r['fin']: r for r in rows}
print('socle v1 :', len(rows), 'EHPAD')

# ------------------------------------------- 2. libellés officiels FINESS (MFT)
cl = json.load(open(A + 'finess_classique_500.json', encoding='utf-8'))
HAB = {'40', '41', '44', '45', '50', '56'}
NONHAB = {'42', '43', '46', '47', '51', '55'}
stats = collections.Counter()
for f9, r in m.items():
    c = cl.get(f9)
    r['mft'] = c['mft'] if c else None
    r['mftlib'] = c['libmft'] if c else None
    lib = (c['libmft'] if c else '') or ''
    r['tarif'] = 'G' if 'Tarif global' in lib else ('P' if 'Tarif partiel' in lib else ('V' if 'PUV' in lib else None))
    r['pui'] = 1 if 'recours PUI' in lib else (0 if lib else None)
    code = c['mft'] if c else None
    off = 1 if code in HAB else (0 if code in NONHAB else None)
    declare_ash = bool(r['pa'])                      # tarif « aide sociale » déclaré à la CNSA 2025/2026
    if off == 1:
        r['ash'], r['ashsrc'] = 1, 'finess'
    elif off == 0 and declare_ash:
        r['ash'], r['ashsrc'] = 2, 'divergence'      # habilitation partielle probable, à confirmer
    elif off == 0:
        r['ash'], r['ashsrc'] = 0, 'finess'
    elif declare_ash:
        r['ash'], r['ashsrc'] = 1, 'csa'
    elif r['ash'] is not None and r['ashsrc'] in ('2020', 'mft'):
        pass                                          # on garde la déduction v1, déjà étiquetée
    else:
        r['ash'], r['ashsrc'] = None, None
    stats[(r['ash'], r['ashsrc'])] += 1
print('habilitation ASH :', {f'{k[0]}/{k[1]}': v for k, v in sorted(stats.items(), key=lambda x: str(x[0]))})
print('  habilités', sum(v for k, v in stats.items() if k[0] == 1),
      '| non habilités', sum(v for k, v in stats.items() if k[0] == 0),
      '| à confirmer', sum(v for k, v in stats.items() if k[0] == 2),
      '| inconnu', sum(v for k, v in stats.items() if k[0] is None))
print('tarification :', collections.Counter(r['tarif'] for r in rows))

# ------------------------------------------------- 3. indicateur HAS documenté
has = pd.read_pickle('has_ehpad.pkl')
ci = {str(r['finess_geo']).strip().zfill(9): (int(r['nb_ci_atteints']) if pd.notna(r['nb_ci_atteints']) else None)
      for _, r in has.iterrows()}
n = 0
for f9, r in m.items():
    if f9 in ci:
        r['hasCI'] = ci[f9]; n += 1
print('critères impératifs atteints renseignés :', n)

# ------------------------------- 4. Alim'confiance : appariement SIREN + commune
def norm(s):
    s = unicodedata.normalize('NFD', (s or '').upper())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9]+', ' ', s).strip()

alim = json.load(open('alim.json', encoding='utf-8'))
fin = {e['finess'].zfill(9): e for e in json.load(open('finess_ehpad.json', encoding='utf-8'))}
by_siret, by_siren = {}, collections.defaultdict(list)
for f9, e in fin.items():
    s = (e.get('siret') or '').strip()
    if len(s) == 14:
        by_siret[s] = f9
        by_siren[s[:9]].append(f9)
ajout = 0
for insp in alim:
    s = (insp.get('siret') or '').strip()
    if len(s) != 14 or s in by_siret:
        continue
    cand = by_siren.get(s[:9], [])
    cp, com = (insp.get('code_postal') or '').strip(), norm(insp.get('com_name'))
    same = [f9 for f9 in cand if m.get(f9) and (m[f9]['cp'] == cp or norm(m[f9]['ville']) == com)]
    if len(same) != 1:
        continue
    f9 = same[0]
    d = (insp.get('date_inspection') or '')[:10]
    cur = m[f9].get('alim')
    if cur and cur[1] >= d:
        continue
    m[f9]['alim'] = [insp.get('synthese_eval_sanit'), d, insp.get('type_suite')]
    ajout += 1
print("Alim'confiance : +", ajout, '→', sum(1 for r in rows if r['alim']), 'établissements')

# --------------------------- 5. densité de la commune + occupation du segment
d = pd.ExcelFile(A + 'densite2026.xlsx').parse('Maille communale', header=4)
dens = {str(r['CODGEO']).strip(): int(r['DENS']) for _, r in d.iterrows() if str(r['DENS']).strip() in ('1', '2', '3')}
# la grille de densité est publiée au niveau de la commune : les arrondissements
# de Paris, Lyon et Marseille y sont absents, on les rattache à leur commune.
def code_dens(insee):
    s = insee or ''
    if s[:3] == '751': return '75056'
    if s[:3] == '132': return '13055'
    if s[:2] == '69' and s[:3] == '693' and '69381' <= s <= '69389': return '69123'
    return s
seg = json.load(open(A + 'ehpa_occupation_segment.json', encoding='utf-8'))
K = {'Commune densément peuplée': 1, 'Commune de densité intermédiaire': 2, 'Commune rurale': 3}
occ = {}
for s in seg:
    for lib, v in K.items():
        if str(s['densite']).startswith(lib[:22]):
            occ[(v, s['statut'])] = s['occupation']
WH, WN = 129195, 165359      # places publiques hospitalières / non hospitalières (Badiane 2023)
for k in (1, 2, 3):
    a, b = occ.get((k, 'Ehpad publics hospitaliers')), occ.get((k, 'Ehpad publics non hospitaliers'))
    occ[(k, 'PUBLIC')] = round((a * WH + b * WN) / (WH + WN), 2)
MAPS = {0: 'PUBLIC', 1: 'Ehpad privés à but non lucratif', 2: 'Ehpad privés à but lucratif'}
nd = no = 0
for f9, r in m.items():
    r['dens'] = dens.get(code_dens(r['insee']))
    r['occ'] = None
    if r['dens'] and r['statut'] is not None:
        r['occ'] = occ.get((r['dens'], MAPS[r['statut']]))
    nd += bool(r['dens']); no += bool(r['occ'])
print('densité connue :', nd, '| taux d’occupation du segment :', no)

json.dump(rows, open('merged_v2.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('→ merged_v2.json écrit')
