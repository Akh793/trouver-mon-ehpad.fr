# -*- coding: utf-8 -*-
"""INSEE, recensement de la population 2023 (RP 2023, population au 1er janvier 2023, âge détaillé)
→ build/insee/pop75.json : habitants, 75 ans et plus, 85 ans et plus, par commune, arrondissement
municipal (Paris, Lyon, Marseille), département et France.

Source : jeu Melodi DS_RP_TD_POPULATION_AGESEX_PRINC (« Population détaillée par sexe et âge »),
fichier France entière :
  curl -sSL -C - -o insee/rp2023_agesex.parquet \
    "https://api.insee.fr/melodi/file/DS_RP_TD_POPULATION_AGESEX_PRINC_2023/PARQUET"
(sans clé ; reprendre avec -C - si le transfert est coupé). Catalogue Melodi : accès « public »,
aucune licence nommée (29/09/2026).

Les valeurs du recensement sont pondérées (décimales) : on arrondit à l'unité après la somme des âges.
75+ = Y75 … Y99 + Y_GE100 ; 85+ = Y85 … Y99 + Y_GE100 ; total = somme de tous les âges."""
import json, os
import pyarrow.parquet as pq
import pyarrow.compute as pc

D = os.path.dirname(os.path.abspath(__file__))
t = pq.read_table(os.path.join(D, 'rp2023_agesex.parquet'),
                  columns=['GEO', 'GEO_OBJECT', 'TIME_PERIOD', 'RP_MEASURE', 'AGE', 'SEX', 'OBS_VALUE'])
t = t.filter(pc.and_(pc.equal(pc.cast(t['SEX'], 'string'), '_T'),
                     pc.equal(pc.cast(t['RP_MEASURE'], 'string'), 'POP')))
df = t.to_pandas()
df = df[df['GEO_OBJECT'].astype(str).isin(['COM', 'ARM', 'DEP', 'FRANCE', 'FE', 'FRA'])]
assert df['TIME_PERIOD'].astype(str).str.startswith('2023').all()
age = df['AGE'].astype(str)


def n(a):
    if a == 'Y_GE100': return 100
    if a.startswith('Y') and a[1:].isdigit(): return int(a[1:])
    return None


num = age.map(n)
df = df.assign(num=num)
tot = df[df['num'].notna()].groupby(['GEO_OBJECT', 'GEO'], observed=True)['OBS_VALUE'].sum()
p75 = df[df['num'] >= 75].groupby(['GEO_OBJECT', 'GEO'], observed=True)['OBS_VALUE'].sum()
p85 = df[df['num'] >= 85].groupby(['GEO_OBJECT', 'GEO'], observed=True)['OBS_VALUE'].sum()
out = {}
for (o, g), v in tot.items():
    out.setdefault(str(o), {})[str(g)] = [round(v), round(p75.get((o, g), 0)), round(p85.get((o, g), 0))]
meta = {'source': 'INSEE, recensement de la population 2023, DS_RP_TD_POPULATION_AGESEX_PRINC',
        'champs': ['habitants', '75 ans et plus', '85 ans et plus'], 'millesime': 'RP 2023'}
json.dump({'meta': meta, **out}, open(os.path.join(D, 'pop75.json'), 'w', encoding='utf-8'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()})
for k in ('COM', 'ARM', 'DEP'):
    if k in out: print(k, list(out[k].items())[:2])
print('Lyon', out.get('COM', {}).get('69123'), '| France', out.get('FRANCE') or out.get('FE') or out.get('FRA'))
