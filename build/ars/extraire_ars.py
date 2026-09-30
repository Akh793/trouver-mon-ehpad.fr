# -*- coding: utf-8 -*-
"""Rapports du plan national d'inspection-contrôle des EHPAD 2022-2024, publiés par les ARS
→ build/ars/ars_inspections.json

Source : page nationale https://www.ars.sante.fr/publication-des-rapports-du-plan-de-controle-des-ehpad
et les 12 pages régionales qu'elle cite (Corse et DROM : « donnée indisponible »).

Règles (29/09/2026) :
  · on ne lit que les pages HTML des ARS (robots.txt respecté, 10 s entre deux requêtes) ; aucun
    document n'est téléchargé, résumé ni noté : le site affiche un lien, daté, vers le document de l'ARS ;
  · un document n'est rattaché à un EHPAD que si son nom porte le numéro FINESS de l'établissement
    (cas de l'Île-de-France). Aucun rapprochement par nom ou par commune : une erreur d'appariement
    attribuerait à tort un rapport d'inspection à un établissement ;
  · ailleurs, la fiche renvoie à la page de l'ARS de la région, sans dire si l'établissement y figure.

Usage : python3 ars/extraire_ars.py            (télécharge les pages, puis extrait)
        python3 ars/extraire_ars.py --local    (réutilise les pages déjà enregistrées dans ars/pages/)"""
import html, json, os, re, subprocess, sys, time, datetime

D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'pages')
HUB = 'https://www.ars.sante.fr/publication-des-rapports-du-plan-de-controle-des-ehpad'
# nom affiché par l'ARS → identifiant de région du site (seo/geo.py)
REG = {'Auvergne-Rhône-Alpes': 'auvergne-rhone-alpes', 'Bourgogne-Franche-Comté': 'bourgogne-franche-comte',
       'Bretagne': 'bretagne', 'Centre-Val de Loire': 'centre-val-de-loire', 'Grand Est': 'grand-est',
       'Hauts-de-France': 'hauts-de-france', 'Ile-de-France': 'ile-de-france', 'Normandie': 'normandie',
       'Nouvelle-Aquitaine': 'nouvelle-aquitaine', 'Occitanie': 'occitanie',
       'Pays de la Loire': 'pays-de-la-loire', "Provence-Alpes-Côte d'Azur": 'provence-alpes-cote-d-azur'}
TYPES = {'LD': 'Lettre de décision', 'RP': 'Rapport d’inspection', 'RAP': 'Rapport d’inspection',
         'SUITE': 'Suites données'}


def get(url, dest):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '90', '--retry', '3', '-o', dest, '-w', '%{http_code}', url],
                       capture_output=True, text=True)
    if r.stdout != '200': sys.exit(f'{url} → {r.stdout} {r.stderr}')
    time.sleep(10)          # Crawl-delay: 10 (robots.txt des ARS)


def texte(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', t)).replace('\xa0', ' ')).strip()


def main():
    local = '--local' in sys.argv
    os.makedirs(P, exist_ok=True)
    if not local: get(HUB, os.path.join(P, 'hub.html'))
    s = open(os.path.join(P, 'hub.html'), encoding='utf-8', errors='ignore').read()
    regions = {}
    for u, n in re.findall(r'href="(https://www\.[a-z-]+\.ars\.sante\.fr/[^"]+)"[^>]*>([^<]+)</a>', s):
        n = html.unescape(n).replace('’', "'").strip()
        if n not in REG: continue
        regions[REG[n]] = {'nom': n.replace('Ile-', 'Île-'), 'url': u}
    assert len(regions) == 12, regions
    fins = {e['finess'] for e in json.load(open(os.path.join(D, '..', 'finessplus', 'finess_ehpad_plus.json'), encoding='utf-8'))}
    docs = {}
    for cle, r in regions.items():
        f = os.path.join(P, cle + '.html')
        if not local: get(r['url'], f)
        s = open(f, encoding='utf-8', errors='ignore').read()
        base = re.match(r'https://[^/]+', r['url']).group(0)
        # date de la liste publiée par l'ARS (IDF : « liste des rapports publiés au 26 juin 2026 »)
        m = re.search(r'liste des rapports publiés au ([0-9]{1,2} \w+ 20[0-9]{2})', texte(s))
        if m: r['liste_au'] = m.group(1)
        n = 0
        for h, t in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
            if '/media/' not in h: continue
            t = texte(t)
            for fin in set(re.findall(r'(?<![0-9])([0-9]{2}[0-9AB][0-9]{6})(?![0-9])', t)):
                if fin not in fins: continue
                ty = re.match(r'[0-9AB]{9}_\s*([A-Z]+)_', t)
                ty = TYPES.get(ty.group(1), 'Document') if ty else 'Document'
                dt = re.search(r'(20[0-9]{2})-([0-9]{2})-([0-9]{2})', t)
                lib = re.sub(r'\s*\((pdf|xlsx?|docx?)[^)]*\)\s*$', '', t)
                d = {'type': ty, 'url': (base + h) if h.startswith('/') else h, 'libelle': lib, 'region': cle}
                if dt: d['date'] = f'{dt.group(3)}/{dt.group(2)}/{dt.group(1)}'
                if all(x['url'] != d['url'] for x in docs.get(fin, [])):
                    docs.setdefault(fin, []).append(d); n += 1
        r['documents_rattaches'] = n
        print(f"{r['nom']} : {n} documents rattachés par numéro FINESS")
    out = {'consulte': datetime.date.today().strftime('%d/%m/%Y'), 'source': HUB,
           'regions': regions, 'documents': docs}
    json.dump(out, open(os.path.join(D, 'ars_inspections.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(docs)} EHPAD avec au moins un document ARS rattaché par FINESS')


if __name__ == '__main__':
    main()
