# MAINTENANCE — mon-ehpad.fr

**Version 2.4 du site · document écrit le 11/09/2026.**

Ce fichier est le mode d'emploi complet de la mise à jour du site : toutes les bases de données
utilisées, leur adresse, leur licence, leur rythme de publication, la clé qui les relie, le format
exact des fichiers produits, l'ordre des scripts et les contrôles à passer avant de publier.

Tout ce qui suit a été réellement exécuté pour produire la v2. Les rares points que je n'ai **pas**
pu revérifier au moment d'écrire ce document (l'accès réseau de l'environnement de construction
était coupé) sont marqués ⚠️ **à revérifier**. Rien n'est deviné : quand une adresse exacte n'a pas
été conservée, le document dit comment la retrouver plutôt que d'en inventer une.

Légende : ✅ vérifié · ⚠️ à revérifier ou daté · ❌ n'existe pas / non disponible.

---

## 0. En trente secondes

```bash
cd build
python3 build_data_v2.py     # croise les sources        → merged_v2.json
python3 split_data_v2.py     # découpe par département   → ../site/data/**
python3 build_site.py        # assemble                  → ../site/index.html
python3 build_pages.py       # pages annexes             → ../site/*.html
python3 seo/build_seo.py     # 7 900 pages de contenu    → ../site/ehpad/**, /guides/**, sitemaps
cd ../site && python3 -m http.server 8000     # puis http://127.0.0.1:8000/
```

Dans la console du navigateur : `runTests()` doit renvoyer `true` (37 tests).

Les scripts ne téléchargent rien : ils lisent des fichiers déjà présents dans `build/`.
Le téléchargement est l'étape manuelle décrite au **§4**.

---

## 1. Carte du projet

```
trouver-mon-ehpad/
├── README.md                   présentation du dépôt
├── DEPLOIEMENT.md              la mise en ligne, pas à pas
├── MAINTENANCE.md              ← ce fichier
├── .gitignore                  les données sources ne sont pas versionnées
├── .github/workflows/pages.yml publication sur GitHub Pages, avec garde-fous
├── build/                      atelier : sources téléchargées + scripts + gabarits
│   ├── build_data_v2.py        croisement de toutes les sources        → merged_v2.json
│   ├── split_data_v2.py        découpage par département               → ../site/data/**
│   ├── build_site.py           assemble index.html (CSS + FAQ inlinés)
│   ├── build_pages.py          méthodologie, qui-sommes-nous, mentions, 404
│   ├── seo/                    générateur des pages de contenu (voir §10)
│   ├── seo.css                 styles propres aux pages de contenu
│   ├── seo_pages.js            script commun aux pages de contenu (consentement, mesure d'usage)
│   ├── index.template.html     gabarit de la page d'accueil (SEO, JSON-LD, formulaire)
│   ├── site.css                feuille de style unique, inlinée dans chaque page
│   ├── fontface.css            @font-face des polices auto-hébergées
│   ├── fetch.py                fonction de téléchargement avec reprise (get(url))
│   ├── vendor/                 Leaflet 1.9.4 + Leaflet.markercluster 1.5.3 (copiés dans site/)
│   ├── audit/                  fichiers issus de l'audit des API (contexte, rotation, occupation…)
│   ├── *.mjs                   scripts Playwright de vérification (tests, perf, captures, og)
│   └── (fichiers sources téléchargés : voir §2)
└── site/                       ce qui est mis en ligne — rien d'autre
    ├── index.html  app.js  data.js
    ├── ehpad/                   région, département, ville, établissement (voir §10)
    ├── prix-ehpad/  aides-ehpad/  guides/  etudes/  calcul-reste-a-charge-ehpad/
    ├── assets/site.css  assets/pages.js   partagés par toutes les pages de contenu
    ├── sitemap.xml + sitemap-*.xml        index et sitemaps thématiques
    ├── data/departements.js  data/prix-reference.js  data/dep/*.js
    ├── notre-methodologie.html  qui-sommes-nous.html  mentions-legales.html  404.html
    ├── assets/fonts/*.woff2  assets/og-image.png  favicon.svg
    ├── vendor/leaflet.js  vendor/markercluster.js  (+ CSS)
    └── robots.txt  sitemap.xml  llms.txt  manifest.json  README.md
```

Règle de séparation : **`build/` ne se met jamais en ligne.** Seul `site/` est publié.

---

## 2. Les bases de données, une par une

### 2.1 Tableau de synthèse

| # | Base | Ce qu'elle apporte au site | Fichier local dans `build/` | Licence | Rythme annoncé | Dernière version utilisée |
|---|---|---|---|---|---|---|
| 1 | **CNSA — prix et tarifs, données brutes** | prix hébergement (chambre seule / double / aide sociale), tarifs GIR 1-2, 3-4, 5-6, accueil temporaire, linge, prestations incluses / en sus, date de mise à jour déclarée | `cnsa_2025.csv`, `cnsa_202601.csv` | ⚠️ **non déclarée** | mensuel | janvier 2026 |
| 2 | **CNSA — archives annuelles 2018 → 2025** | la courbe d'évolution du prix de chaque établissement | `audit/prix/2018.csv` … `2025.csv` | ⚠️ non déclarée | annuel | 2025 |
| 3 | **CNSA — données retraitées 2018-2020** | statut juridique, capacité, habilitation historique | `cnsa_2020_retraitee.xlsx` → `cnsa2020.pkl` | ⚠️ non déclarée | annuel (figé) | 2020 |
| 4 | **FINESS+ Structures (ANS)** | identité, adresse, SIRET, coordonnées, téléphone, gestionnaire, SIREN, date d'ouverture, code MFT | `finess_ehpad.json` (7 417 lignes) | Licence Ouverte 2.0 | quotidien | 10/09/2026 |
| 5 | **FINESS extraction classique** | **libellé officiel** du mode de fixation tarifaire → habilitation aide sociale, tarif global/partiel, PUI | `audit/finess_etab.csv` → `audit/finess_classique_500.json` | Licence Ouverte | bimestriel | 12/05/2026 |
| 6 | **HAS — évaluations ESSMS** | note A à D, date, organisme évaluateur, moyenne des objectifs, cotations de chapitre, **critères impératifs atteints** | `has_essms.parquet` → `has_ehpad.pkl` | Licence Ouverte 2.0 | quotidien | 10/09/2026 |
| 7 | **Alim'confiance (DGAL)** | résultat et date de l'inspection d'hygiène, suites données | `alim.json` (2 357 inspections) | Licence Ouverte | quotidien | 10/09/2026 |
| 8 | **DREES — enquête EHPA 2023** | taux d'occupation par statut × densité de commune, rotation des résidents, délai d'entrée | `audit/ehpa2023_*.xlsx` → `audit/ehpa_occupation_segment.json`, `audit/rotation.json` | Licence Ouverte 2.0 | ponctuel | publiée le 04/11/2025 |
| 9 | **DREES — Badiane 2023** | contexte départemental : places, % de places habilitées ASH, résidents, ETP par résident | `audit/badiane2023.xlsx` → `audit/badiane_dept.json` | Licence Ouverte 2.0 | annuel | publiée le 27/07/2026 |
| 10 | **DREES — indicateurs sociaux départementaux** | part des bénéficiaires de l'ASH, taux d'équipement pour 1 000 habitants de 75 ans et plus | `drees.json` (8 452 lignes) | Licence Ouverte 2.0 | annuel | données 2024, publiées le 03/09/2026 |
| 11 | **DREES — modalités départementales de gestion de l'ASH** | recours sur succession, obligés sollicités, GIR 5-6, charges déductibles, **par département** | `ash_modalites.xlsx` → `ash_dept.json` (100 entrées) | Licence Ouverte 2.0 | ponctuel | ⚠️ **données 2018** |
| 12 | **INSEE — grille de densité des communes 2026** | degré de densité (1 dense, 2 intermédiaire, 3 rural) pour croiser avec l'occupation EHPA | `audit/densite2026.xlsx` | Licence Ouverte | annuel | 2026 |
| 13 | **INSEE — indice des prix à la consommation** | référence de comparaison de l'évolution des prix (+17,2 % de 2018 à 2025) | saisi à la main dans `site/data.js` (`INFLATION`) | Licence Ouverte | mensuel | moyennes annuelles 2019-2025 |
| 14 | **geo.api.gouv.fr — communes** | couples code postal / commune, centres, codes département | `communes_geo.json` (34 969), `arm.json`, `lyonm.json` | Licence Ouverte | continu | 10/09/2026 |
| 15 | **Base adresse nationale** | géocodage des établissements sans coordonnées FINESS | `togeo.csv` → `geocoded.csv` | Licence Ouverte 2.0 | quotidien | 10/09/2026 |
| 16 | **IGN Géoplateforme (WMTS)** | fond de carte, appelé en direct par le navigateur | aucun | conditions IGN ⚠️ à vérifier | continu | — |
| 17 | **OpenFisca-France** | formule de l'APA en établissement + validation à 0,00 € près | `of.json`, `params.json` | AGPL (code) / Licence Ouverte (paramètres) | continu | 10/09/2026 |

⚠️ **Point à traiter avant mise en ligne** : le jeu le plus central du site — les prix CNSA — **ne déclare
aucune licence** sur data.gouv.fr. C'est écrit tel quel dans les mentions légales ; une demande de
précision à la CNSA reste à faire.

### 2.2 Adresses de téléchargement

**Pages de jeu de données** (toujours valables, c'est de là qu'on récupère l'URL de la ressource du jour) :

| Base | Page |
|---|---|
| CNSA prix bruts (#1, #2) | `https://www.data.gouv.fr/datasets/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/` |
| CNSA retraitée (#3) | `https://www.data.gouv.fr/datasets/prix-hebergement-et-tarifs-dependance-des-ehpad/` |
| FINESS (#4, #5) | `https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements/` |
| HAS (#6) | `https://www.data.gouv.fr/datasets/resultats-devaluation-des-etablissements-et-services-sociaux-et-medico-sociaux-essms/` |
| Alim'confiance (#7) | `https://dgal.opendatasoft.com/explore/dataset/export_alimconfiance/` |
| DREES EHPA (#8) | `https://data.drees.solidarites-sante.gouv.fr/explore/dataset/587_l-enquete-aupres-des-etablissements-d-hebergement-pour-personnes-agees-ehpa/` |
| DREES Badiane (#9) | `https://www.data.gouv.fr/datasets/datadrees-badiane/` |
| DREES modalités ASH (#11) | `https://www.data.gouv.fr/datasets/les-modalites-departementales-de-gestion-de-lash-des-personnes-agees/` |
| INSEE densité (#12) | `https://www.insee.fr/fr/information/8571524` |
| INSEE inflation (#13) | `https://www.insee.fr/fr/statistiques/8726461` |
| OpenFisca (#17) | `https://fr.openfisca.org/legislation/apa_etablissement` |

**URL exactes utilisées pour la v2** (elles portent un horodatage : elles resteront valides mais ne
donneront plus la dernière version) :

```bash
# CNSA — archives annuelles 2018 → 2025 (base #2)
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20260212-054051/cnsa-export-prix-ehpad-2025-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20250328-043751/cnsa-export-prix-ehpad-2024-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20240315-081549/cnsa-export-prix-ehpad-2023-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20230106-093633/cnsa-export-prix-ehpad-2022-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20220103-152531/cnsa-export-prix-ehpad-2021-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20210118-175021/cnsa-export-prix-ehpad-2020-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20201127-155733/cnsa-export-prix-ehpad-2019-brute.csv
https://static.data.gouv.fr/resources/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/20201127-155733/cnsa-export-prix-ehpad-2018-brute.csv
# (la liste est aussi conservée dans build/audit/prix_urls.json)

# FINESS extraction classique (base #5)
https://static.data.gouv.fr/resources/finess-extraction-du-fichier-des-etablissements/20260512-091308/etalab-cs1100502-stock-20260512-0339.csv

# FINESS+ Activités — non utilisé en v2, conservé pour mémoire (58 Mo compressés, 1,45 Go décompressés)
https://static.data.gouv.fr/resources/finess-activites-1/20260910-021742/finess-activites-journalier-20260910.json.gz
# (build/audit/finess_act_urls.json)

# DREES Badiane 2023 (base #9)
https://data.drees.solidarites-sante.gouv.fr/api/v2/catalog/datasets/datadrees_badiane_2019/attachments/datadrees_badiane_2023_xlsx

# API tabulaire data.gouv — vérifier un seul établissement sans rien télécharger
https://tabular-api.data.gouv.fr/api/resources/cd04df7c-f78e-461b-aa9d-1df1e5b2d5cf/data/?finessEt__exact=690802384
#   filtres : __exact, __contains, __greater, __less · colonnes : ?columns=a,b · tri : ?col__sort=desc
#   page_size ≤ 200 (500 échoue) · /data/aggregate/ n'existe pas (404)

# Base adresse nationale — géocodage en masse (base #15)
curl -X POST -F data=@togeo.csv -F columns=adresse -F columns=cp -F columns=ville \
     https://api-adresse.data.gouv.fr/search/csv/ -o geocoded.csv

# Communes (base #14)
https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,centre,codeDepartement&format=json
https://geo.api.gouv.fr/communes/{code}/arrondissements-municipaux    # Paris, Lyon, Marseille

# Validation de l'APA (base #17)
curl -X POST https://api.fr.openfisca.org/latest/calculate -H 'Content-Type: application/json' -d @of.json
```

⚠️ **à revérifier** : les URL exactes de FINESS+ Structures, du parquet HAS, de l'export
Alim'confiance, des fichiers DREES ISD / modalités ASH / EHPA et du fichier de densité INSEE n'ont
pas été conservées dans un fichier ; elles se récupèrent en une minute depuis les pages de jeu de
données ci-dessus (bouton « Télécharger » de la ressource la plus récente). Ne pas les inventer.

---

## 3. Les clés de jointure

```
                       ┌──────────────────────────────┐
                       │  FINESS géographique (9 car.)│  ← PIVOT de tout le projet
                       └──────────────┬───────────────┘
       ┌───────────────┬──────────────┼──────────────┬────────────────┐
       ▼               ▼              ▼              ▼                ▼
  CNSA prix      CNSA archives   FINESS classique  HAS évaluations  CNSA 2020
  (finessEt)     (finessEt)      (col. 1 du CSV)   (finess_geo)     (FINESS)

  SIRET (14) ──► Alim'confiance          … puis SIREN (9) + commune identique, candidat unique
  code commune INSEE (5) ──► densité INSEE, DREES départemental, ASH départementale
  SIREN (9) ──► annuaire-entreprises.data.gouv.fr (lien sortant uniquement)
```

Pièges vérifiés :

- le FINESS doit être **complété à 9 caractères par des zéros à gauche** (`zfill(9)`) dans toutes les sources ;
- FINESS **géographique** ≠ FINESS **juridique** : la HAS publie les deux, on n'utilise que le géographique ;
- les **arrondissements** de Paris, Lyon et Marseille n'existent pas dans la grille de densité INSEE :
  `75101-75120 → 75056`, `13201-13216 → 13055`, `69381-69389 → 69123` (fonction `code_dens` de `build_data_v2.py`) ;
- le même problème existe à l'envers pour les codes postaux : les communes parentes 75056 / 69123 / 13055
  sont retirées des codes postaux couverts par leurs arrondissements (`split_data_v2.py`) ;
- codes départementaux de la DREES : `2A` et `2B` → **`20R`** (collectivité de Corse), `69` → **`69D`**
  (Rhône hors métropole) et **`69M`** (Métropole de Lyon, 58 communes listées dans `lyonm.json`) ;
- le décalage FINESS classique (bimestriel) / FINESS+ (quotidien) laisse 28 EHPAD du site absents de
  l'extraction classique et 10 en trop : c'est normal, la fiche le signale par la source de l'habilitation.

---

## 4. Rafraîchir les données : les quatre scénarios

### 4.1 Mensuel — les prix (le seul vraiment récurrent)

1. Ouvrir la page CNSA prix bruts, télécharger la ressource « brute » la plus récente.
2. L'enregistrer dans `build/` sous `cnsa_AAAAMM.csv` (séparateur `;`, encodage UTF-8-BOM).
3. Adapter la ligne 41 de `build_data.py` (`c2026 = read_cnsa('cnsa_202601.csv')`) au nouveau nom.
4. Relancer la chaîne complète (§5).
5. Dans `site/data.js`, mettre `META.lastVerified` à la date du jour.
6. Reporter le nouveau périmètre dans `build/index.template.html` (paragraphe `.s-foot`) et dans la
   méthodologie de `build_pages.py` : total, nombre de prix déclarés, habilitations.

### 4.2 Annuel — la courbe des prix

Quand la CNSA publie le fichier brut de l'année écoulée :

1. Le télécharger dans `build/audit/prix/AAAA.csv`.
2. Ajouter l'année dans `ANS` (`split_data_v2.py`, ligne ~93).
3. Ajouter l'inflation INSEE de l'année dans `INFLATION` (`site/data.js`) et recalculer
   `INFLATION_CUM_2018_2025` (produit des `1 + taux/100`, − 1, en %) — et renommer la constante si
   la période change, elle est citée telle quelle dans la FAQ et la méthodologie.
4. Mettre à jour les phrases chiffrées de la FAQ (`site/data.js`, question « Le prix d'un EHPAD
   augmente-t-il plus vite que l'inflation ? ») : prix médian de départ et d'arrivée, part des
   établissements au-dessus de l'inflation, part de ceux qui ont baissé.

### 4.3 Annuel ou ponctuel — les autres sources

| Quand | Quoi faire |
|---|---|
| FINESS classique (tous les 2 mois) | retélécharger `etalab-cs1100502-stock-*.csv`, régénérer `audit/finess_classique_500.json` (filtre : catégorie d'établissement `500`, colonnes FINESS + code MFT + libellé MFT) |
| HAS (quotidien, utile 1×/trimestre) | retélécharger le parquet, refiltrer sur les EHPAD, réécrire `has_ehpad.pkl` |
| Alim'confiance (quotidien, utile 1×/trimestre) | réexporter le jeu, réécrire `alim.json` |
| DREES EHPA (à la prochaine enquête) | recalculer `audit/ehpa_occupation_segment.json` et `audit/rotation.json`, mettre à jour `ROTATION`, `OCCUPATION_FR` et `DELAI_ATTENTE` dans `site/data.js`, et les chiffres de la FAQ « Comment savoir s'il reste des places ? » |
| DREES Badiane (annuel) | retélécharger le xlsx, régénérer `audit/badiane_dept.json` |
| DREES modalités ASH | ⚠️ figé en 2018. Si la DREES republie : régénérer `ash_dept.json` **et** changer partout la mention « pratique déclarée en 2018 » |
| INSEE densité (annuel) | retélécharger `densite2026.xlsx` (onglet « Maille communale », en-tête ligne 5) |
| Communes (1×/an, au 1ᵉʳ janvier) | réinterroger `geo.api.gouv.fr`, régénérer `communes_geo.json`, `arm.json`, `lyonm.json` |

### 4.4 Quand une règle nationale change

Tout est regroupé dans `site/data.js`, objet `BAREME` — **aucune valeur de barème n'est écrite ailleurs.**

| Constante | Valeur v2 | Ce que c'est | Où la vérifier |
|---|---|---|---|
| `mtp` | 1288.13 | majoration pour tierce personne (revalorisée au 1ᵉʳ avril) | service-public.fr / legifrance |
| `seuilInf` / `seuilSup` | 2.21 / 3.4 | multiplicateurs de la MTP → 2 846,77 € et 4 379,64 € | OpenFisca `apa_etablissement` |
| `pente` | 0.8 | 80 % de l'écart entre tarif GIR et tarif GIR 5-6 | idem |
| `smic` | 12.31 | Smic horaire brut (seuil de non-versement = 3 × Smic) | idem |
| `divisionCouple` | 2 | ressources du ménage divisées par deux | idem |
| `irTaux` / `irPlafond` | 0.25 / 10000 | réduction d'impôt : 25 %, plafond **par personne hébergée** | service-public.fr F17 |
| `ashResteMiniPct` / `ashResteMiniEur` | 0.10 / 125 | minimum laissé au résident en aide sociale | service-public.fr F2444 |
| `ashConjointDomicile` | 1043.59 | minimum laissé au conjoint resté à domicile | idem |
| `obligeMoyenne` | 270 | participation moyenne des obligés alimentaires (DREES, fin 2023) | DREES |

Après toute modification : relancer `runTests()` — plusieurs tests vérifient explicitement les
seuils 2 846,77 € / 4 379,64 € et échoueront si la MTP change sans que les textes de la FAQ, de la
méthodologie et du pied de page soient mis à jour en même temps (ils citent les montants en clair).

---

## 5. Lancer la chaîne de construction

Toujours dans cet ordre, depuis `build/` :

| # | Commande | Lit | Écrit | Sortie console attendue (v2) |
|---|---|---|---|---|
| 1 | `python3 build_data.py` | sources brutes | `merged.json` | socle v1, 7 417 EHPAD |
| 2 | `python3 build_data_v2.py` | `merged.json` + audit | `merged_v2.json` | `habilités 6081 \| non habilités 1142 \| à confirmer 194 \| inconnu 0` · `tarification P:3972 G:3369 V:47` · `Alim + 181 → 1012` · `densité connue : 7414 \| occupation : 6602` |
| 3 | `python3 split_data_v2.py` | `merged_v2.json`, `regimes.json`, `metropole_lyon.json` | `../site/data/**` + le bloc `COUVERTURE` de `site/data.js` | `régime de financement : {'classique': 5800, 'exp': 1617}` · `coordonnées Lambert-93 converties : 18` · `départements : 101 \| total 7417` · `séries de prix : 7255` · `prix médian France : 73.62` · `couverture écrite dans data.js` |
| 3bis | `python3 controles.py` | `../site/data/dep/*.js` | rien (rapport) | **aucune ligne `[BLOQUANT]` suivie d'un nombre de cas.** Sinon, ne pas publier : le script sort en code 1 |
| 4 | `python3 build_site.py` | `index.template.html`, `site.css`, `fontface.css`, `vendor/*.css`, `site/data.js` | `../site/index.html` | `index.html écrit : ~79 700 octets ; 5 questions synchronisées` |
| 5 | `python3 build_pages.py` | `site.css`, `fontface.css` | 4 pages annexes | `pages annexes générées : [...]` |
| 6 | `python3 seo/build_seo.py` | `merged_v2.json`, `communes_geo.json`, `audit/*.json`, `site.css`, `seo.css` | `../site/ehpad/**`, pages nationales, guides, sitemaps | `villes avec page : 985 \| fiches établissement : 6778 \| départements : 101` · `redirections … : 3667` · `→ 7901 pages écrites` |

L'étape 1 n'est à relancer que si les sources brutes changent ; les étapes 2 → 6 sont rejouables
seules et sans risque. **L'étape 3bis n'est pas facultative** : elle relit les fichiers réellement
servis au navigateur et refuse la publication sur une anomalie bloquante. `python3 controles.py --ref`
enregistre l'état courant comme référence de couverture, ce qui permet au contrôle suivant de détecter
une perte de champs entre deux imports. Ne l'exécuter qu'après avoir vérifié le rapport. **Si un chiffre de la colonne de droite change, c'est que les données ont
bougé : comprendre pourquoi avant de publier.** Un écart normal (nouvelle publication CNSA) se voit
sur un seul indicateur ; un écart sur tous signale une source mal téléchargée.

Deux points d'attention techniques :

- `build_site.py` appelle **node** pour lire `site/data.js` et synchroniser la FAQ visible avec le
  balisage `FAQPage` : les deux ne peuvent pas diverger, c'est voulu (une FAQ structurée qui ne
  correspond pas au texte visible est une pénalité Google).
- le fichier de prix CNSA de janvier 2026 utilisé en v2 s'appelle `cnsa_202601.csv` et la variable
  correspondante est en dur dans `build_data.py` : c'est le seul nom de fichier à modifier chaque mois.

---

### 5.1 Reconstruire seulement le style

`build_seo.py` charge d'abord les bases sources (`merged_v2.json` et les autres), qui ne sont
**pas versionnées** : elles pèsent plus de 100 Mo et se retéléchargent (§2.2). Quand on n'a
touché qu'à `site.css` ou `seo.css`, ce détour est inutile — et sur un dépôt fraîchement cloné
il échoue avec `FileNotFoundError: merged_v2.json`.

```bash
cd build
python build_assets.py     # régénère site/assets/site.css et site/assets/pages.js
python build_site.py       # régénère site/index.html (CSS inliné)
python build_pages.py      # régénère les 4 pages annexes (CSS inliné)
```

Les 7 903 pages de contenu, elles, ne contiennent pas de CSS : elles pointent vers
`/assets/site.css`. Un changement de style les atteint donc **sans** avoir à les régénérer.

---

## 6. Format des fichiers produits

### 6.1 `site/data/dep/ehpad-XX.js` — un tableau par EHPAD, 45 colonnes

Écrit sous la forme `ME.dep("69",[[...],[...]]);` — chargé par injection de balise `<script>`, ce qui
fonctionne aussi en `file://` (contrairement à `fetch`). L'ordre des colonnes est **la** convention du
projet : il est défini dans `split_data_v2.py` (liste `COLS`), copié dans `build/cols_v2.json`, et
répliqué dans l'objet `C` en tête de `site/app.js`. **Modifier l'un sans l'autre casse tout le site.**

| # | Clé | Contenu |
|---|---|---|
| 0 | `fin` | FINESS géographique (9 caractères) |
| 1 | `nom` | raison sociale |
| 2-3 | `cp`, `ville` | code postal, commune |
| 4-5 | `lat`, `lon` | coordonnées (null = absent de la carte) |
| 6 | `p` | prix hébergement chambre seule, €/jour |
| 7 | `pcd` | prix chambre double, €/jour |
| 8 | `pa` | prix « aide sociale », €/jour |
| 9-11 | `t12`, `t34`, `t56` | tarifs dépendance GIR 1-2, 3-4, 5-6, €/jour |
| 12 | `maj` | date de mise à jour déclarée (AAAA-MM) |
| 13 | `temp` | tarif accueil temporaire, €/jour |
| 14-15 | `linge`, `lingeU` | prix du linge et son unité |
| 16-19 | `nIncl`, `nSus`, `inclTxt`, `susTxt` | nombre de prestations incluses / en sus + textes libres |
| 20 | `ash` | habilitation aide sociale : `1` habilité · `0` non habilité · `2` à confirmer · `null` inconnu |
| 21 | `ashsrc` | origine : `finess` · `divergence` · `csa` · `2020` · `mft` |
| 22-23 | `statut`, `statutsrc` | `0` public · `1` associatif · `2` privé commercial ; origine du statut |
| 24 | `cap` | capacité (fichier CNSA 2020 — daté, affiché comme tel) |
| 25 | `p2020` | prix 2020 (référence historique) |
| 26-31 | `hasN`, `hasD`, `hasO`, `hasM`, `hasC`, `hasCI` | note A-D, date, organisme évaluateur, moyenne /100, 4 cotations de chapitre, critères impératifs atteints /18 |
| 32 | `alim` | `[résultat, date, suites]` de l'inspection d'hygiène |
| 33-34 | `tel`, `adr` | téléphone, adresse |
| 35-36 | `pm`, `siren` | gestionnaire, SIREN |
| 37 | `ouv` | date d'ouverture |
| 38 | `approx` | `1` = position = centre de la commune |
| 39-40 | `mft`, `mftlib` | code et **libellé officiel** du mode de fixation tarifaire |
| 41-42 | `tarif`, `pui` | `G` global / `P` partiel / `V` PUV ; `1` = pharmacie à usage intérieur |
| 43 | `dens` | densité de la commune : `1` dense · `2` intermédiaire · `3` rural |
| 44 | `occ` | taux d'occupation du **segment** (statut × densité), EHPA 2023 |

### 6.2 Les autres fichiers de données

| Fichier | Forme | Contenu |
|---|---|---|
| `data/dep/communes-XX.js` | `ME.com("69",[[cp, nom, lat, lon, insee], …])` | recherche par code postal |
| `data/dep/prix-XX.js` | `ME.prix("69",{ "690000000": {p:[8 valeurs ou null], e:évolution %, a:% par an, d:"2018", f:"2025"} })` | la courbe de prix |
| `data/departements.js` | `window.ME_DEP`, `window.ME_BBOX`, `window.ME_LYONM` | pratique ASH départementale (+ `ashM` pour la Métropole de Lyon), indicateurs DREES, contexte Badiane, emprises géographiques, communes de la Métropole de Lyon |
| `data/prix-reference.js` | `window.ME_PCT = { "69": [q1, médiane, q3, n], …, "FR": […] }` | quartiles de prix, pour situer un établissement |

Le chargement est paresseux : `ME_BBOX` sert à décider quels départements charger pour le rayon
demandé (fonction `depsInRadius` dans `app.js`). Un département = 3 fichiers de quelques dizaines
de kilo-octets, au lieu des 6,1 Mo du jeu complet.

### 6.3 `site/data.js` — tout ce qui se modifie à la main

C'est le seul fichier à éditer pour changer un contenu sans reconstruire les données :
`META` (version, date de vérification, mois de 30,5 jours), `BAREME`, `SEUILS` (dérivé de `BAREME`,
ne pas saisir à la main), `ROTATION`, `OCCUPATION_FR`, `DELAI_ATTENTE`, `INFLATION`,
`INFLATION_CUM_2018_2025`, `PRIX_ANNEES`, `ASH_ETAT`, `ASH_SRC`, `STATUTS`, `STATUT_COURT`,
`STATUT_SRC`, `TARIF_SOINS`, `HAS_CHAPITRES`, `NON_SIMULE` (ce que le site refuse de simuler), `SOURCES`
(les 14 cartes de la bande « d'où viennent ces données »), `ROADMAPS` (les 9 modes d'emploi) et
`FAQ` (les 5 questions, reprises telles quelles dans le balisage `FAQPage`).

---

## 7. Vérifier avant de publier

```bash
cd site && python3 -m http.server 8000
```

1. **`runTests()` dans la console → `true`.** 37 cas : formule APA (dont couple, seuils, non-versement),
   réduction d'impôt et son plafond par personne, deux résidents hébergés, conjoint à domicile,
   minimum laissé en ASH, part de chaque enfant et coût après déduction, couleurs, courbe de prix,
   disponibilité estimée, fraîcheur de la déclaration, géographie, tri, lien de partage.
2. **Aucune erreur dans la console** hors fond de carte si la machine est hors ligne.
3. **Scripts Playwright de `build/`** : `node test.mjs` (parcours complet), `node perf.mjs`,
   `node over.mjs` (débordement horizontal à 390 px → doit valoir 0), `node a11y.mjs`,
   `node shots.mjs` (captures), `node og.mjs` (régénère `assets/og-image.png`), `node tile.mjs`.
4. **Impression** : depuis le navigateur, la fiche imprimée ne doit contenir que la bande 2 et la
   bande 3 (formulaire, sources, FAQ, boutons et tableau d'inflation sont masqués).
5. **Lien de partage** : cliquer sur « Copier le lien », rouvrir l'URL dans un autre onglet, la
   simulation doit se recharger à l'identique (l'état est encodé en base64 dans `#s=`, sans aucun nom).
6. **Export CSV** en mode professionnel.
7. Repères de poids mesurés en v2 : **8 requêtes / 254 Ko au chargement**, 19 requêtes / 670 Ko après
   une recherche à 20 km de Lyon, calcul en **~30 ms** pour 119 établissements.

### Checklist de première mise en ligne

1. `ME_GTM_ID` en tête d'`index.html` (vide = aucune mesure d'audience ; le bandeau de consentement reste actif).
2. Éditeur, directeur de la publication et **hébergeur réel** dans `mentions-legales.html` (via `build_pages.py`).
3. Licence de chaque jeu réutilisé + formulation d'attribution exigée par l'IGN pour le fond de plan.
4. Domaine servi = URL canoniques `https://mon-ehpad.fr/` dans `index.html`, les pages annexes,
   `sitemap.xml` et `llms.txt`.
5. `sitemap.xml` : dates `lastmod` à la date de publication.
6. En-têtes serveur recommandés : `Cache-Control: public, max-age=3600` pour les pages,
   `max-age=31536000, immutable` pour `assets/`, `vendor/` et `data/dep/`.

---

## 8. Ce qui est bloqué, et pourquoi

| Sujet | État | Ce qu'il faudrait |
|---|---|---|
| Places réellement disponibles par établissement | ❌ n'existe pas en données ouvertes (9 sources testées) | ouverture de ViaTrajectoire ou du tableau de bord de la performance médico-sociale |
| Capacité à jour | ❌ la plus récente en open data date de 2020 | nomenclatures FINESS+ (`statutCapacite`, `habilitation`) à demander à l'ANS |
| Encadrement, absentéisme, rotation du personnel par établissement | ❌ affichés sur le portail officiel depuis août 2026 mais **pas en données ouvertes** ; l'API interne est en `Disallow` dans le `robots.txt` | demande d'ouverture à la CNSA |
| Libellés des prestations `PREST1..11` | ❌ absents du dictionnaire CNSA v26 | demande à la CNSA — en attendant, le site n'affiche que **leur nombre** |
| Barème national d'obligation alimentaire | ❌ n'existe pas | — (le site divise à parts égales et le dit) |
| Pratique départementale de l'ASH après 2018 | ⚠️ dernière publication DREES : 2018 | republication DREES |
| Aide au logement | ❌ dépend du conventionnement, non publié | champ de saisie manuelle |
| CCAS et conseil départemental réels dans le mode d'emploi | ⚠️ source identifiée et testée (annuaire DILA, 11 969 CCAS, 87,5 % de couverture) mais **non intégrée** : l'export en masse n'a pas pu être réalisé | relancer l'extraction par commune et générer un fichier statique au build |
| Temps de trajet réel / isochrone (Géoplateforme) | ⚠️ testé et fonctionnel, non intégré | v3 |
| Groupe gestionnaire (Recherche d'entreprises) | ⚠️ testé, non intégré (lien sortant seulement) | v3 |
| Scénario « vendre le logement » (DVF) | ⚠️ testé, non intégré | v3 |

---

## 9. Les pages de contenu : région, département, ville, établissement

### 9.1 À quoi elles servent

Le calculateur répond à « combien vais-je payer ». Les pages de contenu répondent aux questions que les
gens tapent avant d'en arriver là : « prix EHPAD Lyon », « EHPAD aide sociale Rhône », « combien coûte un
EHPAD ». Chacune donne une réponse chiffrée immédiate, puis mène au calculateur **déjà réglé** sur la
commune ou l'établissement consulté.

Elles sont **générées**, jamais écrites à la main : leurs chiffres sont recalculés à chaque passage du
script à partir de `merged_v2.json`. Un tarif qui change dans le fichier CNSA change partout.

### 9.2 L'arborescence

| Adresse | Nombre | Contenu |
|---|---|---|
| `/ehpad/` | 1 | chiffres nationaux, accès par région |
| `/ehpad/<region>/` | 13 | tarif médian par département (l'outre-mer n'a pas de page de région : elle ferait doublon avec le département) |
| `/ehpad/<departement>/` | 100 | tarif médian, répartition par statut, villes, dix tarifs les plus bas, pratique départementale de l'aide sociale |
| `/ehpad/<ville>/` | 985 | tableau comparatif complet, chiffres clés, financement, questions fréquentes propres à la commune |
| `/ehpad/<ville>/<nom>-<finess>/` | 6 778 | tarifs, comparaison locale, évolution depuis 2018, aide sociale, évaluation, voisins |
| pages nationales | 10 | `/prix-ehpad/`, `/prix-ehpad-par-departement/`, `/ehpad-les-moins-chers/`, `/calcul-reste-a-charge-ehpad/`, `/aides-ehpad/` et ses 4 sous-pages |
| guides | 13 | `/guides/` et 12 guides courts |
| études | 2 | `/etudes/`, `/etudes/barometre-prix-ehpad-2026/` |

Plus **3 667 redirections** : les communes à établissement unique n'ont pas de page (elle ferait doublon
avec la fiche), mais leur adresse reste devinable — elle redirige vers la fiche, en `noindex`.

Paris est un cas particulier : la commune et le département se confondent, une seule page les couvre.
Les arrondissements de Paris, Lyon et Marseille sont regroupés avec leur commune — personne ne cherche
« EHPAD Lyon 3e ».

### 9.3 Les règles qui décident qu'une page existe

Elles sont dans `seo/build_seo.py`, et ce sont elles qui empêchent le site de devenir une ferme à pages :

1. **Une commune a sa page à partir de 2 établissements** (`--villes-min`). En dessous, la fiche de
   l'établissement dit déjà tout.
2. **Un établissement a sa fiche s'il a un tarif déclaré ou une évaluation publiée** (`--fiches`).
   6 778 sur 7 417. Les autres restent visibles dans les listes et dans le calculateur.
3. **Aucun chiffre n'est écrit s'il n'est pas calculable** : les quartiles à partir de 5 établissements,
   l'évolution des prix à partir de 5 séries, les comparaisons de ville à partir de 3 tarifs connus.
   Sinon, la phrase n'est pas produite du tout.
4. **Aucun classement « meilleur EHPAD »**. Les seuls classements portent sur le tarif déclaré, et le
   critère est écrit dans la page.

### 9.4 Élargir la couverture (les vagues suivantes)

L'architecture supporte déjà la couverture complète. Pour l'élargir :

```bash
python3 seo/build_seo.py --villes-min 1     # toutes les communes ont leur page (≈ 4 990)
python3 seo/build_seo.py --fiches toutes    # les 7 417 établissements ont leur fiche
```

**À ne faire qu'après avoir mesuré.** La bonne méthode est celle des vagues : publier ce qui existe,
attendre 4 à 6 semaines, regarder dans la Search Console quelles pages sont indexées et lesquelles
n'obtiennent aucune impression, puis élargir. Ouvrir 5 000 pages supplémentaires d'un coup sans savoir
si les premières fonctionnent est le meilleur moyen de diluer le site.

### 9.5 Où se trouve quoi

| Fichier | Rôle |
|---|---|
| `seo/build_seo.py` | chef d'orchestre : regroupements, adresses, règles d'existence, sitemaps, feuille de style partagée |
| `seo/base.py` | chargement, slugs, statistiques, formats de nombres, lien profond vers le calculateur |
| `seo/geo.py` | 18 régions, 101 départements, et la préposition correcte de chacun (« dans le Rhône », « en Isère ») |
| `seo/layout.py` | gabarit HTML : en-tête, fil d'Ariane, pied de page, données structurées, titres |
| `seo/pieces.py` | briques réutilisées : chiffres clés, tableaux, appels à l'action, questions fréquentes, sources |
| `seo/territoires.py` | pages France, région, département, ville |
| `seo/fiches.py` | fiches d'établissement |
| `seo/contenus.py` | pages nationales, guides, baromètre — **c'est ici qu'on modifie un texte éditorial** |
| `seo.css` | styles des pages de contenu (le tableau devient une liste de cartes sous 720 px) |
| `seo_pages.js` | consentement et mesure d'usage, chargé une fois pour tout le site |

### 9.6 Le lien vers le calculateur

Chaque page de contenu mène au calculateur **pré-réglé**, par un lien de la forme `/#s=<état encodé>`.
C'est le même mécanisme que le lien de partage : un objet JSON encodé en base64, qui ne contient que
le code postal, le code commune, le rayon et, depuis une fiche, le numéro FINESS de l'établissement
(clé `f`, qui le place en comparaison et le met en évidence). Aucun nom, aucune donnée personnelle.
Fonction : `base.lien_calc()`. Côté navigateur : `litHash()` dans `app.js`.

### 9.7 Mesure

Chaque bouton porte un attribut `data-ev`, poussé dans `dataLayer` au clic :
`seo_city_to_configurator`, `seo_establishment_to_calculator`, `seo_dept_to_configurator`,
`seo_prix_to_calculator`, `seo_aides_to_calculator`, `seo_compare_click`… Chaque événement est
accompagné du type de page et du lieu (`seo_page`, `seo_lieu`), jamais d'une donnée personnelle.
À brancher dans Google Tag Manager le jour de la mise en ligne, en même temps que `ME_GTM_ID`.

À suivre dans la Search Console, dans cet ordre : pages indexées par type, impressions et clics des
pages de ville, requêtes qui déclenchent les fiches, puis taux de départ vers le calculateur.

### 9.8 Ce qui n'est pas indexable

- Les combinaisons de filtres du calculateur (`/?...`) : bloquées dans `robots.txt`, elles ne créent
  aucune page distincte.
- Les redirections de communes à établissement unique : `noindex`, avec une adresse canonique
  pointant vers la fiche.
- `mentions-legales.html` et `404.html` : `noindex`.

---

## 10. L'interface du calculateur

### 10.1 Le principe

La page d'accueil n'est plus une longue liste que l'on parcourt de haut en bas. C'est un **espace de
travail en deux volets** : la liste des établissements à gauche, la carte **ou** la fiche de
l'établissement sélectionné à droite. Cliquer sur un établissement remplace le contenu du volet droit
sans que la page bouge : on peut en consulter cinq de suite sans jamais perdre sa place.

Deux règles ont guidé chaque arbitrage :

1. **On ne doit jamais avoir à faire défiler la page pour voir le résultat de l'action qu'on vient de faire.**
2. **On montre la bonne donnée au bon moment** : quatre informations sur la carte de résultat, le reste
   dans la fiche, et la fiche elle-même en quatre onglets.

### 10.2 Les composants et où ils vivent

Tout est dans `site/app.js` (aucun framework, aucune dépendance ajoutée) :

| Fonction | Rôle |
|---|---|
| `render()` | recalcule la sélection, la synthèse, la liste, la carte, la feuille de route |
| `majListe()` | n'affiche que les 15 premiers résultats, puis 15 de plus à la demande |
| `res()` | la carte de résultat compacte : nom, montant, distance, trois indications au plus |
| `pourquoi()` | la phrase « En tête parce que : … » sur le premier résultat — jamais un score opaque |
| `selectionne()` / `ferme()` | ouverture et fermeture de la fiche, historique du navigateur compris |
| `ficheHtml()` / `ongletHtml()` | la fiche et ses quatre onglets (Essentiel, Prix & aides, L'établissement, Qualité) |
| `majCompare()` / `comparHtml()` | la barre de comparaison et le tableau, avec « uniquement les différences » |
| `survole()` / `marqueSelection()` | la synchronisation entre la liste et la carte |
| `videHtml()` | l'état « aucun résultat », avec les sorties possibles |
| `chercheZone()` | « Rechercher dans cette zone » quand on déplace la carte |
| `evt()` | les événements de mesure, poussés dans `dataLayer` |

La mise en page est dans `build/site.css`, section « ESPACE DE COMPARAISON ».

### 10.3 Les trois comportements selon la taille d'écran

| Largeur | Comportement |
|---|---|
| ≥ 1040 px | deux colonnes ; le volet droit est collé en haut, de hauteur fixe — basculer de la carte à la fiche ne fait jamais bouger la page |
| 640 – 1039 px | une colonne ; la carte est au-dessus de la liste, la fiche s'ouvre en panneau glissant |
| < 640 px | idem, et le panneau glissant a deux hauteurs : aperçu (42 % de l'écran) et plein écran, par la poignée ou le glissement |

Sur petit écran, `.col-detail` passe en `display:contents` : ses deux enfants redeviennent des éléments
de la colonne, sans déplacer un seul nœud du DOM — ce qui évite de réinitialiser la carte Leaflet.

### 10.4 Ce que l'état retient

`state` (enregistré dans `localStorage`, clé `mon_ehpad_state_v2`) porte désormais :
`selection` (l'établissement ouvert), `compare` (jusqu'à 4 en parcours famille, 12 en mode
professionnel), `favoris`, `nbAffiches`, `vue` (carte ou fiche), `priorite`, `besoinAsh`
(oui / non / je ne sais pas), `favorisOnly`, `mode` (`famille` ou `pro`), `demarche`
(`{ FINESS: { s: état, n: note } }`) et `dossier` (le nom de la recherche ouverte).

Ouvrir une fiche empile une entrée d'historique (`#e=<FINESS>`) : le bouton « retour » du navigateur
revient à l'établissement précédent, puis referme la fiche. Une adresse `#e=` ouverte directement
sélectionne l'établissement, en élargissant le rayon une fois s'il est hors du périmètre — c'est ce
qui fait fonctionner le bouton « Estimer mon reste à charge » des 6 778 fiches d'établissement.

### 10.5 Les événements de mesure

`search_started`, `filters_applied`, `result_opened`, `ehpad_compared`, `comparison_opened`,
`calculator_started`, `calculator_completed`, `favorite_added`, `map_opened`, `result_list_more`,
plus les `seo_*` des pages de contenu (§9.7). Aucun ne transporte de donnée personnelle : au plus un
numéro FINESS, un code commune et un nom de critère.

En mode professionnel, trois de ces événements sont renommés à la volée par la table `PRO_EVT`
(`search_started` → `pro_search_started`, `search_completed` → `pro_search_completed`,
`result_opened` → `pro_result_opened`), et cinq événements n'existent que là :
`pro_landing_view`, `pro_add_to_action_list`, `pro_action_status_changed`, `pro_export_csv`,
`pro_research_saved`, `pro_research_reopened`. Mêmes règles : jamais de nom, de revenu, de GIR
ni de note — seulement des identifiants d'établissement et des compteurs.

### 10.6 Ce qui a été volontairement écarté

- **Pas de score de qualité composite.** Aucune donnée publique ne permet de le fonder ; le classement
  s'explique en une phrase.
- **Pas de modale pour la fiche.** Un panneau, un tiroir ou un glissement selon l'écran — la modale
  n'est utilisée que pour la comparaison et les filtres, où l'interruption est assumée.
- **Pas de liste infinie.** 15 résultats, puis 15 de plus : à 421 résultats (Paris), le DOM contient
  15 cartes et 16 Ko, et le calcul prend 20 ms.

### 10.7 Thème clair / sombre et barre de défilement

**Le thème.** Toute la palette passe par des variables CSS déclarées sur `:root`
(`build/site.css`, en tête de fichier) : fonds (`--pg`, `--surf`, `--bg`), textes
(`--ink`, `--txt2`, `--mut`, `--mut2`), bordures, teintes d'état (`--ti-*`) et couleurs de
texte associées (`--sur-*`), ombres (`--om`). Le bloc `[data-theme="dark"]` **ne redéfinit
que ces variables** : aucune règle de mise en page n'est dupliquée, donc les deux thèmes ne
peuvent pas diverger. Trois exceptions, toutes commentées dans le fichier :

- `--bl-t`, le bleu quand il sert de **couleur de texte**. Le bleu de marque `#2548FF` ne
  donne que 2,8:1 sur fond sombre ; il devient `#8ba4ff` (7,3:1). Les aplats — boutons,
  pastilles, marqueurs — gardent `--bl`, le bleu d'origine.
- `#total-card` est un aplat bleu dans les deux thèmes : les variables y sont remises à
  leurs valeurs claires, sinon un bouton blanc deviendrait sombre sur fond bleu.
- Le fond de carte de l'IGN est une image : on ne peut pas le recolorer, il est inversé par
  un filtre CSS (`--carte`).

**Où il est posé.** Un script de quatre lignes dans le `<head>` lit `localStorage`
(clé `mon_ehpad_theme`), retombe sur `prefers-color-scheme` si rien n'est mémorisé, et pose
`data-theme="dark"` sur `<html>` **avant le premier rendu** — sinon la page clignote en
blanc. Il doit rester **avant** la feuille de style : un `<link>` bloque l'exécution des
scripts qui le suivent. Il est présent dans les trois gabarits : `build/index.template.html`,
`build/seo/layout.py`, `build/build_pages.py`.

**La bascule.** Deux boutons portent la classe `js-theme` : un dans l'en-tête de page
(visible sans défiler) et un dans la barre de défilement. Le script les pilote tous les deux.
Tant que l'utilisateur n'a rien choisi, le site suit le réglage du système, y compris s'il
change en cours de visite. L'icône bascule en CSS, pas en JavaScript.

**L'impression reste claire** : un bloc `@media print` remet toutes les variables à leurs
valeurs claires, même quand le thème sombre est actif.

**La barre de défilement.** `#topbar`, `position:fixed`, révélée au-delà de 260 px de
défilement. Elle contient le logo, le menu « Naviguer », le bouton de thème, l'appel à
l'action et le liseré de progression. Trois précautions :

- le défilement n'anime que `transform` et `opacity`, et la mesure est faite **une fois par
  image** (`requestAnimationFrame`), jamais une fois par événement ;
- le liseré est un `scaleX()`, pas une largeur : aucune reprise de mise en page ;
- cachée, la barre est en `visibility:hidden`, donc hors du parcours au clavier.

Le script publie la hauteur réelle de la barre dans `--tb-h` ; la barre de résultats
(`.barre`, en `position:sticky`) s'y colle au lieu de passer dessous. Aucune hauteur n'est
codée en dur.

Le même code tourne sur les trois familles de pages : l'accueil (`site/app.js`), les 7 903
pages de contenu et les pages annexes (`build/seo_pages.js` → `/assets/pages.js`).

### 10.8 Le mode professionnel

**Entrée.** Il n'y a plus de bascule « Famille / Pro » en haut du configurateur. L'accès se fait par
un lien discret dans l'en-tête (`.lien-pro`) vers `/professionnels/`, et par l'adresse `/?pro=1`
(ou `#pro`), que les boutons des deux pages professionnelles utilisent. `pro-quitter` ramène au
parcours famille. `passeEnPro(on, source)` fait la bascule ; `majTitre()` remplace le titre et le
chapô de l'en-tête (le HTML livré porte la version famille, c'est elle qui est indexée).

**Ce qui change à l'écran.** Le numéro FINESS s'affiche sur chaque carte (`.res-fin`) ; le bouton
« Comparer » devient « Ajouter aux démarches » ; la fiche gagne un bloc « Ce qui est vérifiable »
(`compatibilites()`, rendu en ✓ / · / ? — jamais un score global) ; le tiroir de comparaison devient
« Ma liste de démarches » (`demarchesHtml()`), avec un état par établissement parmi les huit de
`STATUTS_DEMARCHE` et une note libre de 140 caractères ; l'export CSV réapparaît en pied de tiroir
(`exportDemarches()`), à côté de l'impression.

**Les recherches enregistrées.** Clé `localStorage` distincte : `mon_ehpad_dossiers_v1`, 20 entrées
au maximum. Une entrée retient `DOSSIER_CLES` (zone, commune, rayon, GIR, type de chambre, besoin
d'aide sociale, filtres, tri, favoris), la liste `compare` et les `demarche`. Elle **ne retient pas**
les ressources, l'épargne, l'aide au logement, la situation familiale ni l'imposition : ces valeurs
servent au calcul du moment et ne sont jamais écrites dans une recherche. Nom par défaut
« Dossier 001 », incrémenté ; un nom déjà pris remplace l'entrée existante plutôt que d'en créer
une seconde.

**Les règles à ne pas casser.**

- Ne jamais annoncer de places libres. Le produit ne connaît que le nombre d'**établissements
  correspondant aux critères** ; aucune base publique nationale ne donne la disponibilité réelle.
- Ne jamais affirmer une compatibilité médicale. `compatibilites()` ne parle que de budget, de
  distance, d'habilitation et de tarif.
- Ne jamais laisser croire à une sauvegarde qui n'existe pas : tout est dans le navigateur, les
  textes de l'interface le disent, et il n'y a ni compte, ni serveur, ni partage.
- Ne jamais demander d'identité. Si un champ nominatif devait être ajouté un jour, il faudrait
  d'abord revoir les mentions légales et la base légale du traitement.

**Les deux pages de contenu.** `/professionnels/` et `/professionnels/assistant-social/`, produites
par `build/seo/contenus.py` (fonctions `professionnels()` et `assistant_social()`), publiées dans
`sitemap-contenus.xml`, liées depuis le pied de page de tout le site et depuis la page de l'aide
sociale à l'hébergement. Leurs chiffres viennent de `ctx['FR']` : aucun n'est écrit en dur.

---

## 11. La mise en ligne

Le site est publié sur **GitHub Pages**, à l'adresse `trouver-mon-ehpad.fr`.
La marche à suivre complète est dans **`DEPLOIEMENT.md`** ; l'essentiel tient en quatre points.

### 11.1 Ce qui est publié, et ce qui ne l'est pas

`.github/workflows/pages.yml` met en ligne **le seul dossier `site/`**. `build/` reste dans le dépôt
mais n'est jamais servi. Les données sources téléchargées (environ 200 Mo) ne sont pas versionnées du
tout : `.gitignore` les exclut, elles se retéléchargent avec le §2.2 et le §4.

Le dépôt suit ainsi **11 985 fichiers pour 133 Mo**, dont 11 914 dans `site/`.

### 11.2 Les garde-fous du workflow

Avant toute publication, le workflow refuse de déployer si :

- une page contient encore la mention `À COMPLÉTER` (les mentions légales : article 6 III de la loi
  pour la confiance dans l'économie numérique) ;
- l'adresse canonique de l'accueil ne correspond pas au domaine du fichier `site/CNAME` ;
- un fichier de travail (`*.v2.js`, `*.bak`) traîne dans le dossier publié.

Il affiche ensuite le nombre de pages et le poids mis en ligne. Ces trois contrôles sont la raison
d'être du workflow : ils empêchent les erreurs qui ne se voient qu'une fois le site en ligne.

### 11.3 Deux contraintes à ne pas oublier

- **Le site doit être servi à la racine d'un domaine.** Tous les liens internes sont absolus
  (`/ehpad/`, `/assets/site.css`). Sur `compte.github.io/depot/`, le site est cassé. C'est pourquoi le
  domaine personnalisé n'est pas optionnel — ou alors il faut un dépôt `compte.github.io`.
- **`site/.nojekyll`** empêche GitHub de faire tourner Jekyll sur 11 573 fichiers HTML à chaque push.
  Ne pas le supprimer.

### 11.4 Après la bascule

Déclarer `https://trouver-mon-ehpad.fr/sitemap.xml` dans la Search Console, puis renseigner
`ME_GTM_ID` en tête de `build/index.template.html` et relancer `build_site.py`. Tant que cet
identifiant est vide, aucune mesure d'audience ne part.

---

## 11 bis. Les règles nationales dont dépend le calcul

Trois fichiers portent les règles, séparément du code, pour qu'une évolution réglementaire
se corrige sans relire le moteur.

| Fichier | Ce qu'il contient | Quand le rouvrir |
|---|---|---|
| `build/regimes.json` | Expérimentation de fusion des financements soins et dépendance : les 23 territoires, les montants successifs de la participation forfaitaire avec leur source, les exclusions connues, la date de fin annoncée et son incertitude | À chaque changement de montant, d'échéance ou de périmètre |
| `build/regime.py` | Déduit le régime d'un établissement de son **territoire** (code commune INSEE, à défaut département) ; jamais de ses tarifs déclarés. Autotest : `python3 regime.py` doit afficher 8/8 | Si un territoire entre ou sort de l'expérimentation |
| `build/metropole_lyon.json` | Les 58 codes commune de la Métropole de Lyon, récupérés de `geo.api.gouv.fr/epcis/200046977/communes` | En cas de fusion de communes |
| `site/data.js` → `window.BAREME` | Seuils APA, taux et plafond de la réduction d'impôt, minimums de l'aide sociale | À chaque revalorisation |

**Le piège à ne jamais retomber dedans.** Dans les territoires d'expérimentation, le fichier CNSA
inscrit la participation forfaitaire dans les colonnes de tarif GIR : les trois tarifs y sont égaux.
Il est tentant d'en déduire le régime. C'est faux dans les deux sens — un établissement de droit
commun peut déclarer trois tarifs identiques (le contrôle `gir.egaux_hors_exp` les compte), et la
valeur déclarée est en retard d'une publication. Le moteur retient donc le **montant national en
vigueur à la date du calcul**, avec sa source, et signale l'écart avec la valeur déclarée.

Le Rhône est le cas limite : la Métropole de Lyon expérimente, le département du Rhône non. Les
distinguer exige le **code commune**, jamais le code postal. Sans code commune, `regime.py` renvoie
`inconnu`, et le moteur s'abstient de chiffrer l'aide au quotidien plutôt que de deviner.

---

## 11 ter. Le contrat de données

`build/contrat_donnees.json` décrit les 46 colonnes servies au navigateur : libellé, unité,
**portée** (l'établissement ? le segment ? le département ?), source, état possible et limites.
Il sert de référence commune au moteur, aux pages de contenu et aux contrôles.

Trois définitions à ne pas perdre de vue :

- **`fin`** est le FINESS **géographique** — le site — et non le FINESS juridique de la personne
  morale gestionnaire (`pm`). Son format est deux caractères de département, chiffres **ou `2A`/`2B`
  pour la Corse**, puis sept chiffres. La règle « neuf chiffres » est fausse et rejette 30 établissements
  corses parfaitement valides. En outre-mer, tous les FINESS commencent par `970`, quel que soit le
  département : le préfixe n'y indique rien.
- **`occ`** est une **moyenne de segment** issue d'une enquête nationale. Elle ne décrit pas
  l'établissement sur la ligne duquel elle figure, et aucun nombre de places libres ne peut en être
  déduit. L'extrapolation qui existait jusqu'en v2.4 a été retirée.
- un champ vide signifie **non déclaré**, jamais « non » : une prestation non citée n'est pas une
  prestation non facturée.

---

## 12. Journal des versions

| Version | Date | Contenu |
|---|---|---|
| 1.0 | 10/09/2026 | Première version : 7 417 EHPAD, calcul du reste à charge, carte, aide sociale, mode d'emploi, mode professionnel |
| 2.5 | 12/09/2026 | **Régime de financement de la dépendance** (46ᵉ colonne `reg`) : l'expérimentation de fusion soins/dépendance est modélisée pour les 1 617 établissements des 23 territoires — APA en établissement supprimée, participation forfaitaire de 6,16 €/jour retenue au montant national en vigueur avec sa source, et non à la valeur déclarée à la CNSA, en retard d'une publication. Le régime vient du **territoire** (code commune INSEE), jamais des tarifs déclarés : `regimes.json`, `regime.py`, `metropole_lyon.json` · **Trois montants séparés** là où il n'y en avait qu'un : ce que l'établissement facture, ce qu'il faut décaisser chaque mois, et l'avantage fiscal — annuel, différé, plafonné, retiré du calcul mensuel où il minorait le reste à charge de 25 % · **Couples** : les ressources du conjoint ont leur propre champ ; le barème APA divise les ressources **du ménage**, non celles du résident seul (l'APA était surestimée) · **Aide sociale** : la part « aide au quotidien » reste due et apparaît enfin, avec le reste à vivre qu'elle absorbe ; la créance successorale cesse d'être présentée comme calculable · **Extrapolations de places libres retirées** (tri, colonne du comparateur, export, fiche) au profit des questions à poser et du numéro à appeler · **18 établissements en coordonnées Lambert-93** convertis (`lambert93.py`, pur Python, 4/4 aux cas de contrôle) : ils étaient hors de toute recherche par rayon · **Contrôles automatiques** (`controles.py`, 3bis de la chaîne) : 20 contrôles bloquants ou d'alerte sur les données publiées, référence de couverture, sortie en erreur si anomalie bloquante · **Contrat de données** (`contrat_donnees.json`, 46 champs) · **Bloc `COUVERTURE`** réécrit à chaque build et affiché en clair : ce que le site ne sait pas · **JSON-LD de l'accueil réparé** (`mainEntity` d'une `FAQPage` n'était pas un tableau : le bloc entier était invalide) et validé au build · **Partage** : la recherche part seule par défaut, la situation financière et le GIR seulement sur demande, avec la mention que le lien est encodé et non chiffré · **Export CSV** : injection de formule neutralisée, en-têtes réalignés, en-tête de provenance daté et rejouable · **Parcours « pour qui »** : un choix explicite proche / soi-même reformule l'interface · **Cas limites** : ressources sans retraite, GIR inconnu resté inconnu et signalé sur le montant, chambre double sans tarif, accueil temporaire traité comme un autre régime · **Convention annuelle corrigée** : 30,5 × 12 = 366, les montants annuels se comptent en jours réels · **Historique de prix** : la courbe s'interrompt aux années manquantes (elle les reliait en affirmant le contraire), l'écart à l'inflation est en **points**, la comparabilité est explicitée · **Contenus administratifs** : conditions d'âge et de résidence de l'ASH, règle des cinq ans en établissement non habilité, domicile de secours, habilitation par places, anecdote CAF ramenée à ce qu'elle est, déploiement régional de ViaTrajectoire · **63 tests** (37 → 63) |
| 2.4 | 11/09/2026 | **Thème clair / sombre** : toute la palette passée en variables CSS, un seul bloc `[data-theme="dark"]` qui ne redéfinit que des variables — aucune règle de mise en page dupliquée · bascule mémorisée, `prefers-color-scheme` suivi tant que rien n'est choisi, thème posé avant le premier rendu (pas de clignotement blanc) · bleu de texte éclairci pour tenir le contraste (2,8:1 → 7,3:1), fond de carte IGN inversé par filtre, impression toujours claire · deux boutons de bascule, un dans l'en-tête et un dans la barre · **barre de défilement** révélée au-delà de 260 px : logo, menu « Naviguer », bouton de thème, appel à l'action et liseré de progression, sur l'accueil, les 7 903 pages de contenu et les pages annexes · mesure une fois par image, `transform` et `opacity` seulement, barre cachée hors du parcours clavier, hauteur réelle publiée dans `--tb-h` pour que la barre de résultats s'y colle · **en-tête d'accueil** : titre sur deux lignes de 390 à 1 440 px (la colonne de repères descend d'elle-même sous 34 rem plutôt que de comprimer le titre), chapô sorti de la colonne de gauche pour occuper toute la largeur — une phrase par ligne jusqu'à 900 px |
| 2.3 | 11/09/2026 | **Mode professionnel repensé** : entrée discrète par `/professionnels/` et `/?pro=1` à la place de la bascule Famille/Pro · titre et chapô adaptés à celui qui accompagne · bandeau de contexte avec « Mes recherches » et retour au parcours famille · sélection devenue **liste de démarches** (12 établissements, 8 états, note libre) reportée sur les cartes de résultat · bloc « Ce qui est vérifiable » sur la fiche, en ✓ / · / ? — toujours aucun score global · numéro FINESS visible en contexte professionnel · export CSV conservé mais ramené au pied du tiroir · **recherches enregistrées** (`mon_ehpad_dossiers_v1`, 20 max) qui retiennent la zone, les critères et les démarches, **jamais les ressources ni une identité** · 6 nouveaux événements `pro_*` sans donnée personnelle · deux pages de contenu `/professionnels/` et `/professionnels/assistant-social/`, liées depuis le pied de page et depuis l'aide sociale à l'hébergement · aucune promesse de disponibilité réelle ni de compatibilité médicale · **accueil** : chapô raccourci, colonne de repères (accès professionnel, « Qui sommes-nous ? », date de mise à jour) placée à droite du texte d'introduction, et léger relief au survol des blocs de contenu — `transform` et `box-shadow` seulement, jamais sur les cartes de résultat, neutralisé sur écran tactile et si l'utilisateur demande moins d'animations · **trois correctifs de carte et de barre** : la légende décrit désormais ce qui est réellement dessiné (bleu « tarif déclaré » tant que les ressources ne sont pas saisies, l'échelle de reste à charge ensuite, plus le point de départ et les pastilles de regroupement, qui comptent des établissements et ne disent rien du prix) · les boutons « Carte / Fiche » se dimensionnent sur leur texte et ne se coupent plus en « Ca… » · le bouton correspondant au panneau affiché est allumé dès le premier rendu, alors que les deux restaient éteints jusqu'au premier clic |
| 2.2 | 11/09/2026 | **Mise en ligne préparée** : workflow GitHub Pages avec garde-fous, `CNAME`, `.nojekyll`, `.gitignore`, `README.md`, `DEPLOIEMENT.md`, mentions légales complétées (hébergeur GitHub, licences relevées, propriété intellectuelle) · **Refonte du parcours** : espace de travail en deux volets (liste à gauche, carte ou fiche à droite), cartes de résultat réduites à quatre informations, fiche en quatre onglets, reste à charge devenu l'information principale · exploration possible **sans remplir sa situation** (le tarif s'affiche, le reste à charge apparaît dès que la retraite est saisie) · comparateur permanent avec barre flottante, tableau et « uniquement les différences » · panneau glissant à deux hauteurs sur mobile, avec retour à la position exacte dans la liste · liste paginée par 15 · filtres en tiroir avec compteur et pastilles de retrait · question « avez-vous besoin de l'aide sociale ? » à trois réponses dont « je ne sais pas » · favoris · état vide avec sorties proposées · « rechercher dans cette zone » en déplaçant la carte · survol croisé liste ↔ carte · historique du navigateur et adresses `#e=` · 10 événements de mesure |
| 2.1 | 11/09/2026 | **Nom de domaine trouver-mon-ehpad.fr** et marque « Trouver mon EHPAD » partout · **7 901 pages de contenu générées** : 13 régions, 100 départements, 985 villes, 6 778 fiches d'établissement, 10 pages nationales, 12 guides, un baromètre · fil d'Ariane, maillage interne, données structurées (fil d'Ariane, article, jeu de données), sitemaps thématiques avec index · lien profond vers le calculateur pré-réglé depuis chaque page (et établissement mis en évidence depuis une fiche) · feuille de style et script partagés et mis en cache · événements de mesure `seo_*` · filtres du calculateur exclus de l'exploration · correction : l'historique de prix n'était pas rechargé par le générateur, aucune page n'affichait l'évolution |
| 2.0 | 11/09/2026 | Habilitation ASH depuis le libellé officiel FINESS, 3 états (corrige une surestimation de 270 établissements) · indicateur HAS documenté (`nb_ci_atteints` sur 18) · tarif global/partiel et PUI · appariement Alim'confiance élargi (+181) · **courbe d'évolution du prix 2018-2025** pour 7 255 établissements avec comparaison à l'inflation · **estimation de disponibilité** (occupation de segment EHPA 2023 + rotation 38,8 %) pour 6 602 établissements · autres revenus · couple hébergé à deux · conjoint resté à domicile · **part de chaque enfant et coût après déduction fiscale** · lien de partage · deux nouveaux tris · petits-enfants dispensés (loi du 8 avril 2024), donations dix ans avant **et après**, retour à meilleure fortune · tests portés de 25 à 37 |

---

*Un chiffre de ce fichier ne correspond plus à ce que produit un script ? Le script fait foi :
ce document décrit l'état du 12/09/2026.*
