# trouver-mon-ehpad.fr — site local (v2.2, 11/09/2026)

La page d'accueil est un espace de travail en deux volets : la liste des établissements à gauche, la carte ou la fiche de l'établissement sélectionné à droite. On passe d'un établissement à l'autre sans perdre sa place. Le détail de l'interface est au **§10 de `MAINTENANCE.md`**.

Site statique, sans dépendance réseau au chargement (hors fond de carte IGN et, si vous l'activez, la mesure d'audience). Même gabarit que mes-aides-auto.fr : bande 1 « la situation », bande 2 « la carte », bande 3 « le mode d'emploi », puis sources, questions fréquentes et pied de page.

## Lancer en local

```bash
cd site
python3 -m http.server 8000
# puis ouvrir http://127.0.0.1:8000/
```

Un simple double-clic sur `index.html` fonctionne aussi (les données sont chargées par balises `<script>`, pas par `fetch`), mais un serveur local est préférable : certains navigateurs bloquent le stockage local sur `file://`.

## Arborescence

```
index.html                 page principale — le calculateur (CSS et polices inlinés, scripts en defer)
ehpad/                     l'annuaire : région → département → ville → établissement (7 877 pages)
prix-ehpad/ aides-ehpad/ guides/ etudes/ calcul-reste-a-charge-ehpad/   pages nationales et guides
assets/site.css            feuille de style partagée par les pages de contenu (une requête, mise en cache)
assets/pages.js            consentement et mesure d'usage des pages de contenu
sitemap.xml + sitemap-*.xml  index de sitemaps et sitemaps thématiques
app.js                     moteur : calcul du reste à charge, liste, fiche, carte, comparateur, feuille de route, tests
data.js                    barèmes nationaux, sources, modes d'emploi, questions fréquentes
data/departements.js       table départementale (ASH, indicateurs DREES, emprises) + communes de la Métropole de Lyon
data/prix-reference.js     quartiles de prix par département
data/dep/ehpad-XX.js       les EHPAD du département XX (chargés à la demande)
data/dep/communes-XX.js    couples code postal / commune du département XX (chargés à la demande)
data/dep/prix-XX.js        série de prix 2018-2025 par établissement (chargée à la demande)
vendor/leaflet.js          Leaflet 1.9.4 (local, aucune requête vers un CDN)
vendor/markercluster.js    Leaflet.markercluster 1.5.3 (local)
assets/fonts/              Inter et Poppins auto-hébergés (woff2, sous-ensemble latin)
assets/og-image.png        image de partage 1200×630
notre-methodologie.html    méthode, règles de déduction, limites
qui-sommes-nous.html       objet du site, financement, données personnelles
mentions-legales.html      mentions légales (éditeur et hébergeur à compléter)
404.html  robots.txt  sitemap.xml  llms.txt  manifest.json  favicon.svg
```

## Tests

Ouvrir la console du navigateur et lancer :

```js
runTests()      // 37 tests : APA (couple, seuils, non-versement), réduction d'impôt et plafond par personne,
                // deux résidents, conjoint à domicile, minimum ASH, part de chaque enfant et coût après
                // déduction, couleurs, courbe de prix, disponibilité estimée, fraîcheur, géographie, tri, partage
```

## Performance

- Aucune requête bloquante : CSS et `@font-face` inlinés, polices auto-hébergées avec préchargement, scripts en `defer`.
- Les données ne sont chargées que pour les départements dont l'emprise croise le rayon de recherche : quelques dizaines de kilo-octets, au lieu des 6,1 Mo du jeu complet.
- Mesuré en v2 : 8 requêtes et 254 Ko au chargement, calcul en ~30 ms pour 119 établissements.
- Leaflet et markercluster (181 Ko) ne sont chargés qu'au premier affichage de la carte.
- La mesure d'audience ne part qu'après acceptation **et** au premier geste sur la page.

## Les pages de contenu

7 901 pages sont générées à partir de la base : une par région, par département, par ville d'au moins deux établissements et par établissement documenté, plus les pages nationales, les guides et un baromètre. Elles ne sont jamais écrites à la main : `python3 ../build/seo/build_seo.py` les régénère. Le détail des règles (quelle page existe et pourquoi, comment élargir la couverture) est au **§9 de `MAINTENANCE.md`**.

Chaque page mène au calculateur déjà réglé sur la commune ou l'établissement consulté, par le même mécanisme que le lien de partage : aucune donnée personnelle ne circule.

## À faire avant une mise en ligne

1. Renseigner `ME_GTM_ID` en tête d'`index.html` (vide = aucune mesure d'audience).
2. Compléter l'éditeur et l'hébergeur dans `mentions-legales.html`.
3. Vérifier la licence exacte de chaque jeu de données réutilisé et la formulation d'attribution exigée par l'IGN pour le fond de plan.
4. Vérifier que le domaine servi correspond aux URL canoniques (`https://trouver-mon-ehpad.fr/`) dans `index.html`, les pages de contenu, `sitemap.xml` et `llms.txt`. Le domaine est défini à un seul endroit : `DOMAINE` dans `../build/seo/base.py`.
5. Configurer le serveur pour servir `dossier/index.html` sur les adresses finissant par `/`, et renvoyer `404.html` sur les adresses inconnues.
6. Déclarer `sitemap.xml` dans la Search Console, puis suivre l'indexation par type de page (§9.7 de `MAINTENANCE.md`).

## Rafraîchir les données

**Tout est dans `MAINTENANCE.md`**, à la racine de l'archive — à conserver hors du dossier mis en ligne : les 17 bases de données utilisées, leurs adresses, leurs licences, leurs rythmes de publication, les clés de jointure, le format des 45 colonnes, l'ordre des scripts avec les sorties console attendues, et la procédure de mise à jour mensuelle, annuelle et ponctuelle.

En résumé, depuis `../build` : `python3 build_data_v2.py` puis `split_data_v2.py`, `build_site.py`, `build_pages.py`.
