# Audit des données ouvertes et gratuites — v2 (29/09/2026)

Cet audit fait suite à `mon-ehpad-audit-api-v1` (10/09/2026). Trois balayages ont été menés en parallèle, par appels réels :

| Balayage | Volume | Détail |
|---|---|---|
| A — data.gouv.fr | 451 requêtes API v1 + 97 v2 | 104 organisations listées (≈ 19 800 jeux vus), ≈ 100 fiches examinées, ≈ 40 ressources ouvertes |
| B — API publiques | 40 API, 224 appels | |
| C — Sources hors data.gouv | 38 sources | dont les règlements départementaux d'aide sociale (RDAS) de 20 collectivités lus |

Légende : ✅ vérifié en ouvrant la donnée · ⚠️ d'après la description, ou vérification partielle · ❌ non trouvé ou inaccessible.
Les fichiers de travail détaillés sont dans le dossier de travail (`data-sweep/A_datagouv.md`, `B_apis.md`, `C_hors_datagouv.md`).

---

## 1. Corrections à apporter au site

**1. MTP périmée : les seuils de l'APA sont faux de 23 € et 35 €.** ✅
- La majoration pour tierce personne vaut **1 298,44 €/mois depuis le 01/04/2026** (circulaire CNAV 2026-09 du 02/04/2026, texte lu).
- Le site utilise encore 1 288,13 € (valeur 2025). OpenFisca aussi, ce qui explique pourquoi la validation « 0,00 € d'écart » du 10/09 n'avait rien détecté.
- Seuils calculés selon la formule réglementaire, R232-19 du Code de l'action sociale et des familles (2,21 et 3,40 × MTP) :

| Seuil | Selon la formule | Affiché par le site |
|---|---|---|
| Inférieur (2,21 × MTP) | **2 869,55 €** | 2 846,77 € |
| Supérieur (3,40 × MTP) | **4 414,70 €** | 4 379,64 € |

- ⚠️ **Contradiction entre sources officielles.** Le portail pour-les-personnes-agees.gouv.fr (page APA en établissement, mise à jour le 09/06/2026) affiche encore « 2 846,77 € en 2026 ». La formule est réglementaire ; le portail semble ne pas avoir été mis à jour.

**2. L'extraction FINESS « classique » est gelée.** ✅ (description du jeu sur data.gouv)
- Les données s'arrêtent au 04/05/2026 et plus aucune mise à jour ne sera publiée.
- Depuis le 20/07/2026, seul FINESS+ (Agence du numérique en santé) est à jour, chaque jour.
- Le site lit dans l'ancien fichier l'habilitation à l'aide sociale et l'identité des établissements. Il doit passer à FINESS+ ; sinon les ouvertures, fermetures et changements d'habilitation postérieurs à mai 2026 lui échappent.

**3. Correction de l'audit v1 sur la HAS.** ✅
- Les variables `indice_qualite`, `nb_ci_sup_3_5` et `moy_objectifs_100` **sont documentées**, dans deux autres feuilles du dictionnaire HAS : l'audit v1 n'avait lu que la première.
- À vérifier : ce que le site affiche aujourd'hui, et si le libellé « critères impératifs » est le bon.

**4. Conformité aux fichiers robots.txt.** ✅
- Les portails Opendatasoft (DREES, Annuaire de l'administration, BODACC, CNSA Data Autonomie, départements) et l'ATIH interdisent `/api/` à tout robot autre que Googlebot.
- Aucun script de construction du site ne les appelle aujourd'hui (vérifié).
- Les mises à jour futures des données DREES doivent passer par les miroirs data.gouv ou par un téléchargement manuel.

---

## 2. Données nouvelles utiles, par intérêt

| # | Source | Statut | Ce que ça débloque | Effort ⚠️ |
|---|---|---|---|---|
| 1 | **FINESS+ Activités + nomenclatures ANS (NOS)** : 961 PASA, 962 UHR, 657 accueil temporaire, 21 accueil de jour, clientèle 436 Alzheimer. Nomenclatures sur mos.esante.gouv.fr/NOS, sans clé, mises à jour le 28/09 | ✅ nomenclatures ouvertes (TRE_R279 lue) | Sur chaque fiche : PASA, UHR, unité Alzheimer, accueil de jour, hébergement temporaire. Nouveaux filtres. Pages « EHPAD avec unité Alzheimer à [ville] » (fortes requêtes). Corrige le guide qui dit que « les données publiques ne disent pas » quels EHPAD ont une unité protégée | 1 à 2 jours |
| 2 | **Atlasanté t_actfiness** : capacités par activité et par EHPAD, CSV 2019 → janvier 2026, avec les libellés. 2 268 EHPAD avec PASA, 210 avec UHR, 3 566 avec hébergement temporaire (17 338 places), 1 321 avec accueil de jour | ✅ | Contrôle croisé de la n° 1, et historique | inclus dans la n° 1 |
| 3 | **Rapports d'inspection des ARS** (plan de contrôle EHPAD 2022-2024) : hub national, 12 régions, ≈ 6 000 documents ; IDF avec FINESS dans le nom de fichier | ✅ hub et comptages ; ❌ téléchargement automatisé des PDF (403) | Lien daté « Rapport d'inspection ARS » sur la fiche. Jamais de résumé | 2 à 4 jours, en partie manuel |
| 4 | **INSEE, population par âge et par commune** (Melodi `DS_RP_TD_POPULATION_AGESEX_PRINC`, RP 2023, sans clé) | ✅ (Lyon : 41 008 personnes de 75 ans et plus, 15 026 de 85 ans et plus) | Pages villes : nombre de 75+ et de 85+, places d'EHPAD pour 1 000 habitants de 75 ans et plus | ½ jour |
| 5 | **DREES : bénéficiaires APA et ASH par département** (2024 définitif, 2025 provisoire) ; dépenses d'aide sociale 1999-2024 | ⚠️ non ouvert (API interdite aux robots) | Pages départements : nombre de bénéficiaires, dépense moyenne | ½ jour, après téléchargement manuel |
| 6 | **ATIH, tableau de bord ESMS** : taux d'occupation, rotation, absentéisme, par région et catégorie, 2019-2024 | ✅ (EHPAD 2024 : occupation médiane 97 %, rotation 14 %) — jamais par établissement | Repères régionaux de tension et de personnel, à citer comme tels | ½ jour |
| 7 | **RDAS départementaux** : texte lu pour 20 collectivités | ✅ | « Les règles de votre département » : barème indicatif d'obligation alimentaire (méthodes incompatibles d'un département à l'autre), argent de poche extra-légal (Paris, Finistère), charges déductibles (mutuelle, obsèques), minimum du conjoint à domicile, La Réunion qui renonce à la récupération sur succession | Lourd, manuel : 101 départements |
| 8 | **Hébergement temporaire en sortie d'hospitalisation (HTSH)** : 30 jours au plus, reste à charge ≈ 20 €/jour (IDF), 0 € selon la page Grand Est | ⚠️ règles régionales, à lire en entier | Guide « Après une hospitalisation » et fiches des EHPAD participants : change fortement le reste à charge d'un séjour temporaire | 1 jour |
| 9 | **Arrêts de transport en commun** (fichier national, 437 Mo, janvier 2026) | ⚠️ structure vue, contenu non ouvert | « Arrêt de bus ou de tram à X m » sur la fiche : question des familles qui rendent visite sans voiture | 1 jour |
| 10 | **Acceslibre** : 4 387 fiches « Ehpad » avec attributs d'accessibilité, SIRET | ✅ | Accessibilité de l'entrée ; jointure par SIRET à vérifier | 1 jour |
| 11 | **INSEE, temps d'accès aux équipements** (urgences, pharmacie, médecin), carreaux de 200 m, 2024-2025 | ⚠️ structure vue | Pages villes : temps d'accès aux urgences | 1 jour, fichiers de plusieurs Go |
| 12 | **Recherche d'entreprises** avec le filtre `id_finess=` | ✅ (690802384 → MEDOTELS, grande entreprise) | « Géré par [groupe], [catégorie] » sur la fiche. ⚠️ Débit limité (erreurs 429) : à faire au build, lentement | ½ jour |
| 13 | **OpenFisca ASPA** | ✅ (576,93 €/mois sur le cas testé) | Signaler un droit probable à l'ASPA quand la retraite est basse (non-recours) | ½ jour |
| 14 | **Annuaire de l'administration (DILA)** : 780 points d'information personnes âgées, 387 maisons de l'autonomie, 142 plateformes de répit, 11 908 CCAS | ✅ comptages ; ⚠️ API interdite aux robots, licence non renseignée | Étapes « à qui s'adresser » avec l'adresse réelle, via un export téléchargé à la main | 1 jour |
| 15 | **RPPS, fichier des activités** (822 Mo, quotidien) : « FINESS site » de chaque professionnel | ⚠️ couverture des salariés non vérifiée | Nombre de médecins et d'infirmiers rattachés à un EHPAD. À vérifier avant toute publication | à évaluer |

---

## 3. Confirmé : toujours rien d'ouvert

- **Places disponibles et délais par établissement** ❌ : l'export ouvert du ROR n'a aucun champ de disponibilité.
- **Personnel par EHPAD** (encadrement, absentéisme, rotation) ❌.
  - Le décret n° 2026-760 du 8 août 2026 fixe les 3 indicateurs, mais seul le portail CNSA les affiche, et son API est interdite aux robots.
  - L'ATIH ne publie que des agrégats régionaux.
- **Prix CNSA plus récents que janvier 2026** ❌. Le ROR ne donne presque aucun prix (Bretagne : 0 EHPAD sur 512).
- **Résidences autonomie ou services seniors avec leurs prix** ❌ : seulement des listes locales, sans prix.
- **Montants d'ASH par département** ❌ : la publication DREES est annoncée, mais pas en ligne.
- **APL en EHPAD** ❌ : OpenFisca indique lui-même que le cas n'est pas calculable. Le site continue de ne pas l'estimer, et c'est la bonne décision.

## 4. Écartés

| Source | Raison |
|---|---|
| OpenStreetMap | 93 % des EHPAD cartographiés viennent d'un import FINESS de 2019 ; licence ODbL |
| Wikidata | Un site web pour 127 EHPAD seulement |
| BODACC | Procédures collectives des gestionnaires : risque juridique |
| Offres France Travail | Indicateur de tension peu fiable et stigmatisant |
| Synerpa, KPMG | Problème de neutralité |
| Ma Boussole Aidants | Conditions d'utilisation interdisant l'extraction : lien uniquement |
| ANAP / tableau de bord ATIH par établissement | Accès réservé |
| data.inclusion | Nouveau domaine, données derrière un jeton |
| Annuaire Santé FHIR | Clé gratuite nécessaire, apport faible par rapport à FINESS+ |
| Légifrance | API PISTE en OAuth ; site en 403, non contourné. Alternative : les archives LEGI de la DILA |

## 5. Incidents pendant l'audit, à connaître

- **Adresse e-mail transmise à un service tiers.** Un appel à l'API Wikidata est parti avec l'adresse e-mail de l'éditeur dans l'en-tête User-Agent. L'appel a été refusé (429) ; les suivants ont utilisé un identifiant générique. C'est une erreur de notre part : cette adresse ne devait pas quitter la session.
- **Appels à des API interdites aux robots.** Environ 30 appels (métadonnées, comptages) ont visé des API Opendatasoft, et 3 CSV ont été téléchargés à l'ATIH, avant la lecture de leur robots.txt. Aucune de ces données n'est ni ne sera utilisée dans le site.
- **Connexions instables.** Le proxy sortant a coupé beaucoup de connexions vers data.gouv. Géorisques, l'API Adresse, Overpass et annuaire.sante.fr n'ont pas pu être évalués ; ces échecs ne prouvent pas que ces services sont en panne.

## 6. Décisions à prendre

1. **MTP** : appliquer la formule réglementaire dès maintenant (seuil inférieur à 2 869,55 €), ou attendre que le portail officiel se mette à jour.
2. **Ordre des lots.**
   - Proposé : corrections (MTP, bascule FINESS+), puis activités Alzheimer / PASA / UHR / accueil de jour, puis population 75+ par commune, puis liens vers les rapports d'inspection.
   - Plus tard : RDAS, sortie d'hospitalisation, transports, accessibilité, gestionnaire, ASPA.
3. **Données DREES** : téléchargement manuel par l'éditeur (les fichiers sont publics, seule l'API est interdite aux robots) ou demande écrite à la DREES.
