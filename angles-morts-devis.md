# Comparateur de devis EHPAD — angles morts (itération 2)

Date : 14/09/2026. Méthode : 7 recherches documentaires + mesures directes sur la base du site
(7 417 établissements) et sur le fichier brut CNSA téléchargé le jour même.
Convention : ✅ vérifié · ⚠️ inféré · ❌ non trouvé.

## 0. Rappel de l'itération 1

❌ Aucun modèle de devis normalisé n'existe (preuve : le tableau INC recensant les 11 secteurs
soumis à obligation de devis n'inclut pas l'EHPAD). Régime applicable : R.111-3 code de la
consommation — devis à la demande, sans format imposé.

✅ Trois choses sont normalisées : le socle de prestations (annexe 2-3-1 CASF, 5 groupes,
modifié par le décret 2022-734) ; la structure hébergement / dépendance GIR / soins ; le
formulaire de déclaration CNSA Prix-ESMS (40 colonnes, dont 11 prestations déclinées en
« incluse » et « en sus », dont 2 mortes depuis 2023).

## A. Angles morts qui invalident la comparaison elle-même

### A1. Le tarif dépendance n'est pas le même flux d'argent selon le département ✅
Deux régimes de versement de l'APA en établissement :
- **dotation globale** (art. L.232-8, R.314-173 CASF) versée par le département à l'établissement
  au 1/12e, sans dossier individuel : le tarif dépendance est **déjà déduit** de la facture ;
- **versement individuel** (art. R.232-30) au résident ou à l'établissement : le tarif dépendance
  **plein** peut apparaître, l'APA étant versée à part.
Conséquence : deux devis affichant « GIR 1-2 : 23,46 € » ne décrivent pas la même dépense.
❌ Aucune base publique ne dit quel département applique quel régime.

### A2. 22 % du parc n'a plus de structure GIR — MESURÉ
Expérimentation fusion soins/dépendance (art. 79 LFSS 2024, décret 2025-168, arrêté du 6 juin
2025), 23 territoires, depuis le 01/07/2025, prolongation au 31/12/2027 ⚠️ (adoptée en
commission le 31/10/2025, texte final non vérifié).
L'APA en établissement y est **supprimée**, remplacée par une participation forfaitaire
nationale : **6,10 € en 2025, 6,16 € en 2026**, identique quel que soit le GIR et les ressources.

Mesure sur la base du site :
| Régime | Établissements | 3 tarifs GIR identiques |
|---|---|---|
| classique | 5 800 (78 %) | 0 (0 %) |
| expérimental | 1 617 (22 %) | 1 350 (**83 %**) |

Un comparateur générique afficherait une grille GIR 1-2 / 3-4 / 5-6 qui n'existe plus
pour 1 617 établissements. La détection du régime par code commune INSEE est donc
**une dépendance dure du module**, pas une finesse.

### A3. Clause de non-augmentation : deux voisins, deux montants ✅
Dans les territoires expérimentateurs, un résident qui payait moins de 6,10 €/jour au 30/06/2025
**conserve son montant antérieur**. Le devis d'un nouvel entrant (6,16 €) ne décrit donc pas la
situation des résidents en place. Toute comparaison « ce que paient les résidents » est fausse.

### A4. Tarifs différenciés : jusqu'à +35 % dans le même établissement ✅
Art. L.342-3-1 et D.342-6 CASF : un EHPAD totalement ou majoritairement habilité peut appliquer
un tarif « libre » aux non-bénéficiaires de l'ASH, plafonné à **+35 %** au niveau national (le
département peut fixer moins), pour les admissions à compter du 01/01/2025.
Deux prix légaux coexistent donc dans le même établissement, pour la même chambre.

### A5. Tarif « moins de 60 ans » ✅
Admission par dérogation. L'APA étant réservée aux 60 ans et plus, le tarif est **unique et
intègre la dépendance** — non comparable ligne à ligne avec un devis standard.
Dans les territoires expérimentaux la formule devient « 6,16 € + tarif hébergement ».

## B. Angles morts de données — MESURÉS sur la base du site

### B1. Fraîcheur de la déclaration CNSA
| Dernière déclaration | Établissements | Part |
|---|---|---|
| 2026 | 1 132 | 15 % |
| 2025 | 4 954 | 67 % |
| **aucune date** | **1 331** | **18 %** |

Obligation légale : déclarer avant le 30 juin de chaque année. 18 % du parc n'a aucune date.
Un recoupement devis / déclaration est impossible pour ceux-là, et doit le dire.

### B2. Couverture du prix par statut
| Statut | Prix hébergement renseigné |
|---|---|
| Public | 2 443 / 3 269 (75 %) |
| Privé à but non lucratif | 1 745 / 2 342 (75 %) |
| Privé commercial | 1 600 / 1 798 (**89 %**) |

Contre-intuitif et utile : le privé commercial déclare **mieux** que le public. ⚠️ Explication
probable : les non habilités fixent librement leur prix (L.342-3) et doivent le publier, alors
que le tarif d'un habilité est arrêté par le département.

### B3. Fiches réellement exploitables pour un recoupement
**5 793 / 7 417 (78 %)** ont à la fois un prix hébergement, un talon GIR 5-6 et une déclaration
de 2025 ou 2026. Pour les 22 % restants, le module doit afficher « pas de déclaration
comparable », jamais un écart.

### B4. Champs morts du contrat de données
`linge` et `lingeU` : **0 / 7 417**. Cohérent avec l'entrée du linge personnel dans le socle au
01/01/2023 (décret 2022-734) et avec les colonnes PREST1/PREST2/PRESTSUS1/PRIX_LINGE désormais
vides côté CNSA. À retirer du contrat de données ou à documenter comme abandonnés.

### B5. Prestations déclarées : moitié du parc muette
49 % déclarent au moins une prestation incluse, 38 % au moins une en sus, 25 % remplissent le
champ libre. Le contrat de données le formule déjà correctement — « une prestation non citée
n'est pas non comprise : elle est non renseignée » — et c'est ce que l'écran devra répéter.

### B6. Conventionnement APL : donnée publique périmée ✅
Le champ `IsCONV_APL` existe dans le jeu « Établissements EHPAD… » de data.gouv.fr, mais ce jeu
affiche une dernière mise à jour au **11 novembre 2020**. APL et ALS ne sont jamais cumulables
et dépendent de ce conventionnement. ❌ Aucune base publique à jour et faisant foi.

### B7. Place habilitée ASH : information inexistante ✅/❌
Les jeux publics ne portent qu'un booléen **au niveau établissement** (`IsHAB_AIDE_SOC`), sans
distinction habilitation totale / partielle ni nombre de places.
❌ Aucune base ne publie le nombre ou l'identité des places habilitées.
Conséquence : **un devis peut porter sur une place non habilitée dans un EHPAD pourtant
référencé « habilité »** — l'ASH sera refusée et le prix jusqu'à 35 % supérieur.

## C. Angles morts de calcul du reste à charge

### C1. Réduction d'impôt : trompeuse dans la majorité des cas ✅
Art. 199 quindecies CGI. 25 % des dépenses d'hébergement **et dépendance** restant à charge,
**après déduction de l'APA, de l'ASH et des aides au logement**, plafond **10 000 € par an et
par personne hébergée**, soit 2 500 € maximum.
Deux écrêtages que le module doit rendre visibles :
- le plafond est atteint dès **~830 €/mois** de reste à charge : au-delà, l'avantage n'augmente plus ;
- c'est une **réduction**, pas un crédit : une personne non imposable ne touche **rien**, et
  ❌ aucun crédit d'impôt de substitution n'existe.
Afficher « −2 500 €/an » sur un devis est donc faux pour une grande partie des résidents.

### C2. Ticket modérateur GIR 5-6 ✅
Dû par **tous** les résidents, quel que soit le GIR et les ressources (art. R.232-19).
❌ Aucun montant national : il est fixé établissement par établissement. Non généralisable.

### C3. Barème de participation APA 2026 ✅
Ressources ≤ 2 846,77 € → seul le talon GIR 5-6 ; entre 2 846,77 € et 4 379,64 € → participation
progressive jusqu'à 80 % de l'écart au talon ; au-delà → 80 %.

### C4. ASH — minimums et récupération 2026 ✅
90 % des ressources reversées ; **125 €/mois minimum** laissés au résident ; **1 043,59 €/mois**
au conjoint resté à domicile (indexé sur l'ASPA, change chaque année).
Récupération sur succession **dès le premier euro** (❌ pas de seuil, contrairement à l'ASPA et
son seuil de 108 586,14 € — ne pas transposer), sur les donations des **10 ans** précédant *ou
suivant* la demande, et en cas de retour à meilleure fortune.
Obligation alimentaire après la loi 2024-317 du 08/04/2024 : **petits-enfants dispensés** dans le
cadre d'une demande d'ASH ; **enfants, gendres et belles-filles toujours sollicités**.
⚠️ solidarites.gouv.fr mentionne encore les petits-enfants : deux sites de l'État se contredisent.

### C5. Postes absents des devis mais réellement facturés ✅
Revalorisation annuelle **+0,86 % en 2026** (arrêté du 24/12/2025) — uniquement non habilités et
tarifs différenciés ; absence pour hospitalisation : plein tarif 72 h puis minoration du forfait
journalier hospitalier (**23 €/jour depuis le 01/03/2026**), le forfait restant dû à l'hôpital
(double charge) ; facturation jusqu'à **6 jours après le décès** (R.314-149) ; dépôt de garantie
plafonné au **tarif mensuel d'hébergement** (R.314-149), restitution sous 30 jours ; préavis
1 mois, rétractation 15 jours.

## D. Angles morts juridiques — le risque porte sur l'éditeur

### D1. Le site serait ÉDITEUR, pas hébergeur ⚠️
Statut dissocié : les montants saisis par la famille sont un contenu tiers — et s'ils restent en
session, il n'y a même pas « stockage pour mise à disposition du public », donc le régime
hébergeur n'a pas d'objet. En revanche **le calcul, la méthode, les écarts affichés et la
désignation des établissements sont produits par le site** : éditeur au sens plein. Le bouclier
LCEN ne couvre pas le résultat. ❌ Aucune décision ne qualifie un simulateur au regard de la LCEN.

### D2. Dénigrement : ni la vérité ni l'absence de concurrence ne protègent ✅
- **Cass. com. 8 nov. 2017, n° 16-15.162** : « le seul fait de comparer les prix […] ne
  caractérise pas un dénigrement ». La comparaison en soi est licite.
- **Cass. com. 9 janv. 2019, n° 17-18.350** : une information échappe au dénigrement seulement si
  elle réunit **cumulativement** un sujet d'intérêt général, une **base factuelle suffisante** et
  **une certaine mesure** dans l'expression.
- **Cass. com. 4 mars 2020, n° 18-15.651** : le dénigrement est constitué **même sans situation
  de concurrence**. Le site n'est donc pas à l'abri parce qu'il ne vend rien.
- L'exactitude n'exonère pas (rejet de l'*exceptio veritatis*).
- **T. com. Lyon, 24 avr. 2017** : comparaison illicite pour écart annoncé 41,00 € contre 0,95 €
  réel — **comparer des périmètres différents est le piège documenté**.

### D3. Cinq causes légitimes d'écart déclaré CNSA / devis ✅
Le portail officiel avertit lui-même : « Des prix hébergement différents du prix affiché peuvent
être pratiqués ». Les causes : (1) le prix CNSA est un **« à partir de »** ; (2) il couvre le
**socle seul** ; (3) il peut dater de la dernière déclaration au 30 juin ; (4) le devis peut
inclure le tarif dépendance ; (5) un **tarif différencié** (+35 %) peut s'appliquer.
Afficher un écart brut serait donc à la fois **faux** et **risqué**.

### D4. Obligations de transparence des comparateurs ⚠️
Art. L.111-7 et D.111-6 à D.111-8 code de la consommation, décret 2016-505 : s'appliquent à tout
service de classement d'offres de tiers, **même gratuit et non rémunéré**. Sanction jusqu'à
375 000 € (personne morale). **Cass. com. 4 déc. 2012, n° 11-27.729** (Leguide.com) : condamnation
pour défaut d'information sur le référencement payant.
⚠️ La qualification est incertaine pour un outil où la famille saisit ses propres devis, mais dès
lors que le site y adjoint ses données d'établissements et nomme des EHPAD, la frontière devient
ténue. **S'y conformer volontairement est la position sûre.**

### D5. Ce que le module doit dire à l'utilisateur ✅
Le devis n'est qu'une **offre** : il n'engage qu'une fois accepté, et l'acte qui fixe le prix dû
est le **contrat de séjour** (ou le DIPC). En EHPAD non habilité le prix est **librement fixé à la
signature** (L.342-3) : un devis de septembre ne verrouille rien pour une entrée en janvier, sauf
clause expresse. ❌ Aucune durée de validité légale chiffrée n'existe ; à défaut de mention,
art. 1117 C. civ. — « délai raisonnable », non défini. ⚠️ Le « 3 mois » avancé par l'INC n'est
adossé à aucune décision citée : ne pas l'affirmer.

## E. L'angle mort d'usage — le plus dangereux, et il ne se corrige pas par du code

Question : une famille a-t-elle réellement plusieurs devis à comparer ?

Contre :
- ✅ **29 % des entrées en 2023 proviennent d'un établissement de santé** (DREES ER 1351). Une
  sortie d'hospitalisation ne laisse pas le temps d'une mise en concurrence.
- ✅ **55 % des admis en 2023 entrent moins d'un mois après réception du dossier** (62,1 % en
  2019). Lu comme une bonne nouvelle, ce chiffre signe plutôt un **choix subi**.
- ✅ Les places vacantes sont dans le **mauvais segment** : privé lucratif 89,3 % d'occupation,
  grands groupes 89 % et +8 €/nuit à caractéristiques égales, Île-de-France 83-85 % — c'est-à-dire
  le segment le plus cher et non habilité. Le privé non lucratif reste à 94 %.
- ✅ **La fenêtre se referme** : Clariane +1,3 pt (T1 2026), emeis +2,4 à +2,9 pts (S1 2026).
- ✅ **La disponibilité reste non publique** : le décret du 08/08/2026 a ajouté trois indicateurs
  (encadrement, absentéisme, rotation) mais **pas les places disponibles**.
- ❌ Aucune enquête ne démontre que les familles comparent, ni que le prix pèse dans leurs critères.

Pour :
- ✅ ViaTrajectoire permet d'adresser un dossier unique à un nombre **illimité** d'établissements.
- ✅ **≈ 36 870 places vacantes** en EHPAD fin 2023 (DREES), contre 97 % d'occupation en 2019.
- ✅ L'écart à comparer est massif : ~1 000 €/mois entre public et privé ; 1 749 € (Meuse) à
  3 698 € (Paris) ; reste à charge moyen de 416 €/mois prélevé sur l'épargne (UFC 2022).

⚠️ **Conclusion** : le marché adressable n'est pas « les familles qui cherchent un EHPAD » mais
l'intersection *entrée anticipée × famille solvable × zone où le privé commercial est présent ×
avant que l'occupation ne repasse au-dessus de 93-94 %*. C'est un segment réel mais minoritaire,
et la fenêtre se referme d'environ 2 points par an.

**Donnée manquante à aller chercher en priorité** : le module Observatoire de ViaTrajectoire
calcule le nombre moyen d'établissements destinataires par dossier. Il n'est pas publié. Une
demande auprès d'un GRADeS régional ou d'une ARS est le chemin le plus court.

## F. Ce qui reste non trouvé

- ❌ Fondement de l'obligation d'affichage des prix en EHPAD (la DGCCRF la décrit sans citer de texte).
- ❌ Maquette de saisie de Prix-ESMS (le manuel CNSA ne traite que de la connexion).
- ❌ Base légale ou interdiction des « frais de dossier » / « frais d'entrée ».
- ❌ Jurisprudence sur la caducité d'un devis d'EHPAD ; sur la qualification LCEN d'un simulateur ;
  sur la condamnation d'un site d'information gratuit pour comparaison tarifaire nominative.
- ❌ Part des entrées non programmées ; nombre d'établissements sollicités par dossier ;
  hiérarchie des critères de choix des familles.
- ⚠️ Légifrance bloque l'accès automatisé : aucun contournement tenté. Toutes les références de
  textes proviennent de relais institutionnels et n'ont pas été lues à la source.
