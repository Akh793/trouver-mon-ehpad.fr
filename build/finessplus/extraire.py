# -*- coding: utf-8 -*-
"""FINESS+ (ANS) → build/finess_ehpad.json : même format que l'extraction du 10/09/2026.

Source : « FINESS - Structures », fichier journalier (data.gouv.fr, Licence Ouverte 2.0).
L'ancienne extraction FINESS « classique » est gelée au 04/05/2026 : c'est FINESS+ qui fait foi.
Les EHPAD retenus : entités géographiques de catégorie 500, sans date de fermeture, état « A » (actif).
Usage : python3 extraire.py str.json.gz"""
import gzip, ijson, json, sys, os

src = sys.argv[1] if len(sys.argv) > 1 else 'str.json.gz'
out, vus = [], 0
with gzip.open(src, 'rb') as fh:
    for pm in ijson.items(fh, 'pmej.item'):
        ig = pm.get('informationsGeneralesPMEJ') or {}
        for e in pm.get('ege') or []:
            vus += 1
            if e.get('categorieentiteGeographiqueExercice') != '500': continue
            g = e.get('informationsGeneralesEGE') or {}
            if g.get('dateFermeture') or e.get('etatObjet') not in ('A', None): continue
            ad = (e.get('adresse') or [{}])[0]
            co = ad.get('coordonneesGeographique') or {}
            tel = None
            for c in e.get('contact') or []:
                t = (c.get('telecom') or {}).get('telephone')
                if t: tel = t; break
            out.append({
                'finess': g.get('numFinessEge'), 'nom': g.get('nomEgeLong') or g.get('nomEgeCourt'),
                'siret': g.get('siret'), 'ouverture': g.get('dateOuverture'),
                'mft': e.get('modefixationtarifaire'),
                'cp': ad.get('codePostal'), 'ville': ad.get('ligneAcheminement'), 'insee': ad.get('cogCommune'),
                'adr': ad.get('ligneQuatre'), 'lon': co.get('coordonneeX'), 'lat': co.get('coordonneeY'),
                'scoreBAN': co.get('scoreBAN'), 'tel': tel,
                'pm_nom': ig.get('denominationPm'), 'pm_siren': ig.get('siren'), 'pm_statut': ig.get('statutJuridique'),
                'maj': e.get('dateDerniereMaj'),
            })
out.sort(key=lambda r: r['finess'] or '')
print(f'{vus} entités géographiques lues, {len(out)} EHPAD ouverts')
json.dump(out, open('finess_ehpad_plus.json', 'w', encoding='utf-8'), ensure_ascii=False)
