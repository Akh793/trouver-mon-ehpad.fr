# -*- coding: utf-8 -*-
"""Génère worker-mesure/chemins.js : la liste des chemins que le compteur accepte.

Seuls les chemins du sitemap sont comptés à leur nom. Tout autre chemin — une
adresse fabriquée par un robot, une faute de frappe qui mène à la page 404 —
est compté sous « /(hors-liste) » : le volume reste visible, mais il ne peut
pas polluer le classement des pages les plus vues.

À relancer, puis redéployer le Worker (wrangler deploy), chaque fois que des
pages sont ajoutées au site. Une page absente de la liste n'est pas perdue :
ses vues tombent dans « /(hors-liste) », ce qui signale l'oubli.
"""
import re, glob, os, json

SITE = '../site'
SORTIE = '../worker-mesure/chemins.js'


def main():
    chemins = set()
    for f in glob.glob(os.path.join(SITE, 'sitemap-*.xml')):
        txt = open(f, encoding='utf-8').read()
        chemins.update(re.findall(r'<loc>https://trouver-mon-ehpad\.fr([^<]*)</loc>', txt))
    if len(chemins) < 1000:
        raise SystemExit(f'seulement {len(chemins)} chemins lus : sitemaps absents ou vides, rien n’est écrit')
    liste = '\n'.join(sorted(chemins))
    js = ('// Généré par build/chemins_mesure.py — ne pas modifier à la main.\n'
          f'// {len(chemins)} chemins, lus dans les sitemaps du site.\n'
          'export const CHEMINS = new Set(' + json.dumps(liste, ensure_ascii=False) + ".split('\\n'));\n")
    open(SORTIE, 'w', encoding='utf-8').write(js)
    print(f'{SORTIE} : {len(chemins)} chemins, {len(js.encode()) // 1024} Ko')


if __name__ == '__main__':
    main()
