# -*- coding: utf-8 -*-
"""P2 (29/09/2026) — pages piliers : APA (+ fusion), aide sociale, réduction d'impôt, obligation
alimentaire (nouvelle page), dossier d'admission, prix, reste à charge. Chaque ajout repose sur une
source officielle lue le 29/09/2026 (service-public.gouv.fr, pour-les-personnes-agees.gouv.fr,
cnsa.fr, bofip, impots.gouv.fr, DREES), citée dans la page. Idempotent (marque P2-PILIERS)."""
import os, re
B = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(B, 'seo', 'contenus.py')
s = open(P, encoding='utf-8').read()
if 'P2-PILIERS' in s:
    print('déjà appliqué'); raise SystemExit
def R(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70]); s = s.replace(a, b)

SP = 'https://www.service-public.gouv.fr/particuliers/vosdroits/'
PPA = 'https://www.pour-les-personnes-agees.gouv.fr/'

# ---------------------------------------------------------------- APA
R("""Il est évalué par une équipe médico-sociale du
département. L’allocation n’est versée que du GIR 1 au GIR 4.</p></section>""",
f"""En établissement, il est évalué par
l’EHPAD lui-même (médecin coordonnateur), avec la grille officielle AGGIR. L’allocation n’est versée que du GIR 1 au
GIR 4 <!-- P2-PILIERS -->.</p></section>

<section><h2>Les conditions</h2>
<ul>
<li>Avoir <b>60 ans ou plus</b> et être évalué en <b>GIR 1 à 4</b>. Il n’y a <b>pas de plafond de ressources</b>&nbsp;: seules
la participation du résident, donc le montant de l’allocation, en dépendent.</li>
<li>Être hébergé dans un établissement situé en France qui accueille <b>au moins 25 personnes âgées dépendantes</b>.
En dessous, c’est l’allocation « à domicile » qui s’applique.</li>
<li>Ne pas percevoir une aide incompatible&nbsp;: prestation de compensation du handicap, majoration pour tierce
personne, aide ménagère des caisses de retraite, entre autres (un droit d’option existe dans certains cas).</li>
</ul>
<p>Ressources exclues du calcul&nbsp;: la résidence principale, les aides au logement, les rentes viagères de
prévoyance dépendance, les sommes versées par les enfants pour la perte d’autonomie, la retraite du combattant.
Source&nbsp;: <a href="{SP}F10009">service-public, fiche F10009</a> (vérifiée le 01/06/2026).</p></section>

<section><h2>Le versement et les recours</h2>
<ul>
<li>Le département décide dans les <b>deux mois</b> suivant la réception du dossier complet. En urgence, une avance
peut être accordée pour deux mois au plus.</li>
<li>L’allocation est versée chaque mois, au plus tard le 10, le plus souvent directement à l’établissement, qui la
déduit de la facture. Certains départements la versent en <b>dotation globale</b>&nbsp;: la facture arrive alors déjà
nette du tarif dépendance.</li>
<li>Elle n’est <b>ni imposable, ni récupérable</b> sur la succession, et n’est jamais demandée aux enfants.</li>
<li>En cas de désaccord&nbsp;: recours préalable auprès du président du conseil départemental dans les deux mois,
puis tribunal administratif.</li>
</ul></section>

<section id="fusion"><h2>Dans 23 départements, l’allocation en établissement est supprimée</h2>
<p>Depuis le <b>1<sup>er</sup> juillet 2025</b>, 23 territoires expérimentent la fusion des financements « soins » et
« dépendance » (article 79 de la loi de financement de la sécurité sociale pour 2024, décret n° 2025-168)&nbsp;:
Aude, Cantal, Charente-Maritime, Corrèze, Côtes-d’Armor, Creuse, Finistère, Haute-Garonne, Landes, Lot,
Lot-et-Garonne, Maine-et-Loire, Haute-Marne, Mayenne, Morbihan, Nièvre, Pas-de-Calais, Pyrénées-Orientales,
Métropole de Lyon, Savoie, Seine-Saint-Denis, Guyane et La Réunion.</p>
<ul>
<li>Il n’y a plus de tarif par GIR ni d’allocation personnalisée d’autonomie en établissement.</li>
<li>Chaque résident paie une <b>participation forfaitaire identique</b>&nbsp;: 6,10 € par jour en 2025, <b>6,16 € par
jour depuis le 1<sup>er</sup> janvier 2026</b>, quels que soient son GIR et ses ressources.</li>
<li>Les résidents présents avant le 1<sup>er</sup> juillet 2025 qui payaient moins ont gardé leur ancien montant en
2025&nbsp;; aucune source officielle ne précise encore la règle pour 2026.</li>
<li>La CNSA indique une expérimentation jusqu’au 31 décembre 2027.</li>
</ul>
<p>Sur ce site, 1 617 établissements relèvent de ce régime, et chacune de leurs fiches applique la participation
forfaitaire au lieu de la grille GIR. Sources&nbsp;: <a href="{PPA}actualites/financement-des-ehpad-une-experimentation-dans-23-departements">portail
national des personnes âgées</a> (03/02/2026), <a href="https://www.cnsa.fr/budget-et-financement/modeles-tarifaires/reforme-de-la-tarification-des-ehpad">CNSA</a>.</p></section>""")

# --------------------------------------------------------- aide sociale
R("""<section><h2>Les trois conditions</h2>
<ul>
<li><b>L’établissement doit être habilité</b> à recevoir des bénéficiaires de l’aide sociale. Toutes les fiches de
ce site indiquent cette information, tirée du répertoire officiel FINESS.</li>
<li><b>Les ressources doivent être insuffisantes</b>, épargne et revenus du patrimoine compris.</li>
<li><b>La personne doit résider en France</b> de façon stable et régulière.</li>
</ul></section>""",
f"""<section><h2>Les conditions</h2>
<ul>
<li><b>Avoir 65 ans</b>, ou 60 ans en cas d’inaptitude au travail, et résider en France de façon stable et régulière.</li>
<li><b>L’établissement doit être habilité</b> à recevoir des bénéficiaires de l’aide sociale, sur tout ou partie de
ses places. Toutes les fiches de ce site indiquent cette information, tirée du répertoire officiel FINESS.
Exception&nbsp;: après <b>cinq ans de séjour payant</b> dans un établissement non habilité, le département
<i>peut</i> participer.</li>
<li><b>Les ressources doivent être insuffisantes</b>. Le département ne verse rien tant qu’il reste de l’épargne ou un
patrimoine autre que la résidence principale&nbsp;; la vente de celle-ci n’est pas un préalable.</li>
</ul>
<p>Sources&nbsp;: <a href="{SP}F2444">service-public, fiche F2444</a> (vérifiée le 01/01/2026)&nbsp;;
<a href="{PPA}vivre-dans-un-ehpad/aides-financieres-en-ehpad/l-aide-sociale-a-l-hebergement-ash-en-etablissement">portail
national des personnes âgées</a> (09/04/2026).</p></section>

<section><h2>Déposer la demande — et à temps</h2>
<ul>
<li>Il n’existe <b>pas de formulaire national</b>&nbsp;: chaque département a son dossier. On le dépose à la mairie ou
au centre communal d’action sociale, qui le transmet.</li>
<li>Pièces habituelles&nbsp;: identité, avis d’imposition de la personne et du conjoint, justificatifs de revenus des
trois derniers mois, liste des enfants d’après le livret de famille (les obligés alimentaires).</li>
<li><b>Déposez dans les deux mois qui suivent l’entrée</b>&nbsp;: la prise en charge peut alors remonter à la date
d’entrée. L’instruction est souvent longue, l’établissement est payé rétroactivement.</li>
<li>Désaccord&nbsp;: recours préalable auprès du président du conseil départemental, puis tribunal administratif,
chaque fois dans les deux mois.</li>
</ul></section>

<section><h2>Un tarif différent pour les bénéficiaires de l’aide sociale</h2>
<p>Depuis le 1<sup>er</sup> janvier 2025, un EHPAD majoritairement habilité peut facturer aux résidents qui ne
bénéficient pas de l’aide sociale un tarif plus élevé que le tarif « aide sociale », <b>dans la limite de 35 %</b> à
prestations identiques (décret n° 2024-1270). Le département peut fixer un écart plus faible. Nos fiches affichent
les deux tarifs quand l’établissement les a déclarés. Source&nbsp;: <a href="https://solidarites.gouv.fr/faq-tarifs-differencies-dans-les-ehpad">ministère
des Solidarités</a> (21/07/2025).</p></section>""")
R("""<p>C’est l’obligation alimentaire, prévue par le code civil. Le département peut solliciter les enfants, ainsi que
les gendres et belles-filles. <b>Les petits-enfants ne sont plus sollicités depuis la loi du 8 avril 2024.</b></p>""",
"""<p>C’est l’obligation alimentaire, prévue par le code civil. Le département peut solliciter les enfants, ainsi que
les gendres et belles-filles. <b>Dans le cadre de l’aide sociale à l’hébergement, les petits-enfants ne sont plus
sollicités depuis la loi du 8 avril 2024.</b> <a href="/aides-ehpad/obligation-alimentaire/">Tout sur l’obligation alimentaire</a></p>""")
R("""<p>Les sommes versées par le département sont récupérables&nbsp;: sur la succession du résident, sur les donations
consenties dans les dix ans qui précèdent la demande <b>comme après elle</b>, et en cas de retour à meilleure fortune.
Les sommes versées par les enfants, elles, ne sont pas récupérables.</p>""",
"""<p>Les sommes versées par le département sont récupérables&nbsp;: sur la succession du résident, sur les donations
consenties dans les dix ans qui précèdent la demande <b>comme après elle</b>, et en cas de retour à meilleure fortune.
Les sommes versées par les enfants, elles, ne sont pas récupérables.</p>
<ul>
<li>La récupération porte sur l’<b>actif net</b> de la succession (biens moins dettes)&nbsp;: le patrimoine personnel
des héritiers n’est jamais concerné, et sans succession il n’y a rien à récupérer.</li>
<li>Pour l’aide à l’hébergement, elle s’exerce <b>dès le premier euro</b> — le seuil de 46 000 € souvent cité ne
concerne que d’autres aides, comme l’aide ménagère à domicile.</li>
<li>Les biens immobiliers d’une valeur d’au moins 1 500 € peuvent être grevés d’une <b>hypothèque légale</b>, sans
dépossession.</li>
</ul>""")

# ------------------------------------------------------ réduction d'impôt
R("""<section><h2>Attention au mot « réduction »</h2>""",
f"""<section><h2>Les règles précises</h2>
<ul>
<li>Base légale&nbsp;: article 199 quindecies du code général des impôts. Aucune condition d’âge.</li>
<li>Établissements concernés&nbsp;: EHPAD, unités de soins de longue durée, accueil de jour Alzheimer, en France ou
dans l’Espace économique européen.</li>
<li>Dépenses retenues&nbsp;: la <b>dépendance</b>, et l’hébergement seulement s’il s’ajoute à la dépendance. Les soins
sont toujours exclus. On retient les sommes <b>payées dans l’année</b>, après déduction de <b>toutes</b> les aides
reçues pour ces dépenses (allocation personnalisée d’autonomie, aide au logement, aide sociale).</li>
<li>Déclaration&nbsp;: lignes 7CD (et 7CE pour une deuxième personne hébergée) de la déclaration complémentaire
2042 RICI. Une avance de 60 % est versée en janvier, régularisée à l’été.</li>
<li>Justificatif&nbsp;: l’attestation annuelle de l’établissement, qui distingue hébergement et dépendance, à
conserver trois ans. La réduction n’entre pas dans le plafonnement global des niches fiscales.</li>
</ul>
<p>Sources&nbsp;: <a href="{SP}F17">service-public, fiche F17</a> (vérifiée le 15/04/2026)&nbsp;;
<a href="https://bofip.impots.gouv.fr/bofip/526-PGP.html/identifiant=BOI-IR-RICI-140-20140625">Bulletin officiel des finances publiques, BOI-IR-RICI-140</a>&nbsp;;
<a href="{PPA}vivre-dans-un-ehpad/aides-financieres-en-ehpad/la-reduction-d-impot-en-etablissement-d-hebergement">portail
national des personnes âgées</a> (27/03/2026).</p></section>

<section><h2>Attention au mot « réduction »</h2>""")
R("""<b>déductible du revenu imposable sans plafond</b>, sur justificatifs, y compris lorsqu’elle est versée directement à
l’établissement. Le parent doit en revanche déclarer la somme reçue. Le calculateur estime ce coût réel après
déduction pour chaque enfant.</p></section>""",
"""<b>déductible du revenu imposable</b> (case 6GU), sans plafond chiffré&nbsp;: la limite est celle des besoins du parent
et des ressources de l’enfant. Elle reste déductible lorsqu’elle est versée directement à l’établissement. Le parent
doit en principe déclarer la somme reçue — sauf lorsque l’enfant paie directement l’établissement pour un parent aux
très faibles ressources. Le calculateur estime ce coût réel après déduction pour chaque enfant. Source&nbsp;:
<a href="https://www.impots.gouv.fr/portail/particulier/questions/puis-je-deduire-les-sommes-que-je-verse-la-maison-de-retraite-de-mes-parents">impots.gouv.fr</a> (07/07/2026).</p></section>""")

# ------------------------------------------------- obligation alimentaire
R("""attestation annuelle : conservez-la.')]),
]""", f"""attestation annuelle : conservez-la.')]),
 ('obligation-alimentaire', 'L’obligation alimentaire envers un parent en EHPAD',
  'Qui peut être sollicité, comment la part de chacun est fixée, et les cas de dispense.',
  \"\"\"<div class="note"><b>En résumé.</b> Les enfants, et les gendres et belles-filles, doivent aider un parent dans
le besoin (articles 205 et suivants du code civil). Il n’existe <b>aucun barème national</b>&nbsp;: la part de chacun
est fixée à l’amiable, par le département lorsqu’une aide sociale est demandée, et en cas de désaccord par le juge
aux affaires familiales. Ce qui est versé est déductible des impôts de celui qui paie.</div>

<section><h2>Qui est concerné</h2>
<ul>
<li><b>Les enfants</b>, et <b>les gendres et belles-filles</b>, sans hiérarchie entre eux. Le parent sollicite
d’abord son conjoint, au titre du devoir de secours.</li>
<li>L’obligation d’un gendre ou d’une belle-fille <b>cesse</b> lorsque l’époux qui créait le lien est décédé <b>et</b>
que les enfants issus de cette union sont eux aussi décédés.</li>
<li><b>Les petits-enfants</b>&nbsp;: dans le cadre d’une demande d’<a href="/aides-ehpad/aide-sociale-hebergement/">aide
sociale à l’hébergement</a>, ils sont dispensés depuis la loi n° 2024-317 du 8 avril 2024. <b>En dehors de ce cadre,
ils restent tenus</b> par le code civil.</li>
</ul></section>

<section><h2>Les dispenses</h2>
<ul>
<li><b>Automatiques</b>&nbsp;: l’enfant retiré de son milieu familial avant ses 18 ans pendant au moins 36 mois,
l’enfant dont le parent a été condamné pour un crime ou une agression sexuelle sur l’autre parent, le parent qui
s’est vu retirer l’autorité parentale.</li>
<li><b>Sur décision du juge</b> (article 207 du code civil)&nbsp;: un enfant peut être déchargé, en tout ou partie,
si le parent a gravement manqué à ses obligations envers lui — abandon, violences —, preuves à l’appui. Cette
décharge ne se demande pas par avance.</li>
</ul></section>

<section><h2>Comment la part de chacun est fixée</h2>
<p>Selon les <b>besoins</b> du parent et les <b>ressources et charges</b> de chaque obligé&nbsp;; les revenus du conjoint
de l’obligé ne s’ajoutent pas, sauf s’il est lui-même sollicité comme gendre ou belle-fille. Lorsqu’une aide sociale
est demandée, le département évalue les ressources de chacun et fixe sa propre aide en conséquence&nbsp;; certains
départements publient un barème indicatif. En cas de désaccord, le juge aux affaires familiales est saisi (tribunal
judiciaire, avocat non obligatoire en première instance). Le montant peut être révisé si la situation change.
La participation moyenne constatée au niveau national est de <b>270 € par mois</b> et par obligé (DREES, fin 2023).</p>
<div class="att">Ne pas payer une pension fixée par le juge pendant plus de deux mois constitue le délit d’abandon
de famille.</div></section>

<section><h2>La déduction fiscale</h2>
<p>Les sommes versées sont déductibles du revenu imposable de l’enfant (case 6GU), y compris lorsqu’elles sont
payées directement à l’établissement. <a href="/aides-ehpad/reduction-impot/#pension">Le détail</a>.
Les sommes versées par les obligés alimentaires ne sont <b>pas</b> récupérables sur la succession.</p>
<p>Sources&nbsp;: <a href="{SP}F2009">service-public, fiche F2009</a> (vérifiée le 12/12/2025)&nbsp;;
<a href="{SP}F2444">fiche F2444</a>&nbsp;; <a href="{PPA}preserver-son-autonomie/les-obligations-de-la-famille/qu-est-ce-que-l-obligation-alimentaire">portail
national des personnes âgées</a> (24/12/2025).</p></section>\"\"\",
  [('Un gendre doit-il payer après le décès de son épouse&nbsp;?',
    'Non, si les enfants nés de cette union sont eux aussi décédés. Tant qu’un de ces enfants est en vie, l’obligation demeure.'),
   ('Peut-on refuser de payer pour un parent qui nous a abandonné&nbsp;?',
    'Oui, mais seulement sur décision du juge aux affaires familiales, qui peut décharger l’enfant en tout ou partie lorsque le parent a gravement manqué à ses obligations. Certains cas sont dispensés automatiquement, notamment l’enfant placé au moins 36 mois avant ses 18 ans.')]),
]""")
R("""<section><h2>Et la participation des enfants&nbsp;?</h2>""", """<section id="pension"><h2>Et la participation des enfants&nbsp;?</h2>""")

# -------------------------------------------------- guide « qui paie »
R("""belles-filles&nbsp;; <b>les petits-enfants ne le sont plus depuis la loi du 8 avril 2024</b>.""",
  """belles-filles&nbsp;; <b>dans le cadre de l’aide sociale à l’hébergement, les petits-enfants ne le sont plus depuis la
loi du 8 avril 2024</b>. <a href="/aides-ehpad/obligation-alimentaire/">Les règles détaillées</a>.""")
R("""    'Non. La loi du 8 avril 2024 a supprimé l’obligation alimentaire des petits-enfants envers leurs grands-parents accueillis en établissement.'),""",
  """    'Pas dans le cadre d’une aide sociale à l’hébergement : la loi du 8 avril 2024 les en dispense, eux et leurs descendants. En dehors de ce cadre, le code civil les maintient parmi les obligés alimentaires.'),""")

# --------------------------------------------------- dossier d'admission
i = s.index(" ('dossier-admission-ehpad',"); j = s.index(" ('urgence-apres-hospitalisation',")
s = s[:i] + f""" ('dossier-admission-ehpad', 'Le dossier d’admission en EHPAD',
  'Le formulaire unique, les pièces, la liste d’attente, puis le contrat de séjour : ce qui engage et ce qui protège.',
  \"\"\"<div class="note"><b>En résumé.</b> Un seul formulaire pour toute la France, le Cerfa n° 14732*03, en deux
volets. Déposé en plusieurs exemplaires ou en ligne, il vaut <b>inscription sur une liste d’attente</b>, pas
admission. L’admission est prononcée par le directeur après avis du médecin coordonnateur, et la personne peut
refuser une place proposée.</div>

<section><h2>Le formulaire unique</h2>
<ul><li><b>Le volet administratif</b>, rempli par la personne ou un proche habilité et signé par elle ou son
représentant légal&nbsp;: identité, situation familiale, ressources, protection juridique éventuelle.</li>
<li><b>Le volet médical</b>, rempli par le médecin traitant et remis <b>sous pli confidentiel</b> au médecin
coordonnateur de l’établissement.</li></ul>
<p>Le même formulaire sert pour l’hébergement temporaire et l’accueil de jour. Télécharger&nbsp;:
<a href="{SP}R17461">Cerfa n° 14732*03 sur service-public</a>.</p></section>

<section><h2>Les pièces à joindre</h2><ul>
<li>Carte d’identité ou passeport, livret de famille, titre de séjour le cas échéant.</li>
<li>Attestation de carte Vitale et de mutuelle.</li>
<li>Justificatifs de retraite, dernier avis d’imposition ou de non-imposition.</li>
<li>Selon le cas&nbsp;: notification d’aide sociale, notification d’allocation personnalisée d’autonomie, jugement de
mesure de protection.</li></ul>
<p>L’établissement peut demander d’autres pièces une fois l’admission acceptée.</p></section>

<section><h2>Où et à combien d’établissements l’envoyer</h2>
<p>Il n’y a <b>aucune limite</b>&nbsp;: déposer plusieurs demandes en même temps est recommandé. Dans la quasi-totalité
des départements, le service en ligne <b>ViaTrajectoire</b> envoie le même dossier à plusieurs établissements et suit
leurs réponses. Sur papier, l’envoi en recommandé avec accusé de réception garde une trace. Avant d’envoyer, vérifiez
pour chaque établissement le tarif et l’habilitation à l’aide sociale&nbsp;: <a href="/ehpad/">l’annuaire</a> les donne.</p></section>

<section><h2>Le contrat de séjour&nbsp;: ce qui vous protège</h2><ul>
<li>Obligatoire dès que le séjour peut dépasser deux mois. Il précise les prestations, le calcul de la facture en
cas d’absence ou d’hospitalisation et l’évolution annuelle des tarifs.</li>
<li><b>Rétractation</b>&nbsp;: 15 jours après la signature (ou après l’admission si elle est postérieure), par écrit,
sans préavis — seule la durée effectivement passée est due.</li>
<li><b>Résiliation</b> par le résident&nbsp;: à tout moment, par écrit, avec un délai de réflexion de 48 heures et le
préavis prévu au contrat (un mois au plus). L’établissement ne peut résilier que dans trois cas&nbsp;: manquement grave
du résident, cessation d’activité, besoins de soins qu’il ne peut plus assurer — après avoir trouvé une solution.</li>
<li><b>Dépôt de garantie</b>&nbsp;: au plus un mois de tarif d’hébergement, restitué dans les 30 jours après le départ.
<b>État des lieux</b> contradictoire à l’entrée et à la sortie&nbsp;: sans lui, aucune remise en état ne peut être facturée.</li>
<li>Une <b>caution solidaire</b> peut être demandée aux enfants&nbsp;; pour un bénéficiaire de l’aide sociale, elle est
limitée à ce qui reste à sa charge.</li>
<li>Demandez la <b>liste écrite des prestations facturées en plus</b> du socle (linge personnel, coiffeur…) avant de
signer&nbsp;: <a href="/comparer-devis-ehpad/">comparez-les d’un établissement à l’autre</a>.</li></ul>
<p>Sources&nbsp;: <a href="{SP}F763">service-public, fiche F763</a>&nbsp;;
<a href="{PPA}vivre-dans-un-ehpad/preparer-l-entree-en-ehpad/le-contrat-de-sejour-en-ehpad">portail national des
personnes âgées</a> (21/11/2024).</p></section>

<section><h2>Les pièges qui font perdre des semaines</h2><ul>
<li><b>Le volet médical oublié.</b> C’est la première cause de dossier bloqué&nbsp;: relancez le médecin traitant.</li>
<li><b>Attendre l’entrée pour demander les aides.</b> L’allocation personnalisée d’autonomie est due à compter du dépôt
du dossier complet, et l’aide sociale doit être demandée dans les deux mois suivant l’entrée.</li>
<li><b>Une seule demande</b>, dans l’établissement le plus proche&nbsp;: la liste d’attente peut être longue.</li></ul></section>\"\"\",
  [('Le dépôt du dossier vaut-il réservation&nbsp;?',
    'Non. Le formulaire le précise lui-même : il vaut inscription sur une liste d’attente, en aucun cas admission.'),
   ('Peut-on refuser une place proposée&nbsp;?',
    'Oui. La personne reste libre d’accepter ou non la place proposée ; il suffit de prévenir l’établissement pour qu’il la propose à quelqu’un d’autre.')]),

""" + s[j:]

# --------------------------------------------------------------- prix
R("""<section><h2>Pourquoi un tel écart entre deux établissements&nbsp;?</h2>""",
f"""<section><h2>Les chiffres officiels de la CNSA</h2>
<p>La Caisse nationale de solidarité pour l’autonomie publie chaque année son analyse des prix. Données 2024,
publiées en avril 2026, pour une chambre seule, hébergement et tarif GIR 5-6 compris&nbsp;:</p>
<div class="tbl-wrap"><table class="tbl"><caption>Prix mensuel de référence en 2024 — source&nbsp;: CNSA, Repères statistiques n° 27</caption>
<thead><tr><th>Chambre</th><th class="num">Médiane</th><th class="num">Moyenne</th><th class="num">1 sur 10 en dessous de</th><th class="num">1 sur 10 au-dessus de</th></tr></thead><tbody>
<tr><td>Habilitée à l’aide sociale</td><td class="num" data-l="Médiane">2 138 €</td><td class="num" data-l="Moyenne">2 164 €</td><td class="num" data-l="1er décile">1 901 €</td><td class="num" data-l="9e décile">2 463 €</td></tr>
<tr><td>Non habilitée</td><td class="num" data-l="Médiane">3 016 €</td><td class="num" data-l="Moyenne">3 128 €</td><td class="num" data-l="1er décile">2 270 €</td><td class="num" data-l="9e décile">3 903 €</td></tr>
</tbody></table></div>
<p>Près de <b>1 000 € par mois d’écart</b> entre les deux. Le prix de l’hébergement a augmenté de 4,0 % en 2024,
après 4,4 % en 2023. <a href="https://www.cnsa.fr/actualites/prix-des-ehpad-en-2024-un-ecart-important-entre-les-chambres-habilitees-laide-sociale-et">L’étude
de la CNSA</a>. Nos propres chiffres, établissement par établissement, portent sur les tarifs déclarés jusqu’en
{{CNSA_MAJ}}.</p></section>

<section><h2>Qui fixe le prix, et comment il évolue</h2>
<ul>
<li><b>Places habilitées à l’aide sociale</b>&nbsp;: le prix est fixé par le conseil départemental.</li>
<li><b>Places non habilitées</b>&nbsp;: le gestionnaire le fixe librement à l’entrée, puis ne peut l’augmenter chaque
1<sup>er</sup> janvier que dans la limite d’un pourcentage fixé par arrêté ministériel. Pour 2026, ce plafond est de
<b>0,86 %</b>, contre 3,21 % en 2025 (arrêté du 24 décembre 2025, relayé par la presse spécialisée&nbsp;; nous n’avons
pas pu consulter le texte sur Légifrance).</li>
<li>Le prix inscrit au contrat ne change pas en cours d’année.</li>
<li>Chaque établissement doit transmettre ses prix à la CNSA au plus tard le 30 juin. Le « prix à partir de » du
portail officiel est le prix d’hébergement plus le tarif GIR 5-6, multipliés par 30 jours.</li>
</ul>
<p>Le prix d’hébergement couvre obligatoirement un <b>socle de prestations</b>&nbsp;: administration, chambre avec
salle de bain, entretien, accès à Internet, trois repas, un goûter et une collation nocturne, linge de lit et de
toilette, marquage et entretien du linge personnel, animation. Tout le reste peut être facturé en plus.
Source&nbsp;: <a href="https://www.pour-les-personnes-agees.gouv.fr/comprendre-les-prix-tarifs-et-prestations-affiches-dans-lannuaire-des-ehpad">portail
national des personnes âgées</a> (20/08/2026).</p></section>

<section><h2>Pourquoi un tel écart entre deux établissements&nbsp;?</h2>""")

# ---------------------------------------------------- reste à charge
R("""<section><h2>1. Ce que l’établissement facture</h2>""",
"""<section><h2>Ce que disent les statistiques publiques</h2>
<p>La DREES a estimé, pour 2019, des frais de séjour moyens de <b>2 385 € par mois</b> (1 875 € d’hébergement et
510 € de dépendance) et un <b>reste à charge moyen de 1 957 € par mois</b> avant aide sociale. <b>79 %</b> des
résidents ne pouvaient pas le financer avec leurs seules ressources courantes, et 18 % percevaient l’aide sociale à
l’hébergement. Aucune estimation plus récente n’a été publiée. Source&nbsp;:
<a href="https://drees.solidarites-sante.gouv.fr/sites/default/files/2024-10/ASPH%20-%20Fiche%2008%20-%20Le%20co%C3%BBt%20de%20la%20prise%20en%20charge%20de%20la%20perte%20d%E2%80%99autonomie.pdf">DREES,
« L’aide sociale aux personnes âgées ou handicapées », édition 2024, fiche 08</a>.</p></section>

<section><h2>1. Ce que l’établissement facture</h2>""")

open(P, 'w', encoding='utf-8').write(s)
print('P2 appliqué')
