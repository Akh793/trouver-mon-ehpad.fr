# Données publiques — lot 1 de l'audit v2 (29/09/2026)

## Décisions de l'éditeur

- Exploiter l'audit v2 (`claude/mon-ehpad-audit-donnees-v2.md`) au lieu de refaire un balayage.
- Corriger la MTP tout de suite.
- Lot 1 : bascule vers FINESS+ ; PASA, UHR, unité Alzheimer, accueil de jour ; personnes de 75 ans et plus par commune ; rapports d'inspection ARS.

## 1. Majoration pour tierce personne (MTP)

- ✅ 1 298,44 € par mois depuis le 01/04/2026 (service-public F36489, circulaire CNAV 2026-09).
- Seuils APA recalculés : 2,21 × MTP = 2 869,55 € et 3,40 × MTP = 4 414,70 €.
- Mis à jour : `site/data.js` (BAREME, SOURCES), le test de `runTests`, la méthodologie, les guides, les études et llms.txt.
- ⚠️ Le portail officiel et OpenFisca affichent encore 2 846,77 € et 4 379,64 € (seuils 2025). La méthodologie le signale.

## 2. Bascule vers FINESS+ (ANS)

L'ancienne extraction FINESS n'est plus mise à jour depuis le 04/05/2026. La chaîne lit désormais les jeux data.gouv.fr « FINESS - Structures » et « FINESS - Activités » (fichiers du 29/09/2026, Licence Ouverte 2.0).

**Scripts** (`build/finessplus/`)

| Script | Rôle | Fichier produit |
|---|---|---|
| `extraire.py` | EHPAD (catégorie 500), ouverts, actifs | `finess_ehpad_plus.json` |
| `mft.py` | Mode de fixation tarifaire, libellé TRE_R74 | `audit/finess_plus_500.json` |
| `activites.py` | Places installées par activité | `audit/activites_plus.json` |

**Résultats**

- **Périmètre** : 7 415 EHPAD, contre 7 417 auparavant.
  - 3 disparus : 310784723, 560011876, 750823965.
  - 1 nouveau : 260024492 (Die).
  - 16 changements de mode de fixation tarifaire.
- **Habilitation à l'aide sociale** : 6 071 habilités, 1 140 non habilités, 204 à confirmer.
- **Tarif de soins** : partiel 3 889, global 3 476, petite unité de vie 46, indéterminé 4 (code 99).

**Offre spécialisée**

- Règle : places installées uniquement (statut 08), activités actives uniquement.
- Le PASA est compté en présence, car FINESS+ lui attribue une capacité de 0.
- Établissements concernés :

| Offre | EHPAD |
|---|---|
| Hébergement permanent | 7 347 |
| Unité protégée Alzheimer | 2 845 |
| Hébergement temporaire | 3 567 |
| PASA | 2 289 |
| Accueil de jour | 1 571 |
| UHR | 210 |
| Plateforme de répit | 167 |

- **Contrôle croisé avec Atlasanté `t_actfiness`** (photo du 05/01/2026) :
  - PASA : 2 141 EHPAD en commun, 17 seulement chez Atlasanté, 148 seulement dans FINESS+ ;
  - UHR : 201 sur 201.
- ⚠️ Le nombre de places « habilitées » de FINESS+ est incomplet (4 756 EHPAD renseignés) : il n'est pas utilisé.

**Affichage**

- **Capacité** : places installées FINESS+. La capacité CNSA 2020 ne sert plus que pour 3 établissements ; 65 restent sans capacité connue.
- **Données servies** : 6 colonnes ajoutées (`capsrc`, `alz`, `pasa`, `uhr`, `ht`, `aj`), soit 52 colonnes.
- **Accueil** : ligne « Accueil spécialisé » sur la fiche, badge « Unité Alzheimer », filtre « Unité protégée Alzheimer ou UHR » (sur Lyon 3e dans un rayon de 20 km : 119 → 69 établissements), et une ligne dans le comparatif.
- **Pages de département et de ville** : section `#unites-specialisees`.
- **Nouvelle page nationale** `/ehpad-alzheimer/`, avec un tableau par département. Le guide Alzheimer y renvoie.

**Adresses stables**

- `build/seo/urls_fiches.json` : une fiche garde son adresse même si FINESS change le nom ou la commune de l'établissement. C'est le cas de 6 fiches aujourd'hui.
- Une fiche disparue redirige vers la page de sa commune (meta refresh à 0 s) : 2 cas aujourd'hui.

## 3. Personnes âgées par commune (INSEE)

- **Source** : recensement 2023, jeu Melodi `DS_RP_TD_POPULATION_AGESEX_PRINC`, fichier Parquet sans clé. Script `build/insee/pop75.py`, sortie `insee/pop75.json`.
- **Contrôle** : Lyon compte 519 127 habitants, dont 41 008 de 75 ans et plus et 15 026 de 85 ans et plus, soit exactement les chiffres de l'audit v2.
- **Pages** : section `#population` sur les pages de ville et de département.
  - Nombre d'habitants de 75 ans et plus (et leur part dans la population) et de 85 ans et plus.
  - Département seulement : places pour 1 000 habitants de 75 ans ou plus (France : 85). Exemples : Rhône 76, Paris 38.
  - Pas de taux par commune : un EHPAD accueille aussi les habitants des communes voisines.
- ⚠️ Le catalogue Melodi indique un accès « public » sans nommer de licence. Les mentions légales le disent.

## 4. Contrôles des ARS

- **Script** : `build/ars/extraire_ars.py`.
  - Il lit la page nationale et les 12 pages régionales, en respectant le robots.txt (Crawl-delay de 10 s).
  - Aucun PDF n'est téléchargé.
- **Rattachement** : un document n'est rattaché à un établissement que si son nom porte le numéro FINESS. C'est le cas de 677 EHPAD d'Île-de-France (874 documents : lettres de décision, rapports, documents datés).
- **Autres régions** : lien vers la page de l'ARS. Aucun rapprochement par nom, pour éviter d'attribuer un rapport au mauvais établissement.
- **Corse et DROM** : aucune publication, donc aucune mention.
- **Sur la fiche** (bloc « Évaluation et contrôles ») : lien daté, avec la phrase « Ils décrivent la situation constatée le jour du contrôle ». Aucun résumé, aucune note.

## 5. Corrections annexes

- Chiffres de périmètre mis à jour dans la méthodologie, llms.txt et les sources de data.js.
- **Méthodologie §6** : le texte décrivait encore une estimation de places libres, retirée du site. Il est réécrit pour dire qu'il n'y a pas d'estimation et que les places installées ne sont pas des places libres.
- Retrait de la limite « capacité à jour » : FINESS+ la donne désormais.
- Tables des départements : un établissement sans fiche ni page de commune n'est plus lié (239 liens morts évités).
- Ancres : décalage sous l'en-tête collant (`scroll-margin-top`).
- `.gitignore` : fichiers bruts FINESS+, INSEE et ARS exclus (jusqu'à 88 Mo).
- MAINTENANCE.md : procédure de rafraîchissement (§4.3), 52 colonnes (§6.1), registre d'adresses (§5).

## Vérifications

- **Pages** : 11 586. Liens internes cassés : 0. JSON-LD invalides : 0. Titres de plus de 60 caractères : 0. Liens imbriqués : 0. Un seul H1 par page.
- **Tests** : runTests 66/66, t_ux_accueil 52/52, Worker 42/42. `controles.py` : aucun cas bloquant.
- **Chemins du compteur** : 7 913, page `/ehpad-alzheimer/` comprise.
- **Captures** : aucun débordement à 390 px.

## À signaler

- 204 habilitations « à confirmer » : le libellé FINESS et la déclaration CNSA divergent.
- HAS : `indice_qualite`, `nb_ci_sup_3_5` et `moy_objectifs_100` sont documentés (correction de l'audit v2). Non exploités dans ce lot.
