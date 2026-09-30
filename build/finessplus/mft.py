# -*- coding: utf-8 -*-
"""Mode de fixation tarifaire des EHPAD, depuis FINESS+ et la nomenclature officielle TRE_R74 (ANS, NOS).
Remplace audit/finess_classique_500.json (extraction FINESS « classique », gelée au 04/05/2026).
Même format : {finess: {mft, libmft, siret, tel, maj}}. Libellé ANS : « ARS-PCD, Tarif global, habilité aide sociale… »."""
import csv, io, json, os
D = os.path.dirname(os.path.abspath(__file__))
lib = {}
with open(os.path.join(D, 'TRE_R74-ModeFixationTarifaire.tabs'), encoding='utf-8') as fh:
    lignes = fh.read().splitlines()
entete = next(i for i, l in enumerate(lignes) if l.startswith('<OID>;<Code>'))
for l in lignes[entete + 1:]:
    p = l.split(';')
    if len(p) > 2 and p[1]: lib[p[1]] = p[2]
e = json.load(open(os.path.join(D, 'finess_ehpad_plus.json'), encoding='utf-8'))
out = {r['finess']: {'mft': r['mft'], 'libmft': lib.get(r['mft']), 'siret': r['siret'], 'tel': r['tel'], 'maj': (r.get('maj') or '')[:10]}
       for r in e}
sans = [k for k, v in out.items() if not v['libmft']]
json.dump(out, open(os.path.join(D, '..', 'audit', 'finess_plus_500.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(out), 'EHPAD ;', len(lib), 'libellés TRE_R74 ; sans libellé :', len(sans), sans[:5])
