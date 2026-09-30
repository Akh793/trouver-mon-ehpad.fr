# -*- coding: utf-8 -*-
"""FINESS+ Activités (ANS) → audit/activites_plus.json : offre de chaque EHPAD, en places INSTALLÉES.

Nomenclatures officielles (ANS, dépôt NOS) : TRE_r401 activité, TRE_r404 mode de fonctionnement,
TRE_R279 clientèle, JDV_j353 statut de capacité (08 installé constaté, 09 autorisé),
JDV_j354 habilitation (02 habilité aide sociale).

On ne garde que les activités actives (état « A », sans fin effective) et les capacités installées
(statut 08) : une place autorisée n'est pas une place qui existe. Aucune place « libre » n'est déduite.

Par EHPAD :
  perm   hébergement permanent (924, mode 11), toutes clientèles
  hab    dont places habilitées à l'aide sociale (habilitation 02)
  alz    hébergement permanent réservé aux personnes Alzheimer (924, mode 11, clientèle 436) : unité protégée
  pasa   pôle d'activités et de soins adaptés (961) : présence (1), sans nombre de places
  uhr    unité d'hébergement renforcée (962)
  ht     hébergement temporaire (657, modes 11 / 40 / 43 / 45)
  aj     accueil de jour (mode 21, activité 924 ou 657)
  pfr    plateforme de répit des aidants (963)"""
import gzip, ijson, json, os, sys, collections
D = os.path.dirname(os.path.abspath(__file__))
ehpad = {e['finess'] for e in json.load(open(os.path.join(D, 'finess_ehpad_plus.json'), encoding='utf-8'))}
out = {}
cpt = collections.Counter()
with gzip.open(os.path.join(D, sys.argv[1] if len(sys.argv) > 1 else 'act.json.gz'), 'rb') as fh:
    for pm in ijson.items(fh, 'pmej.item'):
        for e in pm.get('ege') or []:
            fin = e.get('numFinessEge')
            if fin not in ehpad: continue
            o = collections.Counter()
            for a in e.get('activitesExercees') or []:
                cg = a.get('caracteristiquesGeneriques') or {}
                if cg.get('etatObjet') != 'A' or cg.get('dateFinEffectiveActivite'): continue
                t = (((a.get('nature') or {}).get('caracteristiquesSpecifiques') or {}).get('typeActiviteAMSR')) or {}
                act, mode, pub = t.get('activiteSocialeRegulee'), t.get('modeFonctionnement'), t.get('public')
                inst = [c for c in a.get('capacite') or [] if c.get('statutCapacite') == '08']
                # une capacité installée peut figurer deux fois : avec et sans la mention d'habilitation
                tot = max([int(c['nombre']) for c in inst if c.get('habilitation') != '02' and c.get('nombre')] or [0])
                hab = max([int(c['nombre']) for c in inst if c.get('habilitation') == '02' and c.get('nombre')] or [0])
                n = max(tot, hab)
                # Le PASA n'a pas de places propres (il accueille en journée des résidents de l'EHPAD) :
                # FINESS+ l'enregistre avec une capacité de 0. Sa présence vaut activité active.
                # Une activité seulement « autorisée » (statut 09, sans installé) n'est pas comptée.
                # Règle retenue après contrôle croisé avec Atlasanté t_actfiness (05/01/2026) :
                # 2 141 EHPAD en commun, 17 absents de FINESS+, 148 plus récents que la photo de janvier.
                sts = {c.get('statutCapacite') for c in a.get('capacite') or []}
                if act == '961':
                    if '08' in sts or not sts: o['pasa'] = 1
                    continue
                if act == '963': o['pfr'] = 1; continue
                if not n: continue
                if act == '924' and mode == '11':
                    o['perm'] += n; o['hab'] += hab
                    if pub == '436': o['alz'] += n
                elif act == '962': o['uhr'] += n
                elif act == '657' and mode in ('11', '40', '43', '45'): o['ht'] += n
                elif mode == '21' and act in ('924', '657'): o['aj'] += n
            out[fin] = dict(o)
            for k, v in o.items():
                if v: cpt[k] += 1
json.dump(out, open(os.path.join(D, '..', 'audit', 'activites_plus.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(f'{len(out)} EHPAD lus sur {len(ehpad)} ; établissements concernés :', dict(cpt))
