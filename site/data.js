/* =====================================================================
   data.js — Règles, barèmes, sources et modes d'emploi de trouver-mon-ehpad.fr — v2.0
   Chaque valeur porte sa source et sa date de vérification.
   Aucune donnée n'est inventée : ce qui n'est pas publié est affiché comme tel.
   ===================================================================== */

window.META = {
  version: '2.5',
  lastVerified: '2026-09-12',
  month: 30.5,
  monthNote: 'Les prix publiés par la CNSA sont journaliers. Nous les multiplions par 30,5 jours (moyenne d’un mois). La CNSA communique parfois sur 30 jours : l’écart est d’environ 1,7 %.',
};

/* ---------- Barèmes nationaux (vérifiés le 10/09/2026) ---------- */
window.BAREME = {
  // APA en établissement — formule OpenFisca-France « apa_etablissement », validée à 0,00 € près
  // contre l'API de référence sur cinq cas de test (voir MAINTENANCE.md §7).
  mtp: 1288.13,                      // majoration pour tierce personne, depuis le 01/04/2025
  seuilInf: 2.21,                    // × MTP → 2 846,77 €/mois
  seuilSup: 3.4,                     // × MTP → 4 379,64 €/mois
  pente: 0.80,
  divisionCouple: 2,
  smicHoraire: 12.31,                // Smic brut horaire au 01/06/2026
  seuilVersementSmic: 3,

  // Réduction d'impôt (art. 199 quindecies du CGI) — par personne hébergée
  irTaux: 0.25,
  irPlafond: 10000,

  // Aide sociale à l'hébergement (service-public F2444, vérifiée le 01/01/2026)
  ashResteMiniPct: 0.10,
  ashResteMiniEur: 125,
  ashConjointDomicile: 1043.59,
  obligeMoyenne: 270,                // participation moyenne d'un obligé alimentaire (DREES, fin 2023)
};

window.SEUILS = {
  apaInf: +(window.BAREME.seuilInf * window.BAREME.mtp).toFixed(2),
  apaSup: +(window.BAREME.seuilSup * window.BAREME.mtp).toFixed(2),
  apaVersement: +(window.BAREME.seuilVersementSmic * window.BAREME.smicHoraire).toFixed(2),
};

/* ---------- Occupation et rotation (DREES, enquête EHPA 2023) ----------
   Le taux d'occupation de chaque établissement vient de son segment
   (statut juridique × densité de la commune) : il est stocké dans les données.
   La rotation est calculée : sorties définitives 2023 ÷ places installées 2023. */
/* La rotation servait à extrapoler un nombre de places libres par établissement.
   Cette extrapolation a été retirée : une moyenne de segment ne dit rien d'un
   établissement un jour donné. Les constantes sont conservées comme repères
   sectoriels, sans être utilisées par le calcul. */
window.ROTATION = { 0: 0.359, 1: 0.366, 2: 0.480, FR: 0.388 };
window.OCCUPATION_FR = 93.95;
window.DELAI_ATTENTE = 'Un mois ou moins pour 55 % des personnes entrées en établissement en 2023 (DREES).';

/* ---------- Couverture des données — RECALCULÉE À CHAQUE BUILD ----------
   Ne pas modifier à la main : le bloc entre les deux marques est réécrit par
   build/split_data_v2.py. Ces chiffres disent ce que le site NE SAIT PAS. */
/* @couverture:debut */
window.COUVERTURE = {"date": "2026-09-12", "total": 7417, "prix": 5794, "dependance": 6081, "has": 4815, "capacite": 5307, "position": 7350, "positionApprochee": 151, "tel": 7346, "exp": 1617, "classique": 5800, "regimeInconnu": 0, "ashHabilite": 6081, "ashAConfirmer": 194};
/* @couverture:fin */

/* ---------- Inflation (INSEE, moyenne annuelle) ---------- */
window.INFLATION = { 2019: 1.1, 2020: 0.5, 2021: 1.6, 2022: 5.2, 2023: 4.9, 2024: 2.0, 2025: 0.9 };
window.INFLATION_CUM_2018_2025 = 17.2;
window.PRIX_ANNEES = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];

/* ---------- Libellés ---------- */
window.STATUTS = ['Public', 'Privé à but non lucratif', 'Privé commercial'];
window.STATUT_COURT = ['Public', 'Associatif', 'Privé commercial'];
window.HAS_CHAPITRES = ['La personne', 'Les professionnels', 'L’ESSMS'];
window.ASH_ETAT = {
  1: { txt: 'Habilité à l’aide sociale', cls: 'b-bleu' },
  0: { txt: 'Non habilité à l’aide sociale', cls: 'b-gris' },
  2: { txt: 'Habilitation à confirmer', cls: 'b-orange' },
};
window.ASH_SRC = {
  finess: '✅ mode de fixation tarifaire officiel (FINESS)',
  csa: '⚠️ déduit du tarif « aide sociale » déclaré à la CNSA',
  divergence: '⚠️ FINESS indique « non habilité » mais l’établissement déclare un tarif « aide sociale » à la CNSA : habilitation partielle probable, à vérifier auprès de l’établissement',
  '2020': '⚠️ habilitation déclarée à la CNSA en 2020',
  mft: '⚠️ déduit du mode de fixation tarifaire',
};
window.STATUT_SRC = {
  '2020': 'statut déclaré à la CNSA (fichier 2020)',
  has: 'statut publié par la Haute Autorité de santé',
  code: 'statut déduit du code juridique FINESS (méthode : §4 de la page méthodologie)',
};
window.TARIF_SOINS = {
  G: 'Tarif global de soins : l’établissement finance les médecins, les auxiliaires médicaux et les médicaments.',
  P: 'Tarif partiel de soins : les médicaments et les dispositifs médicaux passent par les soins de ville (votre médecin, votre pharmacie).',
  V: 'Petite unité de vie : financement des soins par forfait ou par convention avec un service de soins infirmiers.',
};

/* ---------- Ce que le site ne simule pas, et pourquoi ---------- */
window.NON_SIMULE = [
  { t: 'Les places réellement disponibles',
    d: 'Neuf pistes testées, aucune ouverte : ViaTrajectoire n’a pas d’API publique, l’annuaire officiel interdit son API aux robots, le tableau de bord de la performance médico-sociale est réservé aux professionnels. Nous n’affichons donc aucune estimation de places libres : une moyenne de segment ne dit rien d’un établissement un jour donné. À la place, la fiche donne les questions précises à poser à l’établissement et son numéro de téléphone.' },
  { t: 'Le taux d’encadrement, l’absentéisme et la rotation du personnel par établissement',
    d: 'Publiés depuis août 2026 sur le portail officiel, mais pas en données ouvertes. Nous donnons la moyenne départementale (Badiane 2023) et un lien vers la fiche officielle.' },
  { t: 'Le barème de l’obligation alimentaire',
    d: 'Il n’existe pas au niveau national : le conseil départemental, et à défaut le juge aux affaires familiales, fixe la part de chaque enfant. Nous proposons des clés de répartition à titre de discussion familiale, jamais comme une règle.' },
  { t: 'Le montant exact de l’aide au logement',
    d: 'Il dépend du conventionnement de l’établissement, absent des données ouvertes. Demandez-le, puis saisissez le montant notifié.' },
  { t: 'La capacité à jour de chaque établissement',
    d: 'Les capacités figurent dans FINESS mais sans la nomenclature qui dirait s’il s’agit de l’autorisé ou de l’installé : trois règles d’agrégation testées donnent des écarts de −12 % à +56 %. Nous utilisons donc la capacité déclarée à la CNSA en 2020, en le disant.' },
  { t: 'Les frais du premier mois',
    d: 'Dépôt de garantie (souvent trente jours d’hébergement), frais de dossier, éventuel préavis du logement quitté, déménagement, mobilier : rien de cela n’est publié dans une base, et rien n’entre dans le montant mensuel affiché ici. Demandez-en le détail chiffré avant de signer le contrat de séjour.' },
  { t: 'Les dépenses personnelles du quotidien',
    d: 'Mutuelle, coiffeur, pédicure, téléphone, télévision, protections non comprises, transports et consultations non prises en charge. Elles se règlent sur le reste à vivre, et une partie des établissements les facturent en supplément : la fiche indique les prestations déclarées comprises et celles déclarées en supplément, mais un champ vide signifie « non déclaré », jamais « non facturé ».' },
  { t: 'Les avis de familles',
    d: 'Modérer des avis sur des établissements accueillant des personnes vulnérables demande des moyens qu’un site gratuit n’a pas.' },
];

/* ---------- Provenance des données ---------- */
window.SOURCES = [
  { cat: 'Prix et tarifs dépendance', what: 'Prix de l’hébergement (chambre seule et double), tarif « aide sociale », tarifs GIR 1-2 / 3-4 / 5-6, prix du linge, accueil temporaire, avec la date de mise à jour déclarée par chaque établissement.', src: 'CNSA — Prix hébergement et tarifs dépendance des EHPAD, données brutes', url: 'https://www.data.gouv.fr/datasets/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/', note: 'Fichier annoncé mensuel ; le dernier disponible au 11/09/2026 porte sur janvier 2026. 5 794 établissements déclarent un prix, 1 623 n’en déclarent aucun. Ce jeu de données ne déclare pas de licence.' },
  { cat: 'Évolution du prix depuis 2018', what: 'Les fichiers annuels 2018 à 2025 de la CNSA, fusionnés par numéro FINESS, donnent la courbe du prix de la chambre seule pour 7 255 établissements.', src: 'CNSA — fichiers annuels 2018 à 2025', url: 'https://www.data.gouv.fr/datasets/prix-hebergement-et-tarifs-dependance-des-ehpad-donnees-brutes/', note: '2 860 établissements ont les huit années complètes. Une variation très forte traduit souvent un changement de ce que le prix recouvre, pas une décision tarifaire.' },
  { cat: 'Identité, adresse, habilitation et tarification', what: 'Nom, adresse géocodée, téléphone, date d’ouverture, gestionnaire, et le mode de fixation tarifaire dont le libellé officiel indique l’habilitation à l’aide sociale et le tarif de soins (global ou partiel, avec ou sans pharmacie à usage intérieur).', src: 'Agence du numérique en santé — FINESS (extraction du fichier des établissements et FINESS+ Structures)', url: 'https://www.data.gouv.fr/datasets/finess-extraction-du-fichier-des-etablissements/', note: '6 081 établissements habilités à l’aide sociale, 1 142 non habilités, 194 dont l’habilitation est à confirmer (le libellé FINESS et la déclaration CNSA divergent).' },
  { cat: 'Qualité', what: 'Note d’évaluation A à D, cotations des trois chapitres (« La personne », « Les professionnels », « L’ESSMS »), nombre de critères impératifs atteints sur 18, date de l’évaluation et organisme évaluateur.', src: 'Haute Autorité de santé — Résultats d’évaluation des ESSMS', url: 'https://www.data.gouv.fr/datasets/resultats-devaluation-des-etablissements-et-services-sociaux-et-medico-sociaux-essms/', note: '4 815 EHPAD évalués sur 7 417. L’organisme évaluateur est choisi et rémunéré par l’établissement : c’est pourquoi nous affichons son nom.' },
  { cat: 'Hygiène alimentaire', what: 'Résultat de la dernière inspection sanitaire de la cuisine, sa date et la suite donnée.', src: 'Direction générale de l’alimentation — Alim’confiance', url: 'https://dgal.opendatasoft.com/explore/dataset/export_alimconfiance/', note: '1 012 établissements appariés (SIRET, puis SIREN et commune quand un seul établissement correspond). L’absence de résultat ne signifie pas mauvaise note : seules 2 357 inspections en établissement médico-social sont publiées.' },
  { cat: 'Occupation du secteur', what: 'Taux d’occupation moyen du segment auquel appartient l’établissement (statut juridique × densité de la commune). Repère sectoriel affiché comme tel : aucun nombre de places libres n’en est déduit pour un établissement.', src: 'DREES — enquête EHPA 2023 (publiée le 04/11/2025) et Études et Résultats n° 1351', url: 'https://data.drees.solidarites-sante.gouv.fr/explore/dataset/587_l-enquete-aupres-des-etablissements-d-hebergement-pour-personnes-agees-ehpa/', note: 'Moyennes nationales issues d’une enquête : elles ne disent pas si une place est libre dans cet établissement aujourd’hui, et ce site n’en tire aucune estimation.' },
  { cat: 'Contexte départemental', what: 'Places installées, places habilitées à l’aide sociale, résidents, ETP par résident, part des places occupées par un bénéficiaire de l’ASH, taux d’équipement.', src: 'DREES — Badiane 2023 et Indicateurs sociaux départementaux 2024', url: 'https://www.data.gouv.fr/datasets/datadrees-badiane/', note: 'France entière : 612 292 places, dont 74,7 % habilitées à l’aide sociale, 0,671 ETP par résident.' },
  { cat: 'Aide sociale : pratique de votre département', what: 'Recours sur succession, personnes sollicitées au titre de l’obligation alimentaire, prise en charge du GIR 5-6, charges déductibles.', src: 'DREES — Modalités départementales de gestion de l’ASH', url: 'https://www.data.gouv.fr/datasets/les-modalites-departementales-de-gestion-de-lash-des-personnes-agees/', note: 'Enquête portant sur 2018, dernière publiée. Depuis, la loi du 8 avril 2024 a dispensé les petits-enfants de l’obligation alimentaire : la règle nationale prime sur la pratique déclarée en 2018.' },
  { cat: 'Statut, habilitation et capacité (historique)', what: 'Statut juridique en clair, capacité installée et prix 2020.', src: 'CNSA — données retraitées 2018-2020', url: 'https://www.data.gouv.fr/datasets/prix-hebergement-et-tarifs-dependance-des-ehpad/', note: 'Fichier arrêté en 2020 : la capacité affichée date de 2020. Ce jeu ne déclare pas de licence.' },
  { cat: 'APA en établissement', what: 'Formule de participation du résident et seuils de ressources : 2 846,77 € et 4 379,64 € par mois.', src: 'OpenFisca-France — variable apa_etablissement', url: 'https://fr.openfisca.org/legislation/apa_etablissement', note: 'Formule recopiée du code source, puis validée à 0,00 € près contre l’API de référence sur cinq cas, cas du couple compris.' },
  { cat: 'Fiscalité', what: 'Réduction d’impôt de 25 % pour la personne hébergée, plafonnée à 10 000 € de dépenses par an et par personne ; déduction sans plafond de la pension alimentaire versée par un enfant à un parent dans le besoin.', src: 'Service-public.fr fiche F17 et economie.gouv.fr', url: 'https://www.service-public.gouv.fr/particuliers/vosdroits/F17', note: 'La réduction appartient à la personne hébergée, pas à l’enfant qui paie. L’enfant, lui, déduit la pension de son revenu imposable ; le parent doit alors la déclarer.' },
  { cat: 'Aide sociale : règles nationales', what: 'Le résident conserve au moins 10 % de ses ressources et jamais moins de 125 €/mois ; le conjoint resté à domicile au moins 1 043,59 €/mois ; récupération sur la succession, sur les donations des dix années précédant ou suivant la demande, et en cas de retour à meilleure fortune.', src: 'Service-public.fr fiche F2444 (vérifiée le 01/01/2026)', url: 'https://www.service-public.gouv.fr/particuliers/vosdroits/F2444', note: 'Les petits-enfants sont dispensés de l’obligation alimentaire depuis la loi n° 2024-317 du 8 avril 2024. Les sommes versées par les enfants ne sont pas récupérables sur la succession.' },
  { cat: 'Inflation', what: 'Évolution moyenne annuelle de l’indice des prix à la consommation, pour comparer la hausse du prix de l’établissement à celle du coût de la vie.', src: 'INSEE — indice des prix à la consommation', url: 'https://www.insee.fr/fr/statistiques/8726461', note: '+1,8 % (2018), +1,1 %, +0,5 %, +1,6 %, +5,2 %, +4,9 %, +2,0 %, +0,9 % (2025). Cumul 2018→2025 : +17,2 %.' },
  { cat: 'Communes, densité et fond de carte', what: '35 493 couples code postal / commune, degré de densité des 34 875 communes, fond de plan IGN.', src: 'geo.api.gouv.fr, INSEE grille de densité 2026, IGN Géoplateforme', url: 'https://www.insee.fr/fr/information/8571524', note: 'La bibliothèque de cartographie est servie depuis ce site. Les tuiles du fond de plan, elles, sont téléchargées auprès de l’IGN à l’affichage de la carte : cet organisme public voit alors l’adresse IP du visiteur et la zone consultée.' },
];

/* ---------- Modes d'emploi ---------- */
window.ROADMAPS = {
  gir: {
    title: 'Faire évaluer le GIR de votre parent',
    when: 'En premier, avant toute demande d’aide — le GIR conditionne l’APA et le tarif dépendance facturé.',
    steps: [
      'Parlez-en au médecin traitant, qui rédige le certificat médical.',
      'Le médecin coordonnateur de l’EHPAD, ou l’équipe médico-sociale du conseil départemental, évalue la perte d’autonomie avec la grille AGGIR.',
      'Le GIR retenu (1 à 6) vous est notifié : conservez la notification, elle sert pour l’APA et pour la facture.',
    ],
    docs: ['Certificat médical du médecin traitant', 'Pièce d’identité et livret de famille', 'Justificatif de domicile'],
    warnings: ['La mini-grille de cette page n’est qu’une estimation : seul le GIR notifié fait foi. Ne payez pas un tarif dépendance GIR 1-2 sans notification.'],
  },
  apa: {
    title: 'Demander l’APA en établissement',
    when: 'Dès l’entrée — l’APA est le plus souvent versée directement à l’établissement, qui la déduit de la facture.',
    steps: [
      'Retirez le dossier auprès du conseil départemental du lieu de résidence du parent, ou de l’EHPAD qui le transmet souvent lui-même.',
      'Joignez la notification de GIR et les ressources du parent — toutes ses ressources, pas seulement ses retraites.',
      'Le département notifie le montant : c’est lui qui fait foi, pas l’estimation de cette page.',
    ],
    docs: ['Notification de GIR', 'Dernier avis d’imposition ou de non-imposition', 'Relevé d’identité bancaire', 'Justificatif de domicile en établissement'],
    warnings: ['Jusqu’à 2 846,77 € de ressources par mois, votre parent ne paie que le tarif GIR 5-6. Entre 2 846,77 € et 4 379,64 €, sa participation augmente progressivement. Au-delà, elle est plafonnée à 80 % de l’écart entre son tarif GIR et le tarif GIR 5-6.'],
  },
  via: {
    title: 'Déposer un dossier unique sur ViaTrajectoire',
    when: 'En parallèle des demandes d’aide, dès que la décision d’entrée est prise.',
    steps: [
      'Vérifiez que votre région utilise ViaTrajectoire : le déploiement est régional, et quelques départements passent encore par un dossier papier national (Cerfa 14732). L’établissement vous dira lequel il accepte.',
      'Créez le dossier sur ViaTrajectoire (volet grand âge) : un seul dossier, envoyé à autant d’établissements que vous le souhaitez parmi ceux qui y sont inscrits.',
      'Faites remplir le volet médical par le médecin traitant.',
      'Sélectionnez les établissements de votre liste — le plateau de comparaison de cette page vous donne leurs coordonnées.',
    ],
    docs: ['Compte ViaTrajectoire', 'Volet médical rempli par le médecin', 'Coordonnées des établissements visés'],
    warnings: [
      'Aucun site, celui-ci compris, ne connaît les places réellement disponibles : elles ne sont publiées nulle part. Seul l’établissement peut le dire.',
      'Le délai d’un mois ou moins concerne 55 % des personnes entrées en 2023 (DREES, enquête EHPA) : c’est une statistique nationale sur des entrées passées, pas une prévision pour votre dossier.',
    ],
  },
  apl: {
    title: 'Demander l’aide au logement (APL ou ALS)',
    when: 'Dès l’entrée. L’aide n’est pas rétroactive : elle part du dépôt de la demande, pas de l’entrée.',
    steps: [
      'Demandez à l’établissement s’il est conventionné : si oui, c’est l’APL ; sinon, c’est l’ALS.',
      'Déposez la demande auprès de la CAF ou de la MSA.',
      'Reportez le montant notifié dans le champ « aide au logement » de cette page pour affiner le calcul.',
    ],
    docs: ['Attestation de résidence délivrée par l’EHPAD', 'Ressources du parent', 'Relevé d’identité bancaire'],
    warnings: [
      'Le parcours en ligne n’accepte pas toujours l’hébergement en EHPAD : plusieurs usagers rapportent avoir dû passer par le formulaire papier. Ce n’est pas une règle nationale que nous ayons pu vérifier auprès de la CNAF — si le formulaire en ligne bloque, demandez le formulaire papier à votre caisse plutôt que de renoncer.',
      'Une aide au logement est notifiée POUR un établissement précis. Changer d’établissement suppose une nouvelle demande, et le montant peut être différent : ne reportez pas le même chiffre d’un EHPAD à l’autre.',
    ],
  },
  ash: {
    title: 'Demander l’aide sociale à l’hébergement (ASH)',
    when: 'Quand les ressources et l’épargne ne couvrent pas la facture. Il faut avoir 65 ans, ou 60 ans si l’on est reconnu inapte au travail, et résider en France de manière stable et régulière.',
    steps: [
      'Vérifiez auprès de l’établissement qu’une place habilitée à l’aide sociale est disponible : l’habilitation porte sur un nombre de places, pas sur l’établissement entier.',
      'Déposez le dossier au CCAS de la commune de résidence du parent, ou à la mairie, qui le transmet au conseil départemental.',
      'Le département examine toutes les ressources du parent, puis sollicite les obligés alimentaires selon sa propre pratique.',
      'La décision fixe la part du parent, celle des enfants et celle du département.',
    ],
    docs: ['Dossier de demande d’aide sociale du département', 'Avis d’imposition du parent et des obligés alimentaires', 'Relevés de comptes et d’épargne', 'Titre de propriété le cas échéant'],
    warnings: [
      'Votre parent conserve au moins 10 % de ses ressources, et jamais moins de 125 € par mois. Si son conjoint reste à domicile, celui-ci conserve au moins 1 043,59 € par mois.',
      'Les petits-enfants ne sont plus sollicités depuis la loi du 8 avril 2024. Les enfants, gendres et belles-filles peuvent l’être.',
      'L’aide versée est récupérable sur la part d’actif net de la succession, sur les donations des dix années précédant ou suivant la demande, et en cas de retour à meilleure fortune. Les sommes versées par les enfants, elles, ne le sont pas.',
      'Dans un établissement NON habilité, l’aide reste possible après un séjour payé sur ses propres ressources : cinq ans dans la plupart des départements, parfois moins. Le département fixe alors un tarif forfaitaire. Demandez la règle appliquée chez vous : elle figure au règlement départemental d’aide sociale.',
      'Le département compétent est celui du domicile de secours, acquis par trois mois de résidence habituelle. L’entrée en établissement n’en fait pas acquérir un nouveau : c’est donc le département d’avant l’entrée qui instruit, même si l’EHPAD est ailleurs.',
      'L’aide sociale ne couvre que l’hébergement. La part « aide au quotidien » reste due par le résident, et se prélève sur le peu que la règle des 90 % lui laisse.',
    ],
  },
  impot: {
    title: 'Déclarer les frais : réduction d’impôt et pension alimentaire',
    when: 'Au printemps suivant, sur la déclaration de revenus.',
    steps: [
      'Demandez à l’EHPAD l’attestation annuelle des frais d’hébergement et de dépendance.',
      'Sur la déclaration du parent hébergé : reportez les frais restant à charge après APA, aide sociale et aide au logement dans la case « Dépenses d’accueil dans un établissement pour personnes dépendantes ». Réduction de 25 %, dans la limite de 10 000 € de dépenses par an et par personne hébergée.',
      'Sur la déclaration de chaque enfant qui paie : la pension alimentaire versée à un parent dans le besoin se déduit du revenu imposable, sans plafond, sur justificatifs — les versements faits directement à l’EHPAD comptent (case « autres pensions alimentaires versées »).',
      'Le parent qui reçoit une pension alimentaire doit la déclarer en revenu, sauf ressources très faibles.',
    ],
    docs: ['Attestation annuelle de l’établissement', 'Notifications d’APA, d’ASH et d’aide au logement', 'Preuves des versements des enfants'],
    warnings: [
      'La réduction de 25 % appartient à la personne hébergée : un enfant qui paie n’y a pas droit. Si le parent n’est pas imposable, elle vaut zéro — c’est alors la déduction de pension alimentaire côté enfants qui joue.',
      'Piège signalé le 27/04/2026 : la case a changé de place dans la déclaration en ligne. Cherchez « accueil dans un établissement pour personnes dépendantes ».',
    ],
  },
  contrat: {
    title: 'Lire le contrat de séjour avant de signer',
    when: 'Avant l’entrée — c’est le seul moment où la négociation est possible.',
    steps: [
      'Vérifiez la liste des prestations comprises dans le prix et celles facturées en sus (linge, coiffeur, télévision, téléphone).',
      'Vérifiez la clause d’absence : au-delà de trois jours de carence, le tarif hébergement doit être minoré dès le quatrième jour.',
      'Vérifiez la clause de caution solidaire : qui s’engage, et à quelle hauteur.',
      'Vérifiez le mode de révision annuelle du prix, et demandez l’historique des trois dernières années — cette page vous donne déjà la courbe depuis 2018.',
    ],
    docs: ['Contrat de séjour et règlement de fonctionnement', 'Grille tarifaire de l’année en cours', 'Dernière décision tarifaire du département'],
    warnings: ['Une caution solidaire signée par plusieurs enfants permet à l’établissement de réclamer la totalité à un seul d’entre eux.'],
    checklist: [
      'Que couvre exactement le prix affiché ? Demandez la liste écrite.',
      'Combien a augmenté le prix ces trois dernières années, et de combien augmentera-t-il l’an prochain ?',
      'L’établissement est-il habilité à l’aide sociale, et sur combien de places ?',
      'Que se passe-t-il en cas d’hospitalisation : à partir de quel jour le tarif est-il minoré ?',
      'Y a-t-il un infirmier la nuit ? Un médecin coordonnateur à temps plein ?',
      'Quel est le taux d’encadrement réel, et le turnover de l’équipe ?',
      'Qui signe la caution solidaire, et pour quel montant ?',
      'Que devient le dépôt de garantie au départ ou au décès ?',
    ],
  },
  logement: {
    title: 'Décider quoi faire du logement',
    when: 'Une fois l’entrée confirmée — mais avant de demander l’ASH, car le patrimoine entre dans l’examen.',
    steps: [
      'Comparez trois scénarios : conserver, louer, vendre. Le loyer perçu devient une ressource et augmente la participation du parent.',
      'Si votre parent est sous mesure de protection, la vente doit être autorisée par le juge.',
      'Faites le point avec un notaire avant toute donation : le département peut récupérer sur les donations des dix ans précédant comme des dix ans suivant la demande d’aide sociale.',
    ],
    docs: ['Titre de propriété', 'Dernier avis de taxe foncière', 'Décision de protection juridique le cas échéant'],
    warnings: ['Cette page ne simule ni la valeur du bien ni la fiscalité de la vente. C’est un sujet de notaire.'],
  },
  pro: {
    title: 'Mode professionnel : constituer une liste de dépôt',
    when: 'Pour un dépôt multiple depuis un service social hospitalier, un CCAS ou un service mandataire.',
    steps: [
      'Réglez les filtres sur les critères du dossier, puis exportez la liste en CSV.',
      'L’export contient le FINESS, le nom, l’adresse, le téléphone, l’habilitation, la note de qualité, le reste à charge calculé, le taux d’occupation du segment et le rythme de libération des places.',
      'Le FINESS permet le rapprochement avec ViaTrajectoire et les dossiers d’aide sociale.',
    ],
    docs: ['Mandat ou habilitation du service', 'Éléments de ressources du majeur protégé'],
    warnings: ['L’export est produit dans votre navigateur : aucune donnée de la personne accompagnée n’est transmise.'],
  },
};

/* ---------- Questions fréquentes (texte identique au balisage FAQPage) ---------- */
window.FAQ = [
  ['Puis-je consulter les tarifs sans donner mes revenus ?',
   'Oui. Choisissez une zone pour voir les établissements et leur tarif. Vous pourrez ensuite préciser votre situation pour estimer le budget mensuel.'],
  ['Le montant affiché est-il définitif ?',
   'Non, c’est une estimation. Chaque fiche indique les aides prises en compte et les frais exclus. Confirmez le tarif auprès de l’établissement.'],
  ['Comment connaître les places disponibles ?',
   'Contactez l’établissement. Aucune base publique ne publie les places libres, et ce site n’en estime aucune. Le numéro figure sur chaque fiche.'],
  ['Que faire si les revenus ne suffisent pas ?',
   'Des aides et une participation familiale sont possibles selon la situation. L’aide sociale dépend d’une décision du département et peut être récupérée sur la succession. <a href="/aides-ehpad/aide-sociale-hebergement/">Les conditions</a>'],
  ['Le service est-il gratuit, et mes réponses sont-elles enregistrées ?',
   'Le service est gratuit, sans inscription. Vos réponses restent dans ce navigateur, sur votre appareil. Si vous les ajoutez à un lien partagé, ses destinataires pourront les lire.'],
];
