# -*- coding: utf-8 -*-
"""Pages nationales, guides et baromètre. Textes courts : on répond, puis on s'arrête."""
import collections, json
import geo, layout
from base import (esc, nb, eur, eur2, pct, mois_eur, stats, mediane, lien_calc, MOIS,
                  MARQUE, MAJ, MAJ_ISO, CNSA_MAJ, DOMAINE)
from pieces import kpis, cta, tableau, qa, sources, explique_heberg, SOURCES_PRIX
from layout import titre_page
from territoires import phrase_dep, med_mois

INFL = {'2019': 1.1, '2020': 0.5, '2021': 1.6, '2022': 5.2, '2023': 4.9, '2024': 2.0, '2025': 0.9}
INFL_CUM = 17.2


def art(ctx, ecrire, url, h1, sub, corps, titre, desc, ariane_sup, faq=None, prio=0.7,
        type_page='guide', article=True, groupe='contenus'):
    q_html, q_ld = qa(faq or [])
    ld = []
    if article:
        ld.append({"@type": "Article", "headline": h1[:110], "description": desc[:250],
                   "inLanguage": "fr-FR", "datePublished": MAJ_ISO, "dateModified": MAJ_ISO,
                   "author": {"@id": DOMAINE + "/#organization"},
                   "publisher": {"@id": DOMAINE + "/#organization"},
                   "mainEntityOfPage": DOMAINE + url})
    if q_ld: ld.append(q_ld)
    html = f"""<h1 class="p-h1">{h1}</h1>
<p class="p-sub">{sub}</p>
<p class="p-maj">Règles et chiffres vérifiés le {MAJ}</p>
{corps}
{q_html}
{sources()}"""
    ariane = [('Accueil', '/')] + ariane_sup
    ecrire(url, layout.page(url, titre_page(titre.split(' | ')[0]), desc, html, ariane, ld_extra=ld, type_page=type_page), prio, groupe)


# ============================================================ pages nationales
def prix(ctx, ecrire):
    s = ctx['FR']
    lignes_infl = ''.join(f'<tr><td>{a}</td><td class="num" data-l="Inflation">{pct(v)}</td></tr>' for a, v in INFL.items())
    corps = f"""{kpis([(med_mois(s), 'tarif d’hébergement médian, par mois', True),
        (eur(mois_eur(s['q1'])) + ' – ' + eur(mois_eur(s['q3'])), 'la moitié des établissements'),
        (pct(s['evol_med']), 'hausse depuis 2018'),
        (nb(s['n_prix']), 'tarifs déclarés sur ' + nb(s['n']))])}
<p>Le tarif d’hébergement médian d’un EHPAD en France est de <b>{med_mois(s)} par mois</b> pour une chambre seule
({eur2(s['med'])} par jour). La moitié des établissements se situe entre {eur(mois_eur(s['q1']))} et
{eur(mois_eur(s['q3']))} par mois ; le plus bas déclaré est à {eur(mois_eur(s['mini']))}, le plus élevé à {eur(mois_eur(s['maxi']))}.</p>
<p>Nous donnons la <b>médiane</b> et non la moyenne&nbsp;: quelques établissements très chers tirent la moyenne
vers le haut et donnent une idée fausse de ce que paie la majorité des familles.</p>

<section><h2>Ce que recouvre la facture</h2>
<p>Une facture d’EHPAD se lit en trois lignes, et une seule est entièrement à la charge de la famille&nbsp;:</p>
<ul>
<li><b>L’hébergement</b> — la chambre, les repas, le ménage, l’animation. C’est la ligne la plus lourde, payée par le résident et, si besoin, par sa famille ou le département.</li>
<li><b>La dépendance</b> — l’aide apportée pour se lever, se laver, manger. Son montant dépend du niveau de perte d’autonomie, mesuré par une grille officielle appelée GIR, du plus dépendant (GIR 1) au plus autonome (GIR 6). Cette ligne est en grande partie couverte par l’allocation personnalisée d’autonomie, versée par le département.</li>
<li><b>Les soins</b> — les infirmiers, le médecin coordonnateur, parfois les médicaments. Cette ligne n’apparaît pas sur la facture&nbsp;: elle est payée par l’assurance maladie.</li>
</ul>
{explique_heberg()}</section>

<section><h2>Pourquoi un tel écart entre deux établissements&nbsp;?</h2>
<p>Trois facteurs expliquent l’essentiel des écarts&nbsp;:</p>
<ul>
<li><b>Le statut.</b> {nb(s['public'])} établissements sont publics, {nb(s['assoc'])} associatifs à but non lucratif et {nb(s['prive'])} privés commerciaux. Les deux premiers sont en moyenne moins chers, et bien plus souvent habilités à l’aide sociale.</li>
<li><b>Le territoire.</b> L’écart entre le département le moins cher et le plus cher dépasse un rapport de un à deux. <a href="/prix-ehpad-par-departement/">Voir le classement</a></li>
<li><b>Le bâtiment et les services.</b> Une résidence récente, avec de grandes chambres et des services hôteliers, coûte plus cher qu’un établissement ancien. Cela ne présume pas de la qualité de l’accompagnement.</li>
</ul></section>

<section><h2>Les tarifs augmentent-ils plus vite que le coût de la vie&nbsp;?</h2>
<p>Oui, depuis 2024. Mesurée établissement par établissement, la hausse médiane du tarif d’hébergement est de
<b>{pct(s['evol_med'])}</b> entre 2018 et 2025, sur {nb(s['n_evol'])} établissements dont le tarif est connu à deux
dates au moins. Sur la même période, les prix à la consommation ont augmenté de <b>17,2 %</b>. Environ deux
établissements sur trois ont donc augmenté plus vite que le coût de la vie.</p>
<div class="tbl-wrap"><table class="tbl" style="max-width:20rem"><caption>Inflation annuelle en France — source&nbsp;: Institut national de la statistique (INSEE)</caption>
<thead><tr><th>Année</th><th class="num">Inflation</th></tr></thead><tbody>{lignes_infl}</tbody></table></div>
<p><a href="/etudes/barometre-prix-ehpad-2026/">Voir le baromètre complet, département par département</a></p></section>

<section><h2>Ce que vous paierez vraiment</h2>
<p>Le tarif affiché n’est pas ce qu’il faut sortir chaque mois. L’allocation personnalisée d’autonomie et l’aide
au logement viennent en déduction de la facture&nbsp;; la réduction d’impôt, elle, n’arrive que l’année suivante et
ne diminue pas la dépense mensuelle. L’écart se compte souvent en centaines d’euros par mois, et il dépend
entièrement de la situation de la personne.</p>
{cta('/', 'Estimer mon reste à charge', 'seo_prix_to_calculator', 'Gratuit, sans inscription. Le calcul reste sur votre appareil.')}</section>"""
    art(ctx, ecrire, '/prix-ehpad/', 'Le prix des EHPAD en France en 2026',
        f'Tarif médian, écarts entre établissements, évolution depuis 2018 et ce qui reste réellement à payer.',
        corps, f'Prix des EHPAD en 2026 : {med_mois(s)} par mois en médiane | {MARQUE}',
        f'Le tarif d’hébergement médian d’un EHPAD en France est de {med_mois(s)} par mois. Écarts, évolution depuis 2018 et méthode de calcul du reste à charge.',
        [('Prix des EHPAD', None)], faq=[
            ('Quel est le prix moyen d’un EHPAD en France&nbsp;?',
             f'Le tarif d’hébergement médian est de <b>{med_mois(s)} par mois</b> pour une chambre seule, soit {eur2(s["med"])} par jour, sur {nb(s["n_prix"])} établissements ayant déclaré leur tarif. La moitié des établissements se situe entre {eur(mois_eur(s["q1"]))} et {eur(mois_eur(s["q3"]))} par mois. À ce tarif s’ajoute le tarif dépendance.'),
            ('Ce tarif comprend-il tout&nbsp;?',
             'Non. Il couvre la chambre, les repas et l’entretien. S’y ajoutent le tarif dépendance et certaines prestations facturées en plus, comme le blanchissage du linge personnel ou le coiffeur. Les soins médicaux, eux, sont payés par l’assurance maladie et n’apparaissent pas sur la facture.'),
            ('Comment savoir ce que je paierai réellement&nbsp;?',
             'En déduisant les aides du tarif de l’établissement visé. Le calculateur de ce site le fait pour chaque établissement autour d’une commune, à partir de la retraite, du niveau d’autonomie et de la situation familiale.'),
        ], prio=0.9, type_page='national')


def prix_par_dep(ctx, ecrire):
    lignes = []
    dd = []
    for d, lot in ctx['par_dep'].items():
        sd = stats(lot)
        if sd['med']: dd.append((sd['med'], d, sd))
    dd.sort()
    for rang, (m, d, sd) in enumerate(dd, 1):
        lignes.append(f'<tr><td><a href="{ctx["url_dep"][d]}">{esc(geo.DEPARTEMENTS[d])} ({d})</a></td>'
                      f'<td class="num" data-l="Rang">{rang}</td>'
                      f'<td class="num" data-l="Tarif médian">{med_mois(sd)}</td>'
                      f'<td class="num" data-l="EHPAD">{sd["n"]}</td>'
                      f'<td class="num" data-l="Habilités à l’aide sociale">{sd["ash"]}</td></tr>')
    bas = ', '.join(f'{geo.DEPARTEMENTS[d]} ({med_mois(s)})' for _, d, s in dd[:5])
    haut = ', '.join(f'{geo.DEPARTEMENTS[d]} ({med_mois(s)})' for _, d, s in dd[-5:][::-1])
    ecart = dd[-1][0] / dd[0][0]
    s = ctx['FR']
    corps = f"""<p>Les {len(dd)} départements classés par tarif d’hébergement médian, du moins cher au plus cher.
Le rapport entre les deux extrêmes est de <b>un à {nb(ecart, 1)}</b>&nbsp;: c’est le premier levier d’économie,
bien avant le choix entre deux établissements d’une même ville.</p>
<p><b>Les cinq départements les moins chers&nbsp;:</b> {esc(bas)}.<br>
<b>Les cinq plus chers&nbsp;:</b> {esc(haut)}.</p>
<div class="att">Un tarif départemental médian ne dit rien d’un établissement précis&nbsp;: à l’intérieur d’un même
département, l’écart entre deux EHPAD dépasse souvent 1 000 € par mois. Ouvrez la page du département pour voir le détail.</div>
<div class="tbl-wrap"><table class="tbl"><caption>Tarif d’hébergement médian mensuel pour une chambre seule — source&nbsp;: Caisse nationale de solidarité pour l’autonomie, {CNSA_MAJ}</caption>
<thead><tr><th>Département</th><th class="num">Rang</th><th class="num">Tarif médian</th><th class="num">EHPAD</th><th class="num">Aide sociale</th></tr></thead>
<tbody>{''.join(lignes)}</tbody></table></div>
{cta('/', 'Estimer mon reste à charge', 'seo_prixdep_to_calculator')}"""
    ld = [{"@type": "Dataset", "name": "Tarif d’hébergement médian des EHPAD par département (2026)",
           "description": "Tarif d’hébergement médian mensuel d’une chambre seule en EHPAD, pour chacun des 101 départements français, calculé à partir des tarifs déclarés à la CNSA.",
           "url": DOMAINE + '/prix-ehpad-par-departement/', "inLanguage": "fr-FR",
           "isAccessibleForFree": True, "creator": {"@id": DOMAINE + "/#organization"},
           "temporalCoverage": "2026", "dateModified": MAJ_ISO,
           "spatialCoverage": {"@type": "Country", "name": "France"},
           "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence"}]
    q_html, q_ld = qa([
        ('Dans quel département les EHPAD sont-ils les moins chers&nbsp;?',
         f'D’après les tarifs déclarés à la Caisse nationale de solidarité pour l’autonomie, le tarif d’hébergement médian le plus bas est constaté {phrase_dep(dd[0][1])} ({med_mois(dd[0][2])} par mois), le plus élevé {phrase_dep(dd[-1][1])} ({med_mois(dd[-1][2])} par mois).'),
        ('Pourquoi de tels écarts entre départements&nbsp;?',
         'Le coût de l’immobilier, l’ancienneté des bâtiments et la part d’établissements publics ou associatifs expliquent l’essentiel. Les départements où les établissements publics sont majoritaires affichent des tarifs plus bas et davantage de places habilitées à l’aide sociale.'),
    ])
    html = f"""<h1 class="p-h1">Le prix des EHPAD par département</h1>
<p class="p-sub">Les 101 départements classés par tarif d’hébergement médian, calculé sur les {nb(s['n_prix'])} établissements ayant déclaré leur tarif.</p>
<p class="p-maj">Source&nbsp;: Caisse nationale de solidarité pour l’autonomie, {CNSA_MAJ}</p>
{corps}{q_html}{sources()}"""
    ecrire('/prix-ehpad-par-departement/', layout.page('/prix-ehpad-par-departement/',
        titre_page('Prix des EHPAD par département : le classement 2026'),
        'Le tarif d’hébergement médian d’un EHPAD dans chacun des 101 départements français, du moins cher au plus cher, avec le nombre d’établissements habilités à l’aide sociale.',
        html, [('Accueil', '/'), ('Prix des EHPAD', '/prix-ehpad/'), ('Par département', None)],
        ld_extra=ld + ([q_ld] if q_ld else []), type_page='national'), 0.8, 'contenus')


def moins_chers(ctx, ecrire):
    lot = [r for r in ctx['rows'] if r['p'] and r['fin'] in ctx['url_fiche']]
    lot.sort(key=lambda r: r['p'])
    s = ctx['FR']
    corps = f"""<p>Les 40 EHPAD au tarif d’hébergement déclaré le plus bas de France, pour une chambre seule.
Le critère est unique et vérifiable&nbsp;: le tarif déclaré à la Caisse nationale de solidarité pour l’autonomie.
Aucun jugement de qualité n’entre dans ce classement.</p>
<div class="att"><b>À lire avant de s’y fier.</b> Un tarif bas s’explique le plus souvent par le statut de
l’établissement (public ou associatif), par sa localisation et par l’ancienneté du bâtiment. Il ne dit rien de la
qualité de l’accompagnement, et un établissement peu cher mais très éloigné de la famille est rarement un bon choix&nbsp;:
la distance décide de la fréquence des visites.</div>
{tableau(lot[:40], ctx['lien_de'], 'Les 40 tarifs d’hébergement les plus bas de France', avec_ville=True)}
<p>Pour trouver les moins chers <b>autour de chez vous</b>, ce qui est presque toujours la vraie question&nbsp;:</p>
{cta('/', 'Comparer les EHPAD autour de ma commune', 'seo_moinschers_to_configurator')}
<p>Voir aussi&nbsp;: <a href="/prix-ehpad-par-departement/">le prix médian par département</a> —
c’est le premier levier d’économie, bien avant le choix de l’établissement.</p>"""
    art(ctx, ecrire, '/ehpad-les-moins-chers/', 'Les EHPAD les moins chers de France',
        'Classement par tarif d’hébergement déclaré. Un critère unique, vérifiable, et ce qu’il ne dit pas.',
        corps, f'Les EHPAD les moins chers de France en 2026 | {MARQUE}',
        f'Les 40 EHPAD au tarif d’hébergement le plus bas de France, à partir de {eur(mois_eur(s["mini"]))} par mois. Classement sur les tarifs déclarés, avec ce que ce critère ne dit pas.',
        [('Prix des EHPAD', '/prix-ehpad/'), ('Les moins chers', None)], prio=0.7, type_page='national')


def calcul(ctx, ecrire):
    s = ctx['FR']
    corps = f"""<div class="note"><b>La réponse courte.</b> Trois montants, à ne pas confondre. La <b>facture</b> de
l’établissement&nbsp;: hébergement plus aide au quotidien. Ce qu’il faut <b>sortir chaque mois</b>&nbsp;: la facture
moins les aides versées à l’établissement. Et, à part, un <b>avantage fiscal</b> qui arrive l’année suivante et ne
diminue aucune mensualité. Pour un tarif médian et une retraite modeste, la somme à sortir représente souvent une
à deux fois le montant de la retraite.</div>

<section><h2>1. Ce que l’établissement facture</h2>
<ol>
<li><b>Hébergement</b> — le tarif journalier de l’établissement, multiplié par {str(MOIS).replace('.', ',')} jours (la durée moyenne d’un mois).</li>
<li><b>Aide au quotidien</b> — dans la plupart des départements, le tarif dépendance correspondant au niveau
d’autonomie de la personne, mesuré par la grille officielle GIR. Dans vingt-trois territoires qui expérimentent
depuis le 1<sup>er</sup> juillet 2025 la fusion des financements soins et dépendance, c’est à la place une
<b>participation forfaitaire</b> de 6,16 € par jour en 2026, identique pour tous&nbsp;: ni le GIR ni les ressources
n’y changent quoi que ce soit.</li>
</ol></section>

<section><h2>2. Ce qu’il faut sortir chaque mois</h2>
<ol>
<li><b>Moins l’allocation personnalisée d’autonomie</b> — versée directement à l’établissement par le département.
Jusqu’à 2 846,77 € de ressources par mois, le résident ne paie que le tarif dépendance le plus faible. Au-delà de
4 379,64 €, sa participation est plafonnée. Dans les territoires d’expérimentation, cette allocation en établissement
est <b>supprimée</b>&nbsp;: la participation forfaitaire en tient lieu. <a href="/aides-ehpad/apa/">Le détail</a></li>
<li><b>Moins l’aide au logement</b> — si l’établissement est conventionné. Son montant est notifié par la caisse
d’allocations familiales ou la Mutualité sociale agricole, <b>pour un établissement précis</b>&nbsp;: il n’est pas
transposable d’un EHPAD à l’autre. <a href="/aides-ehpad/aide-au-logement/">Dans quels cas</a></li>
</ol></section>

<section><h2>3. Et, séparément, la réduction d’impôt</h2>
<p>25 % des frais d’hébergement et de dépendance restants, dans la limite de 10 000 € de dépenses par an et par
personne hébergée, soit 2 500 € de réduction au maximum. Elle ne se retranche <b>pas</b> de la somme à sortir chaque
mois&nbsp;: elle arrive l’année suivante, elle ne peut pas dépasser l’impôt réellement dû, et elle n’est pas
remboursée. Une personne non imposable n’en tire rien. <a href="/aides-ehpad/reduction-impot/">Qui y a droit</a></p></section>

<section><h2>Un exemple chiffré</h2>
<p>Une personne seule, 1 600 € de retraite par mois, autonomie moyenne (GIR 3-4), dans un établissement au tarif médian&nbsp;:</p>
<ul>
<li>Hébergement&nbsp;: {med_mois(s)} par mois.</li>
<li>Aide au quotidien&nbsp;: environ 420 € par mois en régime de droit commun, dont l’essentiel est pris en charge
par l’allocation personnalisée d’autonomie, puisque la retraite est inférieure à 2 846,77 €. Dans un territoire
d’expérimentation, ce serait à la place une participation forfaitaire d’environ 188 € par mois, sans aucune aide
à déduire.</li>
<li>Aide au logement&nbsp;: dépend du conventionnement de l’établissement, à demander à la caisse d’allocations familiales.</li>
<li>Réduction d’impôt&nbsp;: nulle ici, la personne n’étant pas imposable — et de toute façon elle n’allègerait
aucune mensualité.</li>
</ul>
<p>Le reste à charge tourne alors autour de <b>{eur(mois_eur(s['med']) + 180)} par mois</b>, pour 1 600 € de ressources.
L’écart se comble par l’épargne, par la famille, par la vente ou la location du logement, ou par
<a href="/aides-ehpad/aide-sociale-hebergement/">l’aide sociale à l’hébergement</a>.</p>
<div class="att">Cet exemple est une illustration, pas une simulation. Les tarifs varient d’un établissement à
l’autre, le régime de financement dépend du territoire, et le montant exact dépend de la situation complète de la
personne. Il ne comprend ni les frais du premier mois — dépôt de garantie, souvent trente jours d’hébergement,
frais de dossier, déménagement — ni les dépenses personnelles du quotidien.</div></section>

<section><h2>Faire le calcul sur un établissement réel</h2>
<p>Le calculateur applique ces cinq lignes à chaque EHPAD autour d’une commune, avec les tarifs réellement déclarés
par chaque établissement. Il gère aussi les situations que les simulateurs ignorent&nbsp;: couple dont les deux membres
sont hébergés, conjoint resté à domicile, autres revenus, et répartition entre les enfants.</p>
{cta('/', 'Estimer mon reste à charge', 'seo_calcul_to_calculator', 'Aucune inscription, aucune donnée transmise : le calcul s’exécute dans votre navigateur.')}</section>"""
    art(ctx, ecrire, '/calcul-reste-a-charge-ehpad/', 'Calculer le reste à charge d’un EHPAD',
        'Les cinq lignes du calcul, un exemple chiffré, et ce qui fait varier le résultat.',
        corps, f'Calcul du reste à charge en EHPAD : la méthode | {MARQUE}',
        'Comment calculer ce que coûtera réellement un EHPAD : tarif d’hébergement, tarif dépendance, allocation personnalisée d’autonomie, aide au logement et réduction d’impôt, avec un exemple chiffré.',
        [('Calculer le reste à charge', None)], faq=[
            ('Quel est le reste à charge moyen en EHPAD&nbsp;?',
             f'Il n’existe pas de montant unique&nbsp;: le reste à charge dépend du tarif de l’établissement, du niveau d’autonomie et des ressources. Pour une personne seule avec une retraite modeste, dans un établissement au tarif médian ({med_mois(s)} par mois), il dépasse généralement le montant de la retraite.'),
            ('L’allocation personnalisée d’autonomie est-elle versée à la famille&nbsp;?',
             'Non. En établissement, elle est le plus souvent versée directement à l’EHPAD, qui la déduit de la facture. La famille voit donc un tarif dépendance déjà allégé.'),
            ('Faut-il vendre la maison pour payer l’EHPAD&nbsp;?',
             'Pas nécessairement. La louer permet souvent de couvrir une partie du reste à charge. En revanche, si l’aide sociale à l’hébergement est demandée, le département peut récupérer les sommes versées sur la succession, donc sur le bien.'),
        ], prio=0.9, type_page='national')


# ------------------------------------------------------------------- aides
AIDES = [
 ('apa', 'L’allocation personnalisée d’autonomie (APA) en EHPAD',
  'Qui y a droit, comment elle est calculée, à qui elle est versée.',
  """<div class="note"><b>En résumé.</b> L’allocation personnalisée d’autonomie couvre une grande partie du tarif
dépendance. Elle est accordée par le département, sans condition de ressources, aux personnes de 60 ans et plus
dont la perte d’autonomie est mesurée entre GIR 1 et GIR 4. En établissement, elle est presque toujours versée
directement à l’EHPAD.</div>

<section><h2>Ce que veut dire « GIR »</h2>
<p>Le GIR, ou groupe iso-ressources, mesure le degré de perte d’autonomie sur six niveaux&nbsp;: GIR 1 pour une
personne entièrement dépendante, GIR 6 pour une personne autonome. Il est évalué par une équipe médico-sociale du
département. L’allocation n’est versée que du GIR 1 au GIR 4.</p></section>

<section><h2>Comment le montant est calculé</h2>
<p>L’établissement affiche trois tarifs dépendance&nbsp;: un pour les GIR 1-2, un pour les GIR 3-4, un pour les GIR 5-6.
Le résident paie au minimum le tarif GIR 5-6, quel que soit son niveau d’autonomie&nbsp;: c’est le « ticket modérateur ».
L’allocation couvre la différence, selon ses ressources&nbsp;:</p>
<ul>
<li>jusqu’à <b>2 846,77 € de ressources par mois</b>&nbsp;: le résident ne paie que le tarif GIR 5-6 ;</li>
<li>entre 2 846,77 € et <b>4 379,64 €</b>&nbsp;: sa participation augmente progressivement ;</li>
<li>au-delà&nbsp;: elle est plafonnée à 80 % de l’écart entre son tarif et le tarif GIR 5-6.</li>
</ul>
<p>En couple, les ressources du ménage sont divisées par deux. L’allocation n’est pas versée si son montant est
inférieur à trois fois le SMIC horaire brut.</p></section>

<section><h2>Comment la demander</h2>
<p>Le dossier se dépose auprès du conseil départemental de la commune où vivait la personne, ou du centre communal
d’action sociale. Beaucoup d’EHPAD s’en chargent à l’entrée&nbsp;: demandez-le. Le département dispose de deux mois
pour répondre ; l’allocation est due à compter de la date de dépôt du dossier complet.</p></section>""",
  [('L’allocation personnalisée d’autonomie est-elle soumise à condition de ressources&nbsp;?',
    'Non pour y avoir droit, oui pour son montant. Toute personne de 60 ans et plus évaluée entre GIR 1 et GIR 4 peut en bénéficier ; plus ses ressources sont élevées, plus sa participation au tarif dépendance l’est aussi.'),
   ('Est-elle récupérable sur la succession&nbsp;?',
    'Non. Contrairement à l’aide sociale à l’hébergement, l’allocation personnalisée d’autonomie n’est jamais récupérée sur la succession, ni demandée aux enfants.'),
   ('Peut-on la cumuler avec l’aide au logement&nbsp;?',
    'Oui. Les deux aides portent sur des lignes différentes de la facture et se cumulent, tout comme la réduction d’impôt.')]),

 ('aide-sociale-hebergement', 'L’aide sociale à l’hébergement (ASH)',
  'L’aide du département quand les ressources ne suffisent pas — et ce qu’elle implique pour la famille.',
  """<div class="note"><b>En résumé.</b> Quand les ressources et l’épargne ne suffisent pas à payer l’hébergement,
le département peut compléter. Trois conséquences à connaître avant de demander&nbsp;: l’établissement doit être
habilité, les enfants peuvent être appelés à participer, et les sommes versées sont récupérées sur la succession.</div>

<section><h2>Les trois conditions</h2>
<ul>
<li><b>L’établissement doit être habilité</b> à recevoir des bénéficiaires de l’aide sociale. Toutes les fiches de
ce site indiquent cette information, tirée du répertoire officiel FINESS.</li>
<li><b>Les ressources doivent être insuffisantes</b>, épargne et revenus du patrimoine compris.</li>
<li><b>La personne doit résider en France</b> de façon stable et régulière.</li>
</ul></section>

<section><h2>Ce que garde le résident, ce que garde le conjoint</h2>
<p>Le résident conserve au moins <b>10 % de ses ressources, et jamais moins de 125 € par mois</b>, pour ses dépenses
personnelles. Si son conjoint est resté à domicile, celui-ci doit conserver au moins <b>1 043,59 € par mois</b>&nbsp;:
le département ne peut pas descendre en dessous.</p></section>

<section><h2>Ce qui peut être demandé aux enfants</h2>
<p>C’est l’obligation alimentaire, prévue par le code civil. Le département peut solliciter les enfants, ainsi que
les gendres et belles-filles. <b>Les petits-enfants ne sont plus sollicités depuis la loi du 8 avril 2024.</b></p>
<p>Il n’existe <b>aucun barème national</b>&nbsp;: c’est le conseil départemental, et à défaut le juge aux affaires
familiales, qui fixe la part de chacun. La seule référence chiffrée publiée est la participation moyenne constatée
au niveau national, <b>270 € par mois</b>. Les sommes versées par les enfants sont déductibles de leur revenu
imposable, sans plafond, sur justificatifs.</p></section>

<section><h2>La récupération sur la succession</h2>
<p>Les sommes versées par le département sont récupérables&nbsp;: sur la succession du résident, sur les donations
consenties dans les dix ans qui précèdent la demande <b>comme après elle</b>, et en cas de retour à meilleure fortune.
Les sommes versées par les enfants, elles, ne sont pas récupérables.</p>
<div class="att">Chaque département applique ces règles à sa manière. La page de votre département indique la
pratique déclarée lors de la dernière enquête nationale&nbsp;: c’est le règlement départemental en vigueur qui fait foi.</div></section>

<section><h2>Vous montez ce dossier pour quelqu’un d’autre&nbsp;?</h2>
<p>Assistants de service social, coordinateurs, mandataires&nbsp;: l’<a href="/professionnels/">espace professionnel</a>
permet de filtrer directement sur les établissements habilités, d’estimer le reste à charge et de suivre les démarches
établissement par établissement. Le parcours dédié aux
<a href="/professionnels/assistant-social/">assistants de service social</a> en détaille les étapes.</p></section>""",
  [('Peut-on demander l’aide sociale dans n’importe quel EHPAD&nbsp;?',
    'Non. Seuls les établissements habilités à l’aide sociale peuvent l’accueillir, et certains ne le sont que sur une partie de leurs places. L’information figure sur chaque fiche d’établissement de ce site.'),
   ('Les enfants sont-ils obligés de payer&nbsp;?',
    'Le département peut leur demander une participation au titre de l’obligation alimentaire, en tenant compte de leurs revenus et de leurs charges. En cas de désaccord, c’est le juge aux affaires familiales qui tranche. Les petits-enfants ne sont plus concernés depuis avril 2024.'),
   ('Que se passe-t-il pour la maison du parent&nbsp;?',
    'Elle n’est pas vendue de son vivant du fait de l’aide sociale, mais le département inscrit sa créance et la récupère au moment de la succession, dans la limite des sommes versées.')]),

 ('aide-au-logement', 'L’aide au logement en EHPAD (APL ou ALS)',
  'Elle existe aussi en maison de retraite — à condition que l’établissement soit conventionné.',
  """<div class="note"><b>En résumé.</b> Un résident d’EHPAD peut percevoir l’aide personnalisée au logement (APL)
si l’établissement est conventionné, ou à défaut l’allocation de logement sociale (ALS). Elle vient directement en
déduction du tarif d’hébergement. Il faut la demander&nbsp;: elle n’est jamais automatique.</div>

<section><h2>Laquelle des deux&nbsp;?</h2>
<p>Cela dépend d’une convention signée entre l’établissement et l’État, et non de la personne&nbsp;:</p>
<ul>
<li><b>Établissement conventionné</b>&nbsp;: aide personnalisée au logement, souvent versée directement à l’EHPAD, qui la déduit de la facture.</li>
<li><b>Établissement non conventionné</b>&nbsp;: allocation de logement sociale, en général d’un montant plus faible.</li>
</ul>
<p>La question à poser à l’établissement, avant de signer, tient en une phrase&nbsp;: <i>« Êtes-vous conventionné pour
l’aide personnalisée au logement, et quel montant perçoivent vos résidents en moyenne&nbsp;? »</i></p></section>

<section><h2>Pourquoi ce site ne la calcule pas</h2>
<p>Le montant dépend du conventionnement de l’établissement, des ressources du foyer et du tarif appliqué. Le
conventionnement n’est publié dans aucune base ouverte&nbsp;: nous préférons laisser un champ de saisie pour le montant
déjà notifié plutôt qu’afficher une estimation qui serait fausse pour beaucoup de familles. Le calcul du site est
donc <b>prudent</b>&nbsp;: le reste à charge affiché est plutôt majoré.</p></section>

<section><h2>Comment la demander</h2>
<p>La demande se fait auprès de la caisse d’allocations familiales, ou de la Mutualité sociale agricole pour les
personnes relevant du régime agricole. Un simulateur officiel existe sur leur site. Le service social de
l’établissement peut accompagner la démarche&nbsp;: c’est souvent le plus rapide.</p></section>""",
  [('L’aide au logement est-elle cumulable avec l’allocation personnalisée d’autonomie&nbsp;?',
    'Oui. Elles portent sur des lignes différentes de la facture : l’aide au logement réduit le tarif d’hébergement, l’allocation personnalisée d’autonomie réduit le tarif dépendance.'),
   ('Est-elle récupérée sur la succession&nbsp;?',
    'Non. Seule l’aide sociale à l’hébergement est récupérable sur la succession.')]),

 ('reduction-impot', 'La réduction d’impôt pour frais d’EHPAD',
  '25 % des frais restants, dans la limite de 2 500 € par an et par personne hébergée.',
  """<div class="note"><b>En résumé.</b> Une personne hébergée en EHPAD et redevable de l’impôt sur le revenu
bénéficie d’une réduction d’impôt de <b>25 % des frais d’hébergement et de dépendance</b> restant à sa charge,
dans la limite de 10 000 € de dépenses par an, soit <b>2 500 € de réduction au maximum</b>.</div>

<section><h2>Ce qui compte dans le calcul</h2>
<p>On retient les frais d’hébergement et de dépendance <b>après déduction des aides</b> déjà perçues — allocation
personnalisée d’autonomie et aide au logement. Les frais de soins n’entrent pas dans le calcul&nbsp;: ils sont payés
par l’assurance maladie.</p>
<p>Le plafond de 10 000 € s’apprécie <b>par personne hébergée</b>&nbsp;: un couple dont les deux membres sont en
établissement bénéficie donc de deux plafonds, soit jusqu’à 5 000 € de réduction.</p></section>

<section><h2>Attention au mot « réduction »</h2>
<p>Il s’agit d’une réduction d’impôt, et non d’un crédit d’impôt&nbsp;: elle vient diminuer l’impôt dû, mais elle
n’est pas remboursée si la personne n’est pas imposable. <b>Pour une personne non imposable, l’avantage est nul.</b>
C’est pourquoi le calculateur de ce site demande si la personne paie de l’impôt sur le revenu.</p></section>

<section><h2>Et la participation des enfants&nbsp;?</h2>
<p>C’est un autre mécanisme, souvent plus avantageux. La pension alimentaire versée à un parent dans le besoin est
<b>déductible du revenu imposable sans plafond</b>, sur justificatifs, y compris lorsqu’elle est versée directement à
l’établissement. Le parent doit en revanche déclarer la somme reçue. Le calculateur estime ce coût réel après
déduction pour chaque enfant.</p></section>""",
  [('Peut-on cumuler la réduction d’impôt et la déduction de la pension alimentaire&nbsp;?',
    'Oui, mais sur des contribuables différents : la réduction s’applique à la personne hébergée, la déduction de pension alimentaire à l’enfant qui verse. La même dépense ne peut pas être comptée deux fois.'),
   ('Quel montant déclarer&nbsp;?',
    'Les frais d’hébergement et de dépendance réellement payés dans l’année, après déduction des aides perçues. L’établissement délivre une attestation annuelle : conservez-la.')]),
]


def aides(ctx, ecrire):
    liens = ''.join(
        f'<a class="lien-c" href="/aides-ehpad/{s}/"><b>{esc(t.split("(")[0].strip())}</b><span>{esc(sub)}</span></a>'
        for s, t, sub, _, _ in AIDES)
    corps = f"""<div class="note"><b>L’ordre compte.</b> On demande d’abord l’allocation personnalisée d’autonomie et
l’aide au logement, on applique ensuite la réduction d’impôt, et l’aide sociale à l’hébergement n’intervient qu’en
dernier — c’est la seule qui soit récupérée sur la succession et qui puisse être demandée aux enfants.</div>
<div class="liens-grid">{liens}</div>

<section><h2>Ce que chaque aide réduit</h2>
<div class="tbl-wrap"><table class="tbl"><caption>Les quatre aides et la ligne de facture qu’elles allègent</caption>
<thead><tr><th>Aide</th><th>Qui la verse</th><th>Ce qu’elle réduit</th><th>Récupérable&nbsp;?</th></tr></thead><tbody>
<tr><td><a href="/aides-ehpad/apa/">Allocation personnalisée d’autonomie</a></td><td data-l="Qui la verse">Le département</td><td data-l="Ce qu’elle réduit">Le tarif dépendance</td><td data-l="Récupérable">Non</td></tr>
<tr><td><a href="/aides-ehpad/aide-au-logement/">Aide au logement</a></td><td data-l="Qui la verse">Caisse d’allocations familiales ou Mutualité sociale agricole</td><td data-l="Ce qu’elle réduit">Le tarif d’hébergement</td><td data-l="Récupérable">Non</td></tr>
<tr><td><a href="/aides-ehpad/reduction-impot/">Réduction d’impôt</a></td><td data-l="Qui la verse">L’administration fiscale</td><td data-l="Ce qu’elle réduit">25 % des frais restants, jusqu’à 2 500 €/an</td><td data-l="Récupérable">Non</td></tr>
<tr><td><a href="/aides-ehpad/aide-sociale-hebergement/">Aide sociale à l’hébergement</a></td><td data-l="Qui la verse">Le département</td><td data-l="Ce qu’elle réduit">Le solde de l’hébergement</td><td data-l="Récupérable"><b>Oui</b>, sur la succession</td></tr>
</tbody></table></div></section>

<section><h2>Voir ce que ça donne dans votre cas</h2>
<p>Ces aides ne prennent leur sens qu’appliquées à un établissement précis et à une situation précise.</p>
{cta('/', 'Estimer mon reste à charge après aides', 'seo_aides_to_calculator', 'Le calcul reste sur votre appareil : aucune ressource, aucune situation familiale n’est transmise.')}</section>"""
    art(ctx, ecrire, '/aides-ehpad/', 'Les aides pour financer un EHPAD',
        'Quatre aides, dans un ordre précis. Ce que chacune réduit, qui la verse, et ce qu’elle implique.',
        corps, f'Aides pour payer un EHPAD : les 4 dispositifs en 2026 | {MARQUE}',
        'Allocation personnalisée d’autonomie, aide au logement, réduction d’impôt et aide sociale à l’hébergement : ce que chaque aide réduit, qui la verse, et laquelle est récupérée sur la succession.',
        [('Aides financières', None)], prio=0.9, type_page='national')

    for s, t, sub, corps_a, faq in AIDES:
        art(ctx, ecrire, f'/aides-ehpad/{s}/', t, sub, corps_a + cta('/', 'Estimer mon reste à charge', f'seo_aide_{s}_to_calculator'),
            f'{t} | {MARQUE}', sub + ' Conditions, montants et démarches, vérifiés en septembre 2026.',
            [('Aides financières', '/aides-ehpad/'), (t.split('(')[0].strip(), None)], faq=faq, prio=0.8, type_page='national')


# ------------------------------------------------------------------- guides
GUIDES = [
 ('comment-choisir-un-ehpad', 'Comment choisir un EHPAD', 'Six critères qui comptent vraiment, dans l’ordre.',
  """<div class="note"><b>La réponse courte.</b> La distance avec la famille avant tout, puis l’habilitation à
l’aide sociale si le budget est juste, puis le tarif, puis l’évaluation officielle, puis la visite. Le reste se
décide sur place.</div>
<section><h2>1. La distance</h2><p>C’est le critère le plus sous-estimé. Un établissement à 40 minutes de route se
visite une fois par semaine&nbsp;; à 10 minutes, tous les deux jours. La fréquence des visites pèse plus sur le
quotidien d’un résident que la décoration du hall.</p></section>
<section><h2>2. L’habilitation à l’aide sociale</h2><p>Si les ressources risquent de ne pas suffire un jour, cherchez
dès le départ un établissement habilité. Déménager un parent âgé parce que le budget ne suit plus est une épreuve
qui s’évite en posant la question au premier jour.</p></section>
<section><h2>3. Le tarif, et surtout ce qu’il comprend</h2><p>Demandez la liste des prestations facturées en plus&nbsp;:
blanchissage du linge personnel, coiffeur, sorties, téléphone. Deux établissements au même tarif affiché peuvent
avoir 150 € d’écart réel par mois.</p></section>
<section><h2>4. L’évaluation officielle</h2><p>Depuis 2023, chaque établissement est évalué par un organisme
extérieur et reçoit une note de A à D. <a href="/guides/lire-une-evaluation-ehpad/">Comment la lire</a></p></section>
<section><h2>5. Le personnel</h2><p>Le nombre de professionnels par résident et le taux de rotation des équipes
en disent plus que les locaux. Ces chiffres figurent sur la fiche officielle de chaque établissement, sur le
portail public des personnes âgées.</p></section>
<section><h2>6. La visite</h2><p>Elle tranche. <a href="/guides/questions-a-poser-lors-dune-visite/">Les questions
à poser</a>, et une règle simple&nbsp;: venez sans rendez-vous une seconde fois, à l’heure du déjeuner.</p></section>""",
  [('Faut-il choisir un EHPAD public ou privé&nbsp;?',
    'Ni l’un ni l’autre par principe. Le public et l’associatif sont en moyenne moins chers et plus souvent habilités à l’aide sociale ; le privé commercial propose plus souvent des chambres récentes et de grande taille. La qualité de l’accompagnement ne se déduit pas du statut.'),
   ('Combien d’établissements faut-il visiter&nbsp;?',
    'Trois suffisent généralement pour se faire une idée des écarts. Au-delà, la décision se brouille. Comparez d’abord les tarifs et les évaluations sur dossier, puis visitez les trois retenus.')]),

 ('questions-a-poser-lors-dune-visite', 'Les questions à poser lors d’une visite d’EHPAD',
  'Douze questions concrètes, à imprimer avant de partir.',
  """<p>Une visite dure une heure et l’on repart souvent sans avoir posé les questions qui comptent. Voici celles
dont la réponse change vraiment la décision.</p>
<section><h2>Sur l’argent</h2><ul>
<li>Quel est le tarif d’hébergement du jour, et quand a-t-il augmenté pour la dernière fois&nbsp;?</li>
<li>Quelles prestations sont facturées en plus du tarif&nbsp;? Pouvez-vous me donner la liste et les montants&nbsp;?</li>
<li>Êtes-vous habilité à l’aide sociale à l’hébergement&nbsp;? Sur toutes vos places ou sur une partie&nbsp;?</li>
<li>Êtes-vous conventionné pour l’aide personnalisée au logement&nbsp;?</li>
<li>Que se passe-t-il financièrement en cas d’hospitalisation ou d’absence prolongée&nbsp;?</li></ul></section>
<section><h2>Sur le quotidien</h2><ul>
<li>Combien de professionnels sont présents la nuit, pour combien de résidents&nbsp;?</li>
<li>Y a-t-il un infirmier la nuit, ou une astreinte&nbsp;?</li>
<li>Quels sont les horaires des repas, et peut-on manger avec son parent&nbsp;?</li>
<li>Les visites sont-elles libres&nbsp;?</li></ul></section>
<section><h2>Sur l’équipe</h2><ul>
<li>Combien de départs avez-vous eu dans l’équipe soignante cette année&nbsp;?</li>
<li>Faites-vous appel à de l’intérim, et à quelle fréquence&nbsp;?</li>
<li>Quand votre dernière évaluation a-t-elle eu lieu, et puis-je en lire le rapport&nbsp;?</li></ul></section>
<div class="note">Une seconde visite, sans rendez-vous, à l’heure du déjeuner, apprend souvent plus que la première.</div>""",
  None),

 ('lire-une-evaluation-ehpad', 'Comment lire l’évaluation officielle d’un EHPAD',
  'Ce que mesure la note de A à D, et ce qu’elle ne mesure pas.',
  """<div class="note"><b>En résumé.</b> Depuis 2023, chaque établissement médico-social est évalué tous les cinq ans
par un organisme extérieur, selon un référentiel de la Haute Autorité de santé. Le résultat est une note de A à D et
un nombre de critères impératifs atteints.</div>
<section><h2>Ce que dit la note</h2><p>Elle synthétise trois chapitres&nbsp;: la personne accompagnée, les
professionnels, et l’établissement lui-même. Elle est accompagnée du nombre de <b>critères impératifs atteints sur
18</b>&nbsp;: ce sont les exigences non négociables, notamment sur la sécurité et le respect des droits. Un
établissement noté B mais avec 18 critères impératifs atteints n’est pas dans la même situation qu’un établissement
noté B avec 12.</p></section>
<section><h2>Ce qu’elle ne dit pas</h2><ul>
<li>L’organisme évaluateur est <b>choisi et rémunéré par l’établissement</b> lui-même. Nous l’indiquons sur chaque fiche.</li>
<li>La note date du jour de l’évaluation&nbsp;: une équipe peut avoir entièrement changé depuis.</li>
<li>Toutes les évaluations ne sont pas encore publiées. Une absence de note n’est pas un mauvais signe.</li></ul></section>
<section><h2>Les autres signaux publics</h2><p>Deux sources complètent utilement l’évaluation&nbsp;: les contrôles
d’hygiène alimentaire, publiés par la Direction générale de l’alimentation et repris sur nos fiches, et les
indicateurs de personnel du portail public des personnes âgées (taux d’encadrement, absentéisme, rotation).</p></section>""",
  None),

 ('ehpad-public-prive-ou-associatif', 'EHPAD public, privé ou associatif : quelles différences ?',
  'Le statut change le tarif, l’accès à l’aide sociale et le mode de gestion — pas la qualité par principe.',
  """<section><h2>Les trois statuts</h2><ul>
<li><b>Public</b> — rattaché à un hôpital ou à une commune. Tarifs fixés par le conseil départemental, presque toujours habilité à l’aide sociale.</li>
<li><b>Privé à but non lucratif (associatif)</b> — géré par une association, une fondation ou une mutuelle. Souvent habilité à l’aide sociale, tarifs proches du public.</li>
<li><b>Privé commercial</b> — géré par une entreprise. Tarifs libres à l’ouverture puis encadrés dans leur évolution, plus souvent des chambres récentes, moins souvent habilité à l’aide sociale.</li></ul></section>
<section><h2>Ce que cela change concrètement</h2>
<p>Le statut est le premier facteur d’écart de tarif, avec la localisation. Il détermine aussi largement la
possibilité de demander un jour l’aide sociale à l’hébergement. En revanche, il ne permet de rien conclure sur la
qualité de l’accompagnement&nbsp;: les évaluations officielles ne montrent pas de hiérarchie nette entre statuts.</p>
<p>Sur chaque fiche de ce site, le statut est indiqué, ainsi que l’habilitation à l’aide sociale.</p></section>""",
  None),

 ('ehpad-alzheimer-unite-protegee', 'EHPAD, Alzheimer et unité protégée',
  'Ce qu’est une unité protégée, quand elle est utile, et ce qu’elle change au tarif.',
  """<div class="note"><b>En résumé.</b> Une unité protégée est un espace fermé au sein d’un EHPAD, destiné aux
personnes désorientées qui risquent de se mettre en danger en sortant seules. L’équipe y est formée aux troubles
cognitifs et l’environnement est adapté.</div>
<section><h2>Quand elle est utile</h2><p>Quand la personne déambule, ne reconnaît plus les lieux, ou a déjà fugué.
Elle ne se justifie pas pour une simple perte de mémoire&nbsp;: un EHPAD classique accompagne très bien une maladie
d’Alzheimer débutante, et un environnement fermé n’est pas neutre.</p></section>
<section><h2>Les termes que vous entendrez</h2><ul>
<li><b>Unité protégée</b> ou <b>unité de vie protégée</b>&nbsp;: hébergement permanent en espace fermé.</li>
<li><b>Pôle d’activités et de soins adaptés</b>&nbsp;: accueil de jour, au sein de l’établissement, pour des activités thérapeutiques.</li>
<li><b>Unité d’hébergement renforcée</b>&nbsp;: pour les troubles du comportement les plus sévères.</li></ul></section>
<section><h2>Et le tarif&nbsp;?</h2><p>Le tarif d’hébergement est en général le même que dans le reste de
l’établissement&nbsp;; c’est le tarif dépendance qui est plus élevé, la perte d’autonomie étant plus importante — et
c’est justement la ligne que couvre en grande partie l’allocation personnalisée d’autonomie.</p>
<div class="att">Les données publiques ne disent pas quels établissements disposent d’une unité protégée, ni combien
de places y sont disponibles. C’est une question à poser directement à l’établissement&nbsp;: nous préférons l’écrire
plutôt que d’afficher une information que nous n’avons pas.</div></section>""",
  None),

 ('trouver-une-place-en-ehpad', 'Comment trouver une place en EHPAD',
  'Le dossier unique, le délai réel, et ce qui accélère vraiment les choses.',
  """<div class="note"><b>En résumé.</b> Il n’existe qu’une seule porte d’entrée&nbsp;: le dossier unique national,
déposé sur la plateforme ViaTrajectoire. Un seul dossier vaut candidature dans autant d’établissements que vous
voulez.</div>
<section><h2>Le délai, en vrai</h2><p>Le délai entre le dépôt du dossier et l’entrée a été d’<b>un mois ou moins pour
55 % des personnes entrées en 2023</b>, d’après l’enquête nationale de la Direction de la recherche, des études, de
l’évaluation et des statistiques. L’image d’une attente systématique de plusieurs années ne correspond pas aux
chiffres, même si elle est réelle dans certains établissements très demandés.</p></section>
<section><h2>Ce qui accélère</h2><ul>
<li><b>Candidater largement.</b> Dix établissements plutôt que trois, sur un rayon plus large.</li>
<li><b>Élargir le rayon.</b> Quelques kilomètres suffisent souvent à changer complètement la disponibilité.</li>
<li><b>Relancer.</b> Un appel tous les quinze jours fait exister le dossier.</li>
<li><b>Accepter un accueil temporaire</b> en attendant une place définitive, quand l’établissement en propose.</li></ul></section>
<section><h2>Pourquoi personne ne publie les places libres</h2>
<p>Aucune base publique ne recense les places réellement disponibles. La plateforme qui détient l’information est
réservée aux professionnels. Ce site affiche donc, à la place, une estimation clairement présentée comme telle&nbsp;:
le taux d’occupation des établissements comparables et le rythme auquel des places s’y libèrent — environ 38 % des
places changent d’occupant chaque année, soit une place tous les douze jours dans un établissement de 80 places.</p></section>""",
  [('Peut-on s’inscrire dans plusieurs EHPAD en même temps&nbsp;?',
    'Oui, et c’est recommandé. Le dossier unique national est transmis à tous les établissements que vous sélectionnez, sans avoir à remplir un dossier par établissement.'),
   ('Faut-il attendre des années pour avoir une place&nbsp;?',
    'Pas en règle générale : plus de la moitié des personnes entrées en 2023 ont attendu un mois ou moins. Les délais longs concernent surtout les établissements les plus demandés et les zones tendues.')]),

 ('dossier-admission-ehpad', 'Le dossier d’admission en EHPAD',
  'Les pièces à réunir, qui remplit quoi, et les pièges qui font perdre des semaines.',
  """<section><h2>Ce que contient le dossier</h2><p>Le dossier unique national comporte deux parties&nbsp;:</p>
<ul><li><b>Un volet administratif</b>, rempli par la famille&nbsp;: identité, situation familiale, ressources, régime de retraite, mesure de protection éventuelle.</li>
<li><b>Un volet médical</b>, rempli par le médecin traitant&nbsp;: état de santé, traitements, degré d’autonomie. Il est confidentiel et n’est lu que par le médecin coordonnateur de l’établissement.</li></ul></section>
<section><h2>Les pièces à préparer</h2><ul>
<li>Pièce d’identité et livret de famille.</li>
<li>Avis d’imposition ou de non-imposition le plus récent.</li>
<li>Justificatifs de toutes les pensions et retraites.</li>
<li>Attestation de sécurité sociale et carte de mutuelle.</li>
<li>Notification d’allocation personnalisée d’autonomie si elle existe déjà.</li>
<li>Jugement de protection juridique le cas échéant.</li>
<li>Coordonnées des enfants — le département les demandera si l’aide sociale est sollicitée.</li></ul></section>
<section><h2>Les pièges</h2><ul>
<li><b>Le volet médical oublié.</b> C’est la première cause de dossier bloqué&nbsp;: relancez le médecin traitant.</li>
<li><b>Signer le contrat de séjour sans la liste des prestations facturées en plus.</b> Demandez-la par écrit.</li>
<li><b>Attendre l’entrée pour demander les aides.</b> L’allocation personnalisée d’autonomie est due à compter du dépôt du dossier complet&nbsp;: déposez-le tôt.</li></ul></section>""",
  None),

 ('urgence-apres-hospitalisation', 'Trouver un EHPAD en urgence, après une hospitalisation',
  'Ce qui fonctionne quand il faut une solution en quelques jours.',
  """<div class="note"><b>Le bon interlocuteur.</b> Le service social de l’hôpital. Il connaît les établissements qui
ont des places, dispose de circuits d’admission rapides et peut monter le dossier en 48 heures. Demandez-le dès le
premier jour d’hospitalisation, pas la veille de la sortie.</div>
<section><h2>Les solutions transitoires</h2><ul>
<li><b>L’accueil temporaire</b> en EHPAD&nbsp;: quelques semaines à quelques mois, souvent disponible plus vite qu’une place permanente. Les tarifs figurent sur nos fiches quand l’établissement les a déclarés.</li>
<li><b>Les soins de suite et de réadaptation</b>&nbsp;: un passage intermédiaire par un service hospitalier, qui laisse le temps de chercher.</li>
<li><b>Un retour à domicile renforcé</b>, avec passage d’infirmiers et portage de repas, le temps qu’une place se libère.</li></ul></section>
<section><h2>Ce qu’il ne faut pas faire</h2>
<p>Accepter la première place proposée sans en vérifier le tarif ni l’habilitation à l’aide sociale. Un déménagement
six mois plus tard, faute de moyens, est bien plus difficile qu’un choix un peu plus long au départ. Vérifiez au
minimum ces deux points, ils tiennent en un appel.</p></section>""",
  None),

 ('tarif-hebergement-et-tarif-dependance', 'Tarif d’hébergement et tarif dépendance : la différence',
  'Deux lignes, deux logiques, deux payeurs. C’est la clé pour lire une facture.',
  """<section><h2>Le tarif d’hébergement</h2><p>Il couvre la chambre, les repas, l’entretien, l’animation et
l’administration. Il est <b>entièrement à la charge du résident</b>, aidé le cas échéant par l’aide au logement, la
réduction d’impôt, sa famille ou le département. C’est la ligne la plus lourde&nbsp;: environ 80 % de ce que paie
une famille.</p></section>
<section><h2>Le tarif dépendance</h2><p>Il couvre l’aide apportée pour les gestes quotidiens. Il dépend du niveau de
perte d’autonomie, mesuré par la grille officielle GIR, et l’établissement affiche trois tarifs&nbsp;: GIR 1-2,
GIR 3-4, GIR 5-6. Le résident paie au minimum le tarif GIR 5-6&nbsp;; le reste est pris en charge par
<a href="/aides-ehpad/apa/">l’allocation personnalisée d’autonomie</a>.</p></section>
<section><h2>Et les soins&nbsp;?</h2><p>Troisième ligne, invisible sur la facture&nbsp;: infirmiers, médecin
coordonnateur, parfois médicaments. Elle est financée par l’assurance maladie. Selon que l’établissement est en
« tarif global » ou en « tarif partiel », les médicaments et certains soins passent par l’établissement ou par les
professionnels de ville — sans changer le reste à charge sur l’hébergement.</p></section>
<div class="note">Retenez ceci&nbsp;: quand un site annonce un prix d’EHPAD « à partir de », il parle presque toujours
du seul tarif d’hébergement, en chambre seule, hors dépendance et hors aides.</div>""",
  None),

 ('pourquoi-les-prix-varient', 'Pourquoi les prix des EHPAD varient autant',
  'Un rapport de un à six entre le moins cher et le plus cher de France. Les raisons.',
  """<section><h2>Le territoire</h2><p>C’est le premier facteur. Le tarif médian d’un département à l’autre varie du
simple au double. Le foncier explique l’essentiel&nbsp;: un établissement paie son bâtiment, et le répercute.
<a href="/prix-ehpad-par-departement/">Voir le classement</a></p></section>
<section><h2>Le statut</h2><p>Les établissements publics et associatifs sont en moyenne moins chers&nbsp;: leurs tarifs
d’hébergement sont encadrés par le conseil départemental lorsqu’ils sont habilités à l’aide sociale.
<a href="/guides/ehpad-public-prive-ou-associatif/">Les différences</a></p></section>
<section><h2>Le bâtiment</h2><p>Une chambre de 25 m² avec salle de bain privative dans un immeuble de 2020 ne coûte
pas la même chose qu’une chambre de 18 m² dans un bâtiment des années 1970. C’est souvent la principale différence
entre deux établissements voisins.</p></section>
<section><h2>Ce qui est compris — ou pas</h2><p>Blanchissage du linge personnel, coiffeur, téléphone, sorties&nbsp;:
selon les établissements, ces prestations sont incluses ou facturées en plus. Deux tarifs identiques peuvent
cacher plus de 100 € d’écart réel par mois. Demandez la liste écrite.</p></section>
<section><h2>Ce qui n’explique pas le prix</h2><p>La qualité de l’accompagnement. Les évaluations officielles ne
montrent pas de lien net entre le tarif et la note obtenue. Un établissement cher n’est pas mécaniquement un
établissement où l’on est mieux accompagné.</p></section>""",
  None),

 ('comparer-deux-ehpad', 'Comment comparer deux EHPAD',
  'Sept points à mettre côte à côte — et un seul chiffre qui compte vraiment.',
  """<div class="note"><b>Le seul chiffre qui compte&nbsp;: le reste à charge.</b> Pas le tarif affiché. Deux
établissements dont les tarifs diffèrent de 200 € peuvent finir au même reste à charge, selon leurs tarifs
dépendance et leur conventionnement pour l’aide au logement.</div>
<section><h2>Les sept points</h2><ol>
<li><b>Le reste à charge réel</b>, calculé pour la situation de la personne.</li>
<li><b>Les prestations facturées en plus</b>, liste écrite à l’appui.</li>
<li><b>L’habilitation à l’aide sociale</b>, totale ou partielle.</li>
<li><b>L’évolution du tarif</b> sur les dernières années&nbsp;: elle annonce les suivantes. Chaque fiche de ce site l’affiche.</li>
<li><b>L’évaluation officielle</b> et le nombre de critères impératifs atteints.</li>
<li><b>Le personnel</b>&nbsp;: présence de nuit, rotation des équipes, recours à l’intérim.</li>
<li><b>La distance</b> avec les proches qui viendront.</li></ol></section>
<section><h2>Faire la comparaison</h2>
<p>Le calculateur de ce site compare jusqu’à trois établissements côte à côte, avec le reste à charge de chacun pour
la même situation, et produit une fiche imprimable.</p>
""" + """<div class="cta"><a class="cta-b" href="/" data-ev="seo_compare_click">Comparer trois établissements</a></div></section>""",
  None),

 ('qui-paie-quand-la-retraite-ne-suffit-pas', 'Qui paie quand la retraite ne suffit pas ?',
  'Le résident, puis la famille, puis le département — dans cet ordre, et avec des règles précises.',
  """<div class="note"><b>En résumé.</b> Le résident paie d’abord, avec ses revenus puis son épargne et son
patrimoine. La famille peut ensuite être sollicitée au titre de l’obligation alimentaire. Le département complète
en dernier, et récupère sur la succession.</div>
<section><h2>1. Le résident</h2><p>Retraites, revenus du patrimoine, loyers perçus, épargne. En aide sociale, il
conserve au moins 10 % de ses ressources et jamais moins de 125 € par mois. Si son conjoint est resté à domicile,
celui-ci doit conserver au moins 1 043,59 € par mois.</p></section>
<section><h2>2. Les enfants</h2><p>C’est l’obligation alimentaire. Sont concernés les enfants, les gendres et les
belles-filles&nbsp;; <b>les petits-enfants ne le sont plus depuis la loi du 8 avril 2024</b>. Il n’existe aucun barème
national&nbsp;: le conseil départemental, et à défaut le juge aux affaires familiales, fixe la part de chacun en
fonction de ses revenus et de ses charges. La participation moyenne constatée au niveau national est de 270 € par
mois. Ce qui est versé est déductible du revenu imposable, sans plafond.</p>
<p>Le calculateur de ce site répartit à parts égales ce qui n’est pas couvert et affiche le coût réel de chacun
après déduction fiscale&nbsp;: c’est une hypothèse de travail pour discuter en famille, pas la décision du
département.</p></section>
<section><h2>3. Le département</h2><p>C’est <a href="/aides-ehpad/aide-sociale-hebergement/">l’aide sociale à
l’hébergement</a>, possible uniquement dans un établissement habilité, et récupérable sur la succession ainsi que
sur les donations des dix dernières années.</p></section>
<section><h2>Une conversation à avoir tôt</h2><p>Le sujet se règle mieux avant l’entrée qu’après le premier impayé.
Le lien de partage du calculateur permet d’envoyer la même simulation à toute la fratrie&nbsp;: chacun voit les mêmes
chiffres, sans qu’aucun nom ni aucune donnée ne circule.</p></section>""",
  [('Les petits-enfants doivent-ils payer&nbsp;?',
    'Non. La loi du 8 avril 2024 a supprimé l’obligation alimentaire des petits-enfants envers leurs grands-parents accueillis en établissement.'),
   ('Un enfant peut-il être dispensé&nbsp;?',
    'Oui. Le juge peut décharger un enfant de son obligation, notamment lorsque le parent a gravement manqué à ses propres obligations envers lui. Cette dispense s’apprécie au cas par cas.')]),
]


def guides(ctx, ecrire):
    liens = ''.join(f'<a class="lien-c" href="/guides/{s}/"><b>{esc(t)}</b><span>{esc(sub)}</span></a>'
                    for s, t, sub, _, _ in GUIDES)
    corps = f"""<p>Douze guides courts, écrits pour répondre vite. Chacun donne la réponse dès les premières lignes,
puis les cas particuliers, puis les sources.</p>
<div class="liens-grid">{liens}</div>
<section><h2>Et pour les chiffres</h2><div class="liens-grid">
<a class="lien-c" href="/prix-ehpad/"><b>Le prix des EHPAD</b><span>Tarif médian, écarts, évolution.</span></a>
<a class="lien-c" href="/aides-ehpad/"><b>Les aides financières</b><span>Quatre aides, dans le bon ordre.</span></a>
<a class="lien-c" href="/calcul-reste-a-charge-ehpad/"><b>Calculer le reste à charge</b><span>La méthode, ligne par ligne.</span></a>
</div></section>"""
    art(ctx, ecrire, '/guides/', 'Les guides', 'Choisir, visiter, financer, déposer un dossier.', corps,
        f'Guides EHPAD : choisir, visiter, financer | {MARQUE}',
        'Douze guides courts pour choisir un EHPAD, préparer une visite, monter un dossier d’admission et financer le séjour.',
        [('Guides', None)], prio=0.7, type_page='guide', article=False)
    for s, t, sub, corps_g, faq in GUIDES:
        art(ctx, ecrire, f'/guides/{s}/', t, sub, corps_g,
            f'{t} | {MARQUE}', sub + ' Guide court, sources officielles, vérifié en septembre 2026.',
            [('Guides', '/guides/'), (t, None)], faq=faq, prio=0.6, type_page='guide')


# ---------------------------------------------------------------- baromètre
def barometre(ctx, ecrire):
    s = ctx['FR']
    dd = sorted(((stats(l)['med'], d, stats(l)) for d, l in ctx['par_dep'].items() if stats(l)['med']))
    par_statut = {}
    for k, lib in ((0, 'Public'), (1, 'Associatif'), (2, 'Privé commercial')):
        p = [r['p'] for r in ctx['rows'] if r['p'] and r['statut'] == k]
        if p: par_statut[lib] = (mediane(p), len(p))
    villes = sorted(((stats(ctx['par_ville'][c])['med'], c) for c in ctx['villes_page']
                     if stats(ctx['par_ville'][c])['n_prix'] >= 5), reverse=True)[:15]
    l_statut = ''.join(f'<tr><td>{esc(k)}</td><td class="num" data-l="Tarif médian">{eur(mois_eur(v[0]))}</td>'
                       f'<td class="num" data-l="Établissements">{nb(v[1])}</td></tr>' for k, v in par_statut.items())
    l_villes = ''.join(f'<tr><td><a href="{ctx["url_ville"][c]}">{esc(ctx["nom_ville"][c])}</a></td>'
                       f'<td class="num" data-l="Tarif médian">{eur(mois_eur(m))}</td>'
                       f'<td class="num" data-l="EHPAD">{stats(ctx["par_ville"][c])["n"]}</td></tr>' for m, c in villes)
    corps = f"""<div class="note"><b>À retenir.</b> Tarif d’hébergement médian&nbsp;: <b>{med_mois(s)} par mois</b>
pour une chambre seule ({eur2(s['med'])} par jour), sur {nb(s['n_prix'])} établissements ayant déclaré leur tarif.
Hausse médiane, établissement par établissement, de <b>{pct(s['evol_med'])}</b> depuis 2018, contre +17,2 % d’inflation. <b>{nb(s['ash'])}</b> établissements
sur {nb(s['n'])} sont habilités à l’aide sociale à l’hébergement.</div>

<section><h2>Par statut d’établissement</h2>
<div class="tbl-wrap"><table class="tbl"><caption>Tarif d’hébergement médian mensuel, chambre seule</caption>
<thead><tr><th>Statut</th><th class="num">Tarif médian</th><th class="num">Établissements</th></tr></thead>
<tbody>{l_statut}</tbody></table></div></section>

<section><h2>Les départements les plus chers et les moins chers</h2>
<p>Les cinq départements où le tarif médian est le plus élevé&nbsp;: {', '.join(f'<a href="{ctx["url_dep"][d]}">{esc(geo.DEPARTEMENTS[d])}</a> ({eur(mois_eur(m))})' for m, d, _ in dd[-5:][::-1])}.</p>
<p>Les cinq où il est le plus bas&nbsp;: {', '.join(f'<a href="{ctx["url_dep"][d]}">{esc(geo.DEPARTEMENTS[d])}</a> ({eur(mois_eur(m))})' for m, d, _ in dd[:5])}.</p>
<p><a href="/prix-ehpad-par-departement/">Le classement complet des 101 départements</a></p></section>

<section><h2>Les villes où l’EHPAD coûte le plus cher</h2>
<p>Communes comptant au moins cinq établissements avec tarif déclaré.</p>
<div class="tbl-wrap"><table class="tbl"><caption>Tarif d’hébergement médian mensuel par commune</caption>
<thead><tr><th>Commune</th><th class="num">Tarif médian</th><th class="num">EHPAD</th></tr></thead>
<tbody>{l_villes}</tbody></table></div></section>

<section><h2>Méthode</h2>
<p>Calculs réalisés à partir des tarifs déclarés par les établissements à la Caisse nationale de solidarité pour
l’autonomie (dernier fichier&nbsp;: {CNSA_MAJ}), pour {nb(s['n_prix'])} des {nb(s['n'])} EHPAD ouverts en France.
Le tarif journalier d’hébergement d’une chambre seule est multiplié par {str(MOIS).replace('.', ',')} jours.
Nous retenons la <b>médiane</b> et non la moyenne, la distribution comportant des valeurs extrêmes.
L’évolution est la médiane des évolutions individuelles, calculée sur les {nb(s['n_evol'])} établissements dont le tarif est connu à deux dates au moins.
La référence d’inflation est l’indice des prix à la consommation de l’INSEE.</p>
<p><b>Réutilisation.</b> Ces chiffres sont libres de reprise, avec la mention&nbsp;:
« Données&nbsp;: {MARQUE}, à partir des tarifs déclarés à la CNSA ({CNSA_MAJ}) ».
<a href="/notre-methodologie.html">Méthodologie détaillée</a> ·
<a href="mailto:contact@trouver-mon-ehpad.fr?subject=Barom%C3%A8tre">Nous contacter</a></p></section>"""
    ld = [{"@type": "Dataset", "name": f"Baromètre du prix des EHPAD en France — {MARQUE}, septembre 2026",
           "description": "Tarif d’hébergement médian des EHPAD en France, par département, par statut d’établissement et par commune, avec l’évolution depuis 2018 comparée à l’inflation.",
           "url": DOMAINE + '/etudes/barometre-prix-ehpad-2026/', "inLanguage": "fr-FR",
           "isAccessibleForFree": True, "creator": {"@id": DOMAINE + "/#organization"},
           "temporalCoverage": "2018/2026", "dateModified": MAJ_ISO,
           "spatialCoverage": {"@type": "Country", "name": "France"},
           "license": "https://www.etalab.gouv.fr/licence-ouverte-open-licence"}]
    html = f"""<h1 class="p-h1">Baromètre du prix des EHPAD — septembre 2026</h1>
<p class="p-sub">Ce que coûte réellement un EHPAD en France, département par département, statut par statut, et comment les tarifs ont évolué depuis 2018.</p>
<p class="p-maj">Publié le {MAJ} · calculé sur {nb(s['n_prix'])} établissements</p>
{kpis([(med_mois(s), 'tarif d’hébergement médian, par mois', True),
       (pct(s['evol_med']), 'hausse médiane depuis 2018 (inflation : +17,2 %)'),
       (nb(s['ash']), 'habilités à l’aide sociale'),
       (nb(s['n']), 'EHPAD recensés')])}
{corps}{sources()}"""
    ecrire('/etudes/barometre-prix-ehpad-2026/', layout.page('/etudes/barometre-prix-ehpad-2026/',
        titre_page('Baromètre du prix des EHPAD — septembre 2026'),
        f'Le tarif d’hébergement médian d’un EHPAD est de {med_mois(s)} par mois. Évolution depuis 2018, écarts par département, par statut et par ville. Chiffres libres de reprise.',
        html, [('Accueil', '/'), ('Études', '/etudes/'), ('Baromètre des prix 2026', None)],
        ld_extra=ld, type_page='etude'), 0.8, 'contenus')

    corps_i = """<p>Des analyses construites à partir des données publiques, recalculées à chaque mise à jour.
Les chiffres sont libres de reprise, avec mention de la source.</p>
<div class="liens-grid">
<a class="lien-c" href="/etudes/barometre-prix-ehpad-2026/"><b>Baromètre du prix des EHPAD — septembre 2026</b><span>Tarif médian, évolution depuis 2018, écarts par département et par statut.</span></a>
<a class="lien-c" href="/prix-ehpad-par-departement/"><b>Le prix par département</b><span>Les 101 départements classés.</span></a>
</div>
<p>Vous êtes journaliste, élu, ou vous travaillez dans une association d’aidants&nbsp;? Écrivez-nous&nbsp;:
<a href="mailto:contact@trouver-mon-ehpad.fr">contact@trouver-mon-ehpad.fr</a>. Nous pouvons fournir les données
détaillées de ces calculs.</p>"""
    art(ctx, ecrire, '/etudes/', 'Études et baromètres', 'Ce que disent les données publiques, recalculé à chaque mise à jour.',
        corps_i, f'Études sur les EHPAD en France | {MARQUE}',
        'Baromètre des prix, écarts départementaux, évolution depuis 2018 : nos analyses construites à partir des données publiques, libres de reprise.',
        [('Études', None)], prio=0.6, type_page='etude', article=False)


# -------------------------------------------------------------- espace professionnel
def professionnels(ctx, ecrire):
    s = ctx['FR']
    deps = len(ctx['par_dep'])
    corps = f"""{kpis([(nb(s['n']), 'EHPAD référencés, dans les {} départements'.format(nb(deps)), True),
                       (nb(s['ash'] + s['ash_conf']), 'habilités à l’aide sociale à l’hébergement', True),
                       (nb(s['n_prix']), 'tarifs d’hébergement déclarés à la CNSA'),
                       (nb(s['has']), 'évaluations publiées par la Haute Autorité de santé')])}

<div class="note"><b>Ce que fait cet outil, et ce qu’il ne fait pas.</b> Il vous dit, pour une zone donnée,
quels établissements sont <b>compatibles</b> avec un budget, une distance et un besoin d’aide sociale, et il
estime le reste à charge réel après aides. Il ne connaît <b>pas</b> les places libres en temps réel, il ne
transmet aucune candidature et il ne se prononce pas sur la compatibilité médicale d’un établissement avec
une situation clinique. Il ne remplace ni ViaTrajectoire, ni un appel au directeur d’établissement.</div>

{cta('/?pro=1', 'Démarrer une recherche', 'seo_pro_to_calculator',
     'Gratuit, sans compte. Les informations saisies restent dans votre navigateur : rien n’est transmis, rien n’est stocké sur un serveur.')}

<section><h2>À qui cet outil s’adresse</h2>
<p>À tous ceux qui montent des dossiers d’entrée en EHPAD pour d’autres&nbsp;: assistants de service social
d’hôpital, de centre communal d’action sociale ou de conseil départemental, coordinateurs de dispositifs
d’appui à la coordination, responsables de service d’aide à domicile, gestionnaires de cas, mandataires
judiciaires à la protection des majeurs, cadres de santé qui préparent une sortie d’hospitalisation.</p>
<p>Le point commun&nbsp;: vous avez besoin, en quelques minutes, de la liste des établissements réellement
finançables dans un secteur — pas d’un annuaire de plus.</p>
</section>

<section><h2>Comment ça se passe</h2>
<ol class="etapes">
<li><b>Vous décrivez la situation.</b> Une zone, une distance acceptable, un niveau de perte d’autonomie
(GIR), les ressources mensuelles s’il faut estimer un reste à charge, et le besoin éventuel d’aide sociale.
Aucune identité n’est demandée&nbsp;: ni nom, ni date de naissance, ni adresse personnelle, ni élément médical.</li>
<li><b>Vous obtenez les établissements compatibles.</b> Classés selon la priorité que vous choisissez — reste à
charge, distance, habilitation à l’aide sociale — avec pour chacun la raison du classement écrite en clair.
Aucun score global n’est affiché&nbsp;: vous voyez ce qui est vérifié, ce qui ne l’est pas, et ce qui manque.</li>
<li><b>Vous constituez votre liste de démarches.</b> Jusqu’à douze établissements, chacun avec un état
(à contacter, contacté, dossier envoyé, en attente, place proposée, refus, écarté) et une note libre.
Le tout s’exporte en CSV pour être joint au dossier ou partagé par vos moyens habituels.</li>
</ol>
</section>

<section><h2>Ce que vous voyez pour chaque établissement</h2>
<div class="tbl-wrap"><table class="tbl"><caption>Les informations disponibles, et leur source</caption>
<thead><tr><th>Information</th><th>Source</th><th>Couverture</th></tr></thead><tbody>
<tr><td>Numéro FINESS, raison sociale, adresse, téléphone</td><td data-l="Source">Répertoire FINESS</td><td data-l="Couverture">{nb(s['n'])} établissements</td></tr>
<tr><td>Tarif d’hébergement et tarifs dépendance</td><td data-l="Source">CNSA, fichier «&nbsp;prix et tarifs&nbsp;», {CNSA_MAJ}</td><td data-l="Couverture">{nb(s['n_prix'])} sur {nb(s['n'])}</td></tr>
<tr><td>Habilitation à l’aide sociale à l’hébergement</td><td data-l="Source">FINESS et arrêtés départementaux</td><td data-l="Couverture">{nb(s['ash'] + s['ash_conf'])} habilités</td></tr>
<tr><td>Évaluation de la qualité</td><td data-l="Source">Haute Autorité de santé</td><td data-l="Couverture">{nb(s['has'])} évalués</td></tr>
<tr><td>Évolution du tarif depuis 2018</td><td data-l="Source">Séries CNSA 2018-2025</td><td data-l="Couverture">{nb(s['n_evol'])} établissements</td></tr>
<tr><td>Reste à charge estimé après aides</td><td data-l="Source">Calcul local (APA, aide au logement, réduction d’impôt, aide sociale)</td><td data-l="Couverture">Selon les ressources saisies</td></tr>
<tr><td>Places libres aujourd’hui</td><td data-l="Source"><span class="non">Non disponible</span></td><td data-l="Couverture">Aucune donnée publique nationale</td></tr>
</tbody></table></div>
<p class="def">Quand un chiffre n’est pas connu, il n’est pas affiché et rien n’est estimé à sa place.
Un établissement dont le tarif n’a pas été déclaré apparaît dans la liste, sans montant.</p>
</section>

<section><h2>Données et confidentialité</h2>
<p>Le calcul est fait dans votre navigateur. Les ressources, le niveau de GIR et la situation familiale
que vous saisissez ne quittent pas l’appareil et ne sont <b>pas</b> enregistrés dans une recherche sauvegardée&nbsp;:
ils servent au calcul du moment, puis disparaissent.</p>
<p>Une recherche enregistrée retient la zone, la distance, les critères et la liste de démarches — rien d’autre.
Elle est stockée dans le navigateur de cet appareil&nbsp;: elle n’est ni transmise, ni synchronisée, ni sauvegardée
ailleurs, et vider le cache l’efface. Nommez vos recherches avec un repère neutre, «&nbsp;Dossier 001&nbsp;» par exemple,
jamais avec le nom de la personne accompagnée.</p>
<p>Il n’existe aujourd’hui ni compte, ni espace partagé, ni sauvegarde serveur&nbsp;: l’outil ne prétend pas
assurer une conservation qu’il n’assure pas.</p>
</section>

<section><h2>Pour aller plus loin</h2>
<div class="liens-grid">
<a class="lien-c" href="/professionnels/assistant-social/"><b>Assistants de service social</b><span>Le détail du parcours, de l’évaluation des ressources au dépôt du dossier d’aide sociale</span></a>
<a class="lien-c" href="/aides-ehpad/aide-sociale-hebergement/"><b>L’aide sociale à l’hébergement</b><span>Conditions, obligation alimentaire, récupération sur succession</span></a>
<a class="lien-c" href="/aides-ehpad/apa/"><b>L’allocation personnalisée d’autonomie</b><span>Le calcul exact de la participation, seuil par seuil</span></a>
<a class="lien-c" href="/notre-methodologie.html"><b>Notre méthodologie</b><span>Les sources, les formules, et ce que nous ne simulons pas</span></a>
</div>
</section>"""
    faq = [
        ('Cet outil donne-t-il les places disponibles&nbsp;?',
         'Non. Aucune base publique nationale ne recense les places libres en temps réel, et nous n’en inventons pas. '
         'Une recherche vous donne le nombre d’<b>établissements correspondant à vos critères</b>, pas un nombre de places libres. '
         'La disponibilité se vérifie auprès de l’établissement, ou via ViaTrajectoire dans les régions où le module grand âge est déployé.'),
        ('Peut-on savoir si un établissement peut accueillir une situation médicale précise&nbsp;?',
         'Non. Nous publions ce qui est déclaré dans les répertoires publics — unité protégée, accueil temporaire, évaluation de la qualité — '
         'mais aucune de ces informations ne permet d’affirmer qu’un établissement est «&nbsp;compatible&nbsp;» avec un état de santé donné. '
         'Cette appréciation revient au médecin coordonnateur de l’établissement.'),
        ('Faut-il créer un compte&nbsp;?',
         'Non, et il n’en existe pas. L’outil fonctionne sans inscription. La contrepartie est que rien n’est sauvegardé sur un serveur&nbsp;: '
         'les recherches enregistrées restent dans le navigateur de l’appareil utilisé.'),
        ('Peut-on partager une liste de démarches avec un collègue&nbsp;?',
         'Pas directement&nbsp;: il n’existe pas d’espace partagé. Vous pouvez exporter la liste en CSV et la transmettre par vos moyens habituels, '
         'en veillant à ce qu’elle ne contienne aucune donnée nominative — les notes que vous écrivez sont reprises telles quelles dans l’export.'),
        ('Les tarifs affichés sont-ils à jour&nbsp;?',
         f'Ils viennent du dernier fichier «&nbsp;prix et tarifs des EHPAD&nbsp;» publié par la CNSA ({CNSA_MAJ}), et sont donc à jour de cette publication, pas du jour. '
         f'{nb(s["n_prix"])} établissements sur {nb(s["n"])} y ont déclaré un tarif&nbsp;; pour les autres, aucun montant n’est affiché. '
         'Le tarif réel se confirme auprès de l’établissement.'),
        ('L’outil est-il gratuit, et financé par qui&nbsp;?',
         'Il est gratuit, sans publicité et sans partenariat avec des établissements ou des groupes gestionnaires&nbsp;: aucun établissement ne peut payer '
         'pour être mieux placé. <a href="/qui-sommes-nous.html">Qui nous sommes</a>.'),
    ]
    art(ctx, ecrire, '/professionnels/',
        'Trouvez les EHPAD adaptés aux personnes que vous accompagnez',
        'Identifiez rapidement les établissements compatibles avec le budget, la localisation et les aides disponibles, '
        'puis constituez votre liste de démarches.',
        corps, f'EHPAD : l’outil des professionnels de l’accompagnement | {MARQUE}',
        f'Outil gratuit pour les professionnels de l’accompagnement : {nb(s["n"])} EHPAD, '
        f'{nb(s["ash"] + s["ash_conf"])} habilités à l’aide sociale, reste à charge après aides et liste de démarches.',
        [('Espace professionnel', None)], faq=faq, prio=0.9, type_page='national', groupe='contenus')

    assistant_social(ctx, ecrire)


def assistant_social(ctx, ecrire):
    s = ctx['FR']
    corps = f"""<div class="note"><b>La réponse courte.</b> Deux questions décident presque toujours de l’orientation&nbsp;:
les ressources de la personne couvrent-elles le tarif d’hébergement une fois l’APA et l’aide au logement déduites&nbsp;?
Et si non, l’établissement est-il <b>habilité à l’aide sociale</b>&nbsp;? {nb(s['ash'] + s['ash_conf'])} des {nb(s['n'])}
EHPAD référencés le sont, mais la répartition varie fortement d’un département à l’autre.</div>

{cta('/?pro=1', 'Démarrer une recherche', 'seo_as_to_calculator',
     'Sans compte, sans identité à saisir. Tout reste dans votre navigateur.')}

<section><h2>Le parcours, tel qu’il se déroule</h2>
<ol class="etapes">
<li><b>Évaluer ce que la personne peut payer.</b> Retraites, pensions de réversion, revenus du patrimoine,
moins les charges qui subsistent. L’outil applique ensuite l’APA en établissement, l’aide au logement et la
réduction d’impôt, et affiche le reste à charge mensuel estimé, établissement par établissement.</li>
<li><b>Déterminer s’il faut l’aide sociale à l’hébergement.</b> Si le reste à charge dépasse durablement les
ressources disponibles, la recherche doit être limitée aux établissements habilités. Trois conséquences à
annoncer dès le premier entretien&nbsp;: le recours possible à l’obligation alimentaire des enfants, la
récupération sur la succession, et la participation des ressources de la personne à hauteur de 90&nbsp;%,
un minimum étant laissé à sa disposition.</li>
<li><b>Cibler une zone réaliste.</b> La distance avec la famille est le premier facteur de maintien du lien
après l’entrée. L’outil raisonne en rayon autour d’une commune, pas en frontières administratives&nbsp;:
un établissement du département voisin reste visible s’il est plus proche.</li>
<li><b>Constituer la liste de démarches.</b> Les établissements retenus passent dans une liste de suivi, avec
un état par établissement et une note libre. Chaque entrée porte son numéro FINESS, qui est l’identifiant
utilisé par les administrations et les caisses.</li>
<li><b>Déposer les dossiers.</b> Le dossier national d’admission (Cerfa 14732) reste la pièce commune&nbsp;;
la demande d’aide sociale se dépose au centre communal d’action sociale ou au conseil départemental, avec
des délais et des pièces qui varient selon le département.</li>
</ol>
</section>

<section><h2>Ce que l’outil ne remplace pas</h2>
<ul>
<li><b>ViaTrajectoire.</b> C’est l’outil de gestion des demandes d’admission&nbsp;; nous ne transmettons aucune candidature et n’avons pas accès à l’état des demandes.</li>
<li><b>L’appel à l’établissement.</b> Seul l’établissement connaît ses places, ses délais et sa liste d’attente réelle.</li>
<li><b>L’avis médical.</b> La compatibilité entre une situation clinique et une unité donnée relève du médecin coordonnateur.</li>
<li><b>Le règlement départemental d’aide sociale.</b> Les barèmes d’obligation alimentaire, les plafonds et les pièces exigées sont fixés département par département.</li>
</ul>
</section>

<section><h2>Les points sur lesquels les familles se trompent le plus</h2>
<div class="qa">
<details><summary><span>«&nbsp;Le prix affiché, c’est ce qu’on paiera&nbsp;»</span></summary><p>Le tarif d’hébergement n’est qu’une partie de la facture, et les aides en retirent une partie. Le reste à charge réel est presque toujours différent du prix affiché, dans les deux sens.</p></details>
<details><summary><span>«&nbsp;L’aide sociale, c’est gratuit&nbsp;»</span></summary><p>Elle est récupérable sur la succession, elle peut être demandée aux enfants au titre de l’obligation alimentaire, et elle mobilise 90&nbsp;% des ressources de la personne. <a href="/aides-ehpad/aide-sociale-hebergement/">Le détail</a>.</p></details>
<details><summary><span>«&nbsp;L’APA paiera la dépendance&nbsp;»</span></summary><p>Une participation reste toujours due, au minimum le tarif dépendance GIR 5-6, et elle augmente avec les ressources. <a href="/aides-ehpad/apa/">Le calcul exact</a>.</p></details>
<details><summary><span>«&nbsp;Il faut choisir un établissement dans son département&nbsp;»</span></summary><p>Rien ne l’impose. L’aide sociale suit la personne, avec des règles de domicile de secours qu’il faut vérifier auprès du département d’origine.</p></details>
</div>
</section>

<section><h2>Lancer une recherche</h2>
<p>Indiquez une commune, un rayon, le GIR et, si vous devez estimer un reste à charge, les ressources mensuelles.
Aucune identité n’est demandée et rien n’est transmis.</p>
{cta('/?pro=1', 'Ouvrir l’espace professionnel', 'seo_as_to_calculator_bas',
     second=('/aides-ehpad/aide-sociale-hebergement/', 'Revoir les règles de l’aide sociale', 'seo_as_to_ash'))}
</section>"""
    faq = [
        ('Combien d’EHPAD sont habilités à l’aide sociale&nbsp;?',
         f'{nb(s["ash"])} établissements sont habilités selon les répertoires publics, et {nb(s["ash_conf"])} le sont partiellement '
         'ou de façon à confirmer auprès du département. La proportion varie beaucoup selon les territoires&nbsp;: '
         '<a href="/aides-ehpad/aide-sociale-hebergement/">voir les règles et la répartition</a>.'),
        ('Peut-on saisir le nom de la personne accompagnée&nbsp;?',
         'Ce n’est ni demandé, ni souhaitable. L’outil fonctionne sans identifier qui que ce soit&nbsp;: nommez vos recherches '
         '«&nbsp;Dossier 001&nbsp;», «&nbsp;Recherche secteur nord&nbsp;», et n’écrivez aucune donnée nominative dans les notes de suivi, '
         'qui sont reprises telles quelles dans l’export CSV.'),
        ('Les données saisies sont-elles conservées&nbsp;?',
         'Les ressources et la situation saisies servent au calcul et ne sont pas enregistrées dans une recherche sauvegardée. '
         'Ce qui est conservé — zone, critères, liste de démarches — l’est uniquement dans le navigateur de l’appareil utilisé, '
         'sans transmission ni sauvegarde serveur. Vider le cache efface tout.'),
        ('L’outil calcule-t-il l’obligation alimentaire des enfants&nbsp;?',
         'Il estime une répartition indicative entre les enfants lorsque vous en indiquez le nombre, mais les barèmes réels sont fixés '
         'par chaque département et peuvent être révisés par le juge aux affaires familiales. Ce montant est une aide à la discussion, pas une décision.'),
        ('Peut-on l’utiliser depuis un poste hospitalier sans installation&nbsp;?',
         'Oui&nbsp;: c’est un site, sans installation, sans compte et sans cookie nécessaire au fonctionnement. La mesure d’audience est facultative '
         'et refusable d’un clic.'),
    ]
    art(ctx, ecrire, '/professionnels/assistant-social/',
        'EHPAD : l’outil de recherche des assistants de service social',
        'Évaluer ce que la personne peut payer, repérer les établissements habilités à l’aide sociale, '
        'puis suivre les démarches. Sans identité à saisir.',
        corps, f'EHPAD : outil pour assistant de service social | {MARQUE}',
        'Estimer le reste à charge après aides, repérer les EHPAD habilités à l’aide sociale '
        'et suivre les démarches — sans identité à saisir.',
        [('Espace professionnel', '/professionnels/'), ('Assistants de service social', None)],
        faq=faq, prio=0.8, type_page='national', groupe='contenus')


def construire(ctx, ecrire):
    prix(ctx, ecrire)
    prix_par_dep(ctx, ecrire)
    moins_chers(ctx, ecrire)
    calcul(ctx, ecrire)
    aides(ctx, ecrire)
    guides(ctx, ecrire)
    barometre(ctx, ecrire)
    professionnels(ctx, ecrire)
