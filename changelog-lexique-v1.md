# Lexique et page GIR — v1 (29/09/2026)

## Décisions de l'éditeur

- **Structure** : une page unique `/lexique/` avec une ancre par terme, plus une page dédiée au GIR (`/guides/gir-niveau-autonomie/`).
- **Comportement** : une bulle de définition au survol ou au focus clavier ; le clic mène à `/lexique/#terme`.
- **Fréquence** : seule la première occurrence de chaque terme est soulignée, une fois par page.

## Contenu

- **50 termes, en 6 familles** : établissements, autonomie, tarifs, aides, démarches, données.
- **Vérification** : chaque définition a été vérifiée le 29/09/2026 sur une source officielle consultée ce jour-là (service-public, pour-les-personnes-agees.gouv.fr, CNSA, HAS, BOFiP, CAF…). Bilan : 50 ✅, EHPA retiré (⚠️, aucune définition officielle trouvée).
- **Structure d'une entrée** : une définition de 45 mots au plus, une bulle de 140 caractères au plus, une ligne « Pour vous », la source, et un lien « En savoir plus » vers la page qui approfondit.
- **Balisage** : JSON-LD `DefinedTermSet`. ⚠️ Il n'y a pas d'affichage enrichi dans Google ; le balisage sert la compréhension par les moteurs et les assistants IA.
- **Page GIR**
  - Contenu : les 6 niveaux (service-public F1229), la grille AGGIR, qui évalue le GIR, ses effets sur la facture et l'APA, la réévaluation et la contestation.
  - Tarif dépendance médian par GIR (CNSA, 4 731 établissements hors expérimentation) : 690, 438 et 186 € par mois.
  - Répartition des résidents par GIR : 55 % en GIR 1-2, 39 % en GIR 3-4, 6 % en GIR 5-6, sur 590 834 résidents (DREES Badiane 2023, tableau 11).
- **Données** : `build/lexique.json`. Aucune définition n'est écrite dans le code.

## Soulignement

- **Pages générées** : `build/lexique_liens.py`, lancé en dernier et idempotent.
  - Il n'agit que dans `<main>` ou `<section class="page">`. Sont exclus : titres, liens, boutons, libellés, résumés dépliables, tableaux, menus, pied de page, scripts.
  - Un terme n'est pas souligné sur sa page d'approfondissement.
  - Bilan : 118 326 mots soulignés sur 7 912 pages, 10 par page en moyenne et 20 au plus.
- **Accueil** : `lexiquer()` dans app.js s'applique à la fiche et aux étapes calculées en direct, à partir de `site/data/lexique.js`.
- **Branchement dans les scripts de construction** : `build_seo.py` appelle le soulignement à la fin, et `build_site.py` le fait sur l'accueil.
- **Style** : pointillé discret, couleur du texte conservée, bulle en CSS (`data-def`) au survol (appareils qui en disposent) et au focus clavier.
- **Navigation** : lien « Lexique » dans les menus « Naviguer », les pieds de page et llms.txt. La barre d'en-tête n'est pas modifiée, à la demande de l'éditeur (une ligne).

## Corrections de contenu relevées pendant la vérification

- **Unité protégée**
  - « espace fermé » est retiré : absent de la source officielle.
  - « tarif en général le même » est remplacé par « peut être le même ou différent : demandez-le ».
- **PASA** : il était présenté comme un « accueil de jour ». Il s'agit d'un accueil en journée des résidents de l'EHPAD, à distinguer de l'accueil de jour, destiné aux personnes qui vivent chez elles.
- **ViaTrajectoire** : « une seule porte d'entrée » est remplacé. Le dossier unique se dépose en ligne dans la quasi-totalité des départements, ou sur papier (Cerfa 14732).
- **Tarif global** : « médecins et médicaments » est remplacé par « médecins généralistes et examens courants ». Les médicaments ne figurent pas dans la source officielle consultée (⚠️ lien avec la PUI non vérifié).

## Vérifications

- Pages : 11 583. Liens cassés : 0. JSON-LD invalides : 0. Liens imbriqués : 0. Titres de plus de 60 caractères : 0.
- Tests : t_ux_accueil 52/52, runTests OK, Worker 42/42 (chemins régénérés avec /lexique/ et la page GIR).
- Mobile (360 px) : aucun défilement horizontal.

## À faire par l'éditeur

1. Extraire lexique-1 à lexique-6.zip dans V8, puis add, commit et push.
2. `wrangler deploy` dans worker-mesure, pour que le compteur connaisse les deux nouvelles pages.
